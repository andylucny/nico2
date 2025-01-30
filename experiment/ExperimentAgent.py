from agentspace import Agent, space, Trigger
import numpy as np
import time
import os
import random
from TouchAgent import clean
from replay import prepare, replay_forward, replay_backward, relax, ReplayMode, get_contraid
from beep import beep, fail
from speak import speak
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
        space['DoRests'] = True
        space['DoRepeat'] = True
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
                if self.stopped:
                    return
                time.sleep(0.5)
            print('focused')
                
            # smile
            print('smiling')
            space(validity=2.0)["emotion"] = "happiness"
            time.sleep(2.0)
        
        if self.stopped:
            return
        
        print("introduction")
        if space["TellIstructions"]:
            speak("@introduction")
            
        if self.stopped:
            return

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

            if self.stopped:
                return

            replay_forward(demo,mode=ReplayMode.CONGRUENT,percentage=100)
            clean()

            if self.stopped:
                return

            beep()
            time.sleep(0.75)
            clean()
            
            replay_backward(demo,-1,mode=ReplayMode.CONGRUENT,percentage=100)
            clean()

            if self.stopped:
                return

            relax()

            if self.stopped:
                return

            if space["BodyLanguage"]:
                print('follow face')
                space["dontLook"] = None
                
            print("after demo")
            if space["TellIstructions"]:
                speak("@after-demo")
        
        if self.stopped:
            return

        initialize_eyetracker()
        
        if (experiment > 1 or space(default=False)['doCalibration']) and is_eyetracker():
            
            print("calibration")
            if space["TellIstructions"]:
                speak("@calibration")
                
            start_calibration()
            
        else:
        
            time.sleep(1)
            if space["TellIstructions"]:
                speak("@no-calibration")

        # confirm
        space['touch'] = None
        while space['touch'] is None:
            if self.stopped:
                return
            time.sleep(0.25)

        clean()
        print('touchscreen cleaned')
        
        stop_calibration()
        
        print('eyetracking started')
        start_eyetracker(name)

        if self.stopped:
            return

        if space["TellIstructions"]:
            speak("@letsgo")
            
        if self.stopped:
            return

        if space["BodyLanguage"]:
            print('face following stopped')
            space["dontLook"] = True
            time.sleep(0.5)
                
        if self.stopped:
            return

        print('movement starting')
        
        if experiment == 1:
        
            batch = []
            for i in range(3):
            
                id = np.random.randint(7)+1
                percentage = space(default=80)["StopMode"]
                mode = space(default=ReplayMode.CONGRUENT)["head"]
                
                batch.append((i+1, id, percentage, mode))
            
        elif experiment in [2,3,4]:
        
            group = experiment-1
            batch = load_batch(f"batch{group}.txt")
                    
        batch.append((-1, -1, 0, ReplayMode.END))
        batch = np.array(batch)

        if self.stopped:
            return

        print("preparing")
        _, one, _, mode = batch[0]
        prepare(one,mode)
        
        if self.stopped:
            return

        encourages = [1,2,3,4,5]
        np.random.shuffle(encourages)
        encourage = 0

        j = 0
        while j < len(batch)-1:

            i, one, percentage, mode = batch[j]
            _, two, _, _ = batch[j+1]
            
            space['count'] = i
            space['percentage'] = percentage
            b = 1
            k = j 
            while batch[k][-1].value == batch[k+1][-1].value: # while the same mode
                k += 1
                b += 1
            space['break'] = b
            
            # clean the touchscreen
            clean()
            print('touchscreen cleaned')

            # red .. touch point, green .. gaze point, yellow .. if both are the same
            contra = one if mode.value != ReplayMode.INCONGRUENT.value else get_contraid(one)
            space['emulated'] = [ get_point(one) if mode.value != ReplayMode.HEADONLY.value else (-1.0,-1.0), get_point(contra) if mode.value != ReplayMode.NEUTRAL.value else (-1.0,-1.0) ] 
            space['touch'] = None
            # move forward
            replay_forward(one,mode=mode,percentage=percentage)

            if self.stopped:
                return

            beep()
            limit = 2.0 #[s]
            timestamp = time.time()

            # confirm
            failed = False
            while space['touch'] is None:
                if time.time() - timestamp > limit:
                    fail()
                    failed = True
                    break
                time.sleep(0.25)
                if self.stopped:
                    return

            # move backward
            replay_backward(one,two,mode=mode,percentage=percentage)
            
            if self.stopped:
                return

            if failed:
                if space["TellIstructions"]:
                speak("@touch-expired")
                touch = None
            else:
                touch = space['touch']

            reaction = space(default=timestamp)['reaction'] - timestamp
            record(name, group, i, one, contra, percentage, mode.value, touch, reaction, timestamp)

            # clean the touchscreen
            clean()
            print('touchscreen cleaned')
            
            if self.stopped:
                return
            
            if touch is None and space['DoRepeat']:
                # bubble to the end of the section
                print('repeating',i)
                k = j 
                while batch[k][-1].value == batch[k+1][-1].value: # while the same mode
                    batch[[k,k+1]] = batch[[k+1,k]] # swap
                    k += 1
            else:
                j += 1
                if batch[j][-1].value != ReplayMode.END.value and batch[j][-1].value != mode.value and space['DoRests']:
                    print('rest')
                    speak(f'@encourage{encourages[encourage]}')
                    encourage += 1
                    if encourage == len(encourages):
                        encourage = 0
                    speak('@before-rest')
                    if space["BodyLanguage"]:
                        print('follow face')
                        space["dontLook"] = None

                    for _ in range(15):
                        time.sleep(1)
                        if self.stopped:
                            return

                    if space["BodyLanguage"]:
                        print('face following stopped')
                        space["dontLook"] = True
                    speak('@after-rest')
        
        if self.stopped:
            return

        space['count'] = None
        
        if space["TellIstructions"]:
            speak("@thank-you")
                
        if self.stopped:
            return

        if space["TellIstructions"]:
            speak("@done")

        relax()

        if self.stopped:
            return

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

