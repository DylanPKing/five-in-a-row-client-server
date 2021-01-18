import queue
import socket
import unittest

from server.game_server import GameServer


HOST = '127.0.0.1'
PORT = 8080


class TestGameServer(unittest.TestCase):

    @unittest.mock.patch('socket.socket.bind')
    @unittest.mock.patch('socket.socket.listen')
    def setUp(self, _, __):
        self._server = GameServer(HOST, PORT)

    def test_is_active_player(self):
        expected_value = True
        actual_value = self._server.is_active_player(0)

        assert expected_value == actual_value

    def test_is_active_player_false(self):
        expected_value = False
        actual_value = self._server.is_active_player(1)

        assert expected_value == actual_value

    @unittest.mock.patch(
        'socket.socket.accept', return_value=(socket.socket(), None)
    )
    @unittest.mock.patch('socket.socket.setblocking')
    def test_accept_new_connection(self, patched_blocking, patched_accept):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.accept_new_connection(sock)

        assert len(self._server._inputs) == 2
        assert len(self._server._message_queues.keys()) == 1

    @unittest.mock.patch('socket.socket.getpeername')
    @unittest.mock.patch.object(
        GameServer, '_parse_command', return_value='response'
    )
    def test_read_client_data(self, patched_parse, patched_getpeername):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._message_queues[sock] = queue.Queue()

        data = b'input'

        self._server.read_client_data(sock, data)

        patched_getpeername.assert_called_once()
        patched_parse.assert_called_once()
        assert sock in self._server._outputs

    @unittest.mock.patch('socket.socket.getpeername')
    @unittest.mock.patch.object(
        GameServer, '_parse_command', return_value='response'
    )
    @unittest.mock.patch.object(GameServer, 'start_game')
    def test_read_client_data_starts_game(
        self, patched_start_game, patched_parse, patched_getpeername
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._message_queues[sock] = queue.Queue()
        self._server._connected_clients = 2

        data = b'input'

        self._server.read_client_data(sock, data)

        patched_getpeername.assert_called_once()
        patched_parse.assert_called_once()
        patched_start_game.assert_called_once()
        assert sock in self._server._outputs

    @unittest.mock.patch('socket.socket.close')
    @unittest.mock.patch.object(GameServer, 'end_game_if_started')
    def test_disconnect_client(
        self, patched_end_game_if_started, patched_close
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()

        self._server.disconnect_client(sock)

        patched_close.assert_called_once()
        patched_end_game_if_started.assert_called_once()

    @unittest.mock.patch('socket.socket.close')
    @unittest.mock.patch.object(GameServer, 'end_game_if_started')
    def test_disconnect_client_removed_from_output(
        self, patched_end_game_if_started, patched_close
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._outputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()

        self._server.disconnect_client(sock)

        patched_close.assert_called_once()
        patched_end_game_if_started.assert_called_once()
        assert sock not in self._server._outputs

    @unittest.mock.patch('socket.socket.getpeername')
    @unittest.mock.patch('socket.socket.close')
    @unittest.mock.patch.object(GameServer, 'end_game_if_started')
    def test_handle_client_exception(
        self, patched_end_game_if_started, patched_close, patched_getpeername
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()

        self._server.handle_client_exception(sock)

        patched_getpeername.assert_called_once()
        patched_close.assert_called_once()
        patched_end_game_if_started.assert_called_once()

    @unittest.mock.patch('socket.socket.getpeername')
    @unittest.mock.patch('socket.socket.close')
    @unittest.mock.patch.object(GameServer, 'end_game_if_started')
    def test_handle_client_exception_removed_from_outputs(
        self, patched_end_game_if_started, patched_close, patched_getpeername
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._outputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()

        self._server.handle_client_exception(sock)

        patched_getpeername.assert_called_once()
        patched_close.assert_called_once()
        patched_end_game_if_started.assert_called_once()
        assert sock not in self._server._outputs

    def test_shut_down(self):
        self._server.shut_down()
        assert len(self._server._inputs) == 0

    @unittest.mock.patch('queue.Queue.put')
    def test_end_game_if_started(self, patched_put):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()
        self._server._game_started = True

        self._server.end_game_if_started()

        patched_put.assert_called_once()

    @unittest.mock.patch('queue.Queue.put')
    def test_end_game_if_started_game_not_started(self, patched_put):
        self._server.end_game_if_started()

        patched_put.assert_not_called()
