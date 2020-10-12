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
from PIL import ImageOps
import pyautogui
import socket
import threading
from time import sleep

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"

HEADER = 64
PORT =6666
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.87"
ADDR = (SERVER, PORT)
FIRE_MESSAGE = "Hit"
DEATH_MESSAGE = "Death"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

hardMode = True
isHit = False
firstRun = True

def send(msg):
    print("HIT!")
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))
    sleep(.1)


previousHP = 100
hp = 100
newHp = 100
hpArray = [0]
averageHp = 100
alive = True

lastScreenHP = pyautogui.screenshot()
lastScreenHP = np.array(lastScreenHP)

if hardMode == True:
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

    # Check current HP against last few HPs sent in
    def hpCheck(x):
        global averageHp, isHit, firstRun, hp
        fireDelay = .15
        change = 2
        if isHit == False:
            try:
                if x == 0 or hp - x > hp - 2:
                    print("Big HP Jump - Bonfire or Bug")
                    return
                else:
                    if x >= averageHp:
                        del hpArray[0]
                        hpArray.append(x)
                        #print(hpArray)
                        averageHp = (sum(hpArray) // len(hpArray))
                        print(f"HP is {x} & Average HP is {averageHp} || {hpArray}")
                        sleep(fireDelay)
                        hp = x
                        return averageHp, hp
                    if x < averageHp:
                        if firstRun is False:
                            del hpArray[0]
                            hpArray.append(x)
                            #print(hpArray)
                            averageHp = (sum(hpArray) // len(hpArray))
                            print(f"HIT!!! HP is {x} & Average HP is {averageHp} || {hpArray}")
                            send(FIRE_MESSAGE)
                            isHit is True
                            sleep(fireDelay)
                            hp = x
                            return averageHp, isHit, hp
                        else:
                            print("Starting Bot Status:",firstRun)
                            firstRun = False
                            averageHp = x
                            hp = x
                            print(x,averageHp,hpArray)
                            sleep(3)
                            return averageHp, hp

            except:
                print("Need more data")
        if isHit == True:
            sleep(.25)
            print("reset")
            isHit = False


    class getFucked:
        global lastScreenHP
        def processImage(buyCheck):
            buyCheck = pytesseract.image_to_string(buyCheck)
            incomingText = pytesseract.image_to_string(hp)
            incomingHP = re.sub('[^0-9]', '', incomingText)
            if incomingText == "":
                pass
            else:
                print("HP:", incomingHP, ' | Raw Text: ', incomingText)



        def getContours(img, layer, lastScreenHP, hp):
            global lineLengthP, lineLengthX, firstRun
            #contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                for cnt in contours:
                    # retrieving all the contours in the image
                    area = cv2.contourArea(cnt)
                    # run this command if the area is greater than the amount.
                    # Draw lines on the image sent in.
                    cv2.drawContours(layer, cnt,  0, (0, 0, 180), 2)
                    if area > 0:
                        checkArea = int(area * 2)
                        if checkArea > 1:
                            lastScreenHP = layer
                            # check to see how long the perimeter of the contours is // grab the approx length.
                            epsilon = 0.30 * cv2.arcLength(cnt,True)
                            approx = cv2.approxPolyDP(cnt, epsilon, True)
                            objCor = len(approx)
                            x, y, w, h = cv2.boundingRect(approx)
                            if objCor >= 2: objectType = "HealthBar"
                            else: objectType = "Ignored"
                            lineLengthX = int(((x + w) - x) // 8)
                            if objectType == "HealthBar":
                                cv2.line(layer, (15,y+5),(x+w,y+5),(0,255,255),2)
                                #cv2.rectangle(layer, (x,y),(x+w,y+h+5),(0,0,150),2)
                                cv2.putText(layer, f"HP: {lineLengthX}",
                                            (x + (w // 2), y + (h // 2)),cv2.FONT_HERSHEY_DUPLEX, .4, (200,200,200),1)
                                hpCheck(lineLengthX)
                                #fireCheck(averageHP)
            elif len(contours) == 0:
                if averageHp <= 20:
                    print("You're Dead")
                    send(DEATH_MESSAGE)
                    sleep(16)

        #sleep(.15)


        def empty(self):
            pass

        #Create Trackbars / Trackbar window
        cv2.namedWindow("Control")
        cv2.resizeWindow("Control",400,300)
        cv2.createTrackbar("Hue Min","Control",113,179, empty) #function is empty because it needs to run a function. We'll pull the values from these bars via another function.
        cv2.createTrackbar("Hue Max","Control",147,179, empty)
        cv2.createTrackbar("Sat Min", "Control", 127, 255, empty)
        cv2.createTrackbar("Sat Max", "Control", 187, 255, empty)
        cv2.createTrackbar("Val Min", "Control", 48, 255, empty)
        cv2.createTrackbar("Val Max", "Control", 255, 255, empty)
        cv2.createTrackbar("Width", "Control", 570, 1800, empty)

        while (True):
            # Grab Window
            baseGrab = pyautogui.screenshot()

            #mainGrab = ImageOps.posterize(baseGrab, 2)

            # Conver to Numpy Array
            mainGrab = np.array(baseGrab)




            # Crop the image
            cropWidth = cv2.getTrackbarPos("Width","Control")
            mainGrab = mainGrab[70:95,185:cropWidth]

            # Create a copy to use for the final contours product.
            copyGrab = mainGrab.copy()

            # HSV of Image
            imgHSV = cv2.cvtColor(mainGrab, cv2.COLOR_BGR2HSV)
            h_min = cv2.getTrackbarPos("Hue Min", "Control")
            h_max = cv2.getTrackbarPos("Hue Max", "Control")
            s_min = cv2.getTrackbarPos("Sat Min", "Control")
            s_max = cv2.getTrackbarPos("Sat Max", "Control")
            v_min = cv2.getTrackbarPos("Val Min", "Control")
            v_max = cv2.getTrackbarPos("Val Max", "Control")

            # Create Mask using the trackbar values.
            lower = np.array([h_min,s_min,v_min])
            upper = np.array([h_max,s_max,v_max])

            # Create a Mask
            mask = cv2.inRange(imgHSV, lower, upper)

            # Utilizing the mask to show only the colors we want.
            finalImg = cv2.bitwise_and(mainGrab, mainGrab, mask=mask)



            # Resize the Image
            mainGrab = cv2.resize(mainGrab, dsize=(1280, 720), interpolation=cv2.INTER_CUBIC)
            #another way is cv2.resize(imagegoeshere,(x,y))

            # Adjust Colors // Process Image
            # Conver to Gray
            imgGray = cv2.cvtColor(mainGrab, cv2.COLOR_BGR2GRAY)

            # Blur it
            imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)

            # Find Detect Color

            # Convert to Canny. Black / White lines only.
            imgCanny = cv2.Canny(finalImg, 25, 25)

            # Create the Kernel - Dilate and Erode will use this to adjust their sizes.
            ksize = 10
            kernel = np.ones((ksize, ksize), np.uint8)
            # Dilation means thicker lines.
            imgDilation = cv2.dilate(imgCanny, kernel, iterations=4)
            # Erosion means thinner lines.
            imgEroded = cv2.erode(imgDilation, kernel, iterations=3)

            #Run Contours Function
            getContours(imgCanny, finalImg, lastScreenHP, hp)


            # Show Windows
            #cv2.imshow("1", imgHSV)
            #cv2.imshow("2", mask)

            # Stack the windows
            # If stack needs a blank immage, use this:
            imgBlank = np.zeros_like(finalImg)
            finalStack = stackImages(1,([finalImg],[copyGrab],[mask]))
            cv2.imshow("Final Stack",finalStack)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        print("Done")
        cv2.destroyAllWindows()


bloody = bloodySouls()
if __name__ == "__main__":
    x = Thread(target=bloody.run)
    x.start()


    #bloody.run()

