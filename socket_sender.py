'''
Script to simulate sending data from iot device
'''

import socket
import time
from utils import generate_sample

socketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketObject.connect(("127.0.0.1",8080))

counter = 1
while True:
    data = str(generate_sample(time=counter))
    socketObject.send(data.encode())

    counter += 1
    time.sleep(20)
    print("data sent")