def draw_flower(canvas, x, y):
    """在画布 (x,y) 绘制一朵魔力植物"""
    canvas.create_oval(x-4, y-4, x+4, y+4, fill="#FFD700", outline="", tags="plant")
    for dx, dy in [(-9,0), (9,0), (0,-9), (0,9)]:
        canvas.create_oval(x+dx-3, y+dy-3, x+dx+3, y+dy+3,
                           fill="#FF69B4", outline="#8B008B", width=1, tags="plant")

def draw_hp_bar(canvas, current_hp, max_hp):
    """在 Canvas 内居中绘制方格血条，边长 40"""
    canvas.delete("hp")
    cell = 40          # 边长扩大为 40
    gap = 2            # 间距 2
    cols = 2
    rows = (max_hp + 1) // 2
    total_width = cols * cell + (cols - 1) * gap   # 82
    total_height = rows * cell + (rows - 1) * gap

    canvas_w = int(canvas["width"])   # 80
    canvas_h = int(canvas["height"])  # 240
    start_x = (canvas_w - total_width) // 2
    start_y = (canvas_h - total_height) // 2

    for i in range(max_hp):
        fill = "green" if i < current_hp else "#f0f0f0"
        col = i % cols
        row = i // cols
        x1 = start_x + col * (cell + gap)
        y1 = start_y + row * (cell + gap)
        x2 = x1 + cell
        y2 = y1 + cell
        canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="black", tags="hp")
