import unittest

from server.game_logic import GameBoard
from server.game_errors import ColumnFullError


class TestGameBoard(unittest.TestCase):

    def setUp(self):
        self._board = GameBoard()

    def _fill_column(self, column):
        for i in range(6):
            self._board._game_board[i][column] = 'x'

    def _fill_row(self, row):
        self._board._game_board[row] = ['x' for _ in range(9)]

    def _fill_positive_diagonal(self):
        for i in range(8, 3, -1):
            for j, k in zip(range(6), range(i, i - 5, -1)):
                self._board._game_board[j][k] = 'x'
                self._board._game_board[j + 1][k] = 'x'

    def _fill_negative_diagonal(self):
        for i in range(5):
            for j, k in zip(range(6), range(i, i + 5)):
                self._board._game_board[j][k] = 'x'
                self._board._game_board[j + 1][k] = 'x'

    def test_is_column_full_returns_true(self):
        self._fill_column(0)

        assert self._board._is_column_full(0) is True

    def test_is_column_full_returns_false(self):
        assert self._board._is_column_full(1) is False

    def test_drop_piece(self):
        expected_row, expected_column = 5, 0
        assert (
            self._board._drop_piece('x', 0) == (expected_row, expected_column)
        )

    def test_is_vertical_match_same_piece(self):
        self._fill_column(0)

        assert self._board._is_vertical_match(0, 'x') is True

    def test_is_vertical_match_diff_piece(self):
        self._fill_column(0)

        assert self._board._is_vertical_match(0, 'o') is False

    def test_is_vertical_match_empty(self):
        assert self._board._is_vertical_match(0, 'x') is False

    def test_is_vertical_match_diff_piece_in_middle(self):
        self._board._game_board[1][0] = 'x'
        self._board._game_board[1][0] = 'o'
        self._board._game_board[1][0] = 'x'
        self._board._game_board[1][0] = 'o'
        self._board._game_board[1][0] = 'x'

        assert self._board._is_vertical_match(0, 'x') is False

    def test_is_horizontal_match_same_piece(self):
        self._fill_row(5)

        assert self._board._is_horizontal_match(5, 'x') is True

    def test_is_horizontal_match_diff_piece(self):
        self._fill_row(5)

        assert self._board._is_horizontal_match(5, 'o') is False

    def test_is_horizontal_match_empty(self):
        assert self._board._is_horizontal_match(5, 'x') is False

    def test_is_horizontal_match_diff_piece_in_middle(self):
        self._board._game_board[5] = [
            'x', 'x', 'o', 'x', 'x', ' ', ' ', ' ', ' '
        ]

        assert self._board._is_horizontal_match(5, 'x') is False

    def test_is_positive_diagonal_match_same_piece(self):
        self._fill_positive_diagonal()

        assert self._board._is_positive_diagonal_match(3, 4, 'x') is True

    def test_is_positive_diagonal_match_diff_piece(self):
        self._fill_positive_diagonal()

        assert self._board._is_positive_diagonal_match(3, 4, 'o') is False

    def test_is_positive_diagonal_match_empty(self):
        assert self._board._is_positive_diagonal_match(3, 4, 'x') is False

    def test_is_positive_diagonal_match_diff_piece_in_middle(self):
        self._board._game_board[3] = [
            'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o'
        ]

        assert self._board._is_positive_diagonal_match(3, 4, 'x') is False

    def test_is_negative_diagonal_match_same_piece(self):
        self._fill_negative_diagonal()

        assert self._board._is_negative_diagonal_match(3, 4, 'x') is True

    def test_is_negative_diagonal_match_diff_piece(self):
        self._fill_negative_diagonal()

        assert self._board._is_negative_diagonal_match(3, 4, 'o') is False

    def test_is_negative_diagonal_match_empty(self):
        assert self._board._is_negative_diagonal_match(3, 4, 'x') is False

    def test_is_negative_diagonal_match_diff_piece_in_middle(self):
        self._board._game_board[3] = [
            'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o', 'o'
        ]

        assert self._board._is_negative_diagonal_match(3, 4, 'x') is False

    def test_insert_piece_success(self):
        expected_win_value = False
        expected_row = 5
        expected_column = 0

        actual_win_value, actual_row, actual_column = (
            self._board.insert_piece('x', 0)
        )

        assert expected_win_value == actual_win_value
        assert expected_row == actual_row
        assert expected_column == actual_column

    def test_insert_piece_raises_column_full_error(self):
        self._fill_column(0)
        self.assertRaises(ColumnFullError, self._board.insert_piece, 'x', 0)

    def test_reset_game(self):
        expected_value = ' '

        self._board.reset_game()

        for row in self._board._game_board:
            for actual_value in row:
                assert expected_value == actual_value
