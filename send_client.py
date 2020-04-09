import socket
import sys

message = sys.argv[1]
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('192.168.0.10', 9000)


# Send data
print(f"Sending {message}")
sent = sock.sendto(message.encode(), server_address)
print(sent)
print(f"closing socket")
sock.close()
