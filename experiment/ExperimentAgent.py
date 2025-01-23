from agentspace import Agent, space, Trigger
import numpy as np
import time
import os
import random
from TouchAgent import clean
from speak import speak
from replay import prepare, replay_forward, replay_backward, relax, ReplayMode, get_contraid
from beep import beep, fail
from recording import record, get_point
from eyetracker import initialize_eyetracker, start_calibration, stop_calibration, start_eyetracker, stop_eyetracker
from batch import load_batch

class ExperimentAgent(Agent):

    def init(self):
        self.duration = 2.0
        self.lastName = ""
        self.mouse = None
        space["BodyLanguage"] = True
        space["TellIstructions"] = True
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
        
        if space["BodyLanguage"]:
        
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
            #space["dontLook"] = True
            space(validity=2.0)["emotion"] = "happiness"
            time.sleep(2.0)
        
        print("introduction")
        if space["TellIstructions"]:
            speak("@introduction")
        
        print("calibration")
        if space["TellIstructions"]:
            speak("@calibration")
            
        initialize_eyetracker()
        start_calibration()

        # confirm
        space['touch'] = None
        while space['touch'] is None:
            time.sleep(0.25)

        clean()
        print('touchscreen cleaned')
        
        stop_calibration()
        
        print('eyetracking started')
        start_eyetracker(name)

        if space["TellIstructions"]:
            speak("@letsgo")
            
        if space["BodyLanguage"]:
            print('stoping face following')
            space["dontLook"] = True
                
        print('movement starting')
        
        if experiment == 1:
        
            batch = []
            for _ in range(3):
            
                id = np.random.randint(7)+1
                percentage = space(default=80)["StopMode"]
                mode = space(default=ReplayMode.CONGRUENT)["head"]
                
                batch.append((id, percentage, mode))
            
        elif experiment == 2:
        
            batch = load_batch("batch1.txt")
            group = 1 
            
        elif experiment == 3:
        
            batch = load_batch("batch2.txt")
            group = 2
            
        batch.append((-1, 0, 0))

        print("preparing")
        one, _, mode = batch[0]
        prepare(one,mode)

        for i in range(len(batch)-1):
            space['count'] = i+1

            one, percentage, mode = batch[i]
            two, _, _ = batch[i+1]
            
            # clean the touchscreen
            clean()
            print('touchscreen cleaned')

            # move forward
            contra = one if mode != ReplayMode.INCONGRUENT else get_contraid(one)
            space['emulated'] = [ get_point(one), get_point(contra) ]
            space['touch'] = None
            replay_forward(one,mode=mode,percentage=percentage)

            beep()
            limit = 2.0 #[s]
            t0 = time.time()

            # move backward
            replay_backward(one,two,mode=mode,percentage=percentage)
            
            # confirm
            while space['touch'] is None:
                if time.time() - t0 > limit:
                    fail()
                    if space["TellIstructions"]:
                        speak("@touch-expired")
                    break
                time.sleep(0.25)
                
            touch = space['touch']
            record(name, group, i, one, contra, percentage, mode.value, touch)
        
        space['count'] = None
        
        if space["TellIstructions"]:
            speak("@thank-you")
                
        if space["TellIstructions"]:
            speak("@done")

        relax()
        time.sleep(2)
        
        stop_eyetracker()
        
        clean()
        print('touchscreen cleaned')
        
        space['experiment'] = 0
        
        # follow face if 
        if space["BodyLanguage"]:
            space["dontLook"] = None
        
if __name__ == "__main__":

    import os
    def quit():
        close()
        os._exit(0)

    from TouchAgent import TouchAgent
    TouchAgent()

