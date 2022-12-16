import numpy as np
from collections import deque



class Environment:
    box_shape = (70, 30, 30)
    def __init__(self, memory_max_len) -> None:
        self.memory = deque(maxlen=memory_max_len)
        
        self.box = np.zeros(shape=self.box_shape, dtype=np.float32)

    def get_state(self):
        pass
        
