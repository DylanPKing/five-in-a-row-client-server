# five-in-a-row-client-server
An implementation of a five in a row game utilising a client/server architecture in Python.

## Notes
- Working directory (AKA `./`) has been added to `$PATH`.
- Developed on Ubuntu 20.04 in a WSL2 VM.
- Tested locally. Your mileage may vary if running this across multiple machines.
- Server disconnects all clients and shuts down if it does not receive a request within 15 seconds of handling its previous request.

## Running
Note: These commands work on Ubuntu 20.04 with `python3` and `python3-pytest` installed via `apt`. If they do not work for you try running `python` and `pytest` instead.
### Server
```bash
python3 server
```
### Client
```bash
python3 client
```
### Tests
```bash
pytest-3
```

## Known Issues
- Using Pythons builtin `input` function blocks `stdin` until after the user has sent a command. I tried several solutions to this, with varying degrees of success.
  - Tried running client input and output on separate threads. Did not work as `input` was still blocking `stdin`.
  - Tried implementing a non-blocking method to read `stdin`. This saw some success, but was very inconsistent, and confusing to read.
- If a client tries to disconnect after another client has already disconnected, and is the only client on the server, the server processes the `disconnect` command incorrectly, and does not not disconnect the client properly.
