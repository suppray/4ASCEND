import random

def get_ai_move(board, difficulty):
    """根据难度返回 AI 落子坐标，若无空位返回 None"""
    empty = [(r,c) for r in range(9) for c in range(9) if board.board_state[r][c] is None]
    if not empty:
        return None
    if difficulty == "Easy":
        return _ai_easy(board, empty)
    elif difficulty == "Middle":
        return _ai_middle(board, empty)
    else:
        return _ai_hard(board, empty)

def _ai_easy(board, empty):
    plants = [(r,c) for r,c in empty if board.plant_counts[r][c] > 0]
    if plants:
        return random.choice(plants)
    opp = "black" if board.ai_color == "white" else "white"
    for r,c in empty:
        board.board_state[r][c] = opp
        cnt, _ = board.detect_capture(r,c,opp)
        board.board_state[r][c] = None
        if cnt >= 4:
            return (r,c)
    return random.choice(empty)

def _ai_middle(board, empty):
    best_score = -9999
    best_moves = []
    for r,c in empty:
        snap = board.get_state_snapshot()
        board.simulate_move(r, c, board.ai_color)
        opp = "white" if board.ai_color == "black" else "black"
        board.simulate_opponent_response(opp)
        score = board.evaluate_state()
        board.restore_state(snap)
        if score > best_score:
            best_score = score; best_moves = [(r,c)]
        elif score == best_score:
            best_moves.append((r,c))
    return random.choice(best_moves)

def _ai_hard(board, empty):
    empty_cnt = sum(1 for row in board.board_state for cell in row if cell is None)
    if empty_cnt > 50:
        depth = 5; max_candidates = 8
    elif empty_cnt > 25:
        depth = 3; max_candidates = 6
    else:
        depth = 2; max_candidates = 4

    def move_score(pos):
        r,c = pos
        sc = board.plant_counts[r][c] * 5 + (8 - abs(r-4) - abs(c-4)) * 2
        opp = "black" if board.ai_color == "white" else "white"
        board.board_state[r][c] = opp
        cnt, _ = board.detect_capture(r,c,opp)
        board.board_state[r][c] = None
        if cnt >= 4: sc += 30
        return sc
    sorted_empty = sorted(empty, key=move_score, reverse=True)[:max_candidates]

    best_score = -9999
    best_moves = []
    for r,c in sorted_empty:
        snap = board.get_state_snapshot()
        board.simulate_move(r, c, board.ai_color)
        score = _minimax(board, depth-1, -9999, 9999, False)
        board.restore_state(snap)
        if score > best_score:
            best_score = score; best_moves = [(r,c)]
        elif score == best_score:
            best_moves.append((r,c))
    return random.choice(best_moves) if best_moves else random.choice(empty)

def _minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.game_over:
        return board.evaluate_state()
    cur_color = board.ai_color if maximizing else ("white" if board.ai_color == "black" else "black")
    empty = [(r,c) for r in range(9) for c in range(9) if board.board_state[r][c] is None]
    if not empty:
        return board.evaluate_state()
    def move_score(pos):
        r,c = pos
        return board.plant_counts[r][c]*4 + (8 - abs(r-4) - abs(c-4))*2
    sorted_empty = sorted(empty, key=move_score, reverse=True)[:6]

    if maximizing:
        max_val = -9999
        for r,c in sorted_empty:
            snap = board.get_state_snapshot()
            board.simulate_move(r, c, cur_color)
            if board.pending_capture:
                opp = "white" if cur_color == "black" else "black"
                board.simulate_opponent_response(opp)
            val = _minimax(board, depth-1, alpha, beta, False)
            board.restore_state(snap)
            max_val = max(max_val, val)
            alpha = max(alpha, val)
            if beta <= alpha: break
        return max_val
    else:
        min_val = 9999
        for r,c in sorted_empty:
            snap = board.get_state_snapshot()
            board.simulate_move(r, c, cur_color)
            if board.pending_capture:
                opp = "white" if cur_color == "black" else "black"
                board.simulate_opponent_response(opp)
            val = _minimax(board, depth-1, alpha, beta, True)
            board.restore_state(snap)
            min_val = min(min_val, val)
            beta = min(beta, val)
            if beta <= alpha: break
        return min_val
