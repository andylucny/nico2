import pyttsx3
from agentspace import space

en_dictionary = {
    "@introduction" : "Hello, welcome to the legibility experiment!",
    "@calibration" : "For calibration look at the red point in the middle and corners of the screen. Then sit down and touch the touchscreen.",
    "@letsgo" : "Let's go on! After each beep, guess the point where robot points and touch it on the screen. You have two seconds to do this.",
    "@touch-expired" : "You failed to touch the screen within the time limit, never mind, maybe next time.",
    "@thank-you" : "Thank you.",
    "@done" : "Done.",
}

sk_dictionary = {
    "@introduction" : "Dobrý deň! Vitajte v našom experimente čitateľnosti!",
    "@calibration" : "Pri kalibrácii sa pozerajte vždy na červený bod v strede alebo v rohoch obrazovky. Po ukončení kalibrácie sa posaďte a svoju pripravenosť potvrďte dotykom obrazovky.",
    "@letsgo" : "Poďme na to! Vždy po zaznení zvukového signálu, dotknite sa obrazovky v mieste, kde odhadujete, že sa chcel dotknúť robot. Máte na to dve sekundy.",
    "@touch-expired" : "Nestihli ste sa dotknúť obraovky v časovom limite, nevadí, snáď nabudúce.",
    "@thank-you" : "Ďakujem.",
    "@done" : "Hotovo.",
}

def translate(language,text):
    dictionary = sk_dictionary if language == 'sk' else en_dictionary
    if text in dictionary:
        return dictionary[text]
    return text
    
def speak(text, language='en'):
    language = space(default='en')["language"]
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
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
    space["language"] = 'en'
    speak('preparing, please, wait')
    print('done')
    space["language"] = 'sk'
    speak('Thank you.')
    print('hotovo')
