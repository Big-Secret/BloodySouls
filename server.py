import socket
import threading
from time import sleep
import RPi.GPIO as PIO

HEADER = 64
PORT = 6660
SERVER = socket.gethostbyname(socket.gethostname())2
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
FIRE_MESSAGE = "Hit"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION]{addr} connected")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(24, GPIO.OUT)
    connected = True
    while connected:
        msg_length = conn.recv(HEADER)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"{addr} {msg}")
            conn.send("Message Received".encode(FORMAT))
            if msg == FIRE_MESSAGE:
                thread = threading.Thread(target=fire)
                thread.start()
    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

def fire():
    print("You've Been Shot")
    GPIO.output(24, GPIO.LOW)
    sleep(1)
    GPIO.output(24, GPIO.HIGH)
    GPIO.cleanup()

print("[STARTING] Starting Server..." )
start()
