import tkinter as tk
from tkinter import messagebox
import random
import copy
from ui_components import draw_flower, draw_hp_bar
from ai import get_ai_move

class GoBoard(tk.Frame):
    def __init__(self, parent, black_hp_init=10, white_hp_init=10,
                 on_back_to_menu=None, ai_difficulty=None):
        super().__init__(parent)
        self.parent = parent
        self.on_back_to_menu = on_back_to_menu
        self.board_size = 9
        self.cell_size = 54
        self.padding = self.cell_size // 2
        self.canvas_size = (self.board_size - 1) * self.cell_size + 2 * self.padding

        self.current_player = "black"
        self.game_over = False
        self.consecutive_ascend = False

        self.black_max_hp = black_hp_init
        self.white_max_hp = white_hp_init
        self.black_hp = black_hp_init
        self.white_hp = white_hp_init

        self.board_state = [[None]*9 for _ in range(9)]
        self.stone_ids = [[None]*9 for _ in range(9)]
        self.last_marker = None
        self.pending_capture = None
        self.plant_counts = [[0]*9 for _ in range(9)]

        self.custom_ai = None
        if callable(ai_difficulty):
            self.custom_ai = ai_difficulty
            self.ai_difficulty = None
            self.ai_color = "white"
        else:
            self.ai_difficulty = ai_difficulty
            self.ai_color = "white" if ai_difficulty else None

        self.ghost_id = None
        self.ghost_cross = None
        self.info_var = tk.StringVar(value="")

        self._create_widgets()
        self.draw_board()
        self._redraw_plants()
        self._draw_hp_bars()

        if self.ai_color and self.current_player == self.ai_color:
            self.after(300, self._ai_make_move)

    def _create_widgets(self):
        top_frame = tk.Frame(self)
        top_frame.pack(pady=3)
        if self.on_back_to_menu:
            tk.Button(top_frame, text="返回主菜单", command=self.on_back_to_menu).pack()

        main_frame = tk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 左侧黑方血条（面板宽度 140，居中）
        left_panel = tk.Frame(main_frame, width=140)
        left_panel.pack(side=tk.LEFT, padx=0, fill=tk.Y)
        left_panel.pack_propagate(False)
        tk.Label(left_panel, text="黑方", font=("Arial", 16, "bold"), anchor='center').pack(pady=8)
        self.black_canvas = tk.Canvas(left_panel, width=100, height=240, bg="#f0f0f0", highlightthickness=0)
        self.black_canvas.pack()   # 默认居中

        # 棋盘
        self.canvas = tk.Canvas(main_frame, width=self.canvas_size, height=self.canvas_size, bg="#deb887")
        self.canvas.pack(side=tk.LEFT, expand=True, padx=0, pady=10)
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>", self._on_mouse_move)

        # 右侧白方血条（面板宽度 140，居中）
        right_panel = tk.Frame(main_frame, width=140)
        right_panel.pack(side=tk.RIGHT, padx=0, fill=tk.Y)
        right_panel.pack_propagate(False)
        tk.Label(right_panel, text="白方", font=("Arial", 16, "bold"), anchor='center').pack(pady=8)
        self.white_canvas = tk.Canvas(right_panel, width=100, height=240, bg="#f0f0f0", highlightthickness=0)
        self.white_canvas.pack()

        # 信息提示
        info_frame = tk.Frame(self, height=80, bg="#f0f0f0")
        info_frame.pack(fill=tk.X, padx=5, pady=3)
        info_frame.pack_propagate(False)
        self.info_label = tk.Message(info_frame, textvariable=self.info_var,
                                     font=("Arial", 13, "bold"), fg="red", bg="#f0f0f0",
                                     width=900, justify=tk.CENTER)
        self.info_label.pack(expand=True, fill=tk.BOTH)

    def _draw_hp_bars(self):
        draw_hp_bar(self.black_canvas, self.black_hp, self.black_max_hp)
        draw_hp_bar(self.white_canvas, self.white_hp, self.white_max_hp)
    
    def _open_hp_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("血量调整")
        dialog.resizable(False, False)
        tk.Label(dialog, text="黑方血量:").grid(row=0, column=0)
        bvar = tk.IntVar(value=self.black_hp)
        tk.Button(dialog, text="▼", command=lambda: self._adj(bvar,-1,self.black_max_hp)).grid(row=0,column=1)
        tk.Entry(dialog, textvariable=bvar, width=3).grid(row=0, column=2)
        tk.Button(dialog, text="▲", command=lambda: self._adj(bvar,1,self.black_max_hp)).grid(row=0,column=3)

        tk.Label(dialog, text="白方血量:").grid(row=1, column=0)
        wvar = tk.IntVar(value=self.white_hp)
        tk.Button(dialog, text="▼", command=lambda: self._adj(wvar,-1,self.white_max_hp)).grid(row=1,column=1)
        tk.Entry(dialog, textvariable=wvar, width=3).grid(row=1, column=2)
        tk.Button(dialog, text="▲", command=lambda: self._adj(wvar,1,self.white_max_hp)).grid(row=1,column=3)

        def apply():
            self.black_hp = bvar.get()
            self.white_hp = wvar.get()
            if self.black_hp < 0: self.black_hp = 0
            if self.white_hp < 0: self.white_hp = 0
            self._draw_hp_bars()
            dialog.destroy()
            self._game_over_check()
        tk.Button(dialog, text="确认", command=apply).grid(row=2, column=2)
        tk.Button(dialog, text="取消", command=dialog.destroy).grid(row=2, column=1)

    def _adj(self, var, d, mx):
        v = var.get() + d
        if 0 <= v <= mx: var.set(v)

    def draw_board(self):
        self.canvas.delete("grid")
        for row in range(9):
            y = self.padding + row * self.cell_size
            self.canvas.create_line(self.padding, y,
                                    self.padding + 8*self.cell_size, y, tags="grid")
        for col in range(9):
            x = self.padding + col * self.cell_size
            self.canvas.create_line(x, self.padding,
                                    x, self.padding + 8*self.cell_size, tags="grid")
        self.canvas.tag_lower("grid")

    def _redraw_plants(self):
        self.canvas.delete("plant")
        for r in range(9):
            for c in range(9):
                cnt = min(2, self.plant_counts[r][c])
                if cnt == 0:
                    continue
                x = self.padding + c * self.cell_size
                y = self.padding + r * self.cell_size
                offsets = [(-7, -5), (7, 5)] if cnt == 2 else [(0, 0)]
                for ox, oy in offsets:
                    draw_flower(self.canvas, x + ox, y + oy)

        self.canvas.tag_lower("grid")
        self.canvas.tag_raise("stone")
        self.canvas.tag_raise("capture_marker")
        self.canvas.tag_raise("plant")          # 魔力植物在灰圈之上
        self.canvas.tag_raise("ghost")
        self.canvas.tag_raise("last_marker")

    def _on_mouse_move(self, event):
        if self.game_over or self.pending_capture is not None:
            self._clear_ghost()
            return
        if self.ai_color and self.current_player == self.ai_color:
            self._clear_ghost()
            return

        col = round((event.x - self.padding) / self.cell_size)
        row = round((event.y - self.padding) / self.cell_size)
        if not (0 <= row < 9 and 0 <= col < 9) or self.board_state[row][col] is not None:
            self._clear_ghost()
            return

        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        r = self.cell_size // 2 - 2
        color = self.current_player
        self._clear_ghost()
        self.ghost_id = self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            outline=color, dash=(4, 4), fill="", tags="ghost")
        self.ghost_cross = (row, col)

    def _clear_ghost(self):
        if self.ghost_id:
            self.canvas.delete(self.ghost_id)
            self.ghost_id = None
            self.ghost_cross = None

    def _place_stone(self, row, col):
        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        r = self.cell_size // 2 - 2
        color = self.current_player
        stone_id = self.canvas.create_oval(x-r, y-r, x+r, y+r,
                                           fill=color, outline="black", tags="stone")
        self.stone_ids[row][col] = stone_id
        self.board_state[row][col] = color
        self._redraw_plants()

    def _remove_stones(self, positions):
        for r, c in positions:
            sid = self.stone_ids[r][c]
            if sid:
                self.canvas.delete(sid)
                self.stone_ids[r][c] = None
            self.board_state[r][c] = None

    def _highlight_last_move(self, row, col):
        if self.last_marker:
            self.canvas.delete(self.last_marker)
            self.last_marker = None

        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        ring_radius = self.cell_size // 4 - 1
        self.last_marker = self.canvas.create_oval(
            x - ring_radius, y - ring_radius,
            x + ring_radius, y + ring_radius,
            outline="blue", width=2, fill="", tags="last_marker"
        )
        self.canvas.tag_raise("last_marker")

    def _check_and_capture(self, row, col):
        color = self.board_state[row][col]
        if not color: return 0, set()
        to_remove = set()
        dirs = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in dirs:
            count = 1
            seg = [(row, col)]
            r, c = row+dr, col+dc
            while 0 <= r < 9 and 0 <= c < 9 and self.board_state[r][c] == color:
                count += 1; seg.append((r,c)); r += dr; c += dc
            r, c = row-dr, col-dc
            while 0 <= r < 9 and 0 <= c < 9 and self.board_state[r][c] == color:
                count += 1; seg.append((r,c)); r -= dr; c -= dc
            if count >= 4:
                to_remove.update(seg)
        if to_remove:
            self._remove_stones(to_remove)
            self._redraw_plants()
            return len(to_remove), to_remove
        return 0, set()

    def _draw_capture_markers(self, positions, color):
        ids = []
        for r,c in positions:
            x = self.padding + c*self.cell_size
            y = self.padding + r*self.cell_size
            r_size = self.cell_size//2 - 2
            fill = "#888888" if color=="black" else "#cccccc"
            mid = self.canvas.create_oval(x-r_size, y-r_size, x+r_size, y+r_size,
                                          fill=fill, outline="black", tags="capture_marker")
            ids.append(mid)
        return ids

    def _clear_capture_markers(self):
        if self.pending_capture:
            for mid in self.pending_capture.get("marker_ids", []):
                self.canvas.delete(mid)
        self.pending_capture = None

    def _game_stage(self):
        empty = sum(1 for row in self.board_state for c in row if c is None)
        if empty > 50: return "early"
        if empty > 25: return "mid"
        return "late"

    def _spawn_plants(self, attack_color):
        stage = self._game_stage()
        if stage == "early": amount = 2; stack = False
        elif stage == "mid": amount = random.randint(2,3); stack = False
        else: amount = random.randint(3,5); stack = True
        empty = [(r,c) for r in range(9) for c in range(9) if self.board_state[r][c] is None]
        if not empty: return
        weights = []
        for (r,c) in empty:
            nearby = 0
            for dr in range(-1,2):
                for dc in range(-1,2):
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < 9 and 0 <= nc < 9 and self.board_state[nr][nc] == attack_color:
                        nearby += 1
            weights.append(1 + nearby*2)
        generated = 0
        while generated < amount and empty:
            chosen = random.choices(empty, weights=weights, k=1)[0]
            r, c = chosen
            if self.plant_counts[r][c] >= 2:
                idx = empty.index(chosen); empty.pop(idx); weights.pop(idx); continue
            if not stack and self.plant_counts[r][c] > 0:
                idx = empty.index(chosen); empty.pop(idx); weights.pop(idx); continue
            self.plant_counts[r][c] += 1
            generated += 1
            if not stack:
                idx = empty.index(chosen); empty.pop(idx); weights.pop(idx)
        self._redraw_plants()

    def _natural_plant_growth(self):
        stage = self._game_stage()
        prob = 0.20 if stage == "early" else (0.40 if stage == "mid" else 0.70)
        if random.random() > prob: return
        empty = [(r,c) for r in range(9) for c in range(9) if self.board_state[r][c] is None]
        if not empty: return
        for _ in range(5):
            r, c = random.choice(empty)
            if self.plant_counts[r][c] < 2:
                self.plant_counts[r][c] += 1
                self._redraw_plants()
                return

    @staticmethod
    def _calculate_damage(a_pieces, a_plants, d_pieces, d_plants, attack_color, defend_color):
        common_plants = min(a_plants, d_plants)
        a_plants -= common_plants
        d_plants -= common_plants

        if a_plants > 0:
            sub = min(a_plants, d_pieces)
            d_pieces -= sub
            a_plants -= sub
        if d_plants > 0:
            sub = min(d_plants, a_pieces)
            a_pieces -= sub
            d_plants -= sub

        common_pieces = min(a_pieces, d_pieces)
        a_pieces -= common_pieces
        d_pieces -= common_pieces

        if a_pieces > 0:
            return defend_color, a_pieces
        elif d_pieces > 0:
            return attack_color, d_pieces
        return None, 0

    def _on_click(self, event):
        if self.game_over: return
        if self.ai_color and self.current_player == self.ai_color: return
        col = round((event.x - self.padding) / self.cell_size)
        row = round((event.y - self.padding) / self.cell_size)
        if not (0 <= row < 9 and 0 <= col < 9): return
        if self.board_state[row][col] is not None: return
        self._clear_ghost()
        self.info_var.set("")
        self._process_move(row, col)
        if not self.game_over and self.ai_color and self.current_player == self.ai_color:
            self.after(200, self._ai_make_move)

    def _process_move(self, row, col):
        if self.pending_capture is not None:
            self._handle_settlement(row, col)
            self._game_over_check()
            return
        self._place_stone(row, col)
        self._highlight_last_move(row, col)
        cnt, pos = self._check_and_capture(row, col)
        if cnt >= 4:
            self.pending_capture = {
                'color': self.current_player,
                'positions': pos,
                'count': cnt,
                'marker_ids': self._draw_capture_markers(pos, self.current_player)
            }
            self._redraw_plants()
            name = "黑方" if self.current_player == "black" else "白方"
            self.info_var.set(f"{name} 发动 ASCEND！{cnt} 枚棋子被拿起。等待对方回应。")
        else:
            self.consecutive_ascend = False
            self._natural_plant_growth()
            self.info_var.set("")
        self.current_player = "white" if self.current_player == "black" else "black"
        self._game_over_check()

    def _handle_settlement(self, row, col):
        pending = self.pending_capture
        attack_color = pending['color']
        defend_color = self.current_player

        original_attack_pieces = pending['count']
        original_attack_plants = sum(self.plant_counts[r][c] for r,c in pending['positions'])

        self._place_stone(row, col)
        self._highlight_last_move(row, col)
        defend_pieces, defend_positions = self._check_and_capture(row, col)
        defend_plants_total = sum(self.plant_counts[r][c] for r,c in defend_positions) if defend_pieces >= 4 else 0

        is_counter = (row, col) in pending['positions']
        counter_plant = self.plant_counts[row][col] if is_counter else 0

        if is_counter:
            attack_pieces = original_attack_pieces - 1
            attack_plants_total = original_attack_plants - counter_plant
            defend_plants_total += counter_plant
            remaining_plants = attack_plants_total
        else:
            attack_pieces = original_attack_pieces
            attack_plants_total = original_attack_plants
            remaining_plants = original_attack_plants

        # 若防守方形成新 ASCEND，删除圆环
        if defend_pieces >= 4:
            if self.last_marker:
                self.canvas.delete(self.last_marker)
                self.last_marker = None

        if defend_pieces < 4:
            defend_pieces = 0
            defend_plants_total = 0
            damage = attack_pieces
            if attack_color == "black":
                self.white_hp -= damage
            else:
                self.black_hp -= damage
            if self.black_hp < 0: self.black_hp = 0
            if self.white_hp < 0: self.white_hp = 0
            self._draw_hp_bars()
            att_name = "黑方" if attack_color == "black" else "白方"
            def_name = "白方" if attack_color == "black" else "黑方"
            if is_counter:
                reduced_plants = counter_plant
                msg = (f"{def_name} 使用 BACK ATTACK！\n"
                       f"反击使 {att_name} 减少 1 棋子"
                       + (f"、{reduced_plants} 魔力植物" if reduced_plants > 0 else "") + "。\n"
                       f"{att_name} 有效棋子 {attack_pieces}，剩余魔力植物 {remaining_plants}（不增加伤害）。\n"
                       f"伤害：{damage} 点。")
            else:
                msg = (f"{def_name} 未回应 ASCEND。\n"
                       f"{att_name} 棋子 {original_attack_pieces}，魔力植物 {original_attack_plants}。\n"
                       f"伤害：{damage} 点。（魔力植物不增加伤害）")
            self.info_var.set(msg)
        else:
            target, damage = self._calculate_damage(
                attack_pieces, attack_plants_total,
                defend_pieces, defend_plants_total,
                attack_color, defend_color
            )
            target_name = "黑方" if target == "black" else "白方"
            if target == "black":
                self.black_hp -= damage
            elif target == "white":
                self.white_hp -= damage
            if self.black_hp < 0: self.black_hp = 0
            if self.white_hp < 0: self.white_hp = 0
            self._draw_hp_bars()
            att_name = "黑方" if attack_color == "black" else "白方"
            def_name = "白方" if attack_color == "black" else "黑方"
            if is_counter:
                reduced_plants = counter_plant
                counter_detail = (f"BACK ATTACK：进攻方减少 1 棋子"
                                  + (f"、{reduced_plants} 魔力植物" if reduced_plants > 0 else "") + "。\n")
            else:
                counter_detail = ""
            msg = (f"{counter_detail}"
                   f"{att_name} {attack_pieces}子+{attack_plants_total}魔力植物 vs "
                   f"{def_name} {defend_pieces}子+{defend_plants_total}魔力植物\n"
                   f"抵消后：{target_name}受到 {damage} 点伤害。" if damage > 0 else f"{counter_detail}互相抵消，无伤害。")
            self.info_var.set(msg)

        # 移除植物
        for r,c in pending['positions']:
            if not (is_counter and (r,c) == (row,col)):
                self.plant_counts[r][c] = 0
        if defend_pieces >= 4:
            for r,c in defend_positions:
                self.plant_counts[r][c] = 0

        self._clear_capture_markers()
        if not self.consecutive_ascend:
            self._spawn_plants(attack_color)
            self.consecutive_ascend = True
        self.current_player = attack_color
        self._redraw_plants()

    def _game_over_check(self):
        if self.game_over: return
        winner = None
        reason = ""
        bc = sum(row.count("black") for row in self.board_state)
        wc = sum(row.count("white") for row in self.board_state)

        if self.black_hp <= 0:
            winner = "白方"; reason = "黑方血量为0"
        elif self.white_hp <= 0:
            winner = "黑方"; reason = "白方血量为0"
        elif all(self.board_state[r][c] is not None for r in range(9) for c in range(9)):
            if self.black_hp > self.white_hp:
                winner = "黑方"; reason = "棋盘已满，血量领先"
            elif self.white_hp > self.black_hp:
                winner = "白方"; reason = "棋盘已满，血量领先"
            else:
                if bc > wc:
                    winner = "黑方"; reason = "血量相同，棋子数领先"
                elif wc > bc:
                    winner = "白方"; reason = "血量相同，棋子数领先"
                else:
                    winner = "双方"; reason = "平局"

        if winner:
            self.game_over = True
            msg = f"{winner}获胜！\n{reason}\n黑子：{bc}  白子：{wc}"
            self.canvas.create_text(self.canvas_size//2, self.canvas_size//2,
                                    text=msg, fill="red", font=("Arial", 18, "bold"),
                                    justify=tk.CENTER, tags="game_over")
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<Motion>")
            self.info_var.set("")

    def _ai_make_move(self):
        if self.custom_ai:
            move = self.custom_ai(self)
        else:
            move = get_ai_move(self, self.ai_difficulty)
        if move:
            self.info_var.set("")
            self._process_move(*move)
            if not self.game_over and self.current_player == self.ai_color:
                self.after(200, self._ai_make_move)

    # 以下为 AI 辅助方法，保持不变...
    def detect_capture(self, row, col, color, board=None):
        if board is None: board = self.board_state
        dirs = [(0,1),(1,0),(1,1),(1,-1)]
        to_remove = set()
        for dr,dc in dirs:
            cnt = 1; seg = [(row,col)]
            r,c = row+dr, col+dc
            while 0 <= r < 9 and 0 <= c < 9 and board[r][c] == color:
                cnt += 1; seg.append((r,c)); r += dr; c += dc
            r,c = row-dr, col-dc
            while 0 <= r < 9 and 0 <= c < 9 and board[r][c] == color:
                cnt += 1; seg.append((r,c)); r -= dr; c -= dc
            if cnt >= 4:
                to_remove.update(seg)
        if to_remove: return len(to_remove), to_remove
        return 0, set()

    def get_state_snapshot(self):
        return {
            'board_state': copy.deepcopy(self.board_state),
            'plant_counts': copy.deepcopy(self.plant_counts),
            'black_hp': self.black_hp, 'white_hp': self.white_hp,
            'current_player': self.current_player,
            'pending_capture': copy.deepcopy(self.pending_capture),
            'consecutive_ascend': self.consecutive_ascend,
            'game_over': self.game_over
        }

    def restore_state(self, snap):
        self.board_state = snap['board_state']
        self.plant_counts = snap['plant_counts']
        self.black_hp = snap['black_hp']; self.white_hp = snap['white_hp']
        self.current_player = snap['current_player']
        self.pending_capture = snap['pending_capture']
        self.consecutive_ascend = snap['consecutive_ascend']
        self.game_over = snap['game_over']

    def simulate_move(self, row, col, player):
        self.current_player = player
        self.board_state[row][col] = player
        if self.pending_capture:
            self._simulate_settlement(row, col)
        else:
            cnt, pos = self.detect_capture(row, col, player)
            if cnt >= 4:
                self.pending_capture = {'color': player, 'positions': pos, 'count': cnt}
            else:
                self.consecutive_ascend = False
            self.current_player = "white" if player == "black" else "black"

    def _simulate_settlement(self, row, col):
        pending = self.pending_capture
        attack_color = pending['color']
        defend_color = self.current_player
        attack_pieces = pending['count']
        attack_plants_total = sum(self.plant_counts[r][c] for r,c in pending['positions'])
        self.board_state[row][col] = defend_color
        defend_pieces, defend_positions = self.detect_capture(row, col, defend_color)
        defend_plants_total = sum(self.plant_counts[r][c] for r,c in defend_positions) if defend_pieces >= 4 else 0
        is_counter = (row, col) in pending['positions']
        counter_plant = self.plant_counts[row][col] if is_counter else 0
        if is_counter:
            attack_pieces -= 1
            attack_plants_total -= counter_plant
            defend_plants_total += counter_plant
        if defend_pieces < 4:
            defend_pieces = 0; defend_plants_total = 0
            damage = attack_pieces
            if attack_color == "black": self.white_hp -= damage
            else: self.black_hp -= damage
        else:
            target, damage = self._calculate_damage(
                attack_pieces, attack_plants_total,
                defend_pieces, defend_plants_total,
                attack_color, defend_color)
            if target == "black": self.black_hp -= damage
            elif target == "white": self.white_hp -= damage
        if self.black_hp < 0: self.black_hp = 0
        if self.white_hp < 0: self.white_hp = 0
        for r,c in pending['positions']:
            if not (is_counter and (r,c) == (row,col)):
                self.plant_counts[r][c] = 0
        if defend_pieces >= 4:
            for r,c in defend_positions:
                self.plant_counts[r][c] = 0
        self.pending_capture = None
        self.current_player = attack_color

    def simulate_opponent_response(self, opp_color):
        if self.pending_capture:
            best_score = -9999; best_pos = None
            for pos in self.pending_capture['positions']:
                snap = self.get_state_snapshot()
                self.simulate_move(pos[0], pos[1], opp_color)
                score = self.evaluate_state(ai_color=opp_color)
                self.restore_state(snap)
                if score > best_score:
                    best_score = score; best_pos = pos
            if best_pos:
                self.simulate_move(best_pos[0], best_pos[1], opp_color)
            else:
                pos = random.choice(list(self.pending_capture['positions']))
                self.simulate_move(pos[0], pos[1], opp_color)
        else:
            empty = [(r,c) for r in range(9) for c in range(9) if self.board_state[r][c] is None]
            if not empty: return
            def move_score(pos):
                r,c = pos
                sc = self.plant_counts[r][c]*4 + (8 - abs(r-4) - abs(c-4))*2
                return sc
            sorted_empty = sorted(empty, key=move_score, reverse=True)[:6]
            best_score = -9999; best_move = None
            for r,c in sorted_empty:
                snap = self.get_state_snapshot()
                self.simulate_move(r, c, opp_color)
                score = self.evaluate_state(ai_color=opp_color)
                self.restore_state(snap)
                if score > best_score:
                    best_score = score; best_move = (r,c)
            if best_move:
                self.simulate_move(best_move[0], best_move[1], opp_color)

    def evaluate_state(self, ai_color=None):
        if ai_color is None: ai_color = self.ai_color
        opp_color = "white" if ai_color == "black" else "black"
        my_hp = self.black_hp if ai_color == "black" else self.white_hp
        opp_hp = self.white_hp if ai_color == "black" else self.black_hp
        score = (my_hp - opp_hp) * 70
        my_stones = sum(row.count(ai_color) for row in self.board_state)
        opp_stones = sum(row.count(opp_color) for row in self.board_state)
        score += (my_stones - opp_stones) * 6
        dirs = [(0,1),(1,0),(1,1),(1,-1)]
        def count_line(r,c,color):
            longest = 0
            for dr,dc in dirs:
                cur_len = 1
                nr,nc = r+dr, c+dc
                while 0 <= nr < 9 and 0 <= nc < 9 and self.board_state[nr][nc] == color:
                    cur_len += 1; nr += dr; nc += dc
                nr,nc = r-dr, c-dc
                while 0 <= nr < 9 and 0 <= nc < 9 and self.board_state[nr][nc] == color:
                    cur_len += 1; nr -= dr; nc -= dc
                if cur_len > longest: longest = cur_len
            return longest
        for r in range(9):
            for c in range(9):
                if self.board_state[r][c] == ai_color:
                    line_len = count_line(r,c,ai_color)
                    if line_len >= 2: score += line_len * 4
                elif self.board_state[r][c] == opp_color:
                    line_len = count_line(r,c,opp_color)
                    if line_len >= 3: score -= line_len * 5
        for r in range(9):
            for c in range(9):
                if self.board_state[r][c] == ai_color:
                    for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                        nr,nc = r+dr, c+dc
                        if 0 <= nr < 9 and 0 <= nc < 9:
                            score += self.plant_counts[nr][nc] * 5
        for r in range(9):
            for c in range(9):
                if self.board_state[r][c] is None:
                    self.board_state[r][c] = opp_color
                    cnt, _ = self.detect_capture(r,c,opp_color)
                    self.board_state[r][c] = None
                    if cnt >= 4: score -= 45
        return score
