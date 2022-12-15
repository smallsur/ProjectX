from collections import deque




class Environment:
    def __init__(self, memory_max_len, box) -> None:
        self.memory = deque(maxlen=memory_max_len)
        

    
    
