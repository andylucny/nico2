import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.collections as mcoll
import matplotlib.path as mpath
from mpl_toolkits.mplot3d import Axes3D

def get_transform(src, dst):
    # Step 1: Calculate centroids of both point clouds
    src_centroid = np.mean(src, axis=0)
    dst_centroid = np.mean(dst, axis=0)
    # Step 2: Center the points by subtracting the centroid
    src_centered = src - src_centroid
    dst_centered = dst - dst_centroid
    # Step 3: Compute the scaling factor
    src_scale = np.sqrt(np.sum(src_centered ** 2, axis=1)).mean()
    dst_scale = np.sqrt(np.sum(dst_centered ** 2, axis=1)).mean()
    scale_factor = dst_scale / src_scale
    # Step 4: Scale the src points
    src_scaled = src_centered * scale_factor
    # Step 5: Compute the rotation matrix using SVD
    H = np.dot(src_scaled.T, dst_centered)
    U, _, Vt = np.linalg.svd(H)
    rotation_matrix = np.dot(Vt.T, U.T)
    return rotation_matrix, scale_factor, src_centroid, dst_centroid

def apply_transform(src, transform):
    rotation_matrix, scale_factor, src_centroid, dst_centroid = transform
    # Step 2: Center the points by subtracting the centroid
    src_centered = src - src_centroid
    # Step 4: Scale the src points
    src_scaled = src_centered * scale_factor
    # Step 6: Apply the rotation, scaling, and translation
    transformed_src = np.dot(src_scaled, rotation_matrix.T) + dst_centroid
    return transformed_src

def fit(points):
    # Step 1: Center the data
    mean_point = np.mean(points, axis=0)
    centered_points = points - mean_point
    # Step 2: Compute covariance matrix
    cov_matrix = np.cov(centered_points, rowvar=False)
    # Step 3: Eigen decomposition
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    # Step 4: Select the eigenvector with the largest eigenvalue
    direction_vector = eigenvectors[:, np.argmax(eigenvalues)]   
    return direction_vector

percents = [60,80,100]

keys = [1,2,3,4,5,6,7]

loaded = {}
touches = []
for ind in keys:
    points = np.loadtxt(f'points{ind}.npy')
    loaded[ind] = points
    touches.append(points[-1])

touches = np.array(touches)
real_touches = np.array([
    [0,0,0],
    [-4.5,4.5,0],
    [-9,0,0],
    [-4.5,-4.5,0],
    [4.5,-4.5,0],
    [9,0,0],
    [4.5,4.5,0],
],np.float32)
transform = get_transform(touches,real_touches)
check_touches = apply_transform(touches,transform)

plt.plot(real_touches[:,0],real_touches[:,1],'o',label='ideal')
plt.plot(check_touches[:,0],check_touches[:,1],'.',label='measured')
plt.legend()
plt.savefig('check.png')
plt.clf()

M = 25
data = {}
for ind in keys:
    points = loaded[ind]
    points = apply_transform(points,transform)
    points = points[:,[1,0,2]]
    points[:,2] = - points[:,2]
    
    #with open(f'points{ind}.txt','w') as f:
    #    f.write('[x,y,z]\n')
    #    for point in points:
    #        f.write(f'[{point[0]},{point[1]},{point[2]}]\n')
    
    reserve = 5
    points = points[reserve:,:]
    
    data[ind] = {}
    data[ind]['points'] = points

    vectors = [fit(points[:i]) for i in range(2,len(points))]
    vectors = np.array([vectors[0],vectors[0]] + vectors)

    touch_point = real_touches[ind-1] # ~ points[-1]
    y0, x0, z0 = touch_point
    z0 = -z0

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
plt.savefig('trajectories.png')
#plt.show()
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

