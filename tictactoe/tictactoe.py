"""
Tic Tac Toe Player
"""
import copy
import math
from typing import List

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board: List[List]):
    """
    Returns player who has the next turn on a board.
    """
    x = 0
    o = 0
    for rows in board:
        for cell in rows:
            if cell == X:
                x+=1
            elif cell == O:
                o+=1
    if x>o:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for row in range(len(board)):
        for column in range(len(board[row])):
            if board[row][column] == EMPTY:
                actions.add((row, column))
    return actions

def result(board: List[List], action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(new_board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    size = len(board)

    # Check rows and columns
    for i in range(size):
        if all(board[i][j] == X for j in range(size)) or all(board[j][i] == X for j in range(size)):
            return X
        if all(board[i][j] == O for j in range(size)) or all(board[j][i] == O for j in range(size)):
            return O

    # Check diagonals
    if all(board[i][i] == X for i in range(size)) or all(board[i][size - i - 1] == X for i in range(size)):
        return X
    if all(board[i][i] == O for i in range(size)) or all(board[i][size - i - 1] == O for i in range(size)):
        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return not actions(board) or winner(board)

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if not win:
        return 0
    if win == X:
        return 1
    else:
        return -1


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    def min_val(board):
        if terminal(board):
            return utility(board)
        v = float("-inf")
        for act in actions(board):
            v = min(v, max_val(result(board, act)))
        return v

    def max_val(board):
        if terminal(board):
            return utility(board)
        v = float("inf")
        for act in actions(board):
            v = max(v, min_val(result(board, act)))
        return v

    pl = player(board)
    (action)
    for a in actions(board):
        