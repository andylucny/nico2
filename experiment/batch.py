from replay import ReplayMode

def load_batch(path='batch.txt'):
    batch = []
    
    with open(path,'r') as f:
        for line in f.readlines():
            rank, id, mode = line.split("\n")[0].split()
            
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
                percentage = 20

            batch.append((rank, id, percentage, mode))

    return batch

if __name__ == '__main__':
    batch = load_batch()
    