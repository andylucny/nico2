import pygame

# Initialize pygame mixer
pygame.mixer.init()

def play(filename, wait=False):
    # Load and play a beep sound
    pygame.mixer.Sound(filename).play()
    # Optionally, you can wait for the sound to finish
    if wait:
        pygame.time.wait(500)

def beep(wait=False):
    play("beep.wav",wait)

def fail(wait=False):
    play("fail.wav",wait)

if __name__ == '__main__': # run in the interactive mode
    beep(wait=True)
    fail()
