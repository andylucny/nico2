import os
import numpy as np
import cv2 as cv
from agentspace import Agent, space, Trigger
from datetime import datetime

class RecorderAgent(Agent):

    def init(self):
        self.lastName = ""
        self.number = 0
        self.out = None
        self.fps = 10
        self.size = (1280,960)
        self.hsize = (self.size[0]//2,self.size[1]//2)
        self.blank = np.zeros((self.hsize[1],self.hsize[0],3),np.uint8)
        self.attach_timer(1.0/self.fps)
        space.attach_trigger('experiment',self,Trigger.NAMES)
        
    def senseSelectAct(self):
        experiment = space(default=False)['experiment']
        if self.triggered() == 'experiment':
            if experiment:
                name = space(default='xxx')['name']
                if name != self.lastName:
                    if self.out is not None:
                        self.out.release()
                    try:
                        os.mkdir("data/")
                    except FileExistsError: 
                        pass
                    filename = "data/" + name + ".avi"
                    self.out = cv.VideoWriter()
                    self.out.open(filename,cv.VideoWriter_fourcc('M','J','P','G'),self.fps,self.size)
        else:
            if experiment and (self.out is not None):
                tl = cv.resize(space(default=self.blank)['humanImage'],self.hsize)
                tr = cv.resize(space(default=self.blank)['robotImage'],self.hsize)
                bl = cv.resize(space(default=self.blank)['robotEye'],self.hsize) #np.copy(self.blank)
                br = cv.resize(space(default=self.blank)['touchImage'],self.hsize)
                cv.putText(br,str(datetime.now())[:22],(10,self.hsize[1]-15),0,1.0,(255,255,255),1)
                count = space(default=0)["count"]
                if count > 0:
                    cv.putText(br,'#'+str(count),(10,55),0,2.0,(255,255,255),3)
                frame = cv.vconcat([cv.hconcat([tl,tr]),cv.hconcat([bl,br])])
                self.out.write(frame)
