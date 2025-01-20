from agentspace import Agent, space, Trigger
import numpy as np
import time
import os
import random
from TouchAgent import clean
from speak import speak
from replay import prepare, replay, relax, ReplayMode
from eyetracker import initialize_eyetracker, start_calibration, stop_calibration, start_eyetracker, stop_eyetracker

class ExperimentAgent(Agent):

    def init(self):
        self.duration = 2.0
        self.lastmode = 'congruent'
        self.count = 0
        self.lastName = ""
        self.mouse = None
        space.attach_trigger("experiment",self)
        
    def senseSelectAct(self):
        experiment = space(default=0)["experiment"]
        if experiment == 0:
            return
            
        name = space(default='xy')['name']
        print('name',name)
        
        # clean the touchscreen
        clean()
        print('touchscreen cleaned')
        
        if space(default=False)["BodyLanguage"]:
        
            print('focusing')
            # try to get focused to the face:
            space["dontLook"] = None # to be sure
            for _ in range(20):
                if space["focused"]:
                    break
                time.sleep(0.5)
            print('focused')
                
            # smile
            print('smiling')
            space["dontLook"] = True
            space(validity=2.0)["emotion"] = "happiness"
            time.sleep(2.0)
        
        print("preparing")
        prepare(1,mode=ReplayMode.CONGRUENT)
        
        print("introduction")
        if space(default=False)["TellIstructions"]:
            speak("@introduction")
        
        print("calibration")
        if space(default=False)["TellIstructions"]:
            speak("@calibration")
            
        initialize_eyetracker()
        start_calibration()

        # confirm
        space['touch'] = None
        while space['touch'] is None:
            time.sleep(0.25)

        stop_calibration()
        
        print('eyetracking started')
        start_eyetracker(name)
        
        print('movement starting')
        if experiment == 1:
        
            mode = space(default=1)["head"]
            percentage = space(default=80)["StopMode"]
            
            space['touch'] = None
            one = np.random.randint(7)+1
            
            replay(one,-1,mode=mode,percentage=percentage)
            
            if space(default=False)["TellIstructions"]:
                if space['touch'] is None:
                    speak("@touch-please")

            # confirm
            while space['touch'] is None:
                time.sleep(0.25)
                
            touch = space['touch']
            if space(default=False)["TellIstructions"]:
                speak("@thank-you")
                
        if space(default=False)["TellIstructions"]:
            speak("@done")

        relax()
        time.sleep(2)
        
        stop_eyetracker()
        
        space['experiment'] = 0
        
        # follow face if 
        if space(default=False)["BodyLanguage"]:
            space["dontLook"] = None
        
if __name__ == "__main__":

    import os
    def quit():
        close()
        os._exit(0)

    from TouchAgent import TouchAgent
    TouchAgent()

