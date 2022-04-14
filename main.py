import cvzone
import cv2
import math
import random
import numpy as np
from cvzone.HandTrackingModule import HandDetector
cap=cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)
detector=HandDetector(detectionCon=0.8,maxHands=1)

class SnakeGameClass:
    def __init__(self,pathFood):
        self.points=[] #all points of snake
        self.lengths=[]
        self.gameOver=False
        self.currentLength=0
        self.allowedLength=200
        self.score=0
        self.previousHead=0,0
        self.imgFood=cv2.imread(pathFood,cv2.IMREAD_UNCHANGED)
        self.hFood,self.wFood,_=self.imgFood.shape
        self.foodPoint=0,0
        self.randomFoodlocation()
    def randomFoodlocation(self):
        self.foodPoint=random.randint(10,1000),random.randint(10,600)
        
    def update(self,imgMain,currentHead):
     if self.gameOver!=True:
        px,py=self.previousHead
        cx,cy=currentHead

        self.points.append([cx,cy])
        distance=math.hypot(cx-px,cy-py)
        self.lengths.append(distance)
        self.currentLength+=distance
        self.previousHead=cx,cy

        # length reduction
        if self.currentLength>self.allowedLength:
            for i,length in enumerate(self.lengths):
                self.currentLength-=length
                self.lengths.pop(i)
                self.points.pop(i)
                if self.currentLength<self.allowedLength:
                    break


        #check if snake ate the donut
        rx,ry=self.foodPoint
        if (rx-self.wFood//2)<cx<rx+self.wFood//2 and ry-self.hFood//2<cy<ry+self.hFood//2:
            self.randomFoodlocation()
            self.allowedLength+=50
            self.score+=1
            print(self.score)



        # Draw Snake
        if self.points:
           for i,point in enumerate(self.points):
              if i!=0:
                cv2.line(imgMain,self.points[i-1],self.points[i],(0,0,255),5)
           cv2.circle(imgMain,self.points[-1],10,(200,0,200),cv2.FILLED)




        #Draw Food
        rx,ry=self.foodPoint
        try:
          imgMain=(cvzone.overlayPNG(imgMain,self.imgFood,(rx-self.wFood//2,ry-self.hFood//2)))

          cvzone.putTextRect(imgMain,f'Score: {self.score}',[15,20],scale=1,thickness=2,offset=10)



        except:
            print(imgMain.shape)
            self.randomFoodlocation()

        





        #check for collisions
        pts=np.array(self.points[:-2],np.int32)
        pts=pts.reshape((-1,1,2))
        cv2.polylines(imgMain,[pts],False,(0,200,0),2)
        minDist=cv2.pointPolygonTest(pts,(cx,cy),True)
        if minDist>=-1 and minDist<=1:
            print("Hit",minDist)
            self.gameOver=True      
     else:
              cvzone.putTextRect(imgMain,"Game Over",[150,200],scale=5,thickness=5,offset=10)
              cvzone.putTextRect(imgMain,f'Your score:{self.score}',[75,300],scale=5,thickness=5,offset=10)
              try:
                self.points=[]
                self.lengths=[]
                self.currentLength=0
                self.allowedLength=150
                self.previousHead=0,0
                self.randomFoodlocation()
              except:
                  self.randomFoodlocation()
     return imgMain

            
game=SnakeGameClass("donut.png")



while True:
    success,img=cap.read()
    img=cv2.flip(img,1)
    hands,img=detector.findHands(img,flipType=False)

    if hands:
        lmlist=hands[0]["lmList"]
        pointIndex=lmlist[8][0:2]
        img=game.update(img,pointIndex)
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.imshow("window", img)
    key=cv2.waitKey(1)
    if key==ord('r'):
         game.gameOver=False
         game.score=0