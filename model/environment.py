import numpy as np
import random
import itertools
import torch
from collections import deque
from utils import run_time

box_shape = (15, 15, 15)


materials_shape =  [[1, 1, 1],[1, 1, 2],[1, 1, 3],[1, 1, 4],[1, 1, 5],
                    [1, 2, 2],[1, 2, 3],[1, 2, 4],[1, 2, 5],[1, 3, 3],
                    [1, 3, 4],[1, 3, 5],[1, 4, 4],[1, 4, 5],[1, 5, 5],
                    [2, 2, 2],[2, 2, 3],[2, 2, 4],[2, 2, 5],[2, 3, 3],
                    [2, 3, 4],[2, 3, 5],[2, 4, 4],[2, 4, 5],[2, 5, 5],
                    [3, 3, 3],[3, 3, 4],[3, 3, 5],[3, 4, 4],[3, 4, 5],
                    [3, 5, 5],[4, 4, 4],[4, 4, 5],[4, 5, 5],[5, 5, 5]]

clear_threshold = 0.5

discount = 0.1

# clear_max_reward = 
# materials_weight = [sum(m) for m in materials_shape]
###############################################################################
def clear_lines(box_state, lines):
    '''clear lines in box, and fill zero to box'''
    if len(lines) == 0:
        return box_state
    box_state = np.delete(box_state, lines, axis=2)
    box_state = np.insert(box_state, [0 for i in range(len(lines))], values=0, axis=2)
    return box_state

def get_cleared_lines(box_state, eval=False):
    '''get clear line count,and the new box state'''
    length, width, height = box_state.shape
    _state = box_state != 0
    _lines = np.sum(_state, axis=(0,1))
    _line_full = np.full_like(_lines, fill_value=length * width)
    
    capacities = _lines / _line_full
    
    index = capacities > clear_threshold
    lines = np.argwhere(index).reshape(-1)
    capacities = capacities[index]
    if eval:
        lines = []
    box_state = clear_lines(box_state, lines)        
    return capacities, box_state

def get_height_with_holes(box_state):
    height = box_state.shape[-1]
    mask = box_state != 0
    invert_heights = np.where(mask.any(axis=2), np.argmax(mask, axis=2), height)
    heights = height - invert_heights
    
    holes = heights - np.sum(mask, axis=2)
    
    return np.stack([heights, holes])



def get_state(box_state, eval=False):

    capacities, box_state = get_cleared_lines(box_state, eval)

    diff = get_height_with_holes(box_state)
    
    return torch.FloatTensor(diff), capacities, box_state.copy()


###############################################################################

################################################################################
class Environment:
    def __init__(self):
        self.state_box = np.zeros(shape=box_shape, dtype=np.float32)
        self.game_over = False
        self.cur_material = None
        self.match_candicates = []
        self.score = 0
        self.step_count = 0
        self.lines_count = 0
    
    def generate_candicate(self, num)->list:
        candicates = random.sample(materials_shape, k=num)

        candicates_weight = [sum(m) for m in candicates]
        max_weight = max(candicates_weight)
        candicates_num = [int(max_weight/w) for w in candicates_weight]

        match_candicates = [candicates[i]  for i in range(len(candicates)) for j in  range(candicates_num[i])]
        
        #俩次打乱
        random.shuffle(match_candicates)
        random.shuffle(match_candicates)

        return match_candicates

    def reset_state(self):
        self.state_box[:] = 0.0
        self.game_over = False
        self.score = 0
        self.step_count = 0
        self.lines_count = 0
        
        return get_state(self.state_box)

 

    def rotate_material(self, material):
        return set(itertools.permutations(material))
    
    # @run_time
    def pre_step(self, eval=False):
        states = {}
        
        cur_material = self.get_next_material()
        length, width, height = self.state_box.shape
        
        for i, s in enumerate(self.rotate_material(cur_material)):
            vaildx = length - s[0]
            vaildy = width - s[1]

            for x in range(vaildx + 1):
                for y in range(vaildy + 1):
                    pos = {'x':x, 'y':y, 'z':-1}
                    
                    while pos['z'] < height -1 and not self.check_collision(pos, s):
                        pos['z'] = pos['z'] + 1
                    done = self.check_gameover(pos, s)
                    
                    new_state = self.next_box_state(pos, s, done)

                    diff, capacities, new_state = get_state(new_state, eval)

                    states[(x, y, i)] = [diff, capacities, new_state, done]
        return states
    
    def get_next_material(self):
        if len(self.match_candicates) == 0:
            self.match_candicates = self.generate_candicate(10)
        self.cur_material = self.match_candicates.pop()
        return self.cur_material
                    
               
    def check_collision(self, pos, material_shape):
        length, width, _ = material_shape
        for x in range(length):
            for y in range(width):
                if self.state_box[x + pos['x'], y + pos['y'], pos['z'] + 1] != 0:
                    return True
        return False
    
    def check_gameover(self, pos, material_shape):
        _, _, height = material_shape
        
        if pos['z'] != -1 and height <= pos['z']+1:
            return False
        
        return True
   
    def next_box_state(self, pos, material_shape, done):
        new_state = self.state_box.copy()
        if not done:
            new_state[pos['x']:pos['x'] + material_shape[0], pos['y']:pos['y'] + material_shape[1], pos['z'] - material_shape[2] + 1:pos['z'] + 1] = 1
        else:
            new_state[pos['x']:pos['x'] + material_shape[0], pos['y']:pos['y'] + material_shape[1], :pos['z']+1] = 1
        
        return new_state

    def step(self, capacity, state,  done):
        self.state_box[:] = state[:]
        self.game_over = done
        
        score = 1
        count = len(capacity)
        
        for c in capacity:
            score += (count ** 2) * (c-discount)
            
        self.score += score
        
        self.step_count += 1
        
        self.lines_count += count
        
        if self.game_over:
            self.score -= 2
            
        return score
