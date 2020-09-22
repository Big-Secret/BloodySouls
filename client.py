import socket
import threading
from time import sleep



HEADER = 64
PORT = 7777
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
    print(client.recv(2048).decode(FORMAT))

sleep(1)
send(FIRE_MESSAGE)
sleep(1)
send(DISCONNECT_MESSAGE)
#home/pi/server/server.py