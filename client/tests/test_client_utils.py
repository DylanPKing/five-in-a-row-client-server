import socket
from unittest.mock import patch

from client import client_utils


@patch('yaml.load', return_value={'host': '0.0.0.0', 'port': 0})
def test_load_config(_):
    expected_value = {'host': '0.0.0.0', 'port': 0}
    actual_value = client_utils.load_config()

    assert expected_value == actual_value


@patch('socket.socket.send')
@patch('socket.socket.recv', return_value=b'Name')
def test_send_name(patched_recv, patched_send):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    assert client_utils.send_name(sock, 'Name') is True
    patched_send.assert_called_once()
    patched_recv.assert_called_once()


@patch('socket.socket.send')
@patch('socket.socket.recv', return_value=b'Disconnecting...')
def test_send_name_disconnect(patched_recv, patched_send):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    assert client_utils.send_name(sock, 'disconnect') is False
    patched_send.assert_called_once()
    patched_recv.assert_called_once()


@patch('socket.socket.send')
@patch('socket.socket.recv', return_value=b'Server is full.')
def test_send_name_server_full(patched_recv, patched_send):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    assert client_utils.send_name(sock, 'Name') is False
    patched_send.assert_called_once()
    patched_recv.assert_called_once()


@patch('builtins.input', return_value='disconnect')
@patch('socket.socket.send')
@patch('socket.socket.recv', return_value=b'Disconnecting...')
def test_client_loop_disconnect(patched_recv, patched_send, patched_input):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stay_connected = True
    player_name = 'Name'

    client_utils.client_loop(sock, stay_connected, player_name)

    assert True


@patch('builtins.input', return_value='command')
@patch('socket.socket.send')
@patch('socket.socket.recv', return_value=b'Server is full.')
def test_client_loop_server_full(patched_recv, patched_send, patched_input):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stay_connected = True
    player_name = 'Name'

    client_utils.client_loop(sock, stay_connected, player_name)

    assert True
