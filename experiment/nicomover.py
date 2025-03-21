import time
import os
import numpy as np
try:
    from nicorobot import NicoRobot
    import requests
    motorConfig = 'nico_humanoid_upper_rh7d_ukba.json'

    def download_config(path,url):
        if os.path.exists(path):
            return
        print("downloading",path)
        response = requests.get(url+path)
        if response.ok:
            print("saving",path)
            open(path,"wb").write(response.content)
            
    download_config(motorConfig, "http://www.agentspace.org/download/")
    
    robot = NicoRobot(motorConfig=motorConfig)
    simulated = False
    print('robot ready')
except:
    simulated = True
    from nicodummy import DummyRobot
    robot = DummyRobot()
    print('simulator ready')

from thread_priority import get_thread_priority, set_thread_priority

def release():
    try:
        del robot
    except:
        pass
    
def load_movement(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        dofs = eval(lines[0])
        postures = []
        for line in lines[1:]:
            angles = eval(line[:-1])
            posture = {
                dof : angle for dof, angle in zip(dofs, angles)
            }
            postures.append(posture)
        return postures
    raise(BaseException(filename+" does not exist"))

def enableTorque(dofs=None):
    if dofs is None:
        dofs = robot.getJointNames()
    for dof in dofs:
        if dof != 'timestamp':
            robot.enableTorque(dof)

def disableTorque(dofs=None):
    if dofs is None:
        dofs = robot.getJointNames()
    for dof in dofs:
        if dof != 'timestamp':
            robot.disableTorque(dof)

def setAngle(dof, angle, speed=0.04):
    robot.setAngle(dof, float(angle), speed)

def getAngle(dof):
    return robot.getAngle(dof)
    
def current_posture(dofs=None):
    if dofs is None:
        dofs = robot.getJointNames()
    posture = { 
        dof : getAngle(dof) for dof in dofs 
    }
    return posture
    
def move_to_posture(target_posture, speed=0.04, wait=False):
    for dof in target_posture:
        if dof != 'timestamp':
            setAngle(dof, target_posture[dof], speed)
    if wait:
        current_posture = {
            dof : getAngle(dof) for dof in target_posture
        }
        durations = [ 
            abs(current_posture[dof] - target_posture[dof]) / (1260*speed) for dof in current_posture 
        ]
        duration = np.max(durations)
        time.sleep(duration)

def move_to_posture_through_time(target_posture, duration):
    if duration == 0:
        return
    current_posture = {
        dof : getAngle(dof) for dof in target_posture
    }
    speed_to_reach = {
        dof: abs(current_posture[dof] - target_posture[dof]) / float(1260*duration) for dof in current_posture
    }
    for dof in target_posture:
        setAngle(dof, target_posture[dof], speed_to_reach[dof])

def blind_move_to_posture_through_time(current_posture, target_posture, duration):
    if duration == 0:
        return
    speed_to_reach = {
        dof: abs(current_posture[dof] - target_posture[dof]) / float(1260*duration) for dof in current_posture
    }
    for dof in target_posture:
        setAngle(dof, target_posture[dof], speed_to_reach[dof])

def play_movement(postures, durations=None):
    if len(postures) == 0:
        return
    if durations is None and 'timestamp' in postures[0]:
        timestamps = np.array([ posture['timestamp'] for posture in postures ]) / 1000.0
        durations = [timestamps[0]] + list(timestamps[1:] - timestamps[:-1])
    if durations is None:
        durations = [ 1000 ] * len(postures) # default 1s
    for posture, duration in zip(postures, durations):
        command = {
            dof : posture[dof] for dof in posture if dof != 'timestamp' 
        }
        t0 = time.time()
        move_to_posture_through_time(command, duration)
        t1 = time.time()
        if t1-t0 > duration:
            print(f'BAD {t1-t0} > {duration}')
        time.sleep(duration) 

def blind_play_movement(postures, durations=None):
    if len(postures) == 0:
        return
    if durations is None and 'timestamp' in postures[0]:
        timestamps = np.array([ posture['timestamp'] for posture in postures ]) / 1000.0
        durations = [timestamps[0]] + list(timestamps[1:] - timestamps[:-1])
    if durations is None:
        durations = [ 1000 ] * len(postures) # default 1s
    prio = get_thread_priority()
    set_thread_priority(prio+1)
    for previous_posture, posture, duration in zip(postures[:-1], postures[1:], durations[1:]):
        previous_pose = {
            dof : previous_posture[dof] for dof in previous_posture if dof != 'timestamp' 
        }
        pose = {
            dof : posture[dof] for dof in posture if dof != 'timestamp' 
        }
        t0 = time.time()
        blind_move_to_posture_through_time(previous_pose, pose, duration)
        t1 = time.time()
        if t1-t0 > duration:
            print(f'BAD {t1-t0} > {duration}')
        time.sleep(max(0,duration-(t1-t0)+0.01)) #the bulgarian constant is neccessary for fluent movements
    set_thread_priority(prio)

def park():
    safe = { # standard position for experiment
        'head_y': 0.0,
        'head_z': 0.0,
        'l_arm_x': 8.0,
        'l_elbow_y': 110.0,
        'l_indexfinger_x': -180.0,
        'l_middlefingers_x': -180.0,
        'l_shoulder_y': 19.0,
        'l_shoulder_z': -20.0,
        'l_thumb_x': -180.0,
        'l_thumb_z': -69.0,
        'l_wrist_x': -52.0,
        'l_wrist_z': -13.0,
        'r_arm_x': 8.0,
        'r_elbow_y': 110.0,
        'r_indexfinger_x': -180.0,
        'r_middlefingers_x': -180.0,
        'r_shoulder_y': 19.0,
        'r_shoulder_z': -20.0,
        'r_thumb_x': -180.0,
        'r_thumb_z': -69.0,
        'r_wrist_x': -52.0,
        'r_wrist_z': -13.0
    }
    """
    safe = { # standard position
        'l_shoulder_z':0.0,
        'l_shoulder_y':0.0,
        'l_arm_x':0.0,
        'l_elbow_y':89.0,
        'l_wrist_z':0.0,
        'l_wrist_x':-56.0,
        'l_thumb_z':-57.0,
        'l_thumb_x':-180.0,
        'l_indexfinger_x':-180.0,
        'l_middlefingers_x':-180.0,
        'r_shoulder_z':0.0,
        'r_shoulder_y':0.0,
        'r_arm_x':0.0,
        'r_elbow_y':89.0,
        'r_wrist_z':0.0,
        'r_wrist_x':-56.0,
        'r_thumb_z':-57.0,
        'r_thumb_x':-180.0,
        'r_indexfinger_x':-180.0,
        'r_middlefingers_x':-180.0,
        'head_z':0.0,
        'head_y':0.0
    }
    """
    move_to_posture(safe)
    
def half_duplex(dofs=None):
    if dofs is None:
        dofs = robot.getJointNames()
    for dof in dofs:
        robot.disableResponse(dof)

def close():
    robot.close()

def todicts(dofs,postures):
    return [dict(zip(dofs,posture)) for posture in postures]

def todict(dofs,posture):
    return dict(zip(dofs,posture)) 
