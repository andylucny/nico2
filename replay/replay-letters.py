import time
import numpy as np
import sys # calling with argument novel or traditional

from nicomover import enableTorque, play_movement, todicts, move_to_posture, todict, park
print('started')

park()
time.sleep(1)

head_dofs = ['head_z', 'head_y']

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

postures = []
trajectory_file = '../generate-letters/generated-P30.txt'
    
with open(trajectory_file,'r') as f:
    lines = f.readlines()
    dofs = eval(lines[0])
    for line in lines[1:]:
        posture = eval(line)
        postures.append(posture)

print('loaded',len(postures),'postures')

postures = postures[:int(len(postures)*perc)]

for _ in range(3):

    play_movement(todicts(dofs+finger_dofs+left_arm_dofs,[postures[0]+finger_values+left_arm_values]),[duration])
    time.sleep(1)

    n = len(postures)
    durations = [duration/n]*n

    play_movement(todicts(dofs,postures),durations)
    time.sleep(2)
        
    park()  
    time.sleep(2)
