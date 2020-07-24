import time
import cv2
import mss
import numpy as np
from time import sleep
from tkinter import *



def empty(x):
    pass

def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]),
                                                None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver

leftHealthBar = 0

def getContours(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        #print(area)
        # set the size
        # if area < 100:objectType="none"
        if area >= 100 and area <= 5000:
            cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt, True)
            #print(peri)
            #approx = cv2.approxPolyDP(cnt, .2 * peri, False)
            approx = cv2.convexHull(cnt,False,False,True)
            #print("points:",len(approx))
            objCor = len(approx)
            x, y, w, h = cv2.boundingRect(approx)
            if objCor != int: objectType = "XX"
            if objCor <= 3:objectType = "0"
            if objCor > 3:objectType = "Health Bar"
            cv2.rectangle(imgContour, (x-5, y-5), (x + w+5, y + h+5), (255, 0, 0), 2)
            leftHP = round(peri/10.5)
            boxtext = str(objectType) + ": " + str(leftHP) +"%"
            cv2.putText(imgContour,boxtext,
                        (x+10, y+10), cv2.FONT_HERSHEY_PLAIN, 1, (100, 0, 100), 2)

            global leftHealthBar
            print("Left",boxtext)
            leftHealthBar = leftHP
            return leftHealthBar
            sleep(0.1)
        else:
            pass




# create trackbars / trackbar window
cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 400, 400)
cv2.createTrackbar("Hue Min", "Trackbars", 0, 179, empty)
cv2.createTrackbar("Hue Max", "Trackbars", 70, 179, empty)
cv2.createTrackbar("Sat Min", "Trackbars", 61, 255, empty)
cv2.createTrackbar("Sat Max", "Trackbars", 255, 255, empty)
cv2.createTrackbar("Val Min", "Trackbars", 219, 255, empty)
cv2.createTrackbar("Val Max", "Trackbars", 255, 255, empty)

with mss.mss() as sct:
    # Part of the screen to capture
    monitor = {"top": 310, "left": 250, "width":600, "height": 40}

    while "Screen capturing":
        last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
        img = np.array(sct.grab(monitor))

        # Display the picture
        # cv2.imshow("OpenCV/Numpy normal", img)

        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale',
        #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

        #print("fps: {}".format(1 / (time.time() - last_time)))

        # set kernel size \\ adjust this to fine tune the image
        kernel = np.ones((5, 5), np.uint8)

        # grab screen and alter
        grabCanny = cv2.Canny(img, 40, 40)
        grabDilation = cv2.dilate(grabCanny, kernel, iterations=0)
        grabEroded = cv2.erode(grabCanny, kernel, iterations=1)
        grabHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # assign track bars
        h_min = cv2.getTrackbarPos("Hue Min", "Trackbars")
        h_max = cv2.getTrackbarPos("Hue Max", "Trackbars")
        s_min = cv2.getTrackbarPos("Sat Min", "Trackbars")
        s_max = cv2.getTrackbarPos("Sat Max", "Trackbars")
        v_min = cv2.getTrackbarPos("Val Min", "Trackbars")
        v_max = cv2.getTrackbarPos("Val Max", "Trackbars")
        # print(h_min,h_max,s_min,s_max,v_min,v_max) #print to test if the above is working.
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        grabMask = cv2.inRange(grabHSV, lower, upper)
        grabResult = cv2.bitwise_and(img, img, mask=grabMask)
        grabGray = cv2.cvtColor(grabResult, cv2.COLOR_BGR2GRAY)
        imgContour = grabGray.copy()
        getContours(imgContour)



        # Display Screen and Alterations
        # cv2.imshow("Original",img)
        # SHOW THE VIDEO WINDOW
        # cv2.imshow("Canny Image", grabCanny)
        # cv2.imshow("Dilated Image",grabDilation)
        # cv2.imshow("Eroded Image", grabEroded)
        # cv2.imshow("HSV",grabHSV)
        # cv2.imshow("Mask",grabMask)
        cv2.imshow("Final", grabResult)
        cv2.imshow("CPU Eyes", imgContour)


        # press ` to close
        if cv2.waitKey(60) & 0xFF == ord("`"):
            cv2.destroyAllWindows()
            break
cv2.waitKey(0)
