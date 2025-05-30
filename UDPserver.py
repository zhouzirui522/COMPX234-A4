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

        filePath = os.path.join('.', fileName)
        fileSize = os.path.getsize(filePath)

        okMsg = f"OK {fileName} SIZE {fileSize} PORT {port}"
        clientSocket.sendto(okMsg.encode(), clientAddress)

        with open(filePath, 'rb') as file:
          while True:
            try:
                # 设置超时
                clientSocket.settimeout(10.0)
                data, addr = clientSocket.recvfrom(2048)
                request = data.decode().strip()
                parts = request.split(' ')

                if parts[0] == "FILE" and parts[2] == "CLOSE":
                   closeMsg = f"FILE {fileName} CLOSE_OK"
                   clientSocket.sendto(closeMsg.encode(), addr)
                   break



