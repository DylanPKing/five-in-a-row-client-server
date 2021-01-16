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
                        self._message_queues[sock].put(data)

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
