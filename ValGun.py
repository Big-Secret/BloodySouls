import cv2
import pytesseract

#pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'

# read images
#img = cv2.imread('img/2.png')

# read video / Cameras
cap = cv2.VideoCapture(1)
cap.set(3,640)
cap.set(4,480)

while True:
    success, img = cap.read()
    cv2.imshow("Video", img)
    if cv2.waitKey(1) & 0xFF ==ord('q'):
        break

# Display Image
cv2.imshow('Base', img)
cv2.waitKey(0)