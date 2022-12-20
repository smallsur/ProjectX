from .network import ThreeD_Net

class Client(ThreeD_Net):
    def __init__(self, input_channel, state_dim):
        super(Client, self).__init__(input_channel, state_dim)
        
    def step(self):
        pass
    