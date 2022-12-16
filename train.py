import logging
import sys
import random
import torch
import torch.nn as nn
import numpy as np


import config

from model import Client, Environment
from utils import get_log_format


#device
device = torch.device('cpu')
#seed
if torch.cuda.is_available():
    torch.cuda.manual_seed(3427)
    device = torch.device('cuda') 
else:
    torch.manual_seed(3427)
random.seed(3427)
np.random.seed(3427)

#model
modelcfg = getattr(config.cfg, 'model')

#log
_logger = logging.getLogger(__name__)
_logger.setLevel(getattr(logging, getattr(config.cfg, 'loglevel')))
_handler = logging.StreamHandler(stream=sys.stdout)
_handler.setFormatter(logging.Formatter(get_log_format(thread_info=True)))
_logger.addHandler(_handler)



if __name__=='__main__':

    model = Client(1, 4).to(device=device)

    env = Environment(memory_max_len=modelcfg.replay_memory_size)

    optimizer = torch.optim.Adam(model.parameters(), lr=modelcfg.lr)
    criterion = nn.MSELoss()


    epoch = 0
    while epoch < modelcfg.epochs:
        
        epsilon = modelcfg.final_epsilon + (max(modelcfg.num_decay_epochs - epoch, 0) * (
            modelcfg.initial_epsilon - modelcfg.final_epsilon) / modelcfg.num_decay_epochs)
        
        u = random.random()

