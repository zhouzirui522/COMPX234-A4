import socket
import threading
import random
import os
import base64

def handleFileTransmission(fileName, clientAddress, clientPort):
    try:

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

                clientSocket.settimeout(10.0)
                data, addr = clientSocket.recvfrom(2048)
                request = data.decode().strip()
                parts = request.split(' ')

                if parts[0] == "FILE" and parts[2] == "CLOSE":
                   closeMsg = f"FILE {fileName} CLOSE_OK"
                   clientSocket.sendto(closeMsg.encode(), addr)
                   break

                elif parts[0] == "FILE" and parts[2] == "GET":

                     start = int(parts[4])
                     end = int(parts[6])
                     file.seek(start)
                     chunk = file.read(end - start + 1)

                if chunk:
                    base64_data = base64.b64encode(chunk).decode()
                    response = f"FILE {fileName} OK START {start} END {end} DATA {base64_data}"
                    clientSocket.sendto(response.encode(), addr)

            except socket.timeout:
                continue


            except Exception as e:
                print(f"Error in file transmission: {e}")
            finally:
                clientSocket.close()

            def main():
                if len(sys.argv) != 2:
                    print("Usage: python UDPserver.py <port>")
                    return

                port = int(sys.argv[1])
                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                serverSocket.bind(('', port))
                print(f"Server started on port {port}")

                while True:
                 try:
                   data, addr = serverSocket.recvfrom(1024)
                   request = data.decode().strip()
                   parts = request.split(' ')

                   if parts[0] == "DOWNLOAD" and len(parts) == 2:
                       fileName = parts[1]
                       if os.path.exists(fileName):
                           # 启动新线程处理文件传输
                           threading.Thread(target=handleFileTransmission,
                                            args=(fileName, addr)).start()
                       else:
                           errMsg = f"ERR {fileName} NOT_FOUND"
                           serverSocket.sendto(errMsg.encode(), addr)

