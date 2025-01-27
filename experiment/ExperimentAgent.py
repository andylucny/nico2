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
from eyetracker import initialize_eyetracker, start_calibration, stop_calibration, start_eyetracker, stop_eyetracker, is_eyetracker
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
            print('follow face')
            space["dontLook"] = None # to be sure
            for _ in range(20):
                if space["focused"]:
                    break
                time.sleep(0.5)
            print('focused')
                
            # smile
            print('smiling')
            space(validity=2.0)["emotion"] = "happiness"
            time.sleep(2.0)
        
        print("introduction")
        if space["TellIstructions"]:
            speak("@introduction")
            
        if experiment > 1 or space(default=False)['doIntroduction']:

            print("introduction")
            if space["TellIstructions"]:
                speak("@before-demo")
                
            # demo
            print("demo")
            if space["BodyLanguage"]:
                print('face following stopped')
                space["dontLook"] = True
            demo = 1
            prepare(demo,ReplayMode.CONGRUENT)
            replay_forward(demo,mode=ReplayMode.CONGRUENT,percentage=100)
            clean()
            time.sleep(1)
            clean()
            replay_backward(demo,-1,mode=ReplayMode.CONGRUENT,percentage=100)
            clean()
            relax()
            if space["BodyLanguage"]:
                print('follow face')
                space["dontLook"] = None
                
            print("after demo")
            if space["TellIstructions"]:
                speak("@after-demo")
        
        if (experiment > 1 or space(default=False)['doCalibration']) and is_eyetracker():

            print("calibration")
            if space["TellIstructions"]:
                speak("@calibration")
                
            initialize_eyetracker()
            start_calibration()
            
        else:
        
            time.sleep(1)
            if space["TellIstructions"]:
                speak("@no-calibration")

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
            print('face following stopped')
            space["dontLook"] = True
            time.sleep(0.5)
                
        print('movement starting')
        
        if experiment == 1:
        
            batch = []
            for i in range(3):
            
                id = np.random.randint(7)+1
                percentage = space(default=80)["StopMode"]
                mode = space(default=ReplayMode.CONGRUENT)["head"]
                
                batch.append((i+1, id, percentage, mode))
            
        elif experiment == 2:
        
            batch = load_batch("batch1.txt")
            group = 1 
            
        elif experiment == 3:
        
            batch = load_batch("batch2.txt")
            group = 2
            
        batch.append((-1, -1, 0, ReplayMode.END))
        batch = np.array(batch)

        print("preparing")
        _, one, _, mode = batch[0]
        prepare(one,mode)

        j = 0
        while j < len(batch)-1:

            i, one, percentage, mode = batch[j]
            _, two, _, _ = batch[j+1]
            
            space['count'] = i
            
            # clean the touchscreen
            clean()
            print('touchscreen cleaned')

            # move forward
            contra = one if mode.value != ReplayMode.INCONGRUENT.value else get_contraid(one)
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
            
            if touch is None and space(default=True)['DoRepeat']:
                # bubble to the end of the section
                print('repeating',i)
                k = j 
                while batch[k][-1].value == batch[k+1][-1].value: # while the same mode
                    batch[[k,k+1]] = batch[[k+1,k]] # swap
                    k += 1
            else:
                j += 1
                if batch[j][-1].value != ReplayMode.END.value and batch[j][-1].value != mode.value and space(default=True)['DoRests']:
                    print('rest')
                    speak(f'@encourage{np.random.randint(5)+1}')
                    speak('@before-rest')
                    if space["BodyLanguage"]:
                        print('follow face')
                        space["dontLook"] = None
                    time.sleep(15)
                    if space["BodyLanguage"]:
                        print('face following stopped')
                        space["dontLook"] = True
                    speak('@after-rest')
        
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
            print('follow face')
            space["dontLook"] = None
        
if __name__ == "__main__":

    import os
    def quit():
        close()
        os._exit(0)

    from TouchAgent import TouchAgent
    TouchAgent()

