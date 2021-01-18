from game_server import GameServer
from server_utils import load_config


if __name__ == "__main__":
    config = load_config()

    server = GameServer(config['host'], config['port'])
    server.server_loop()
