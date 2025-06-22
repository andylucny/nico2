import time
import numpy as np
import sys # calling with argument novel or traditional

from nicomover import enableTorque, play_movement, todicts, move_to_posture, todict, park
print('started')

park()
time.sleep(1)

head_postures = []
with open(f'head-to-points.txt','r') as f:
    lines = f.readlines()
    head_dofs = eval(lines[0])
    for line in lines[1:]:
        head_posture = eval(line)
        head_postures.append(head_posture)

left_arm_dofs = ['l_shoulder_z', 'l_shoulder_y', 'l_arm_x', 'l_elbow_y', 'l_wrist_z', 'l_wrist_x', 'l_thumb_z', 'l_thumb_x', 'l_indexfinger_x', 'l_middlefingers_x']
left_arm_values = [-23.0, 14.0, 0.0, 103.0, -1.0, -55.0, -62.0, -180.0, -179.0, -176.0]

finger_dofs = ['r_thumb_z', 'r_thumb_x', 'r_middlefingers_x']
finger_values = [-180, -40, 180]

duration = 2.0
perc = 1.0

previous_postures = []

def blend(postures1,postures2):
    fractions = np.linspace(0,1,len(postures1))
    return [ list(posture1 * (1-fraction) + posture2 * fraction) for fraction, posture1, posture2 in zip(fractions, np.array(postures1), np.array(postures2)) ]

enableTorque(head_dofs)

for ind in [1,2,3,4,5,6,7]: 

    print(ind)
    head_posture = head_postures[ind-1]

    postures = []
    trajectory_file = f'../generate/generated{ind}.txt'
    if len(sys.argv) > 1 and sys.argv[1] == 'traditional':
        trajectory_file = f'../generate-ikpy/generated-ik{ind}.txt'
    
    with open(trajectory_file,'r') as f:
        lines = f.readlines()
        dofs = eval(lines[0])
        for line in lines[1:]:
            posture = eval(line)
            postures.append(posture)

    print('loaded',len(postures),'postures')
    
    postures = postures[:int(len(postures)*perc)]

    if previous_postures:
        play_movement(todicts(dofs,blend(previous_postures[::-1],postures[::-1])),durations)
        time.sleep(3)
    else:
        enableTorque(dofs+finger_dofs+left_arm_dofs)
        play_movement(todicts(dofs+finger_dofs+left_arm_dofs,[postures[0]+finger_values+left_arm_values]),[duration])
        time.sleep(1)

    play_movement(todicts(head_dofs,[head_posture]),[0.5])

    n = len(postures)
    durations = [duration/n]*n

    play_movement(todicts(dofs,postures),durations)
    time.sleep(2)
    
    previous_postures = postures

play_movement(todicts(dofs,postures[::-1]),durations)
time.sleep(2)

park()  
time.sleep(2)
