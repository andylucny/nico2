import numpy as np
import cv2 as cv 
from agentspace import Agent, space
import time

import requests
import os
import zipfile
import io

def download_and_unzip(path,url):
    if os.path.exists(path):
        return
    print("downloading",path)
    response = requests.get(url)
    if response.ok:
        file_like_object = io.BytesIO(response.content)
        zipfile_object = zipfile.ZipFile(file_like_object)    
        zipfile_object.extractall(".")

def download_face():
    os.makedirs('face', exist_ok=True)
    download_and_unzip("face/labels.txt","https://www.agentspace.org/download/face.zip")  

download_face()

class FaceAgent(Agent):

    def __init__(self,nameImage,nameFacePosition="face-position",nameFaceImage="face-image",nameFacePoint="face-point"):
        self.nameImage = nameImage
        self.nameFacePosition = nameFacePosition
        self.nameFaceImage = nameFaceImage
        self.nameFacePoint = nameFacePoint
        super().__init__()

    def init(self): 
        print("faceDetector: loading model")
        face_architecture = 'face/deploy.prototxt'
        face_weights = 'face/res10_300x300_ssd_iter_140000.caffemodel'
        self.net = cv.dnn.readNetFromCaffe(face_architecture,face_weights)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)
        #self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
        #self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)
        print("faceDetector: model loaded")

        space.attach_trigger(self.nameImage, self)

    def senseSelectAct(self):
        image = space[self.nameImage]
        if image is None:
            return

        height = 300
        width = 300
        mean = (104.0, 177.0, 123.0)
        threshold = 0.5
        h, w = image.shape[:2] 

        # convert to RGB
        rgb = cv.cvtColor(image,cv.COLOR_BGR2RGB)

        # blob preparation
        blob = cv.dnn.blobFromImage(cv.resize(image,(width,height)),1.0,(width,height),mean)

        # passing blob through the network to detect and pridiction
        self.net.setInput(blob)
        detections = self.net.forward()

        # loop over the detections
        rects = []
        faces = []
        for i in range(detections.shape[2]):
            # extract the confidence and prediction
            confidence = detections[0, 0, i, 2]
            # filter detections by confidence greater than the minimum
            if confidence > threshold:
                # compute the (x, y)-coordinates of the bounding box for the object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                startX, startY, endX, endY = box.astype(np.int32)
                if startX < 0:
                    startX = 0
                if startY < 0:
                    startY = 0
                if endX > w:
                    endX = w
                if endY > h:
                    endY = h
                if (startY+1 < endY) and (startX+1 < endX):
                    rects.append((startX, startY, endX, endY, confidence))
                    face = np.copy(image[startY:endY,startX:endX,:])
                    faces.append(face)
        
        result = np.copy(image)

        if len(rects) > 0:
            
            rects = np.array(rects,np.float32)
            
            # select the best face
            FOV = 156 # [dg] for zoom 170
            rot = space(default=0.0)['head_x'] / (FOV/2)
            mean = w/2 - w*rot/2
            sigma = w/4
            x = (rects[:,0]+rects[:,2])/2
            confidences = rects[:,4]
            pe = np.exp(-(x-mean)**2/(2*sigma**2))
            best = np.argmax(confidences*pe)
            #best = np.argmin([rect[4] for rect in rects])

            startX, startY, endX, endY = rects[best,:4].astype(np.int32)
            confidence = rects[best,4]
            cv.rectangle(result, (startX, startY), (endX, endY), (0, 0, 255), 2)
            text = "{:.2f}%".format(confidence * 100)
            cv.putText(result, text, (startX, startY-5), 0, 1.0, (0, 0, 255), 2)

            # output the find info to the blackboard
            rect = ((startX+endX)/2/w,(startY+endY)/2/h,(endX-startX-1)/w,(endY-startY-1)/h)
            #space(validity=0.2)[self.nameFacePosition] = rect
            #space(validity=0.2)[self.nameFaceImage] = faces[best]
            point = rect[:2]
            #print('face',point)
            space(validity=0.5)[self.nameFacePoint] = point

        #cv.imshow("faces",result)
        #cv.waitKey(1)

if __name__ == '__main__':
    space['head_x'] = -30.0
    FaceAgent('bgr',nameFacePoint='point')
    camera = cv.VideoCapture(0)
    t0 = int(time.time())
    fps = 0
    i = 0
    while True:
        hasFrame, frame = camera.read() 
        if not hasFrame: 
            break
        space(validity=0.15)['bgr'] = frame
        t1 = int(time.time())
        if t0 != t1:
            fps = i
            i = 0
            t0 = t1
        i += 1
        point = space['point']
        if point is not None:
            x, y = int(point[0]*frame.shape[1]), int(point[1]*frame.shape[0])
            cv.circle(frame,(x,y),2,(0,255,255),cv.FILLED)
        cv.imshow('face',frame)
        if cv.waitKey(1) == 27:
            break
    cv.destroyAllWindows()
