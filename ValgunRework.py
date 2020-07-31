import cv2
import numpy as np
from time import sleep
import socket
import pytesseract
import re
import pyautogui
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"

HEADER = 64
print("Enter matching port")
PORT = int(input())
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.87"
ADDR = (SERVER, PORT)
FIRE_MESSAGE = "Hit"
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
except:
    print("Port Failed. Try a new port.")
    PORT = int(input())

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    # print(client.recv(2048).decode(FORMAT))

# Beginning States
previousHP = 100
currentHP = 100
alive = 1
buyPhase = 0
incomingDeathText = 0
incomingBuyPhaseText = 0
lastHP = 0

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

def processDeath():
    mainGrab = pyautogui.screenshot()
    mainGrab = np.array(mainGrab)
    mainGrab = np.uint8(mainGrab)
    mainGrab = mainGrab[180:420, 1600:1780]
    mainGrab = stackImages(3, [mainGrab])
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
    incomingDeathText = pytesseract.image_to_string(finalImg)
    finalStack = stackImages(.25, ([imgHSV, finalImg], [mask, imgEroded]))
    cv2.imshow("Death Stack", finalStack)
    #print(incomingDeathText)
    incomingDeathText = len(incomingDeathText)
    return incomingDeathText

def processBuyPhase():
    mainGrab = pyautogui.screenshot()
    mainGrab = np.array(mainGrab)
    mainGrab = np.uint8(mainGrab)
    mainGrab = mainGrab[170:240, 805:1115]
    mainGrab = stackImages(1, [mainGrab])
    # imgHSV = cv2.cvtColor(mainGrab, cv2.COLOR_BGR2HSV)
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
    cv2.imshow("Buy Stack", finalStack)
    return incomingBuyPhaseText

def startBuyPhase():
    global buyPhase, alive
    buyPhase = 1
    alive = 1
    print(f"Buy Phase Active - BuyPhase: {buyPhase}, Alive:{alive}")
    sleep(10)
    print("20 seconds remaining")
    sleep(10)
    print("10 seconds remaining")
    sleep(5)
    print("5 seconds remaining")
    buyPhase = 0



def status(x,y):
    global alive, buyPhase
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"[{current_time}] Raw Text: {y} // HP: {x} // Alive: {alive} // Buy Phase: {buyPhase} ")

def processHealth(screen):
    global incomingDeathText, alive, buyPhase, previousHP, currentHP,  lastHP
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if alive == 0:
        if buyPhase == 0:
            print(f"[{current_time}] Watching for Next Round")
            incomingBuyPhaseText = processBuyPhase()
            incomingBuyPhaseText = incomingBuyPhaseText.lower()
            if incomingBuyPhaseText == "buy phase" or incomingBuyPhaseText == "match point" or incomingBuyPhaseText == "ound before":
                startBuyPhase()
    elif alive == 1:
        if buyPhase == 0:
            incomingText = pytesseract.image_to_string(screen)
            incomingHP = re.sub('[^0-9]', '', incomingText)
            try:
                incomingHP = int(incomingHP)
                if 0 < incomingHP < 101:
                    previousHP = currentHP
                    currentHP = incomingHP
                    if currentHP < previousHP:
                        status(incomingHP, incomingText)
                        # fire() command goes here
                        print("Fire!!")
                        send(FIRE_MESSAGE)
                    if currentHP >= previousHP:
                        status(incomingHP, incomingText)
                        pass
                else:
                    status(incomingHP,incomingText)
                    #print(f"[{current_time}] Raw Text: {incomingText} // HP: {incomingHP} // Previous HP: {previousHP} // Alive: {alive} // Buy Phase: {buyPhase} ")
            except:
                if incomingText == "":
                    print(f'[{current_time}] Checking Death')
                    incomingDeathText = processDeath()
                    if incomingDeathText >= 5:
                        print(f"[{current_time}] Fire!!")
                        send(FIRE_MESSAGE)
                        alive = 0
                    if incomingDeathText <= 4:
                        print(
                            f"[{current_time}] Raw Text: {incomingText} // HP: Health Blocked // Alive: {alive} // Buy Phase: {buyPhase}")



class hpWatcher:
    def empty(self):
        pass

    #Create Trackbars / Trackbar window
    cv2.namedWindow("Control")
    cv2.resizeWindow("Control",400,260)
    cv2.createTrackbar("Hue Min","Control",0,179, empty) #function is empty because it needs to run a function. We'll pull the values from these bars via another function.
    cv2.createTrackbar("Hue Max","Control",179,179, empty)
    cv2.createTrackbar("Sat Min", "Control", 0, 255, empty)
    cv2.createTrackbar("Sat Max", "Control", 36, 255, empty)
    cv2.createTrackbar("Val Min", "Control", 232, 255, empty)
    cv2.createTrackbar("Val Max", "Control", 255, 255, empty)


    while (True):
        previousHP = currentHP
        # Grab Window
        mainGrab = pyautogui.screenshot()
        # Conver to Numpy Array
        mainGrab = np.array(mainGrab)
        mainGrab = np.uint8(mainGrab)
        mainGrab = mainGrab[1000:1050,572:650]
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
        mask = cv2.inRange(imgHSV, lower, upper)
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
        processHealth(imgEroded)
        # Show Windows
        #cv2.imshow("1", imgHSV)
        #cv2.imshow("2", mask)
        # stack the windows
        finalStack = stackImages(2,([imgHSV],[mask],[imgEroded]))
        cv2.imshow("Final Stack",finalStack)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    print("Done")
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("Starting in 5.")
    sleep(1)
    print("Starting in 4.")
    sleep(1)
    print("Starting in 3.")
    sleep(1)
    print("Starting in 2.")
    sleep(1)
    print("Starting in 1.")
    sleep(1)


    mp.set_start_method('spawn')
    process1 = Process(target=hpWatcher)
    #process2 = Process(target=hpWatcher)
    process1.start()
    #process2.join()


    # hpValGun = hpWatcher()
    # hpValGun.run()

