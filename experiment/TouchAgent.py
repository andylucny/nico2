from agentspace import Agent, space
import pyautogui
import pygame
import time
import ctypes
import numpy as np
import cv2 as cv

def clean():
    try:
        screen.fill((0, 0, 0)) 
        pygame.display.flip()
    except:
        pass
    color_index = 0
    image[:,:] = (80,80,80)
    space['touchimage'] = image
    
def cross(scr,line_color,point,radius,thickness=1):
    x, y = point
    print(f'[{x},{y}]')
    pygame.draw.line(scr,line_color, (x-radius, y), (x+radius, y), width=thickness)
    pygame.draw.line(scr,line_color, (x, y-radius), (x, y+radius), width=thickness)

def cv_cross(img,point,radius,color,thickness=1):
    x, y = point
    cv.line(img,(int(x-radius),int(y)),(int(x+radius),int(y)),color,thickness)
    cv.line(img,(int(x),int(y-radius)),(int(x),int(y+radius)),color,thickness)

def displayPoints():
    points = []
    
    h=26.5
    ho=5.5 #7.5
    ph=1350//ratio
    pw=2400//ratio
    hb = 9
    hd = hb/2

    dy = int(hd*ph/h)
    ty = int(ho*ph/h)
    my = ty+dy
    by = ty+2*dy

    dx = dy
    tx = (pw-4*dx)/2
    counter = 1
    ids = [5,4,6,1,3,7,2]
    i = 0
    for y in [ph-ty,ph-my,ph-by]:
        for x in [tx,tx+dx,tx+2*dx,tx+3*dx,tx+4*dx]:
            if (counter % 2) == 0:
                print(ids[i],x,y)
                points.append((x//ratio,y//ratio))
                #pygame.draw.circle(screen, (255,0,0), (x,y), 30)
                cross(screen,(255,0,0),(x,y),radius=30,thickness=3)
                text = myfont.render(str(ids[i]), False, (255, 0, 0))
                screen.blit(text, (x+5,y))
                i += 1
            counter +=1

    pygame.display.flip()
    return [ points[3], points[6], points[4], points[1], points[0], points[2], points[5] ]
    
class TouchAgent(Agent):
            
    def init(self):
        # create a Pygame window
        pygame.font.init()
        global myfont
        myfont = pygame.font.SysFont('Comic Sans MS', 30)
        global screen, ratio
        try:
            ratio = 1
            screen = pygame.display.set_mode((2400, 1350), flags=pygame.NOFRAME, depth=0, display=1)
        except:
            ratio = 2
            screen = pygame.display.set_mode((2400//ratio, 1350//ratio))
        global image
        image = np.zeros((1350,2400,3),np.uint8)
        image[:,:] = (80,80,80)
        #pygame.event.set_blocked(pygame.MOUSEMOTION)
        #pygame.event.set_blocked(pygame.MOUSEBUTTONUP)
        #pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)
        pygame.display.set_caption('NICOs touchscreen')
        if ratio == 1:
            HWND = pygame.display.get_wm_info()['window']
            GWL_EXSTYLE = -20
            styles = ctypes.windll.user32.GetWindowLongA(HWND,GWL_EXSTYLE)
            WS_EX_NOACTIVATE = 0x08000000
            styles |= WS_EX_NOACTIVATE
            ctypes.windll.user32.SetWindowLongA(HWND,GWL_EXSTYLE,styles)
        screen_info = pygame.display.Info()
        width, height = screen_info.current_w, screen_info.current_h # 
        colors = [ (255,0,0), (0,255,0), (255,255,0), (80,80,255) ] # Red, Green, Yellow, Light Blue
        print('initialized')
        
        # Run the event loop
        #mouse = pyautogui.position()
        quit = False
        pygame.time.set_timer(pygame.USEREVENT + 1, 500)
        while not quit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or self.stopped:
                    print('quit event')
                    quit = True
                elif event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if event.type == pygame.FINGERDOWN:
                        pos_x, pos_y = int(width*event.x), int(height*event.y)
                    else:
                        pos_x, pos_y = pygame.mouse.get_pos()
                        pos_x, pos_y = ratio*pos_x, ratio*pos_y
                    # Process the first moment of touch
                    circle_color = colors[-1] 
                    circle_radius = 30
                    circle_position = (pos_x, pos_y)
                    print("touch detected at",circle_position)
                    space['touch'] = circle_position
                    screen.fill((0, 0, 0))
                    #pygame.draw.circle(screen, circle_color, circle_position, circle_radius)
                    cross(screen, circle_color, circle_position, circle_radius, 3)
                    pygame.display.flip()
                    cv.circle(image,circle_position,circle_radius,(circle_color[2],circle_color[1],circle_color[0]),cv.FILLED)
                    #cv_cross(image,circle_position,circle_radius,(circle_color[2],circle_color[1],circle_color[0]),7)
                    space['touchImage'] = image
                    #pyautogui.moveTo(mouse[0], mouse[1])
                    #for window in pyautogui.getAllWindows():  
                    #    if "Experiment" in window.title:
                    #        window.activate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == 1073741912: # Numeric ENTER
                        print('stop key pressed')
                        space['stop'] = True
                    elif event.key ==  1073741920: # Numeric arrow up
                        print('run key pressed')
                        space['experiment'] = True
                    #else:
                    #    print('key',event.key)
                #else:
                #    mouse = pyautogui.position()
            pygame.display.flip()
            emulated = space['emulated']
            if emulated is not None:
                circle_radius = 30
                if emulated[0][0] == emulated[1][0] and emulated[0][1] == emulated[1][1]:
                    circle_positions = emulated[:1]
                    circle_colors = colors[2:]
                else:
                    circle_positions = emulated
                    circle_colors = colors
                for circle_position, circle_color in zip(circle_positions,circle_colors):
                    ##pygame.draw.circle(screen, circle_color, circle_position, circle_radius)
                    #cross(screen, circle_color, circle_position, circle_radius)
                    #pygame.display.flip()
                    cv.circle(image,circle_position,circle_radius,(circle_color[2],circle_color[1],circle_color[0]),cv.FILLED)                
                    #cv_cross(image,circle_position,circle_radius,(circle_color[2],circle_color[1],circle_color[0]),7)
                space['touchImage'] = image
                space['emulated'] = None
            time.sleep(0.025)
            
        # quit Pygame
        print('quiting pygame')
        pygame.quit()

    def senseSelectAct(self):
        pass
    
if __name__ == "__main__":
   
    import os
    def quit():
        os._exit(0)

    TouchAgent()
    
    time.sleep(3)
    
    displayPoints()
    