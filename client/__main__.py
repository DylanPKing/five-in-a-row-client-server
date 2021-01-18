import socket

import client_utils


if __name__ == "__main__":
    config = client_utils.load_config()
    server_address = (config['host'], config['port'])
    stay_connected = True
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server.
    print(f'connecting to {server_address[0]} port {server_address[1]}')
    try:
        sock.connect(server_address)
    except ConnectionRefusedError:
        print(
            'Connection refused. '
            'Please make sure the server is live before running the client.'
        )
    else:
        player_name = input('Enter your name:\t')
        stay_connected = client_utils.send_name(sock, player_name)

        if stay_connected:
            client_utils.client_loop(sock, stay_connected, player_name)

        sock.close()
