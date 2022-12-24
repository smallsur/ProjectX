import logging
import sys
import random
import torch
import torch.nn as nn
import numpy as np

from collections import deque
import config

from model import Client, Environment, DeepQNetwork_Two
from utils import get_log_format

modelcfg = getattr(config.cfg, 'model')

#device
device = torch.device('cpu')
#seed
if torch.cuda.is_available():
    torch.cuda.manual_seed(3407)
    torch.cuda.set_device(modelcfg.gpu_id)
    device = torch.device('cuda') 
    
else:
    torch.manual_seed(3407)
random.seed(3407)
np.random.seed(3407)

#model


#log
_logger = logging.getLogger(__name__)
_logger.setLevel(getattr(logging, getattr(config.cfg, 'loglevel')))
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter(get_log_format(thread_info=True)))
_logger.addHandler(_handler)



if __name__=='__main__':


    env = Environment()
    
    model = DeepQNetwork_Two(15*15*2).to(device=device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=modelcfg.lr)
    criterion = nn.MSELoss()

    state = env.reset_state()[0].to(device=device)
    
    replay_memory = deque(maxlen=modelcfg.replay_memory_size)
    
    epoch = 0
    # count = 0
    while epoch < modelcfg.epochs:
        next_steps = env.pre_step()

        epsilon = modelcfg.final_epsilon + (max(modelcfg.num_decay_epochs - epoch, 0) * (
            modelcfg.initial_epsilon - modelcfg.final_epsilon) / modelcfg.num_decay_epochs)
        
        u = random.random()
        
        random_action = u <= epsilon

        next_actions, next_states = zip(*next_steps.items())
        
        next_diffs, next_capacities, next_states, next_dones = zip(*next_states)
        
        next_diffs = torch.stack(next_diffs).to(device=device)
        model.eval()
        
        with torch.no_grad():
            predictions = model(next_diffs)
        
        model.train()

        if random_action:
            index = random.randint(0, len(next_steps) - 1)
        else:
            index = torch.argmax(predictions, dim=0)
        
        #下一步状态,数据存在device上，
        next_diff = next_diffs[index].squeeze(0).to(device=device)
        
        #更新准备，numpy数据，位置一直在内存中，next_state是在env中的拷贝
        next_capacity = next_capacities[index]
        next_state = next_states[index]
        done = next_dones[index]
        
        #更新状态，计算奖励
        reward = env.step(next_capacity, next_state, done)
        
        # next_ = next_property
        replay_memory.append([state, reward, next_diff, done])
        # count += 1
        # print(count)
        if done:
            final_score = env.score
            final_count_step = env.step_count
            final_count_line = env.lines_count
            print('step')
            state = env.reset_state()[0].to(device=device)
        else:
            state = next_diff
            continue
        if len(replay_memory) < modelcfg.replay_memory_size / 10:
            continue
        
        epoch += 1
        
        batch = random.sample(replay_memory, min(len(replay_memory), modelcfg.batch_size))
        
        state_batch, reward_batch, next_state_batch, done_batch = zip(*batch)

        reward_batch = torch.from_numpy(np.array(reward_batch, dtype=np.float32))[:,None].to(device=device)
        next_state_batch = torch.stack(next_state_batch)

        state_batch = torch.stack(state_batch)

        q_values = model(state_batch)
        model.eval()
        with torch.no_grad():
            next_prediction_batch = model(next_state_batch)
            
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
        state = env.reset_state()[0].to(device=device)
        while not eval_done:
            eval_next_steps = env.pre_step(eval=True)
            eval_next_actions, eval_next_states = zip(*eval_next_steps.items())
            eval_next_diffs, eval_next_capacities, eval_next_states, eval_next_dones = zip(*eval_next_states)
            eval_next_diffs = torch.stack(eval_next_diffs).to(device=device)

            model.eval()
            with torch.no_grad():
                eval_predictions = model(eval_next_diffs)
            index = torch.argmax(eval_predictions, dim=0)

            eval_next_state = eval_next_states[index]
            eval_next_capacity = eval_next_capacities[index]
            eval_done = eval_next_dones[index]
            
            env.step(eval_next_capacity, eval_next_state, eval_done)
            
        
        capacity = np.sum(env.state_box!=0) / np.cumprod(env.state_box.shape)[-1]
        print("Testing-Epoch: {}/{}, Score: {}, step_count {}, Cleared lines: {}, capacity: {}".format(
            epoch,
            modelcfg.epochs,
            env.score,
            env.step_count,
            env.lines_count, 
            capacity))
        state = env.reset_state()[0].to(device=device)


        
        