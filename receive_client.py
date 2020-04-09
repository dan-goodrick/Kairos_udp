import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
HOST = socket.gethostname()
print("Host: ", HOST)
server_address = (HOST, 9000)
sock.bind(server_address)
print(f"Waiting to receive")
while True:
    # Receive response
    data, server = sock.recvfrom(4096)
    print(f"Received {data.decode()}")
