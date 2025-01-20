import numpy as np
import time
from agentspace import Agent, space

from nicomover import setAngle, getAngle, simulated
from headlimiter import head_z_limits

class LookAroundAgent(Agent):

    def __init__(self, namePoint, nameSupress, nameFocused):
        self.namePoint = namePoint
        self.nameSupress = nameSupress
        self.nameFocused = nameFocused
        self.candidates = {}
        super().__init__()

    def init(self):
        
        self.laziness = 0
        space.attach_trigger(self.namePoint,self)

    def senseSelectAct(self):
    
        if space(default=False)[self.nameSupress]:
            return
    
        point = space[self.namePoint]
        if point is None:
            return
                
        #print('looking around',time.time())
        x, y = point
        
        head_x = getAngle("head_z")
        head_y = getAngle("head_y")
        
        _, limit_x = head_z_limits(head_y)
        
        reset_x, reset_y = False, False
        if np.abs(head_x) > 40:
            if np.random.rand() > 0.95:
                reset_x = True
        else:
            if np.random.rand() > 0.995:
                reset_x = True
        if head_y > 20: #15
            if np.random.rand() > 0.95:
                reset_y = True
        else:
            if np.abs(head_x) > 5:
                if np.random.rand() > 0.995:
                    reset_y = True
        
        if reset_x:
            delta_degrees_x = -head_x
            #print("RESET X")
        else:
            if simulated:
                delta_degrees_x = 2*30*(0.5-x) - head_x
            else:
                delta_degrees_x = np.arctan2((0.5-x)*np.tan(20*np.pi/180),0.5)*180/np.pi
        if reset_y:
            delta_degrees_y = -head_y - 25
            #print("RESET Y")
        else:
            if simulated:
                delta_degrees_y = 2*30*(0.5-y) - head_y
            else:
                delta_degrees_y = np.arctan2((0.5-y)*np.tan(20*np.pi/180),0.5)*180/np.pi
        
        if head_y + delta_degrees_y <= -limit_x+1:
            delta_degrees_y = 0.0
        if head_y + delta_degrees_y >= limit_x-1:
            delta_degrees_y = 0.0
        
        angular_speed = 0.04
        limit = 2.0 

        self.laziness -= 1.0
        if reset_x or reset_y or self.laziness <= 0:
            if np.abs(delta_degrees_x) > limit:
                setAngle("head_z", head_x + delta_degrees_x, angular_speed)
            if np.abs(delta_degrees_y) > limit:
                setAngle("head_y", head_y + delta_degrees_y, angular_speed)
            
        focus_limit = 5.0 
        if np.abs(delta_degrees_x) <= focus_limit and np.abs(delta_degrees_y) <= focus_limit:
            space(validity=1.0)[self.nameFocused] = True

        timeout = max(np.abs(delta_degrees_x),np.abs(delta_degrees_y))/(1000*angular_speed)
        time.sleep(timeout)
        
        self.laziness = np.random.normal(0,3)

if __name__ == '__main__':
    from CameraAgent import CameraAgent
    from FaceAgent import FaceAgent
    CameraAgent('See3CAM_CU135',0,'robotWideFOV',fps=10,zoom=170) # left eye
    time.sleep(1)
    FaceAgent('robotWideFOV','face position','face image','face point') # face detector
    time.sleep(1)
    LookAroundAgent('face point','dontLook','focused')
    time.sleep(1)
    