import yaml


CONFIG_PATH = './client/config.yaml'


def load_config():
    '''
    Loads config from CONFIG_PATH constant

    Returns:
        dict(): Loaded yaml.
    '''
    with open(CONFIG_PATH) as config_file:
        config = yaml.load(config_file, yaml.FullLoader)

    return config


def send_name(sock, player_name):
    '''
    Send players name to the server, and returns if connection should close.

    Args:
        sock (socket.socket): Connection to the server
        player_name (str): The players name to be encoded and sent.

    Returns:
        bool: Whether to stay connected to the server or not.
    '''
    outgoing_message = player_name.encode()

    sock.send(outgoing_message)

    response = sock.recv(1024)
    response = response.decode()

    if response == 'Disconnecting...' or response == 'Server is full.':
        return False

    print(response)
    return True


def client_loop(sock, stay_connected, player_name):
    '''
    Main body of client functionality. Player enters commands to play game.

    Args:
        sock (socket.socket): Connection to the server.
        stay_connected (bool): Controls server connection.
            True until disconnected.
        player_name (str): The players name. Sent with every command.
    '''
    while stay_connected:
        user_input = input('Enter command or number to drop piece:\t')
        command = f'{player_name},{user_input}'
        outgoing_message = command.encode()
        sock.send(outgoing_message)

        response = sock.recv(1024)
        response = response.decode()
        print(response)
        if (
            'Disconnecting...' in response or
            'Server is full.' in response or
            'Took too long to respond. Shutting down.' in response or
            'disconnect' in user_input
        ):
            stay_connected = False
