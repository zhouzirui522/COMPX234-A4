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