from game_server import GameServer


if __name__ == "__main__":
    server = GameServer('127.0.0.1', 8080)
    server.server_loop()
