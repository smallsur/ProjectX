import numpy as np
import random
import itertools
import torch
from collections import deque


box_shape = (15, 15, 15)


materials_shape =  [[1, 1, 1],[1, 1, 2],[1, 1, 3],[1, 1, 4],[1, 1, 5],
                    [1, 2, 2],[1, 2, 3],[1, 2, 4],[1, 2, 5],[1, 3, 3],
                    [1, 3, 4],[1, 3, 5],[1, 4, 4],[1, 4, 5],[1, 5, 5],
                    [2, 2, 2],[2, 2, 3],[2, 2, 4],[2, 2, 5],[2, 3, 3],
                    [2, 3, 4],[2, 3, 5],[2, 4, 4],[2, 4, 5],[2, 5, 5],
                    [3, 3, 3],[3, 3, 4],[3, 3, 5],[3, 4, 4],[3, 4, 5],
                    [3, 5, 5],[4, 4, 4],[4, 4, 5],[4, 5, 5],[5, 5, 5]]

# materials_weight = [sum(m) for m in materials_shape]
###############################################################################
def clear_lines(box_state, lines):
    '''clear lines in box, and fill zero to box'''
    box_state = np.delete(box_state, lines, axis=2)   
    box_state = np.insert(box_state, [0 for i in range(len(lines))], values=0, axis=2)
        
    return box_state

def get_cleared_lines(box_state, eval=False):
    '''get clear line count,and the new box state'''
    count = 0
    _, _, height = box_state.shape
    lines = []
    for i in range(height):
        if np.all(box_state[:, :, i] != 0):
            count =count + 1
            lines.append(i)
    if not eval:
        box_state = clear_lines(box_state, lines)
    return count, box_state

def get_holes(box_state):
    count = 0
    length, width, height = box_state.shape
    for x in  range(length):
        for y in range(width):
            idx = 0
            while idx < height and box_state[x, y, idx] == 0:
                idx += 1
            while idx < height:
                if box_state[x, y, idx] == 0:
                    count += 1
                idx +=1         
    return count

def get_sum_height(box_state):
    height = box_state.shape[-1]
    mask = box_state != 0
    invert_heights = np.where(mask.any(axis=2), np.argmax(mask, axis=2), height)
    heights = height - invert_heights
    total_height = np.sum(heights)
    currs_x = heights[:-1]
    nexts_x = heights[1:]
    diffs_x = np.sum(np.abs(currs_x - nexts_x))
    currs_y = heights[:, :-1]
    nexts_y = heights[:, 1:]
    diffs_y = np.sum(np.abs(currs_y - nexts_y))

    return diffs_x, diffs_y, total_height

def get_state(box_state, eval=False):

    num_lines, box_state=get_cleared_lines(box_state, eval)

    
    num_holes = get_holes(box_state)
    diff_x, diff_y, sum = get_sum_height(box_state)
    
    return torch.FloatTensor([num_lines, num_holes, diff_x, diff_y, sum])



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
        
        return [torch.FloatTensor(self.state_box.copy()), get_state(self.state_box)]
        
 

    def rotate_material(self, material):
        return set(itertools.permutations(material))

    def pre_step(self, eval=False):
        states = {}
        
        cur_material = self.get_next_material()
        length, width, height = self.state_box.shape
        
        for i, s in enumerate(self.rotate_material(cur_material)):
            vaildx = length - s[0]
            vaildy = width - s[1]
            
            for x in range(vaildx + 1):
                for y in range(vaildy + 1):
                    pos = {'x':x, 'y':y, 'z':0}
                    while pos['z'] < height - 1 and not self.check_collision(pos, s):
                        pos['z'] = pos['z'] + 1
                    done = self.check_gameover(pos, s)
                    
                    new_state = self.next_box_state(pos, s, done)
             
                    properties = get_state(new_state, eval)
                    states[(x, y, i)] = [properties, torch.FloatTensor(new_state), done]
                    # print("%d-%d"%(x, y))       
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
                if self.state_box[x + pos['x'], y + pos['y'], pos['z']] != 0:
                    return True
        return False
    
    def check_gameover(self, pos, material_shape):
        _, _, height = material_shape
        
        if height <= pos['z']+1:
            return False
        
        return True
   
    def next_box_state(self, pos, material_shape, done):
        new_state = self.state_box.copy()
        if not done:
            new_state[pos['x']:pos['x'] + material_shape[0], pos['y']:pos['y'] + material_shape[1], pos['z'] - material_shape[2] + 1:pos['z'] + 1] = 1
        else:
            new_state[pos['x']:pos['x'] + material_shape[0], pos['y']:pos['y'] + material_shape[1], :pos['z']+1] = 1
        
        return new_state
    
    def step(self,  state):
        self.state_box[:] = state['state'].cpu()[:]
        self.game_over = state['gameover']
        
        score = 1 + (state['properties'][0] ** 2) * 10
        self.score += score
        
        self.step_count += 1
        
        self.lines_count += state['properties'][0]
        
        if self.game_over:
            self.score -= 2
            
        return score
