import numpy as np
import random
import itertools
from collections import deque


box_shape = (70, 30, 30)


materials_shape =  [[1, 1, 1],[1, 1, 2],[1, 1, 3],[1, 1, 4],[1, 1, 5],
                    [1, 2, 2],[1, 2, 3],[1, 2, 4],[1, 2, 5],[1, 3, 3],
                    [1, 3, 4],[1, 3, 5],[1, 4, 4],[1, 4, 5],[1, 5, 5],
                    [2, 2, 2],[2, 2, 3],[2, 2, 4],[2, 2, 5],[2, 3, 3],
                    [2, 3, 4],[2, 3, 5],[2, 4, 4],[2, 4, 5],[2, 5, 5],
                    [3, 3, 3],[3, 3, 4],[3, 3, 5],[3, 4, 4],[3, 4, 5],
                    [3, 5, 5],[4, 4, 4],[4, 4, 5],[4, 5, 5],[5, 5, 5]]

# materials_weight = [sum(m) for m in materials_shape]
class Environment:

    def __init__(self, memory_max_len):
        self.memory = deque(maxlen=memory_max_len) 
        self.state_box = np.zeros(shape=box_shape, dtype=np.float32)
        self.state_implicit = {}
        self.game_over = False
        self.match_candicates = self.generate_candicate(10)
    
    def generate_candicate(self, num)->list:
        candicates = random.sample(materials_shape, k=num)

        candicates_weight = [sum(m) for m in candicates]
        max_weight = max(candicates_weight)
        candicates_num = [int(max_weight/w) for w in candicates_weight]

        match_candicates = [candicates[i] * candicates_num[i] for i in range(len(candicates))]
        
        #俩次打乱
        match_candicates = random.shuffle(match_candicates)
        match_candicates = random.shuffle(match_candicates)

        return match_candicates
    
    def reset_state(self):
        self.state_box[:] = 0.0
        self.match_candicates = self.generate_candicate(10)
        self.game_over = False
        for k, v in self.state_implicit:
            self.state_implicit[k] = 0.0


    def rotate_material(self, material):
        return itertools.permutations(material)

    def get_state(self):
        state = []
        for k, v in self.state_implicit:
            state.append(v)

        return state
    
    def step(self):
        states = {}
        cur_material = self.match_candicates.pop()



