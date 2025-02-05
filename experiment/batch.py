import numpy as np
from replay import ReplayMode

def load_batch(path='batch.txt'):
    batch = []
    
    with open(path,'r') as f:
        for line in f.readlines():
            rank, id, mode = line.split("\n")[0].split()
            
            try:
                rank = int(rank)
            except ValueError:
                id = 0
            
            try:
                id = int(id)
            except ValueError:
                id = 1
            
            if mode.startswith("GP"):
                percentage = mode[2:]
                mode = ReplayMode.CONGRUENT
            elif mode.startswith("G"):
                percentage = ""
                mode = ReplayMode.HEADONLY
            elif mode.startswith("P"):
                percentage = mode[1:]
                mode = ReplayMode.NEUTRAL
            elif mode.startswith("I"):
                percentage = mode[1:]
                mode = ReplayMode.INCONGRUENT
            
            try:
                percentage = int(percentage)
            except ValueError:
                percentage = 0

            batch.append((rank, id, percentage, mode))

    batch.append((-1, -1, 0, ReplayMode.END))
    return np.array(batch)

def shuffle_batch(batch):
    bunches = []
    used = set()
    usedmode = None
    for _, id, _, mode in batch:
        if id in used or (usedmode is not None and mode != usedmode):
            bunches.append(len(used))
            used.clear()
        used.add(id)
        usedmode = mode
    bunches.append(len(used))
    #print(bunches)
    #print(np.sum(bunches))
    offset = 0
    for bunch in bunches:
        if bunch > 1:
            np.random.shuffle(batch[offset:offset+bunch])
        offset += bunch
    #print([trial[1] for trial in batch])
    
if __name__ == '__main__':
    batch = load_batch('batch1.txt')
    shuffle_batch(batch)
    