import numpy as np
import matplotlib.pyplot as plt
from dk import dk

keys = [1,2,3,4,5,6,7]
colors = {
    1 : 'red',
    2 : 'orange',
    3 : 'green',
    4 : 'blue',
    5 : 'brown',
    6 : 'pink',
    7 : 'cyan'
}

trajectories = {}
for ind in keys:
    trajectory = []
    with open(f'generated{ind}.txt','r') as f:
        for line in f.readlines()[1:]:
            pose = [float(value) for value in line[1:-2].split(',')]
            trajectory.append(pose)
    trajectories[ind] = trajectory

data = {}
for ind in keys:
    dks = np.array([dk(pose) for pose in trajectories[ind]],np.float32)
    points = dks[:,0,-1,:]
    data[ind] = {}
    data[ind]['points'] = points

# Plot 3D trajectories -> trajectories.eps
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for ind in keys:
    points = data[ind]['points']
    ax.plot(points[:,0], points[:,1], points[:,2], marker='o', markersize=3, label=f'trajectory {ind}', color=colors[ind])

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Trajectory')
ax.legend()
ax.view_init(elev=30, azim=-179)
plt.rcParams['ps.useafm'] = True
plt.rcParams['pdf.use14corefonts'] = True
plt.savefig('trajectories.eps', dpi=300, bbox_inches='tight', pad_inches=0)
plt.clf()

# Plot criterium2.eps
for ind in keys:
    points = data[ind]['points']
    vectors = points[1:] - points[:-1]
    avg_vectors = []
    for i in range(len(points)-1):
        start = max(0, i - 10)
        end = i
        avg = np.mean(vectors[start:end+1], axis=0)
        avg_vectors.append(avg)
    avg_vectors = np.array(avg_vectors)

    z0 = points[-1][2]
    intersections = []
    for p, v in zip(points, avg_vectors): 
        if v[2] != 0:
            t = (z0 - p[2]) / v[2]
            intersection = p + t * v
        else:
            intersection = np.full(3, np.nan)
        intersections.append(intersection)

    intersections = np.array(intersections)
    diffs = intersections - points[-1]
    distances = np.linalg.norm(diffs, axis=1)
    plt.plot(distances, color=colors[ind], label=f'trajectory {ind}')

plt.xlabel('steps') 
plt.ylabel('error [cm]') 
plt.legend()
plt.rcParams['ps.useafm'] = True
plt.rcParams['pdf.use14corefonts'] = True
plt.savefig('criterium2.eps', dpi=300)
