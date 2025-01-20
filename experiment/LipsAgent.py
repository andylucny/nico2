import time
from agentspace import Agent, space

from led import LED

class LipsAgent(Agent):
    
    def __init__(self, nameSpeaking='speaking', nameEmotion='emotion'):
        self.nameSpeaking = nameSpeaking
        self.nameEmotion = nameEmotion
        super().__init__()
    
    def init(self):
        self.led = LED()
        self.last = 'neutral'
        self.led.send_preset(self.last)
        self.attach_timer(0.25)
    
    def senseSelectAct(self):
        if space(default=False)[self.nameSpeaking]:
            if self.last != 'surprise':
                self.last = 'surprise'
            else:
                self.last = 'neutral'
            self.led.send_preset(self.last)
        else:
            emotion = space[self.nameEmotion] 
            if emotion is not None:
                if self.last != emotion:
                    self.last = emotion
                    self.led.send_preset(self.last)
            elif self.last != 'neutral':
                self.last = 'neutral'
                self.led.send_preset(self.last)

if __name__ == "__main__":

    agent = LipsAgent()
    print('started')
    time.sleep(1)
    space(validity=2)['emotion'] = 'happiness'
    time.sleep(4)
    space(validity=3)['speaking'] = True
    time.sleep(4)
