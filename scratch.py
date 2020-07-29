import time
import cv2
import mss
import numpy as np
from time import sleep
from tkinter import *
import socket
import threading
import pytesseract
import re
import pyautogui
from PIL import ImageFilter
import multiprocessing
from datetime import datetime
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"



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
def empty(x):
    pass
cv2.namedWindow("Control")
cv2.resizeWindow("Control",400,260)
cv2.createTrackbar("Hue Min","Control",0,179, empty) #function is empty because it needs to run a function. We'll pull the values from these bars via another function.
cv2.createTrackbar("Hue Max","Control",179,179, empty)
cv2.createTrackbar("Sat Min", "Control", 0, 255, empty)
cv2.createTrackbar("Sat Max", "Control", 36, 255, empty)
cv2.createTrackbar("Val Min", "Control", 232, 255, empty)
cv2.createTrackbar("Val Max", "Control", 255, 255, empty)
while True:
    mainGrab = pyautogui.screenshot()
    mainGrab = np.array(mainGrab)
    mainGrab = np.uint8(mainGrab)
    mainGrab = mainGrab[170:240, 805:1115]
    mainGrab = stackImages(1, [mainGrab])
    #imgHSV = cv2.cvtColor(mainGrab, cv2.COLOR_BGR2HSV)

    imgHSV = cv2.cvtColor(mainGrab, cv2.COLOR_BGR2HSV)
    h_min = cv2.getTrackbarPos("Hue Min", "Control")
    h_max = cv2.getTrackbarPos("Hue Max", "Control")
    s_min = cv2.getTrackbarPos("Sat Min", "Control")
    s_max = cv2.getTrackbarPos("Sat Max", "Control")
    v_min = cv2.getTrackbarPos("Val Min", "Control")
    v_max = cv2.getTrackbarPos("Val Max", "Control")
    # Create Mask using the trackbar values.
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHSV, lower, upper)
    finalImg = cv2.bitwise_and(mainGrab, mainGrab, mask=mask)
    # Adjust Colors // Process Image
    # Conver to Gray
    imgGray = cv2.cvtColor(mainGrab, cv2.COLOR_BGR2GRAY)
    # Blur it
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 0)
    # Find Detect Color
    # Convert to Canny. Black / White lines only.
    imgCanny = cv2.Canny(mainGrab, 150, 200)
    # Create the Kernel - Dilate and Erode will use this to adjust their sizes.
    ksize = 1
    kernel = np.ones((ksize, ksize), np.uint8)
    # Dilation means thicker lines.
    imgDilation = cv2.dilate(imgCanny, kernel, iterations=1)
    # Erosion means thinner lines.
    imgEroded = cv2.erode(imgCanny, kernel, iterations=1)
    incomingBuyPhaseText = pytesseract.image_to_string(finalImg)
    finalStack = stackImages(1, ([imgHSV, finalImg], [mask, imgEroded]))
    cv2.imshow("Scratch Stack", finalStack)
    print(incomingBuyPhaseText)
    incomingBuyPhaseText = len(incomingBuyPhaseText)


    if cv2.waitKey(1) & 0xFF == ord("`"):
                cv2.destroyAllWindows()
                break
