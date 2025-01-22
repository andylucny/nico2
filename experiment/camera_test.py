import numpy as np
import cv2 as cv

camera = cv.VideoCapture(3,cv.CAP_DSHOW)
fps = camera.get(cv.CAP_PROP_FPS)
print('fps:',fps)
while True:
    ret, img = camera.read()
    if not ret:
        break
    cv.imshow('img',img)
    if cv.waitKey(1) == 27:
        break

camera.release()
