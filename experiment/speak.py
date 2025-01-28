import pyttsx3
from agentspace import space

en_dictionary = {
    "@introduction" : "Hello! Thank you for participating in our experiment.",
    "@before-demo" : "I am the robot Niko, and in this experiment I always point to some point on the touchscreen, like this:",
    "@after-demo" : "During the experiment, however, I will only do this action partially, and your task will be to guess the point I would touch if I did it in full.",
    "@calibration" : "Now we will calibrate the eye tracker. For calibration, stand up and look downsss at the red point in the middle and corners of the screen. Then sit down and touch the touchscreen.",
    "@no-calibration" : "Please, sit down and touch the touchscreen, when you are ready.",
    "@letsgo" : "Let's go on! After each beep, guess the point where I aim to point and touch it on the screen. You have two seconds to do this.",
    "@touch-expired" : "You failed to touch the screen within the time limit, never mind, maybe next time.",
    "@thank-you" : "Thank you.",
    "@done" : "Done.",
    "@encourage1" : "You are doing great!",
    "@encourage2" : "You are doing fantastic!",
    "@encourage3" : "We are on the right track!",
    "@encourage4" : "Every step you take brings you closer to the goal!",
    "@encourage5" : "Great, just a little more effort!",
    "@before-rest" : "Let us take a fifteen second break!",
    "@after-rest" : "O.K., keep going!",
}

sk_dictionary = {
    "@introduction" : "Dobrý deň! Ďakujeme, že sa zúčastňujte nášho experimentu!",
    "@before-demo" : "Som robot Niko a v tomto experimente vždy ukazujem na nejaký bod na dotykovej obrazovke, napríklad takto:",
    "@after-demo" : "Počas experimentu, však budem robit túto akciu len čiastočne a Vašou úlohou bude hádať bod, ktorého by som sa dotkol, keby som ju vykonal celú.",
    "@calibration" : "Teraz budeme kalibrovať sledovenie pohybu očí. Pri kalibrácii sa postavte a zhora pozerajte vždy na červený bod v strede alebo v rohoch obrazovky a snažte sa, aby sa zmenil na zelený. Po ukončení kalibrácie sa posaďte a svoju pripravenosť začať experiment potvrďte dotykom obrazovky.",
    "@no-calibration" : "Prosím, sadnite si a svoju pripravenosť potvrďte dotykom obrazovky.",
    "@letsgo" : "Poďme na to! Vždy po zaznení zvukového signálu, dotknite sa obrazovky v mieste, kde odhadujete, že som sa chcel dotknúť. Máte na to dve sekundy.",
    "@touch-expired" : "Nestihli ste sa dotknúť obrazovky v časovom limite, nevadí, snáď nabudúce.",
    "@thank-you" : "Ďakujem.",
    "@done" : "Hotovo.",
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
    
def speak(text):
    language = space(default='sk')["language"]
    engine = pyttsx3.init()
    rate = 130 #150 # higher means faster
    engine.setProperty('rate',rate)
    voices = engine.getProperty('voices')
    speaker = 3 if language == 'sk' else 2 # 3 is slovak Filip, 0 is David, 1 Markus, 2 Hazel
    engine.setProperty('voice', voices[speaker].id)
    text = translate(language,text)
    engine.say(text)
    print('speaking on <'+text+'>')
    space['speaking'] = True
    engine.runAndWait()
    space['speaking'] = False
    print('speaking off')

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
