import os
import pyttsx3
import pygame
import tempfile
from agentspace import space

# Initialize pygame mixer
pygame.mixer.init()

en_dictionary = {
    "@introduction" : "Hello, welcome to our experiment.",
    "@before-demo" : "We will play several games to recognize my intention or, more simply, you have to guess the point I intend to touch. Now I will show you the whole movement.",
    "@after-demo" : "During the game, sometimes I will only look at that point, sometimes I will perform only part of the movement with my hand, sometimes I will use both my gaze and my hand. Your goal is to press the touchscreen in front of you at my intended position.",
    "@calibration" : "Now we will calibrate the eye tracker. For calibration, stand up and look down at the red point in the middle and corners of the screen. When the calibration is concluded, sit down and when you are ready to start, touch the touchscreen.",
    "@no-calibration" : "Please, sit down and when you are ready to start, touch the touchscreen.",
    "@letsgo" : "Let's go on! After each beep, guess the point I intend to touch and touch it on the screen. You have two seconds to do this.",
    "@touch-expired-repeat" : "You failed to touch the screen within the time limit, never mind, hopefully it will work when repeated.",
    "@touch-expired-discard" : "You failed to touch the screen within the time limit, be careful, you have to provide your response more quickly.",
    "@thank-you" : "Thank you.",
    "@done" : "Done. Thank you for your participation in our experiment.",
    "@encourage1" : "You are doing great!",
    "@encourage2" : "You are doing fantastic!",
    "@encourage3" : "We are on the right track!",
    "@encourage4" : "Every step you take brings you closer to the goal!",
    "@encourage5" : "Great, just a little more effort!",
    "@before-rest" : "Let us take a fifteen second break!",
    "@after-rest" : "O.K., keep going!",
}

sk_dictionary = {
    "@introduction" : "Dobrý deň! Vitajte v našom experimente!",
    "@before-demo" : "Budeme sa hrať niekoľko hier zameraných na odhadovanie môjho úmyslu. Jednoducho povedané: budete hádať bod na dotykovej obrazovke, v ktorom sa jej chystám dotknúť. Teraz vám predvediem celý pohyb.",
    "@after-demo" : "Počas experimentu, budem niekedy na ten bod iba hľadieť, niekedy vykonám iba časť pohybu rukou, niekedy budem robiť oboje naraz. Vašou úlohou bude dotknúť sa dotykovej obrazovky, ktorá leží pred vami, v mieste, v ktorom sa jej chcem dotknúť ja.",
    "@calibration" : "Teraz budeme kalibrovať sledovanie pohybu očí. Pri kalibrácii sa postavte a zhora pozerajte vždy na červený bod v strede alebo v rohoch obrazovky a snažte sa, aby sa zmenil na zelený. Po ukončení kalibrácie sa posaďte a svoju pripravenosť začať experiment potvrďte dotykom obrazovky.",
    "@no-calibration" : "Prosím, sadnite si a keď budete pripravený začať, potvrďte to dotykom obrazovky v ľubovoľnom mieste.",
    "@letsgo" : "Poďme na to! Vždy po zaznení zvukového signálu sa dotknite obrazovky v mieste, kde odhadujete, že som mal úmysel sa dotknúť. Máte na to dve sekundy.",
    "@touch-expired-repeat" : "Nestihli ste sa dotknúť obrazovky v časovom limite, nevadí, snáď sa to podarí pri zopakovaní.",
    "@touch-expired-discard" : "Nestihli ste sa dotknúť obrazovky v časovom limite, sústreďte sa, prosím, musíte reagovať rýchlejšie.",
    "@thank-you" : "Ďakujem.",
    "@done" : "Hotovo. Ďakujem za účasť v našom experimente.",
    "@encourage1" : "Len tak ďalej!",
    "@encourage2" : "Ide to výborne!",
    "@encourage3" : "Sme na správnej ceste!",
    "@encourage4" : "Každý krok nás približuje k cieľu!",
    "@encourage5" : "Skvelé! Ešte chvíľu a bude to hotové!",
    "@before-rest" : "Spravme si päťnásť sekundovú prestávku!",
    "@after-rest" : "Dobre. Pokračujme!",
}

def translate(language,text):
    dictionary = sk_dictionary if language == 'sk' else en_dictionary
    if text in dictionary:
        return dictionary[text]
    return text
    
def set_voice(engine, language):
    voices = engine.getProperty('voices')
    if len(voices) == 0:
        import platform 
        if platform.system() == "Windows":
            print("run Registy Editor (regedit) and")
            print("export content of Computer\\HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech_OneCore\\Voices\\Tokens into my.reg file" )
            print("rewrite paths in file to Computer\\HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens")
            print("import the my.reg file")
        else:
            print("install:")
            print("$ sudo apt-get install espeak -y")
        os._exit(0)
    
    voice_names = [ voice.name for voice in voices ] 
    #print(voice_names)
    
    if language == 'sk':
        try:
            speaker = voice_names.index('Microsoft Filip - Slovak (Slovakia)')
        except ValueError:
            try:
                speaker = voice_names.index('Vocalizer Expressive Laura Harpo 22kHz')
            except ValueError:
                speaker = 0
    
    else:
        try:
            speaker = voice_names.index('Microsoft Zira Desktop - English (United States)')
        except ValueError:
            try:
                speaker = voice_names.index('Microsoft David Desktop - English (United States)')
            except ValueError:
                try:
                    speaker = voice_names.index('english-us')
                except ValueError:
                    speaker = 0
    
    #print('speaker:',speaker, voices[speaker].name)
    engine.setProperty('voice', voices[speaker].id)
    
def speak(text):
    language = space(default='sk')["language"]
    engine = pyttsx3.init()
    rate = 130 #150 # higher means faster
    engine.setProperty('rate',rate)
    set_voice(engine, language)
    text = translate(language,text)
    print('speaking on <'+text+'>')
    space['speaking'] = True
    temp_filename = "speech.wav"
    engine.save_to_file(text, temp_filename) # Save the generated speech to a file
    engine.runAndWait() # generate wav
    pygame.mixer.Sound(temp_filename).play() # play the wav
    # Wait until the sound finishes
    while pygame.mixer.get_busy(): # Check if anything is playing
        pygame.time.Clock().tick(10) 
    space['speaking'] = False
    print('speaking off')
    os.remove(temp_filename)

if __name__ == "__main__":
    import time
    from LipsAgent import LipsAgent
    LipsAgent()
    time.sleep(0.5)
    space["language"] = 'sk'
    speak('@after-demo')
    #speak('preparing, please, wait')
    print('done')
    #space["language"] = 'sk'
    #speak('@thank-you.')
    #print('hotovo')
