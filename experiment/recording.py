import os
import time
from datetime import datetime
import numpy as np
from replay import ReplayMode

points = {
    1 : [1200, 841],
    2 : [1429, 612],
    3 : [1658, 841],
    4 : [1429, 1070],
    5 : [971, 1070],
    6 : [742, 841],
    7 : [971, 612],
}

def get_point(id):
    return points[id]

#modes = ["unknown","congruent","incongruent","head only","neutral"]
modes = ["-","GP","I","G","P"]

def record(name, i, id, contraid, percentage, mode, point):
    timestamp = time.time()
    # Get the current date and time
    current_datetime = datetime.now()
    # Convert it to a string in a specific format
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    if point is not None:
        distance = np.linalg.norm(np.array(points[id])-np.array(point))
    else:
        distance = -1000.0
        point = (-1000.0,-1000.0)
    
    filename = f"d:/recordings/{name}/trials.txt"

    if not os.path.exists(filename):
        with open(filename,'wt') as f:
            f.write('rank,percentage,mode[int],mode[str],trajectory id[1-7],gaze id[1-7],goal point x[px],goal point y[px],guessed point x[px],guessed point y[px],distance[px],timestamp[s from 1970],date and time\n')
    
    if mode == ReplayMode.NEUTRAL:
        contraid = -1
    if mode == ReplayMode.HEADONLY:
        id = -1
    
    with open(filename,'at') as f:
        f.write(f'{i},{percentage},{mode},{modes[mode]},{id},{contraid},{points[id][0]},{points[id][1]},{point[0]},{point[1]},{distance},{timestamp},{current_datetime_str}\n')
