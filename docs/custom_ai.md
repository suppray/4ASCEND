# 自定义 AI 接口说明

若要使用自己的 AI 算法，请编写一个 Python 脚本，并在其中定义以下函数：

```python
def get_move(board):
    """
    参数：
        board : GoBoard 实例（与 game.py 中相同）
                可用的属性和方法：
                    - board.ai_color : 'black' 或 'white'，AI 操纵的颜色（始终为 'white'）
                    - board.board_state : 9x9 列表，None/'black'/'white'
                    - board.plant_counts : 9x9 列表，每格的魔力植物数量 (0-2)
                    - board.black_hp, board.white_hp : 双方当前血量
                    - board.current_player : 当前应行动方（与 ai_color 一致）
                    - board.pending_capture : 若存在待结算的 ASCEND，则为字典，
                      包含 'color', 'positions', 'count'；否则为 None
                    - board.get_state_snapshot() : 返回当前状态深拷贝
                    - board.detect_capture(row, col, color) : 模拟在 (row,col) 落子 color 后
                      的四连检测，返回 (数量, 位置集合)
                    * board.evaluate_state(ai_color) : 返回对指定颜色的局势评分
                    - board.simulate_move(row, col, color) : 在内部状态模拟落子（不改变 GUI）
                    - board.restore_state(snapshot) : 恢复状态至快照
                    * board.simulate_opponent_response(opp_color) : 模拟对手最优回应
                标 * 的说明实现极为粗糙。
        注意：不要尝试直接修改 board 的 GUI 元素，AI 应该在模拟状态下工作。

    返回值：
        (row, col) : 落子坐标（0~8），若无法落子可返回 None
    """
    # 示例：随机落子
    import random
    empty = [(r,c) for r in range(9) for c in range(9) if board.board_state[r][c] is None]
    if not empty:
        return None
    return random.choice(empty)
```

具体可参见 docs 文件夹下的 example_ai.py 文件。