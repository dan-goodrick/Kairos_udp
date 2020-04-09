import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print(f"Starting up on {server_address[0]} port {server_address[1]}", file=sys.stderr)

sock.bind(server_address)

while True:
    print(f"Waiting to receive message", file=sys.stderr)
    data, address = sock.recvfrom(4096) #4096 is the max packet size
    print(f"Received {len(data)} bytes from {address} \n {data}", file=sys.stderr)
    if data:
        sent = sock.sendto(data, address)
        print(f"Sent {sent} bytes back to {address}", file=sys.stderr)
