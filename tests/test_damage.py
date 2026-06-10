import sys
sys.path.append('../src')
from game import GoBoard
import tkinter as tk

def test_damage_calculation():
    root = tk.Tk()
    board = GoBoard(root)
    # 进攻方 4子+1花 vs 防守方 无ASCEND 无反击 => 伤害4
    target, dmg = board._calculate_damage(4, 1, 0, 0, "black", "white")
    assert target == "white" and dmg == 4
    # 进攻方 4子+1花 vs 防守方 5子 => 花抵消后 4 vs 4，互相抵消无伤害
    target, dmg = board._calculate_damage(4, 1, 5, 0, "black", "white")
    assert target is None and dmg == 0
    # 反击情形在外部已减1，这里只测通用函数
    root.destroy()
    print("test_damage_calculation passed")
