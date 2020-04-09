import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('192.168.0.10', 9000)
sock.bind(server_address)
print(f"Waiting to receive")
while True:
    # Receive response
    data, server = sock.recvfrom(4096)
    print(f"Received {data.decode()}")
