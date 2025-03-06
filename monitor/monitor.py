#pip install pyrealsense2
#use USB3.0 !!!

import pyrealsense2 as rs
import numpy as np
import cv2
import time

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Get depth sensor's depth scale
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()

print(f"Depth Scale: {depth_scale} meters per unit")

# Align depth frame to color frame
align_to = rs.stream.color
align = rs.align(align_to)

refPoint = None
goalPoint = None
record = False
go_exit = False
def mouseHandler(event, x, y, flags, param):
    global refPoint, goalPoint, record, go_exit
    if event == cv2.EVENT_LBUTTONDOWN:
        refPoint = (x, y)
        record = not record
        if record:
            print('start recording')
        else:
            print('stop recording')
            go_exit = True
    elif event == cv2.EVENT_RBUTTONDOWN:
        goalPoint = (x, y)
        
cv2.namedWindow("RealSense")
cv2.setMouseCallback("RealSense", mouseHandler)

def red_filter(image, ref):

    # Convert the image to HSV (Hue, Saturation, Value) color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the lower and upper range of red color in HSV
    lower_red1 = np.array([0, 80, 50])    # Red in lower range (1-10 hue)
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 80, 50])    # Red in lower range (170-180 hue)
    upper_red2 = np.array([180, 255, 255])

    # Create masks for the red color ranges
    red_mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = red_mask1 | red_mask2 
    
    disp = np.copy(image)
    disp[red_mask == 0] = (0,0,0)
    cv2.imshow('mask',disp)
    hsv_disp = np.copy(hsv_image)
    hsv_disp[red_mask == 0] = (0,0,0)
    cv2.imshow('hsv mask',hsv_disp)

    # Erosion removes isolated points, and dilation restores the shape of valid objects
    #kernel = np.ones((3, 3), np.uint8)  # A 3x3 kernel to check neighbors
    #red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    
    # Find all connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(red_mask, connectivity=8)

    if num_labels < 2:  # Only background found
        return None

    # find the closest point from the reference
    distances = np.linalg.norm(centroids[1:] - np.array(ref), axis=1)
    closest = 1 + np.argmin(distances)
    if distances[closest-1] > 50:
        return None

    # Center of gravity of the largest component
    centroid = tuple(np.int32(np.round(centroids[closest])))
    return centroid

points = []
try:
    t0 = int(time.time())
    f = 0
    fps = 0
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        
        point = None
        center = None
        if refPoint is not None:
            center = red_filter(color_image, refPoint)
            
        # Intrinsic parameters
        depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics

        if center is not None:
            refPoint = center

            # Find 3D point
            x, y = center
            # Get depth at the current pixel
            depth = depth_image[int(y), int(x)] * depth_scale
            if depth > 0:  # Ignore invalid depth
                # Compute 3D point
                point = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x, y], depth)

        if goalPoint is not None:
            gx, gy = goalPoint
            gdepth = depth_image[int(gy), int(gx)] * depth_scale
            if gdepth > 0:
                goal = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [gx, gy], gdepth)
                print('goal:', goal)
            goalPoint = None

        if point is not None:
            if record:
                points.append(point)
        
        t1 = int(time.time())
        if t1 > t0:
            fps = f+1
            f = 0
            t0 = t1
        else:
            f += 1
            
        # Display images
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
        )
        images = np.hstack((color_image, depth_colormap))
        cv2.putText(images,str(fps),(5,20),0,1.0,(0,0,255),1)
        if center is not None:
            cv2.circle(images,(int(x), int(y)),4,(0,255,255),cv2.FILLED)
        if point is not None:
            cv2.putText(images,f'{point[0]:.2f},{point[1]:.2f},{point[2]:.2f}',(5,40),0,0.9,(0,255,255),1)

        cv2.imshow('RealSense', images)

        # Exit on Esc key press
        key = cv2.waitKey(1)
        if key & 0xFF == 27:
            break
        elif key & 0xFF == ord('s'):
            cv2.imwrite(f'image{t0}.png',images)
        elif key & 0xFF == ord('m'):
            cv2.imwrite(f'disp{t0}.png',disp)
            cv2.imwrite(f'hsv{t0}.png',hsv_disp)
        
        if go_exit:
            break

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()

np.savetxt('points.npy',np.array(points))

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Extract the x, y, and z coordinates from the points
x_coords = [p[0] for p in points]
y_coords = [p[1] for p in points]
z_coords = [p[2] for p in points]

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the trajectory
ax.plot(x_coords, y_coords, z_coords, marker='o', label='Trajectory')

# Set axis ranges
ax.set_xlim(-2, 2) # X-axis range
ax.set_ylim(-2, 2) # Y-axis range
ax.set_zlim(-2, 2) # Z-axis range

# Add labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Trajectory')

# Add a legend
ax.legend()

# Show the plot
plt.show()

points = np.array(points)
x, y, z = points.T
plt.plot(x,y)
plt.plot(x,z)
plt.plot(y,z)
plt.savefig('points.png')

print()
print('rename points.png and points.npy (add the trajectory id)')
