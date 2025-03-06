import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.collections as mcoll
import matplotlib.path as mpath
from mpl_toolkits.mplot3d import Axes3D
from dk import dk

percents = [60,80,100]

keys = [1,2,3,4,5,6,7]

trajectories = {}
for ind in keys:
    trajectory = []
    with open(f'generated{ind}.txt','r') as f:
        for line in f.readlines()[1:]:
            pose = [float(value) for value in line[1:-2].split(',')]
            trajectory.append(pose)
    trajectories[ind] = trajectory

real_touches = np.array([
    [0,0,0],
    [-4.5,4.5,0],
    [-9,0,0],
    [-4.5,-4.5,0],
    [4.5,-4.5,0],
    [9,0,0],
    [4.5,4.5,0],
],np.float32)
check_touches = real_touches

plt.plot(real_touches[:,0],real_touches[:,1],'o')
plt.plot(check_touches[:,0],check_touches[:,1],'.')
plt.savefig('check.png')
plt.clf()

M = 25
data = {}
for ind in keys:
    dks = np.array([dk(pose) for pose in trajectories[ind]],np.float32)
    points = dks[:,0,-1,:]
    vectors = dks[:,1,-1,:]
    
    data[ind] = {}
    data[ind]['points'] = points

    touch_point = real_touches[ind-1] # ~ points[-1]
    x0, y0, z0 = touch_point

    intersections = points - np.expand_dims((points[:,2]-z0)/(vectors[:,2]+1e-6),1) * vectors

    # Extract x, y, z coordinates
    x = intersections[:, 0]
    y = intersections[:, 1]
    data[ind]['x'] = x[M:]
    data[ind]['y'] = y[M:]
    
    x0, y0, _ = real_touches[ind-1]
    #x0, y0 = x[-1], y[-1]
    errors = np.linalg.norm([x-x0,y-y0],axis=0)
    p = np.linspace(0,100,len(x))
    fig = plt.subplot()
    plt.ylim(0, 10.0)
    fig.plot(p,errors)
    fig.set_xlabel('%')
    fig.set_ylabel('[cm]')
    fig.set_title(f'trajectory {ind}')
    plt.savefig(f'err{ind}.png')
    plt.clf()
    
    for perc in percents:
        j = (perc * (len(x)-1))//100
        data[ind][f'x{perc}'] = x[j]
        data[ind][f'y{perc}'] = y[j]

plt.clf()

colors = {
    1 : 'red',
    2 : 'orange',
    3 : 'green',
    4 : 'blue',
    5 : 'brown',
    6 : 'pink',
    7 : 'cyan'
}

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the trajectories
for ind in keys:
    points = data[ind]['points']
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    z_coords = [p[2] for p in points]
    ax.plot(x_coords, y_coords, z_coords, marker='o', markersize=3, label=f'trajectory {ind}', color=colors[ind])

# Set axis ranges
#ax.set_xlim(-2, 2) # X-axis range
#ax.set_ylim(-2, 2) # Y-axis range
#ax.set_zlim(-2, 2) # Z-axis range

# Add labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Trajectory')

# Add a legend
ax.legend()
ax.view_init(elev=30, azim=-179)

# Show the plot
#plt.show()
plt.savefig('trajectories.png')
plt.clf()

fig = plt.subplot()

for k in data:
    xs = data[k]['x']
    ys = data[k]['y']
    fig.plot(xs,ys,label=f'trajectory {k}',color=colors[k], linewidth=0.2)

for k in data:
    xs = [ data[k][f'x{perc}'] for perc in percents ]
    ys = [ data[k][f'y{perc}'] for perc in percents ]
    if k == 1:
        fig.scatter(xs[:1], ys[:1], color=colors[k], s=10, label='60%')
        fig.scatter(xs[1:2], ys[1:2], color=colors[k], s=20, label='80%')
        fig.scatter(xs[2:3], ys[2:3], color=colors[k], s=30, label='100%')
    else:
        fig.scatter(xs[:1], ys[:1], color=colors[k], s=10)
        fig.scatter(xs[1:2], ys[1:2], color=colors[k], s=20)
        fig.scatter(xs[2:3], ys[2:3], color=colors[k], s=30)    

fig.set_xlabel('[cm]')
fig.set_ylabel('[cm]')
plt.axis([-20, 25, -15, 15])
#plt.axis('equal')
plt.legend(loc='lower right')
plt.savefig('perc.png')

print('rename points.png and points.npy (add the trajectory id)')
