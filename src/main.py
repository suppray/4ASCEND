import tkinter as tk
from tkinter import messagebox
import webbrowser
from settings import SettingsFrame, AIDifficultyFrame
from game import GoBoard
import os

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("4ASCEND")
        self.geometry("920x740")
        self.resizable(False, False)
        
        # 尝试消除 libpng 警告
        try:
            self.iconbitmap('')
        except:
            pass
        try:
            self.iconphoto(True, tk.PhotoImage(width=1, height=1))
        except:
            pass

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
        main_frame = tk.Frame(self, width=920, height=740)
        main_frame.pack(expand=True, fill=tk.BOTH)

        content_frame = tk.Frame(main_frame)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 左侧植物图例
        legend_frame = tk.Frame(content_frame, width=200, height=200)
        legend_frame.pack(side=tk.LEFT, padx=20, pady=20)
        legend_canvas = tk.Canvas(legend_frame, width=100, height=100, bg="#deb887", highlightthickness=0)
        legend_canvas.pack()
        x, y = 50, 50
        legend_canvas.create_oval(x-4, y-4, x+4, y+4, fill="#FFD700", outline="")
        for dx, dy in [(-9,0),(9,0),(0,-9),(0,9)]:
            legend_canvas.create_oval(x+dx-3, y+dy-3, x+dx+3, y+dy+3, fill="#FF69B4", outline="#8B008B", width=1)
        tk.Label(legend_frame, text="魔力植物", font=("Arial",12)).pack()

        text = tk.Text(content_frame, wrap=tk.WORD, font=("Arial",12), padx=10, pady=10)
        
        # 从外部文件读取规则
        rules_path = os.path.join(os.path.dirname(__file__), "rules.txt")
        try:
            with open(rules_path, "r", encoding="utf-8") as f:
                rules_content = f.read()
        except FileNotFoundError:
            rules_content = "规则文件未找到。"
        text.insert(tk.END, rules_content)
        text.config(state=tk.DISABLED)
        text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        tk.Button(btn_frame, text="返回主菜单", font=("Arial",14), command=self.show_main_menu).pack()

        self.current_frame = main_frame

    def show_prototype(self):
        self.clear_screen()
        frame = tk.Frame(self, width=920, height=740)
        frame.pack(expand=True, fill=tk.BOTH)
        tk.Label(frame, text="游戏原型", font=("Arial",20)).pack(pady=40)
        tk.Label(frame, text="即将打开外部网站：\nhttps://unityroom.com/games/4ascend",
                 font=("Arial",14), wraplength=600).pack(pady=20)
        btn_f=("Arial",13)
        tk.Button(frame, text="打开", font=btn_f, width=10,
                  command=lambda: webbrowser.open_new("https://unityroom.com/games/4ascend")).pack(pady=10)
        tk.Button(frame, text="返回主菜单", font=btn_f, width=14,
                  command=self.show_main_menu).pack(pady=10)
        self.current_frame = frame

    def quit(self):
        self.destroy()

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
