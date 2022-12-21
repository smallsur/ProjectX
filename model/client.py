import torch
import torch.nn as nn
from .network import ThreeD_Net

class Client(ThreeD_Net):
    def __init__(self, input_channel, state_dim, compress_size):
        super(Client, self).__init__(input_channel, state_dim)
        # nn.AdaptiveAvgPool3d((compress_size, compress_size, compress_size))
        
    def step(self):
        pass
    