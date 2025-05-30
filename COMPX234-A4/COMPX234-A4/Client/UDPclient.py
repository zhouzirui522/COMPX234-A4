import socket
import sys
import base64
import os


def sendAndReceive(sock, message, address, port, timeout=1000, max_retries=5):
    current_timeout = timeout
    retries = 0

    while retries < max_retries:
        try:
            sock.settimeout(current_timeout / 1000)
            sock.sendto(message.encode(), (address, port))
            response, _ = sock.recvfrom(2048)
            return response.decode().strip()
        except socket.timeout:
            retries += 1
            current_timeout *= 2
            print(f"Timeout, retrying... (attempt {retries})")

    raise Exception("Max retries reached, giving up")

def downloadFile(sock, fileName, serverAddress, serverPort):
    try:
        response = sendAndReceive(sock, f"DOWNLOAD {fileName}",
                                serverAddress, serverPort)
        parts = response.split(' ')

        if parts[0] == "ERR":
          print(f"Error: {response}")
          return False

        elif parts[0] == "OK":
          fileSize = int(parts[4])
          dataPort = int(parts[6])
          print(f"Downloading {fileName} (size: {fileSize} bytes)", end='', flush=True)


    with open(fileName, 'wb') as file:
        bytesReceived = 0
        chunkSize = 1000

        while bytesReceived < fileSize:
            start = bytesReceived
            end = min(bytesReceived + chunkSize - 1, fileSize - 1)
