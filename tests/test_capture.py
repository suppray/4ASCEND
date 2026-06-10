import sys
sys.path.append('../src')
from game import GoBoard
import tkinter as tk

def test_four_in_a_row():
    root = tk.Tk()
    board = GoBoard(root)
    board.board_state[0][0] = "black"
    board.board_state[0][1] = "black"
    board.board_state[0][2] = "black"
    cnt, pos = board.detect_capture(0, 2, "black")
    assert cnt == 0  # 只有3个
    board.board_state[0][3] = "black"
    cnt, pos = board.detect_capture(0, 3, "black")
    assert cnt == 4
    assert pos == {(0,0),(0,1),(0,2),(0,3)}
    root.destroy()
    print("test_four_in_a_row passed")
