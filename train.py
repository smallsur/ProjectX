import logging
import sys
import random
import torch
import torch.nn as nn
import numpy as np

from collections import deque
import config

from model import Client, Environment, DeepQNetwork
from utils import get_log_format


#device
device = torch.device('cpu')
#seed
if torch.cuda.is_available():
    torch.cuda.manual_seed(3407)
    device = torch.device('cuda') 
else:
    torch.manual_seed(3407)
random.seed(3407)
np.random.seed(3407)

#model
modelcfg = getattr(config.cfg, 'model')

#log
_logger = logging.getLogger(__name__)
_logger.setLevel(getattr(logging, getattr(config.cfg, 'loglevel')))
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter(get_log_format(thread_info=True)))
_logger.addHandler(_handler)



if __name__=='__main__':

    model = Client(1, 5).to(device=device)

    env = Environment()
    
    optimizer = torch.optim.Adam(model.parameters(), lr=modelcfg.lr)
    criterion = nn.MSELoss()

    state = [t.to(device=device) for t in env.reset_state()]
    
    replay_memory = deque(maxlen=modelcfg.replay_memory_size)
    
    epoch = 0
    count = 0
    while epoch < modelcfg.epochs:
        next_steps = env.pre_step()
        
        epsilon = modelcfg.final_epsilon + (max(modelcfg.num_decay_epochs - epoch, 0) * (
            modelcfg.initial_epsilon - modelcfg.final_epsilon) / modelcfg.num_decay_epochs)
        
        u = random.random()
        
        random_action = u <= epsilon

        next_actions, next_states = zip(*next_steps.items())
        
        next_properties, next_states, next_dones = zip(*next_states)
        
        next_properties = torch.stack(next_properties).to(device=device)
        next_states = torch.stack(next_states).to(device=device)
        model.eval()
        
        with torch.no_grad():
            predictions = model(next_states.unsqueeze(1), next_properties)
        
        model.train()
        
        if random_action:
            index = random.randint(0, len(next_steps) - 1)
        else:
            index = torch.argmax(predictions, dim=0)
        
        next_state = next_states[index].to(device=device)
        next_property = next_properties[index].to(device=device)
        action = next_actions[index]
        done = next_dones[index]
        
        reward = env.step({'properties':next_property, 'state':next_state, 'gameover':done})
        
        next_ = [next_state, next_property]
        replay_memory.append([state, reward, next_, done])
        count += 1
        print(count)
        if done:
            final_score = env.score
            final_count_step = env.step_count
            final_count_line = env.lines_count
            
            state = [t.to(device=device) for t in env.reset_state()]
        else:
            state = next_
            continue
        if len(replay_memory) < modelcfg.replay_memory_size / 10:
            continue
        
        epoch +=1
        
        batch = random.sample(replay_memory, min(len(replay_memory), model.batch_size))
        
        state_batch, reward_batch, next_state_batch, done_batch = zip(*batch)
        
        state_batch, property_batch = zip(*state_batch)
        next_state_batch, next_property_batch = zip(*next_state_batch)
        
        reward_batch = torch.from_numpy(np.array(reward_batch, dtype=np.float32))
        next_state_batch = torch.stack(next_state_batch)
        next_property_batch = torch.stack(next_property_batch)
        state_batch = torch.stack(state_batch)
        property_batch = torch.stack(property_batch)
        q_values = model(state_batch.unsqueeze(1), property_batch)
        
        model.eval()
        with torch.no_grad():
            next_prediction_batch = model(next_state_batch.unsqueeze(1), next_property_batch)
            
        model.train()
        
        y_batch = torch.cat(tuple(reward if done else reward + modelcfg.gamma * prediction for reward, done, prediction in
                  zip(reward_batch, done_batch, next_prediction_batch)))[:, None]
        
        optimizer.zero_grad()
        loss = criterion(q_values, y_batch)
        loss.backward()
        optimizer.step()
        
        print("Training-Epoch: {}/{}, Score: {}, step_count {}, Cleared lines: {}".format(
            epoch,
            modelcfg.epochs,
            final_score,
            final_count_step,
            final_count_line))
        ###############eval###############
        eval_done = False
        while not eval_done:
            eval_next_steps = env.pre_step()
            eval_next_actions, eval_next_states = zip(*eval_next_steps.items())
            eval_next_properties, eval_next_states, eval_next_dones = zip(*eval_next_states)
            eval_next_properties = torch.stack(eval_next_properties).to(device=device)
            eval_next_states = torch.stack(eval_next_states).to(device=device)
                  
            model.eval()
            with torch.no_grad():
                eval_predictions = model(eval_next_states.unsqueeze(1), eval_next_properties)
            index = torch.argmax(predictions, dim=0)
            
            eval_next_state = eval_next_states[index].to(device=device)
            eval_next_property = eval_next_properties[index].to(device=device)
            eval_action = eval_next_actions[index]
            eval_done = eval_next_dones[index]
            
            env.step({'properties':eval_next_property, 'state':eval_next_state, 'gameover':eval_done})
            
        
        capacity = np.sum(env.state_box!=0) / np.cumprod(env.state_box.shape)[-1]
        print("Testing-Epoch: {}/{}, Score: {}, step_count {}, Cleared lines: {}, capacity: {}".format(
            epoch,
            modelcfg.epochs,
            env.score,
            env.step_count,
            env.lines_count, 
            capacity))
        state = [t.to(device=device) for t in env.reset_state()]  
            
        if epoch > 0 and epoch % modelcfg.save_interval == 0:
            torch.save(model, "{}/tetris_{}".format(modelcfg.save_path, epoch))
        
        
        
        