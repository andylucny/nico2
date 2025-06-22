import ikpy.chain
import numpy as np
import ikpy.utils.plot as plot_utils
import sys
from simulator import NicoSimulator

import warnings
warnings.filterwarnings("ignore", message=".*")

urdf_path = "nico_upper_ukba_right_arm.urdf"  
my_chain = ikpy.chain.Chain.from_urdf_file(urdf_path, base_elements=["world" ]) # "right_shoulder"

print([link.name for link in my_chain.links])
#'Base link', 'world_to_base_link', 'r_shoulder_z', 'r_shoulder_y', 'r_arm_x', 'r_elbow_y', 'r_wrist_z', 'r_wrist_x', 'r_indexfinger_x'

for i, link in enumerate(my_chain.links):
    print(f"{i}: {link.name} Limits: {link.bounds[0]*180/np.pi:.0f} .. {link.bounds[1]*180/np.pi:.0f} dg")
#0: Base link Limits: -inf .. inf dg
#1: world_to_base_link Limits: -inf .. inf dg
#2: r_shoulder_z Limits: -25 .. 80 dg
#3: r_shoulder_y Limits: 0 .. 180 dg
#4: r_arm_x Limits: 0 .. 70 dg
#5: r_elbow_y Limits: 50 .. 180 dg
#6: r_wrist_z Limits: 0 .. 180 dg
#7: r_wrist_x Limits: -50 .. 30 dg
#8: r_indexfinger_x Limits: -147 .. 0 dg

def rotation_from_z(z_axis_target, up_reference=np.array([0, 1, 0])):
    """
    Construct a 3D rotation matrix given the target Z-axis direction.
    Optionally, an 'up' reference vector can be used to resolve orientation.
    
    Parameters:
        z_axis_target: 3-element array-like (the desired direction of the z-axis)
        up_reference:  3-element array-like (optional 'up' vector; default is +Y)
        
    Returns:
        A 3x3 rotation matrix (NumPy array)
    """
    z_axis = np.asarray(z_axis_target)
    z_axis = z_axis / np.linalg.norm(z_axis)  # normalize

    # Check if z is parallel to the up vector; if so, use a different up vector
    if np.allclose(np.abs(np.dot(z_axis, up_reference)), 1.0):
        up_reference = np.array([1, 0, 0])  # switch to x-axis if needed

    x_axis = np.cross(up_reference, z_axis)
    x_axis = x_axis / np.linalg.norm(x_axis)

    y_axis = np.cross(z_axis, x_axis)

    # Stack axes as columns
    R_matrix = np.column_stack((x_axis, y_axis, z_axis))
    return R_matrix

# forward kinematics
def fk(angles):
    joint_angles =  np.radians([ 0, 0 ] + NicoSimulator.fixmany(dofs,angles))
    frame = my_chain.forward_kinematics(joint_angles)
    point = frame[:3, 3] # [ 0.21710165, -0.12311294, -0.05636721]
    z = np.array([0,0,1],np.float32)
    orientation = frame[:3,:3] @ z
    return point, orientation

# inverse kinematics
def ik(initial_angles, target_point, target_orientation):
    joint_angles =  np.radians([ 0, 0 ] + NicoSimulator.fixmany(dofs,initial_angles))
    target_frame = np.eye(4)
    target_frame[:3, :3] = rotation_from_z(target_orientation)
    target_frame[:3, 3] = np.array(target_point)
    joint_angles2 = my_chain.inverse_kinematics_frame(target=target_frame, initial_position=joint_angles)
    return list(NicoSimulator.unfixmany(dofs,np.degrees(joint_angles2[2:])))

N = 50
# Example input
ind = int(sys.argv[1]) if len(sys.argv) > 1 else 1
touch_postures = { # new
    1 : [33.0, 39.0, 25.0, 134.0, 102.0, 77.0, -168.0],
    2 : [37.0, 31.0, 23.0, 119.0, 107.0, 113.0, -177.0],
    3 : [57.0, 33.0, 40.0, 134.0, 80.0, 36.0, -159.0],
    4 : [51.0, 54.0, 37.0, 161.0, 92.0, 38.0, -174.0],
    5 : [38.0, 49.0, 36.0, 154.0, 80.0, 61.0, -177.0],
    6 : [25.0, 38.0, 31.0, 133.0, 99.0, 86.0, -156.0],
    7 : [34.0, 17.0, 39.0, 107.0, 106.0, 78.0, -180.0],
}
start_pose = [-24.92, 81.45, 46.55, 94.37, -59.03, 28.0, 45.67]
touch_pose = touch_postures[ind]

dofs = ['r_shoulder_z', 'r_shoulder_y', 'r_arm_x', 'r_elbow_y', 'r_wrist_z', 'r_wrist_x', 'r_indexfinger_x']

start_point, _ = fk(start_pose)
touch_point, _ = fk(touch_pose)

goal_vector = np.array(touch_point) - np.array(start_point)
opposite_normalized_goal_vector = list(-goal_vector / np.linalg.norm(goal_vector))
    
fractions = (np.arange(N+1,dtype=np.float32))/N
goal_points = start_point + np.expand_dims(fractions,1) * goal_vector

trajectory = []
previous_pose = touch_pose

for point in goal_points[::-1]:
    pose = ik(previous_pose,point,opposite_normalized_goal_vector)
    trajectory.append(pose)
    previous_pose = pose

def save(poses):
    with open(f'generated-ik{ind}.txt','wt') as f:
        f.write(str(dofs)+'\n')
        for pose in poses:
            f.write(str([angle for angle in pose])+'\n')
    print('saved')    

save(trajectory[::-1])
