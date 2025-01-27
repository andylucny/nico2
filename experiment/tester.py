import pickle

def save(): # to be copied into replay.py
    print('saving')
    import pickle
    with open('move.pkl', 'wb') as file:
        pickle.dump([todicts(dofs,blend(postures[::-1],next_postures[::-1])),durations], file)
    print('saved')

# Loading the dictionary from the file
with open('move.pkl', 'rb') as file:
    poses, durations = pickle.load(file)

from nicomover import play_movement, move_to_posture, park

park()
move_to_posture(poses[-1])
move_to_posture({'r_thumb_z':-180, 'r_thumb_x':-40, 'r_middlefingers_x':180})

play_movement(poses[::-1],durations)
