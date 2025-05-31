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

            request = f"FILE {fileName} GET START {start} END {end}"
            response = sendAndReceive(sock, request, serverAddress, dataPort)

            if response.startswith(f"FILE {fileName} OK"):
                dataParts = response.split('DATA ')
                if len(dataParts) > 1:
                    binaryData = base64.b64decode(dataParts[1])
                    file.seek(start)
                    file.write(binaryData)
                    bytesReceived += len(binaryData)
                    print('*', end='', flush=True)

                closeMsg = f"FILE {fileName} CLOSE"
                sendAndReceive(sock, closeMsg, serverAddress, dataPort)
                print(f"\nDownload of {fileName} completed")
                return True
    except Exception as e:
        print(f"\nError downloading {fileName}: {e}")
        return False

def main():
    if len(sys.argv) != 4:
        print("Usage: python UDPclient.py <hostname> <port> <filelist>")
        return

    hostname = sys.argv[1]
    port = int(sys.argv[2])
    fileList = sys.argv[3]

    try:
        with open(fileList, 'r') as f:
            files = [line.strip() for line in f if line.strip()]

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        for fileName in files:
          if downloadFile(sock, fileName, hostname, port):
            print(f"Successfully downloaded {fileName}")
        else:
            print(f"Failed to download {fileName}")

    except Exception as e:
        print(f"Client error: {e}")
    finally:
        sock.close()