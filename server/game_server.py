import select
import socket
import queue


class GameServer:
    def __init__(self, host, port):
        """
        docstring
        """
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

    def server_loop(self):
        while self._inputs:
            print('Waiting for clients')
            readable, writable, exceptional = select.select(
                self._inputs, self._outputs, self._inputs, 1
            )

            if not (readable or writable or exceptional):
                print('Timed out, to be completed.')
                continue

            for sock in readable:
                if sock is self._server:
                    connection, client_address = sock.accept()

                    print(f'{client_address} has connected')

                    connection.setblocking(0)

                    self._inputs.append(connection)

                    self._message_queues[connection] = queue.Queue()
                else:
                    data = sock.recv(1024)
                    if data:
                        print(f'received {data} from {sock.getpeername()}')
                        user_input = data.decode()
                        output = self._parse_command(user_input)

                        if self._connected_clients == 2:
                            self.start_game()

                        output = output.encode()
                        self._message_queues[sock].put(output)

                        if sock not in self._outputs:
                            self._outputs.append(sock)
                    else:
                        print(f'Closing {client_address}')

                        if sock in self._outputs:
                            self._outputs.remove(sock)

                        self._inputs.remove(sock)
                        sock.close()

                        del self._message_queues[sock]

            for sock in writable:
                try:
                    next_message = self._message_queues[sock].get_nowait()
                except queue.Empty:
                    print(f'{sock.getpeername()} queue empty')
                    self._outputs.remove(sock)
                else:
                    print(f'Sending {next_message} to {sock.getpeername()}')
                    sock.send(next_message)

            for sock in exceptional:
                print(f'Exception condition on {sock.getpeername()}')

                self._inputs.remove(sock)
                if sock in self._outputs:
                    self._outputs.remove(sock)
                sock.close()

                del self._message_queues[sock]

    def is_active_player(self, player_number):
        return player_number == self._active_player

    def start_game(self):
        self._active_player = 0
        self._game_started = True

    def _parse_command(self, client_input):
        player_index = None
        if ',' in client_input:
            player_name, client_input = client_input.split(',')
            player_index = self._client_names.index(player_name)
        if client_input == 'board':
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
