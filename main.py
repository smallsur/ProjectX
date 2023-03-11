import logging
import random

# from database import create_or_update_district, create_or_update_district_include_rel
# from database import getdistrict_by_name
from utils import get_log_format
from model import match_trucks_with_cargos
import config

logfile = getattr(config.cfg, 'logfile')

logging.basicConfig(level=logging.DEBUG, format=get_log_format(thread_info=True, process_info=True), filename=logfile, filemode='w')

#35种
cargos =        [[1, 1, 1],[1, 1, 2],[1, 1, 3],[1, 1, 4],[1, 1, 5],
                    [2, 2, 2],[2, 2, 3],[2, 2, 4],[2, 2, 5],[2, 3, 3],
                    [2, 3, 4],[2, 3, 5],[2, 4, 4],[2, 4, 5],[2, 5, 5],
                    [3, 3, 3],[3, 3, 4],[3, 3, 5],[3, 4, 4],[3, 4, 5],
                    [3, 5, 5],[4, 4, 4],[4, 4, 5],[4, 5, 5],[5, 5, 5]]

#10种
boxes = [[20,20,20],[30,30,30],
             [20,20,30],
             [20,30,30]]

def generateTruck(numTruck = 3, ):
    ans = []
    trucks = random.sample(boxes, k=numTruck)
    for truck in trucks:
        numTruck_every = random.randint(1,3)
        
        ans.extend({'length':truck[0], 'width':truck[1], 'height':truck[2], 'load_capacity':truck[0]*truck[1]*truck[2]} for _ in range(numTruck_every))
    return ans

def generateCargo():
    ans = []
    for cargo in cargos:
        numTruck_every = random.randint(50,100)
        ans.extend({'length':cargo[0], 'width':cargo[1], 'height':cargo[2], 'weight':cargo[0]*cargo[1]*cargo[2]} for _ in range(numTruck_every))
    
    return ans

result,capacity = match_trucks_with_cargos(generateTruck(),generateCargo())

print(result)

for l in result:
    print(l[-1])

print(capacity)
