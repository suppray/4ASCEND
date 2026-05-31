import tkinter as tk

class SettingsFrame(tk.Frame):
    def __init__(self, parent, on_start, on_back):
        super().__init__(parent, width=920, height=740)
        self.on_start = on_start
        self.on_back = on_back

        self.black_hp = tk.IntVar(value=10)
        self.white_hp = tk.IntVar(value=10)

        tk.Label(self, text="血量设置", font=("Arial", 18)).pack(pady=30)

        # 黑方
        frame_black = tk.Frame(self)
        frame_black.pack(pady=10)
        tk.Label(frame_black, text="⚫ 黑方初始血量：", font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Button(frame_black, text="▼", command=lambda: self._adj(self.black_hp, -1)).pack(side=tk.LEFT)
        tk.Entry(frame_black, textvariable=self.black_hp, width=3, justify=tk.CENTER,
                 font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Button(frame_black, text="▲", command=lambda: self._adj(self.black_hp, 1)).pack(side=tk.LEFT)

        # 白方
        frame_white = tk.Frame(self)
        frame_white.pack(pady=10)
        tk.Label(frame_white, text="⚪ 白方初始血量：", font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Button(frame_white, text="▼", command=lambda: self._adj(self.white_hp, -1)).pack(side=tk.LEFT)
        tk.Entry(frame_white, textvariable=self.white_hp, width=3, justify=tk.CENTER,
                 font=("Arial", 12)).pack(side=tk.LEFT)
        tk.Button(frame_white, text="▲", command=lambda: self._adj(self.white_hp, 1)).pack(side=tk.LEFT)

        tk.Button(self, text="开始对战", font=("Arial", 12), width=15,
                  command=lambda: on_start(self.black_hp.get(), self.white_hp.get())).pack(pady=20)
        tk.Button(self, text="返回", font=("Arial", 12), width=15, command=on_back).pack()

    def _adj(self, var, delta):
        v = var.get() + delta
        if 2 <= v <= 20:
            var.set(v)


class AIDifficultyFrame(tk.Frame):
    def __init__(self, parent, on_select, on_back):
        super().__init__(parent, width=920, height=740)
        self.on_select = on_select
        self.on_back = on_back
        tk.Label(self, text="选择 AI 难度", font=("Arial", 20)).pack(pady=50)
        for diff in ["Easy", "Middle", "Hard"]:
            tk.Button(self, text=diff, font=("Arial", 14), width=15, height=2,
                      command=lambda d=diff: on_select(d)).pack(pady=10)
        tk.Button(self, text="返回", font=("Arial", 14), width=15, height=2, command=on_back).pack(pady=20)
