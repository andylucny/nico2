from agentspace import Agent, space, Trigger
import numpy as np
import time
import os
import random
from TouchAgent import clean
from speak import speak
import pyautogui
from datetime import datetime
from replay import prepare, replay, relax

class ExperimentAgent(Agent):

    def ready(self):
        print('ready')
        if self.stopped:
            return
        duration = self.duration if self.lastmode <= 0 else self.duration*self.lastmode/100.0
        duration *= 0.7 # speed up
        playAnimationEnd(home1, speed = 0.06*0.5)
        playAnimationEnd(gaze_home, speed=0.04)
        speak('Preparing. Please, wait.')
        time.sleep(duration)
        if self.stopped:
            return
        clean()
        self.state = 0
        space["experiment"] = False
        if self.stopped:
            return
        if self.mouse is not None:
            pyautogui.moveTo(self.mouse[0], self.mouse[1])
            self.mouse = None
        try:
            for window in pyautogui.getAllWindows():  
                if "Experiment" in window.title:
                    window.activate()
        except:
            pass
        if self.stopped:
            return
        print('Count:',self.count,'Max Count:',space(default=1)["MaxCount"])
        #stimuliRandomization(touches, space["MaxCount"])
        #print('touchesShuffled:', touchesShuffled)
        if self.count > 0 and self.count < space(default=1)["MaxCount"]:
            print("running automatically the next experiment")
            space["experiment"] = True
        else:
            self.count = 0
            space["count"] = self.count
            speak('Please enter your name and start the experiment by clicking Run')

    def init(self):
        self.duration = 2.0
        self.lastmode = 'congruent'
        self.count = 0
        self.lastName = ""
        self.mouse = None
        space.attach_trigger("experiment",self,Trigger.NAMES)
        #space.attach_trigger("stop",self,Trigger.NAMES)
        
    def senseSelectAct(self):
        trigger = self.triggered()
        mode = space(default=40)["StopMode"]
        self.duration = space(default=4)["Duration"]
        if trigger == "experiment":
            print('senseSelectAct')
            
            if self.countTrialsIndex == 0:   
                stimuliId = list(range(len(touches)))
                random.shuffle(stimuliId)
            print("STIMULI",self.countTrialsIndex, stimuliId)
            while self.countTrialsIndex < len(touches):
                self.sample_index = stimuliId[self.countTrialsIndex]
                self.countTrialsIndex += 1
                if space(default=True)["head"]:
                    break
                elif congruences[self.sample_index]:
                    break
            self.countTrials += 1
            print("self.countTrials ", self.countTrials)
            print("stimuliId =", stimuliId,"index =", self.sample_index,"congruent =",congruences[self.sample_index],"head =",space(default=True)["head"])
            if self.countTrialsIndex == len(touches):
                self.countTrialsIndex = 0
                self.countTrials = 0
            if space(default=False)["experiment"]:
                if self.state != 0:
                    self.ready()
                self.mouse = pyautogui.position()
                name = space(default="+++")["name"]
                if name != self.lastName:
                    self.count = 1
                    self.lastName = name
                else:
                    self.count += 1
                space["count"] = self.count
                if space(default=False)['TellIstructions']:
                    speak("Starting experiment...")
                
                #self.touches_shuffled = np.shuffle(touches)#
                #self.sample_index = np.random.randint(len(touches))
                #self.sample_index in self.touches_shuffled:#
                self.posename = str(self.sample_index)    
                print("SELECTED POINT No.",self.posename)
                self.touch = touches[self.sample_index]
                space['emulated'] = self.touch
                self.headMode = space(default=True)['head']
                if self.headMode:
                    #self.head = [0,-30]
                    gaze = animations_gaze[self.sample_index]
                else:
                    #self.head = [0,0]
                    gaze = gaze_home
                #setHead(self.head) 
                playAnimationEnd(gaze, speed=0.04)
                time.sleep(1)
                playAnimationEnd(home2)
                time.sleep(1)
                if mode == 0:
                    time.sleep(1)
                    speak("Please, use button Enter to stop me when you are ready to guess the touch point.")
                self.animation = animations[self.sample_index]
                self.timestamp = time.time()
                space["stop"] = False
                self.lastmode = mode
                self.offset = playAnimation(self.animation,deltaTime=0.01,percentage=mode if mode>0 else 100)
                self.timeElapsed = time.time()-self.timestamp
                if mode == 0:
                    perc = int(100*self.offset/len(self.animation[1]))
                    speak("You have used the stop button at "+str(perc)+" percent, please touch the estimated touch point by your finger.")
                else:
                    speak("The movement of my arm has been stopped after "+str(mode)+" percent, please touch the estimated touch point by your finger.")
                self.timestamp2 = time.time()
                self.state = 2
                space['touch'] = None
        elif trigger == "touch" and space['touch'] is not None:
            if self.state == 2:
                self.timeElapsed2 = time.time()-self.timestamp2
                self.estimatedTouch = space['touch']
                time.sleep(0.5)
                if space(default=False)['CompleteTouch']:
                    speak("Thank you. Let us look on my intention.")
                    playAnimation(self.animation,deltaTime=0.01,offset=self.offset)
                    speak("This was my intention.")
                else:
                    speak("Thank you.")
                    record = True
                name = space(default="+++")["name"]
                try:
                    os.mkdir("data/")
                except FileExistsError: 
                    pass
                with open("data/" + name + ".txt", "a") as f:
                    date = str(datetime.now())
                    f.write(f"{date},{self.count},{self.lastmode},{self.headMode},{self.posename},{self.estimatedTouch[0]},{self.estimatedTouch[1]},{self.touch[0]},{self.touch[1]},{self.timeElapsed:1.3f},{self.timeElapsed2:1.3f}\n")
                speak("Data are recorded.")
                time.sleep(0.5)
            self.ready()
        
if __name__ == "__main__":

    import os
    def quit():
        close()
        os._exit(0)

    from TouchAgent import TouchAgent
    TouchAgent()
       
    time.sleep(2)
    space['ShowIntention'] = True
    for point in touches:
        space['emulated'] = point
        time.sleep(0.1)
    
    touch(1)
    #globalTest()

