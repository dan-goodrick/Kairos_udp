import socket
import time
ip = '127.0.0.1'
port = 7201
msg = "Hello World"
while True:
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.sendto(msg.encode(), (ip, port))
    time.sleep(1)
