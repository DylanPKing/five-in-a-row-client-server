import socket
import sys

messages = [
    'This is the message. ',
    'It will be sent ',
    'in parts.',
]
server_address = ('127.0.0.1', 8080)

# Create a TCP/IP socket
# socks = [
#     socket.socket(socket.AF_INET, socket.SOCK_STREAM),
#     socket.socket(socket.AF_INET, socket.SOCK_STREAM),
# ]

stay_connected = True
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Connect the socket to the port where the server is listening
print('connecting to {} port {}'.format(*server_address),
      file=sys.stderr)
sock.connect(server_address)

player_name = input('Enter your name:\t')
outgoing_message = player_name.encode()
sock.send(outgoing_message)

response = sock.recv(1024)
response = response.decode()
if response == 'Disconnecting...' or response == 'Server is full.':
    stay_connected = False
else:
    print(response)


while stay_connected:

    user_input = input('Enter command or number to drop piece:\t')
    user_input = f'{player_name},{user_input}'
    outgoing_message = user_input.encode()
    sock.send(outgoing_message)

    response = sock.recv(1024)
    response = response.decode()
    if response == 'Disconnecting...' or response == 'Server is full.':
        stay_connected = False
    else:
        print(response)


sock.close()
