import socket
import threading
import random
import os
import base64

def handleFileTransmission(fileName, clientAddress, clientPort):
    try:
        # 创建新的UDP socket
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        port = random.randint(50000, 51000)
        clientSocket.bind(('', port))