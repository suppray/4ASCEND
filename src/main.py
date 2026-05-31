import tkinter as tk
from tkinter import messagebox
import webbrowser
from settings import SettingsFrame, AIDifficultyFrame
from game import GoBoard

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("4ASCEND")
        self.geometry("920x740")
        self.resizable(False, False)
        self.current_frame = None
        self.show_main_menu()

    def clear_screen(self):
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def show_main_menu(self):
        self.clear_screen()
        self.current_frame = tk.Frame(self, width=920, height=740)
        self.current_frame.pack(expand=True, fill=tk.BOTH)
        tk.Label(self.current_frame, text="4ASCEND", font=("Arial",28,"bold")).pack(pady=50)
        btn_f = ("Arial", 14); b_w = 18; b_h = 2
        tk.Button(self.current_frame, text="开始游戏", font=btn_f, width=b_w, height=b_h,
                  command=self.show_game_options).pack(pady=10)
        tk.Button(self.current_frame, text="规则介绍", font=btn_f, width=b_w, height=b_h,
                  command=self.show_rules).pack(pady=10)
        tk.Button(self.current_frame, text="游戏原型", font=btn_f, width=b_w, height=b_h,
                  command=self.show_prototype).pack(pady=10)
        tk.Button(self.current_frame, text="退出游戏", font=btn_f, width=b_w, height=b_h,
                  command=self.quit).pack(pady=10)

    def show_game_options(self):
        self.clear_screen()
        self.current_frame = tk.Frame(self, width=920, height=740)
        self.current_frame.pack(expand=True, fill=tk.BOTH)
        tk.Label(self.current_frame, text="选择游戏模式", font=("Arial",20)).pack(pady=40)
        tk.Button(self.current_frame, text="本地双人对战", font=("Arial",13), width=20, height=2,
                  command=self.show_settings).pack(pady=10)
        tk.Button(self.current_frame, text="人机对战", font=("Arial",13), width=20, height=2,
                  command=self.show_ai_difficulty).pack(pady=10)
        tk.Button(self.current_frame, text="返回主菜单", font=("Arial",13), width=20, height=2,
                  command=self.show_main_menu).pack(pady=10)

    def show_settings(self):
        self.clear_screen()
        self.current_frame = SettingsFrame(self,
                                          on_start=lambda b,w: self.start_local_game(b,w),
                                          on_back=self.show_game_options)
        self.current_frame.pack(expand=True, fill=tk.BOTH)

    def show_ai_difficulty(self):
        self.clear_screen()
        self.current_frame = AIDifficultyFrame(self,
                                              on_select=self.ai_difficulty_selected,
                                              on_back=self.show_game_options)
        self.current_frame.pack(expand=True, fill=tk.BOTH)

    def ai_difficulty_selected(self, diff):
        self.clear_screen()
        self.current_frame = SettingsFrame(self,
                                          on_start=lambda b,w: self.start_ai_game(b,w,diff),
                                          on_back=self.show_ai_difficulty)
        self.current_frame.pack(expand=True, fill=tk.BOTH)

    def start_local_game(self, bh, wh):
        self.clear_screen()
        self.current_frame = GoBoard(self, black_hp_init=bh, white_hp_init=wh,
                                     on_back_to_menu=self.show_main_menu)
        self.current_frame.pack(expand=True, fill=tk.BOTH)

    def start_ai_game(self, bh, wh, diff):
        self.clear_screen()
        self.current_frame = GoBoard(self, black_hp_init=bh, white_hp_init=wh,
                                     on_back_to_menu=self.show_main_menu, ai_difficulty=diff)
        self.current_frame.pack(expand=True, fill=tk.BOTH)

    def show_rules(self):
        self.clear_screen()
        frame = tk.Frame(self, width=920, height=740)
        frame.pack(expand=True, fill=tk.BOTH)
        # 左侧植物图例
        legend_frame = tk.Frame(frame, width=200, height=200)
        legend_frame.pack(side=tk.LEFT, padx=20, pady=20)
        legend_canvas = tk.Canvas(legend_frame, width=100, height=100, bg="#deb887", highlightthickness=0)
        legend_canvas.pack()
        x, y = 50, 50
        legend_canvas.create_oval(x-4, y-4, x+4, y+4, fill="#FFD700", outline="")
        for dx, dy in [(-9,0),(9,0),(0,-9),(0,9)]:
            legend_canvas.create_oval(x+dx-3, y+dy-3, x+dx+3, y+dy+3, fill="#FF69B4", outline="#8B008B", width=1)
        tk.Label(legend_frame, text="魔力植物", font=("Arial",12)).pack()

        text = tk.Text(frame, wrap=tk.WORD, font=("Arial",12), padx=20, pady=20)
        text.insert(tk.END, (
            "4ASCEND 规则\n\n"
            "1. 本游戏是基于五子棋改编的双人棋类游戏，双方轮流落子。\n"
            "2. 黑方为魔族阵营，先手；白方为精灵阵营，后手。游戏目标是通过落子形成攻击以战胜对手。\n"
            "3. 己方回合内，可以在棋盘中线条交叉点上的未落子点位落子。\n"
            "4. 在棋盘上横向、纵向或斜向上有4枚或以上的同色棋子连成一线，所有连线棋子都会被拿起，进入攻击态势，就叫 ASCEND。\n"
            "5. 一方构建出 ASCEND 后会轮到对手进行回应，如果不做任何回应，被攻击方就会受到等同于拿起棋子数量的伤害值。作为攻击的棋子不会再回到棋盘上。\n"
            "6. 如果对手也做出了 ASCEND，会根据棋子数量和魔力植物情况进行抵消，抵消结束后，劣势的一方受到被抵消后的伤害。\n"
            "7. 如果一方生命值为0或81个位置都落满棋子时游戏结束，生还方获胜。落满时，剩余血量多的一方获胜，双方血量相同则棋子较多方获胜（几乎不存在平局）。\n"
            "8. 连3时，意味着下一回合玩家可以发动 ASCEND，如果没有可以形成反击或者连3时，你会吃满伤，所以请确保你可以应对 ASCEND。\n"
            "9. 对局进行时会生长出魔力植物（如图例），落在魔力植物上的棋子可以在 ASCEND 中多抵消1枚棋子，但不会改变该棋子造成的伤害。在对局后期，可以存在魔力植物疯狂生长和一个格子上有两个魔力植物的情况，以加速对局进度。\n"
            "10. 对手做出 ASCEND 后，如果立刻在其组成 ASCEND 的位置上落子，可以构成反击（BACK ATTACK），使得先手攻击方的对应位置的棋子无效，如果有魔力植物，则魔力植物参与反击进攻。\n"
            "11. 对手做出 ASCEND 后，后手方如果不能（或不想）形成 ASCEND，可以直接使用反击来减少一点伤害，如果反击的位置有魔力植物，则可以获得该植物。\n"
            "12. 每次非连续的 ASCEND 结算后棋盘上都会生长魔力植物，这种结算后生长的植物倾向于生长在对进攻方优势的位置。"
        ))
        text.config(state=tk.DISABLED)
        text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Button(frame, text="返回主菜单", font=("Arial",14), command=self.show_main_menu).pack(pady=10)
        self.current_frame = frame

    def show_prototype(self):
        self.clear_screen()
        frame = tk.Frame(self, width=920, height=740)
        frame.pack(expand=True, fill=tk.BOTH)
        tk.Label(frame, text="游戏原型", font=("Arial",20)).pack(pady=40)
        tk.Label(frame, text="即将打开外部网站：\nhttps://unityroom.com/games/4ascend",
                 font=("Arial",14), wraplength=600).pack(pady=20)
        tk.Button(frame, text="打开", font=("Arial",13), width=10,
                  command=lambda: webbrowser.open_new("https://unityroom.com/games/4ascend")).pack(pady=10)
        tk.Button(frame, text="返回主菜单", font=("Arial",13), width=14,
                  command=self.show_main_menu).pack(pady=10)
        self.current_frame = frame

    def quit(self):
        self.destroy()

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
