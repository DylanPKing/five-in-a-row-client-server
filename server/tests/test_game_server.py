import queue
import socket
import unittest

from server.game_server import GameServer
from server.game_logic import GameBoard


HOST = '127.0.0.1'
PORT = 8080


class TestGameServer(unittest.TestCase):

    @unittest.mock.patch('socket.socket.bind')
    @unittest.mock.patch('socket.socket.listen')
    def setUp(self, _, __):
        self._server = GameServer(HOST, PORT)

    def test_is_active_player(self):
        expected_value = True
        actual_value = self._server._is_active_player(0)

        assert expected_value == actual_value

    def test_is_active_player_false(self):
        expected_value = False
        actual_value = self._server._is_active_player(1)

        assert expected_value == actual_value

    @unittest.mock.patch(
        'socket.socket.accept', return_value=(socket.socket(), None)
    )
    @unittest.mock.patch('socket.socket.setblocking')
    def test_accept_new_connection(self, patched_blocking, patched_accept):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._accept_new_connection(sock)

        assert len(self._server._inputs) == 2
        assert len(self._server._message_queues.keys()) == 1

    @unittest.mock.patch.object(
        GameServer, '_parse_command', return_value='response'
    )
    def test_read_client_data(self, patched_parse):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._message_queues[sock] = queue.Queue()

        data = b'input'

        self._server._read_client_data(sock, data)

        patched_parse.assert_called_once()
        assert sock in self._server._outputs

    @unittest.mock.patch.object(
        GameServer, '_parse_command', return_value='response'
    )
    @unittest.mock.patch.object(GameServer, '_start_game')
    def test_read_client_data_starts_game(
        self, patched_start_game, patched_parse
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._message_queues[sock] = queue.Queue()
        self._server._connected_clients = 2

        data = b'input'

        self._server._read_client_data(sock, data)

        patched_parse.assert_called_once()
        patched_start_game.assert_called_once()
        assert sock in self._server._outputs

    @unittest.mock.patch('socket.socket.close')
    @unittest.mock.patch.object(GameServer, '_end_game_if_started')
    def test_disconnect_client(
        self, patched_end_game_if_started, patched_close
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()

        self._server._disconnect_client(sock)

        patched_close.assert_called_once()
        patched_end_game_if_started.assert_called_once()

    @unittest.mock.patch('socket.socket.close')
    @unittest.mock.patch.object(GameServer, '_end_game_if_started')
    def test_disconnect_client_removed_from_output(
        self, patched_end_game_if_started, patched_close
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._outputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()

        self._server._disconnect_client(sock)

        patched_close.assert_called_once()
        patched_end_game_if_started.assert_called_once()
        assert sock not in self._server._outputs

    @unittest.mock.patch('socket.socket.close')
    @unittest.mock.patch.object(GameServer, '_end_game_if_started')
    def test_handle_client_exception(
        self, patched_end_game_if_started, patched_close
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()

        self._server._handle_client_exception(sock)

        patched_close.assert_called_once()
        patched_end_game_if_started.assert_called_once()

    @unittest.mock.patch('socket.socket.close')
    @unittest.mock.patch.object(GameServer, '_end_game_if_started')
    def test_handle_client_exception_removed_from_outputs(
        self, patched_end_game_if_started, patched_close
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock)
        self._server._outputs.append(sock)
        self._server._message_queues[sock] = queue.Queue()

        self._server._handle_client_exception(sock)

        patched_close.assert_called_once()
        patched_end_game_if_started.assert_called_once()
        assert sock not in self._server._outputs

    def test_shut_down(self):
        self._server._shut_down()
        assert len(self._server._inputs) == 0

    @unittest.mock.patch('queue.Queue.put')
    def test_end_game_if_started(self, patched_put):
        sock_one = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock_one)
        self._server._inputs.append(sock_two)
        self._server._message_queues[sock_one] = queue.Queue()
        self._server._message_queues[sock_two] = queue.Queue()
        self._server._game_started = True

        self._server._end_game_if_started(sock_one)

        patched_put.assert_called_once()

    @unittest.mock.patch('queue.Queue.put')
    def test_end_game_if_started_game_not_started(self, patched_put):
        self._server._end_game_if_started(None)

        patched_put.assert_not_called()

    @unittest.mock.patch.object(GameServer, '_help_text')
    def test_parse_command_help(self, patched_help_text):
        test_name = 'Name'
        test_command = 'help'
        self._server._client_names[0] = test_name
        test_input = f'{test_name},{test_command}'

        self._server._parse_command(test_input, None)

        patched_help_text.assert_called_once()

    @unittest.mock.patch.object(
        GameBoard, 'game_board', new_callable=unittest.mock.PropertyMock
    )
    def test_parse_command_board_game_not_started(self, patched_game_board):
        test_name = 'Name'
        test_command = 'board'
        self._server._client_names[0] = test_name
        test_input = f'{test_name},{test_command}'

        self._server._parse_command(test_input, None)

        patched_game_board.assert_not_called()

    @unittest.mock.patch.object(
        GameBoard, 'game_board', new_callable=unittest.mock.PropertyMock
    )
    def test_parse_command_board_game_started(self, patched_game_board):
        test_name = 'Name'
        test_command = 'board'
        self._server._client_names[0] = test_name
        self._server._game_started = True
        test_input = f'{test_name},{test_command}'

        self._server._parse_command(test_input, None)

        patched_game_board.assert_called_once()

    def test_parse_command_turn(self):
        test_name = 'Name'
        test_command = 'turn'
        self._server._client_names[0] = test_name
        self._server._game_started = True
        test_input = f'{test_name},{test_command}'

        output = self._server._parse_command(test_input, None)

        assert output == 'It is Names turn.'

    def test_parse_command_digit_not_active_player(self):
        test_name = 'Name'
        test_command = '1'
        self._server._client_names[1] = test_name
        self._server._game_started = False
        test_input = f'{test_name},{test_command}'

        output = self._server._parse_command(test_input, None)

        assert output == 'Please wait for your turn.'

    def test_parse_command_digit_game_not_started(self):
        test_name = 'Name'
        test_command = '1'
        self._server._client_names[0] = test_name
        self._server._game_started = False
        test_input = f'{test_name},{test_command}'

        output = self._server._parse_command(test_input, None)

        assert output == 'Game has not started.'

    def test_parse_command_digit_game_invalid_number(self):
        test_name = 'Name'
        test_command = '0'
        self._server._client_names[0] = test_name
        self._server._game_started = True
        test_input = f'{test_name},{test_command}'

        output = self._server._parse_command(test_input, None)

        assert output == "That's an invalid number. Try again."

    @unittest.mock.patch.object(GameServer, '_manage_piece_drop')
    def test_parse_command_digit_game_success(
        self, patched_manage_piece_drop
    ):
        test_name = 'Name'
        test_command = '1'
        self._server._client_names[0] = test_name
        self._server._game_started = True
        test_input = f'{test_name},{test_command}'

        self._server._parse_command(test_input, None)

        patched_manage_piece_drop.assert_called_once()

    def test_parse_command_disconnect(self):
        test_command = 'disconnect'

        output = self._server._parse_command(test_command, None)

        assert output == 'Disconnecting...'

    @unittest.mock.patch.object(GameServer, '_name_new_client')
    def test_parse_command_name_success(self, patched_name_new_client):
        test_name = 'Name'

        self._server._parse_command(test_name, None)

        patched_name_new_client.assert_called_once()

    def test_parse_command_name_server_full(self):
        test_name = 'Name'
        self._server._connected_clients = 2

        output = self._server._parse_command(test_name, None)

        assert output == 'Server is full.'

    def test_parse_command_invalid(self):
        test_name = 'Name'
        test_command = 'invalid'
        self._server._client_names[0] = test_name
        test_input = f'{test_name},{test_command}'

        output = self._server._parse_command(test_input, None)

        assert output == 'Invalid command, try again.'

    def test_cannot_send_to_sock_false(self):
        sock_one = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        expected_result = False
        actual_result = self._server._cannot_send_to_sock(sock_one, sock_two)

        assert expected_result == actual_result

    def test_cannot_send_to_sock_true(self):
        sock_one = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        expected_result = True
        actual_result = self._server._cannot_send_to_sock(sock_one, sock_one)

        assert expected_result == actual_result

    def test_change_active_player(self):
        expected_result = 1

        self._server._change_active_player()

        assert expected_result == self._server._active_player

    def test_start_game(self):
        expected_active_player = 0
        expected_game_started = True

        self._server._start_game()

        assert expected_active_player == self._server._active_player
        assert expected_game_started == self._server._game_started

    @unittest.mock.patch('queue.Queue.put')
    def test_send_loss(self, patched_put):
        sock_one = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock_one)
        self._server._inputs.append(sock_two)
        self._server._message_queues[sock_one] = queue.Queue()
        self._server._message_queues[sock_two] = queue.Queue()

        self._server._send_loss(sock_one)

        patched_put.assert_called_once()

    @unittest.mock.patch('queue.Queue.put')
    def test_send_loss_no_clients_to_send_to(self, patched_put):
        sock_one = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock_one)
        self._server._message_queues[sock_one] = queue.Queue()

        self._server._send_loss(sock_one)

        patched_put.assert_not_called()

    @unittest.mock.patch('queue.Queue.put')
    def test_send_board_to_other_player(self, patched_put):
        sock_one = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_two = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock_one)
        self._server._inputs.append(sock_two)
        self._server._message_queues[sock_one] = queue.Queue()
        self._server._message_queues[sock_two] = queue.Queue()

        self._server._send_board_to_other_player(sock_one)

        patched_put.assert_called_once()

    @unittest.mock.patch('queue.Queue.put')
    def test_send_board_to_other_player_no_other_player(self, patched_put):
        sock_one = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server._inputs.append(sock_one)
        self._server._message_queues[sock_one] = queue.Queue()

        self._server._send_board_to_other_player(sock_one)

        patched_put.assert_not_called()
