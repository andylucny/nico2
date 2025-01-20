# https://www.compuphase.com/usbkey/usbkey_en.htm
# https://www.compuphase.com/usbkey/keyconfigurator_en.htm
# configured into the 'right ctrl'
import keyboard
from agentspace import Agent, space

class SafetyAgent(Agent):

    def init(self):
        while True:
            if keyboard.read_key() == 'right ctrl':
                print("You pressed the safety button.")
                Agent.stopAll()
                break
 
    def senseSelectAct(self):
        pass

if __name__ == "__main__":

    import os
    def quit():
        os._exit(0)

    SafetyButtonAgent()
    