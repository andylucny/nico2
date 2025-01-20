import pyttsx3
from agentspace import space

en_dictionary = {
}

sk_dictionary = {
    "Preparing. Please, wait.":
    "Prebieha príprava, čakajte.",
    
    "Please enter your name and start the experiment by clicking Run":
    "Zadajte prosím meno a odštartujte experiment kliknutím Run",
    
    "Starting experiment...":
    "Experiment začína",
    
    "Please, use button Enter to stop me when you are ready to guess the touch point.":
    "Použite tlačidlo stop keď budete schopný odhadnúť bod dotyku.",
    
    "You have used the stop button at ":
    "Použili ste tlačidlo stop pri ",
    
    " percent, please touch the estimated touch point by your finger.":
    " percentách, prosím, dotknite sa prstom odhadovaného miesta dotyku",
    
    "The movement of my arm has been stopped after ":
    "Pohyb mojej ruky bol zastavený po ",
    
    "Thank you. Let us look on my intention.":
    "Ďakujem. Pozrime sa, aký bol môj úmysel.",
    
    "This was my intention.":
    "Toto bol môj úmysel.",

    "Thank you.":
    "Ďakujem.",
    
    "Data are recorded.":
    "Dáta sú uložené."
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
