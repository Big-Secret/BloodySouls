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

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"

HEADER = 64
PORT = 11666
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.87"
ADDR = (SERVER, PORT)
FIRE_MESSAGE = "Hit"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    #print(client.recv(2048).decode(FORMAT))


def empty(x):
    pass

# def stackImages(scale, imgArray):
#     rows = len(imgArray)
#     cols = len(imgArray[0])
#     rowsAvailable = isinstance(imgArray[0], list)
#     width = imgArray[0][0].shape[1]
#     height = imgArray[0][0].shape[0]
#     if rowsAvailable:
#         for x in range(0, rows):
#             for y in range(0, cols):
#                 if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
#                     imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
#                 else:
#                     imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]),
#                                                 None, scale, scale)
#                 if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
#         imageBlank = np.zeros((height, width, 3), np.uint8)
#         hor = [imageBlank] * rows
#         hor_con = [imageBlank] * rows
#         for x in range(0, rows):
#             hor[x] = np.hstack(imgArray[x])
#         ver = np.vstack(hor)
#     else:
#         for x in range(0, rows):
#             if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
#                 imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
#             else:
#                 imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
#             if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
#         hor = np.hstack(imgArray)
#         ver = hor
#     return ver




# cv2.createTrackbar("Hue Min2", "Trackbars", 0, 179, empty)
# cv2.createTrackbar("Hue Max2", "Trackbars", 179, 179, empty)
# cv2.createTrackbar("Sat Min2", "Trackbars", 0, 255, empty)
# cv2.createTrackbar("Sat Max2", "Trackbars", 42, 255, empty)
# cv2.createTrackbar("Val Min2", "Trackbars", 179, 255, empty)
# cv2.createTrackbar("Val Max2", "Trackbars", 255, 255, empty)

# cv2.namedWindow("Trackbars")
# cv2.resizeWindow("Trackbars", 400, 400)
# cv2.createTrackbar("Hue Min", "Trackbars", 0, 179, empty)
# cv2.createTrackbar("Hue Max", "Trackbars", 179, 179, empty)
# cv2.createTrackbar("Sat Min", "Trackbars", 0, 255, empty)
# cv2.createTrackbar("Sat Max", "Trackbars", 255, 255, empty)
# cv2.createTrackbar("Val Min", "Trackbars", 0, 255, empty)
# cv2.createTrackbar("Val Max", "Trackbars", 255, 255, empty)

# SHOOTING FUNCTIONS

currentHealth = 100
previousHealth = 100
buyPhase = False
dead = False
check = False


def fire(x):
    global dead
    send(FIRE_MESSAGE)
    try:
        if x == "":
            dead = True
        if x > 0:
            print("Player Still Alive")
    except:
        pass

def checkHP(text):
    global currentHealth, previousHealth, buyPhase, dead
    #print("Check HP GOT:", text)
    try:
        currentHealth = int(text)
        if currentHealth <=150:
            currentHealth, previousHealth = int(currentHealth), int(previousHealth)
            if currentHealth < 100:
                if currentHealth < previousHealth:
                    fire(currentHealth)
                    print("Fire!")
                    previousHealth = currentHealth
                if currentHealth > previousHealth:
                    difference = currentHealth - previousHealth
                    if difference < 50:
                        print("You're being healed!!!")
                        previousHealth = currentHealth
                    if difference >= 50:
                        dead = True
                        print("You got hit hard")
                        fire(currentHealth)

        else:
            currentHealth = previousHealth
    except:
        print("error")
        pass




with mss.mss() as sct:
    # Part of the screen to capture
    # monitor = {"top": 1320, "left": 730, "width": 110, "height": 75}
    # monitor2 = {"top": 250, "left": 1025, "width": 410, "height": 100}

    monitor = {"top": 1000, "left": 570, "width": 84, "height": 52}
    monitor2 = {"top": 165, "left": 805, "width": 306, "height": 82}

def hpWIN():
    global currentHealth, previousHealth, buyPhase, dead, shopOpen, check
    # create trackbars / trackbar window
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 400, 400)
    cv2.createTrackbar("Hue Min", "Trackbars", 0, 179, empty)
    cv2.createTrackbar("Hue Max", "Trackbars", 179, 179, empty)
    cv2.createTrackbar("Sat Min", "Trackbars", 0, 255, empty)
    cv2.createTrackbar("Sat Max", "Trackbars", 255, 255, empty)
    cv2.createTrackbar("Val Min", "Trackbars", 231, 255, empty)
    cv2.createTrackbar("Val Max", "Trackbars", 255, 255, empty)
    while True:
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
        kernel = np.ones((10, 10), np.uint8)

        # grab screen and alter
        # grabCanny = cv2.Canny(img, 40, 40)
        # grabDilation = cv2.dilate(grabCanny, kernel, iterations=0)
        # grabEroded = cv2.erode(grabCanny, kernel, iterations=1)
        grabHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # assign track bars
        h_min = cv2.getTrackbarPos("Hue Min", "Trackbars")
        h_max = cv2.getTrackbarPos("Hue Max", "Trackbars")
        s_min = cv2.getTrackbarPos("Sat Min", "Trackbars")
        s_max = cv2.getTrackbarPos("Sat Max", "Trackbars")
        v_min = cv2.getTrackbarPos("Val Min", "Trackbars")
        v_max = cv2.getTrackbarPos("Val Max", "Trackbars")
        # # print(h_min,h_max,s_min,s_max,v_min,v_max) #print to test if the above is working.
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        grabMask = cv2.inRange(grabHSV, lower, upper)
        grabResult = cv2.bitwise_and(img, img, mask=grabMask)
        gray = cv2.cvtColor(grabResult, cv2.COLOR_BGR2GRAY)
        #gray = grabGray.copy()

        #new stuff
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
        contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        im2 = img.copy()

        # Display Screen and Alterations
        #v2.imshow("Original",im2)
        # SHOW THE VIDEO WINDOW
        # cv2.imshow("Canny Image", grabCanny)
        # cv2.imshow("Dilated Image",grabDilation)
        # cv2.imshow("Eroded Image", grabEroded)
        # cv2.imshow("HSV",grabHSV)
        # cv2.imshow("Mask",grabMask)
        # cv2.imshow("Final", grabResult)
        cv2.imshow("CPU Eyes", gray)
        # cv2.imshow("Final 2",killedby)


        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            rect = cv2.rectangle(im2, (x, y), (x + w, + h), (0, 255, 0), 2)
            cropped = im2[y:y + h, x:x + w]
            text = pytesseract.image_to_string(im2, config='outputbase digits')
            text = re.sub('[^0-9]', '', text)
            if dead == False:
                if buyPhase == False:
                    try:
                        text = int(text)
                        checkHP(text)
                        print(f"Viewer HP: {text}, Current Health: {currentHealth}, Dead: {dead}, Buy Phase: {buyPhase}")
                    except:
                        if check == False:
                            if text == "" or text < 100:
                                print(f"Viewer HP: {text}, Current Health: {currentHealth}, Dead: {dead}, Buy Phase: {buyPhase}")
                                sleep(.5)
                                check = True
                                text = pytesseract.image_to_string(im2, config='outputbase digits')
                                print("Checking")
                                sleep(.5)
                                newtext = re.sub('[^0-9]', '', text)
                                print("New Text:", newtext)
                                if newtext == "":
                                    fire(newtext)
                                else:
                                    check = False

            if dead == True:
                print("player dead")
                sleep(.5)
                print(".")
                sleep(.5)
                print("..")
                sleep(.5)
                print("...")
                sleep(.5)





        # press ` to close
        if cv2.waitKey(1) & 0xFF == ord("`"):
            cv2.destroyAllWindows()
            break
    cv2.waitKey(2)

def buyWin():
    global currentHealth, previousHealth, status, buyPhase, dead, shopOpen
    while "Screen capturing":
        last_time = time.time()

        # Get raw pixels from the screen, save it to a Numpy array
        killedby = np.array(sct.grab(monitor2))

        # Display the picture
        # cv2.imshow("OpenCV/Numpy normal", img)

        # Display the picture in grayscale
        # cv2.imshow('OpenCV/Numpy grayscale',
        #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

        # print("fps: {}".format(1 / (time.time() - last_time)))

        # set kernel size \\ adjust this to fine tune the image
        kernel = np.ones((5, 5), np.uint8)

        # assign track bars
        h_min = cv2.getTrackbarPos("Hue Min", "Trackbars")
        h_max = cv2.getTrackbarPos("Hue Max", "Trackbars")
        s_min = cv2.getTrackbarPos("Sat Min", "Trackbars")
        s_max = cv2.getTrackbarPos("Sat Max", "Trackbars")
        v_min = cv2.getTrackbarPos("Val Min", "Trackbars")
        v_max = cv2.getTrackbarPos("Val Max", "Trackbars")

        # killed by window
        # grabCanny2 = cv2.Canny(killedby, 40, 40)
        # grabDilation2 = cv2.dilate(grabCanny2, kernel, iterations=0)
        # grabEroded2 = cv2.erode(grabCanny2, kernel, iterations=1)
        # grabHSV2 = cv2.cvtColor(killedby, cv2.COLOR_BGR2HSV)
        gray2 = cv2.cvtColor(killedby,cv2.COLOR_BGR2GRAY)
        # #
        # lower2 = np.array([h_min, s_min, v_min])
        # upper2 = np.array([h_max, s_max, v_max])
        # grabMask2 = cv2.inRange(grabHSV2, lower2, upper2)
        # grabResult2 = cv2.bitwise_and(killedby, killedby, mask=grabMask2)
        # grabGray2 = cv2.cvtColor(grabResult2, cv2.COLOR_BGR2GRAY)
        #gray2 = grabGray2.copy()

        # new stuff
        ret2, thresh2 = cv2.threshold(gray2, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        rect_kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        dilation2 = cv2.dilate(thresh2, rect_kernel2, iterations=1)
        contours, hierarchy = cv2.findContours(dilation2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        im3 = killedby.copy()

        # Display Screen and Alterations
        # cv2.imshow("Original",img)
        # SHOW THE VIDEO WINDOW
        # cv2.imshow("Canny Image", grabCanny)
        # cv2.imshow("Dilated Image",grabDilation)
        # cv2.imshow("Eroded Image", grabEroded)
        # cv2.imshow("HSV",grabHSV)
        # cv2.imshow("Mask",grabMask)
        # cv2.imshow("Final", grabResult)
        # cv2.imshow("Final 2",killedby)
        cv2.imshow("CPU Eyes 2", gray2)

        ret, thresh3 = cv2.threshold(gray2, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
        rect_kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
        dilation2 = cv2.dilate(thresh3, rect_kernel2, iterations=1)
        contours2, hierarchy2 = cv2.findContours(dilation2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        im3 = killedby.copy()

        for cnt2 in contours2:
            x2, y2, w2, h2 = cv2.boundingRect(cnt2)
            rect = cv2.rectangle(im3, (x2, y2), (x2 + w2, + h2), (0, 255, 0), 2)
            cropped2 = im3[y2:y2 + h2, x2:x2 + w2]
            buyText = pytesseract.image_to_string(cropped2)
            buyText = buyText.lower()
            if buyPhase == False:
               if buyText == "buy phase" or buyText == "match point" or buyText == "ound before":
                    buyPhase = True
                    dead = False
                    print("Buy Phase Activated")
                    print("Dead Status:",dead)
            if buyPhase == True:
                if buyText == "":
                    sleep(3)
                    if buyText == "":
                        buyPhase = False
                        print("Buy Phase Deactivated")
        # press ` to close
        if cv2.waitKey(1) & 0xFF == ord("`"):
            cv2.destroyAllWindows()
            break

    cv2.waitKey(2)

if __name__ == "__main__":
    try:
        x = threading.Thread(target=hpWIN)
        y = threading.Thread(target=buyWin)
        y.start()
        x.start()
    except:
        print("thread start failure")
