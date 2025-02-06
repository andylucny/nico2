import PySimpleGUI as sg
from agentspace import Agent, space, Trigger
import numpy as np
import cv2 as cv
import time
import os
from datetime import datetime
from replay import ReplayMode

class GuiAgent(Agent):
      
    def init(self, testing=True):
        #GUI
        self.testing = testing
        layout = [
            [
                sg.Image(filename="", key="humanImage"),
                sg.Image(filename="", key="robotImage"),
            ],
            [
                sg.Image(filename="", key="robotEye"),
                sg.Image(filename="", key="touchImage"),
            ],
            [ 
                sg.Text("Name", size=(5, 1)),
                sg.Input("xy", size=(25, 1), key="Name"), 
                sg.Text("Language:", size=(9, 1)), 
                sg.Radio("EN", "Language:", False, size=(2, 1), key="Language-EN", enable_events=True), 
                sg.Radio("SK", "Language:", True, size=(2, 1), key="Language-SK", enable_events=True), 
            ],
            [ 
                sg.Checkbox("Follow face and smile", default=True, key='BodyLanguage', enable_events=True),
                sg.Checkbox("Tell instructions", default=True, key='TellIstructions', enable_events=True),
                sg.Checkbox("repeat", default=False, key='DoRepeat', enable_events=True),
                sg.Checkbox("rests", default=True, key='DoRests', enable_events=True),
                sg.Push(), 
                sg.Button("", image_filename="redtouch.png", image_size=(32, 32), border_width=0),
                sg.Button("", image_filename="greengaze.png", image_size=(32, 32), border_width=0),
                sg.Button("", image_filename="yellowboth.png", image_size=(32, 32), border_width=0),
            ],
            [
                sg.Button("Run batch 1", size=(11, 1)),
                sg.Button("Run batch 2", size=(11, 1)),
                sg.Button("Run test", size=(10, 1)),
                sg.Button("Resume", size=(7, 1), disabled=True),
                sg.Button("Stop", size=(5, 1)),
                sg.Button("Exit", size=(5, 1)),
            ],
        ]
        if self.testing:
            layout.append([
                [sg.HSeparator()],
                [
                    sg.Text("Head:", size=(5, 1)), 
                    sg.Radio("congruent", "Head:", True, size=(8, 1), key="Head-congruent", enable_events=True), 
                    sg.Radio("incongruent", "Head:", False, size=(10, 1), key="Head-incongruent", enable_events=True), 
                    sg.Radio("only", "Head:", False, size=(6, 1), key="Head-only", enable_events=True), 
                    sg.Radio("neutral", "Head:", False, size=(8, 1), key="Head-neutral", enable_events=True), 
                ],
                [ 
                    sg.Text("Stop mode:", size=(9, 1)), 
                    sg.Radio("at 60%", "StopMode:", False, size=(6, 1), key="StopMode-60", enable_events=True),
                    sg.Radio("at 80%", "StopMode:", True, size=(6, 1), key="StopMode-80", enable_events=True),
                    sg.Radio("at 100%", "StopMode:", False, size=(6, 1), key="StopMode-100", enable_events=True),
                ],
                [
                    sg.Checkbox("calibration", default=False, key='DoCalibration', enable_events=True),
                    sg.Checkbox("introduction", default=False, key='DoIntroduction', enable_events=True),
                    sg.Button("Run", size=(3, 1)),
                ],
            ])
        window = sg.Window("Experiment", layout, finalize=True)
        window.bind("<Return>", "Stop")
        window.move(50,10)
        blank = np.zeros((240,320,3),np.uint8)
        #blank = np.zeros((360,480,3),np.uint8)
        ##blank = np.zeros((480,640,3),np.uint8)
        lastExperimentState = 0
        resume_disabled = True
        while True:
            if self.stopped:
                break
            event, values = window.read(timeout=10)
            if event != "__TIMEOUT__":
                print(event)
            if event == "Exit" or event == sg.WIN_CLOSED:
                Agent.stopAll()
                break
            elif event == "Language-EN":
                space["language"] = "en"
            elif event == "Language-SK":
                space["language"] = "sk"
            elif event == "BodyLanguage":
                bodylang = values["BodyLanguage"]
                space["BodyLanguage"] = bodylang
                if not bodylang:
                    space["dontLook"] = True
                else:
                    space["dontLook"] = None
            elif event == "TellIstructions":
                space["TellIstructions"] = values["TellIstructions"]
            elif event == "DoCalibration":
                space["DoCalibration"] = values["DoCalibration"]
            elif event == "DoIntroduction":
                space["DoIntroduction"] = values["DoIntroduction"]
            elif event == "DoRepeat":
                space["DoRepeat"] = values["DoRepeat"]
            elif event == "DoRests":
                space["DoRests"] = values["DoRests"]
            elif event.startswith("StopMode-"):
                option = event[len("StopMode-"):]
                percentage = int(option)
                space["StopMode"] = percentage
            elif event.startswith("Head-"):
                try:
                    modes = {
                        "congruent" : ReplayMode.CONGRUENT,
                        "incongruent" : ReplayMode.INCONGRUENT,
                        "only" : ReplayMode.HEADONLY,
                        "neutral" : ReplayMode.NEUTRAL,
                    }
                    space["head"] = modes[event[len("Head-"):]]
                except:
                    print("unknown head mode !!!")
                    space["head"] = 1 # congruent
            elif event == "Run batch 1":
                space["experiment"] = 2
            elif event == "Run batch 2":
                space["experiment"] = 3
            elif event == "Run test":
                space["experiment"] = 4
            elif event == "Run":
                space["experiment"] = 1
            elif event == "Resume":
                space['suspended'] = False
            elif event == "Stop":
                print("Stop button pressed")
                break
            
            if "Name" in values.keys():
                if space(default="")["name"] != values["Name"]:
                    space["name"] = values["Name"]
                    print("name",space["name"])
                    
            robot_img = space(default=blank)['robotImage']
            robot_imgbytes = cv.imencode(".png", cv.resize(robot_img,(blank.shape[1],blank.shape[0])))[1].tobytes()
            window["robotImage"].update(data=robot_imgbytes)
            human_img = space(default=blank)['humanImage']
            human_imgbytes = cv.imencode(".png", cv.resize(human_img,(blank.shape[1],blank.shape[0])))[1].tobytes()
            window["humanImage"].update(data=human_imgbytes)
            robot_eye = space(default=blank)['robotWideFOV'] # 'robotEye'
            robot_eyebytes = cv.imencode(".png", cv.resize(robot_eye,(blank.shape[1],blank.shape[0])))[1].tobytes()
            window["robotEye"].update(data=robot_eyebytes)
            robot_touch = np.copy(space(default=blank)['touchImage'])
            robot_touch_resized = cv.resize(robot_touch,(blank.shape[1],blank.shape[0]))
            cv.putText(robot_touch_resized,str(datetime.now())[:22],(10,robot_touch_resized.shape[0]-15),0,0.7,(255,255,255),1)
            count = space(default=0)["count"]
            percentage = space(default=0)["percentage"]
            if count > 0:
                txt = '#'+str(count)
                if percentage > 0:
                    txt += f' {percentage}%'
                cv.putText(robot_touch_resized,txt,(10,28),0,1.0,(255,255,255),1)
            b = space(default=0)["break"]
            if b > 0:
                cv.putText(robot_touch_resized,str(b),(robot_touch_resized.shape[1]-55,28),0,0.8,(180,180,180),1)
            robot_touchbytes = cv.imencode(".png", robot_touch_resized)[1].tobytes()
            window["touchImage"].update(data=robot_touchbytes)
            
            experimentState = space(default=False)["experiment"]
            if experimentState != lastExperimentState:
                window["Run batch 1"].update(disabled=(experimentState>0))
                window["Run batch 2"].update(disabled=(experimentState>0))
                window["Run test"].update(disabled=(experimentState>0))
                if self.testing:
                    window["Run"].update(disabled=(experimentState>0))
                lastExperimentState = experimentState
            
            if space(default=False)['suspended']:
                if resume_disabled:
                    resume_disabled = False
                    window['Resume'].update(disabled=False)
            else: 
                if not resume_disabled:
                    resume_disabled = True
                    window['Resume'].update(disabled=True)

        window.close()
        Agent.stopAll()
        print('exiting')
        os._exit(0)
               
    def senseSelectAct(self):
        pass

if __name__ == "__main__":
    class MonitoringAgent(Agent):
          
        def init(self):
            space.attach_trigger("experiment",self,Trigger.NAMES)
            space.attach_trigger("head",self,Trigger.NAMES)
            space.attach_trigger("StopMode",self,Trigger.NAMES)
            space.attach_trigger("stop",self,Trigger.NAMES)
            space.attach_trigger("name",self,Trigger.NAMES)
            space.attach_trigger("language",self,Trigger.NAMES)
            space.attach_trigger("BodyLanguage",self,Trigger.NAMES)
            space.attach_trigger("TellIstructions",self,Trigger.NAMES)
        
        def senseSelectAct(self):
            name = self.triggered()
            print('space',name,space[name] if name is not None else "None")

    GuiAgent()
    MonitoringAgent()
    time.sleep(1)
    space['robotImage'] = np.ones((480,640,3),np.uint8)*100
    space['humanImage'] = np.ones((480,640,3),np.uint8)*180
    space['robotEye'] = np.ones((480,640,3),np.uint8)*200
    space['touchImage'] = np.ones((480,640,3),np.uint8)*60
