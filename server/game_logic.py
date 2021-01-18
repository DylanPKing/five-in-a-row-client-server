from server.game_errors import ColumnFullError


class GameBoard:
    '''
    Class to represent the game board.

    Attrs:
    _game_board: list(list(str))
        Stores the games state, with a character representing
        a game piece or an empty space.

    Methods:
    game_board(): str
        Prints the board as a string for player.

    is_board_full(): bool
        Returns True if all board spaces have a piece in them.

    insert_piece(piece: str, column: int): bool, int, int
        insert a game piece at the specified column.
    '''
    def __init__(self):
        '''
        Creates a new GameBoard, and generates an empty 6 * 9 2D array.
        '''
        self.player_pieces = ['x', 'o']
        self._game_board = [[' ' for _ in range(9)] for _ in range(6)]

    @property
    def game_board(self):
        '''
        Returns a string representation of the game board for players.

        Returns:
            str
        '''
        output = ''
        for row in self._game_board:
            for space in row:
                output = f'{output}[ {space} ] '
            output = f'{output}\n'
        return output

    def reset_game(self):
        self._game_board = [[' ' for _ in range(9)] for _ in range(6)]

    def _is_column_full(self, column):
        '''
        Returns True if the first space in the column is filled, else False.
        '''
        return self._game_board[0][column] != ' '

    def _is_vertical_match(self, column, piece):
        '''
        Checks the first two rows of a column for the specified piece.
        If found, will check rest of the column. If another piece type is found
        it will return False, else True.
        If not found, will return False.
        '''
        for row in range(2):
            if self._game_board[row][column] == piece:
                for i in range(row, row + 5):
                    if self._game_board[i][column] != piece:
                        return False
                return True  # Found 5!

        return False
        # Since there's only 6 spaces, no need to continue the loop.

    def _is_horizontal_match(self, row, piece):
        '''
        Checks the first 5 columns of a row for the specified piece.
        If found, will check rest of the row. If another piece type is found
        it will return False, else True.
        If not found, will return False.
        '''
        for col in range(5):
            if self._game_board[row][col] == piece:
                for i in range(col, col + 5):
                    if self._game_board[row][i] != piece:
                        return False
                return True  # Found 5!

        return False
        # Since there's only 9 spaces, no need to continue the loop.

    def _is_positive_diagonal_match(self, row, column, piece):
        '''
        First checks if the specified row and column can result in a postive
        diagonal victory If not, returns False.
        If yes, starts at top right of board and and iterates towards bottom
        left, through the specified piece.
        If 5 in a row are found, return True, else return False.
        '''
        if (row < 4 and column < 4) or (row > 2 and column > 4):
            return False  # All can only reach 4 in a row

        diag_column = column + row
        diag_column = diag_column - 1 if diag_column > 8 else diag_column
        # Prevents index errors, and does not cause logic errors.

        for diag_row in range(2):
            if self._game_board[diag_row][diag_column] == piece:
                for i, j in zip(
                    range(diag_row, diag_row + 5),
                    range(diag_column, diag_column - 5, -1)
                ):
                    if self._game_board[i][j] != piece:
                        return False
                return True

        return False

    def _is_negative_diagonal_match(self, row, column, piece):
        '''
        First checks if the specified row and column can result in a negative
        diagonal victory If not, returns False.
        If yes, starts at top left of board and and iterates towards bottom
        right, through the specified piece.
        If 5 in a row are found, return True, else return False.
        '''
        if (row > 1 and column < 4) or (row < 4 and column > 4):
            return False  # All can only reach 4 in a row

        diag_column = column - row
        diag_column = diag_column + 1 if diag_column < 0 else diag_column

        for diag_row in range(2):
            if self._game_board[diag_row][diag_column] == piece:
                for i, j in zip(
                    range(diag_row, diag_row + 5),
                    range(diag_column, diag_column + 5)
                ):
                    if self._game_board[i][j] != piece:
                        return False
                return True

        return False

    def _drop_piece(self, piece, column):
        '''
        Moves piece down column until it meets an filled space, then places
        piece in last empty space.
        '''
        for row in range(len(self._game_board)):
            if self._game_board[row][column] != ' ':
                self._game_board[row - 1][column] = piece
                return row - 1, column

        # if we get here, the whole column is empty,
        # so drop to the bottom of the column.
        self._game_board[5][column] = piece
        return 5, column

    def _is_winning_move(self, row, column, piece):
        return (
            self._is_horizontal_match(row, piece) or
            self._is_vertical_match(column, piece) or
            self._is_positive_diagonal_match(row, column, piece) or
            self._is_negative_diagonal_match(row, column, piece)
        )

    def is_board_full(self):
        '''
        Checks if all spaces on board are filled.

        Returns:
            bool: True if all spaces are filled, False if not.
        '''
        for i in range(len(self._game_board[0])):
            if self._game_board[0][i] == ' ':
                return False
        return True

    def insert_piece(self, piece, column):
        '''
        Will insert the specified piece in the specified column if there is
        space. If not, will raise a ColumnFullError.

        Returns:
            bool: True if this move was a winning move, False if not.
            int: The row of the game piece.
            int: the column of the game piece.
        '''
        if self._is_column_full(column):
            raise ColumnFullError(
                f'Column {column + 1} is already full. '
                'Please select another column'
            )
        row, column = self._drop_piece(piece, column)
        return self._is_winning_move(row, column, piece), row, column
