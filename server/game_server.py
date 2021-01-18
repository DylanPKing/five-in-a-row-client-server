import select
import socket
import queue


class GameServer:
    def __init__(self, host, port):
        '''
        Server for the five in a row game.

        Args:
            host (str): The IPv4 address to use for hosting.
            port (int): Port to use on host IP.

        Attributes:
            _server (socket.socket): main socket all clients connect to.
            _host (str): IPv4 addrss of server
            _port (int): Port server accept connections from
            _inputs (list(socket.socket)): Sockets which send messages.
            _outputs (list(socket.socket)): Sockets awaiting a response.
            _message_queues (dict(queue.Queue)): A dict storing messages
                waiting to be sent to clients.
            _connected_clients (int): Total number of connected clients.
                Limited to two.
            _client_names: Name each client submitted when first connecting.
            _active_player: Current client that can control the game.
            _timeout_count: Counter to determine how many ticks have occurred
                since last client command.
        '''
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setblocking(0)
        self._host = host
        self._port = port
        self._server.bind((self._host, self._port))
        self._server.listen(2)
        self._inputs = [self._server]
        self._outputs = []
        self._message_queues = {}
        self._connected_clients = 0
        self._client_names = ['', '']
        self._game_started = False
        self._active_player = 0
        self._timeout_count = 0

    def server_loop(self):
        '''
        Main body of server functionality.

        Checks for messages from clients, and reads and writes accordingly. If
        it receives an exception, it will disconnect the client.
        '''
        while self._inputs:
            print('Waiting for clients')
            readable, writable, exceptional = select.select(
                self._inputs, self._outputs, self._inputs, 1
            )

            if not (readable or writable or exceptional):
                print('Timed out. Will shut down if no response soon.')
                self._timeout_count += 1
                if self._timeout_count >= 15:
                    self.shut_down()
                continue

            self._timeout_count = 0

            for sock in readable:
                if sock is self._server:
                    self.accept_new_connection(sock)
                else:
                    data = sock.recv(1024)
                    if data:
                        self.read_client_data(sock, data)
                    else:
                        self.disconnect_client(sock)

            for sock in writable:
                self.send_response(sock)

            for sock in exceptional:
                self.handle_client_exception(sock)

    def accept_new_connection(self, sock):
        '''
        Accepts a new connection, and adds socket to inputs, and message queue.

        Args:
            sock (socket.socket): Servers own socket.
        '''
        connection, _ = sock.accept()
        connection.setblocking(0)
        self._inputs.append(connection)
        self._message_queues[connection] = queue.Queue()

    def read_client_data(self, sock, data):
        '''
        Process incoming data from clients, and sends for parsing.
        Starts game when all clients are connected.

        Args:
            sock (socket.socket): Socket data was read from.
            data (bytes): Encoded string from client.
        '''
        print(f'received {data} from {sock.getpeername()}')
        user_input = data.decode()
        output = self._parse_command(user_input)

        if self._connected_clients == 2 and not self._game_started:
            self.start_game()

        output = output.encode()
        self._message_queues[sock].put(output)

        if sock not in self._outputs:
            self._outputs.append(sock)

    def disconnect_client(self, sock):
        '''
        Disconnects a client from the server.

        Args:
            sock (socket.socket): Socket to disconnect.
        '''
        if sock in self._outputs:
            self._outputs.remove(sock)

        self._inputs.remove(sock)
        sock.close()

        del self._message_queues[sock]

        self.end_game_if_started()

    def send_response(self, sock):
        '''
        Sends a response to the specified socket.

        Args:
            sock (socket.socket) Socket to send message to.
        '''
        try:
            next_message = self._message_queues[sock].get_nowait()
        except queue.Empty:
            print(f'{sock.getpeername()} queue empty')
            self._outputs.remove(sock)
        else:
            print(f'Sending {next_message} to {sock.getpeername()}')
            sock.send(next_message)

    def handle_client_exception(self, sock):
        '''
        Disconnect a socket that has sent an exception.

        Args:
            sock (socket.socket): Socket to disconnect.
        '''
        print(f'Exception condition on {sock.getpeername()}')

        self._inputs.remove(sock)
        if sock in self._outputs:
            self._outputs.remove(sock)
        sock.close()

        del self._message_queues[sock]

        self.end_game_if_started()

    def shut_down(self):
        '''Send shutdown message to clients, and then shut down server.'''
        shutdown_message = (
            'Took too long to respond. Shutting down.'
        )
        shutdown_message = shutdown_message.encode()
        for sock in self._inputs:
            if sock is self._server:
                continue
            sock.send(shutdown_message)
            sock.close()
        self._inputs.clear()

    def is_active_player(self, player_number):
        '''
        Returns if the specified player is the active player.

        Args:
            player_number (int): Number of player sending a command.

        Returns:
            bool: True if the player is active, False if not.
        '''
        return player_number == self._active_player

    def start_game(self):
        '''
        Starts the game.
        '''
        self._active_player = 0
        self._game_started = True

    def end_game_if_started(self):
        if self._game_started:
            self._game_started = False
            # Reset game board here
            for sock in self._inputs:
                if sock is self._server:
                    continue
                if sock not in self._outputs:
                    self._outputs.append(sock)
                self._message_queues[sock].put(
                    'Player disconnected. Resetting Game.'
                )

    def _parse_command(self, client_input):
        player_index = None
        if ',' in client_input:
            player_name, client_input = client_input.split(',')
            player_index = self._client_names.index(player_name)

        if client_input == 'help':
            return (
                'Commands:\n'
                '\tboard - Displays current game board.\n'
                '\tturn - Displays current turn number and current player.\n'
                '\tNumber between 1 and 9 - Which column to drop yor piece.\n'
                '\tdisconnect - Leave the game.\n'
            )

        elif client_input == 'board':
            if self._game_started:
                return 'requested board'  # return self._game.game_board()
            else:
                return 'Game has not started.'
        elif client_input == 'turn':
            return 'requested turn info'
            # return (
            #   f'Turn #{self._game.turn_number}. '
            #   f'{self._client_names[self._active_player]}s turn.'
            # )
        elif client_input.isdigit():
            if not self.is_active_player(player_index):
                return 'Please wait for your turn.'
            elif not self._game_started:
                return 'Game has not started.'
            column = int(client_input)
            if 1 <= column <= 9:
                return 'valid number'
                # win, row, col = self._game.insert_piece(column - 1)
                # if win, end game and tell users.
                # else, tell user where piece landed.
            else:
                return 'invalid number'
                # Tell user invalid input, and to try again
        elif client_input == 'disconnect':
            if player_name in self._client_names:
                self._client_names[player_index] = ''
                self._connected_clients -= 1
            return 'Disconnecting...'
        elif (
            not self._game_started and
            self._connected_clients < 2 and
            player_index is None
        ):
            self._client_names[self._connected_clients] = client_input
            self._connected_clients += 1
            output = (
                f'Welcome {client_input}! '
                f'There are {self._connected_clients} clients connected.'
            )
            if self._connected_clients == 2:
                output = f"{output} Let's go!"
            else:
                output = f'{output} Waiting on another player.'

            return output

        elif self._connected_clients == 2 and player_index is None:
            return 'Server is full.'
        else:
            return 'Invalid command, try again.'
