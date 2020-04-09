import socket
import sys

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (192.168.0.10, 10000)
message = 'This is a UDP packet'

try:

    # Send data
    print(f"Sending {message}", file=sys.stderr)
    sent = sock.sendto(message.encode(), server_address)

    # Receive response
    print(f"Waiting to receive", file=sys.stderr)
    data, server = sock.recvfrom(4096)
    print(f"Received {data.decode()}", file=sys.stderr)

finally:
    print(f"closing socket", file=sys.stderr)
    sock.close()
