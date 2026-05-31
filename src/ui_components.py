def draw_flower(canvas, x, y):
    """在画布 (x,y) 绘制一朵魔力植物（中心花蕊 + 四瓣花瓣）"""
    canvas.create_oval(x-4, y-4, x+4, y+4, fill="#FFD700", outline="", tags="plant")
    for dx, dy in [(-9,0), (9,0), (0,-9), (0,9)]:
        canvas.create_oval(x+dx-3, y+dy-3, x+dx+3, y+dy+3,
                           fill="#FF69B4", outline="#8B008B", width=1, tags="plant")

def draw_hp_bar(canvas, current_hp, max_hp):
    """在指定的 Canvas 上绘制两列方格血条"""
    canvas.delete("hp")
    cell, gap = 20, 2
    for i in range(max_hp):
        fill = "green" if i < current_hp else "#deb887"
        col, row = i % 2, i // 2
        x1 = 10 + col * (cell + gap)
        y1 = 10 + row * (cell + gap)
        canvas.create_rectangle(x1, y1, x1+cell, y1+cell,
                                fill=fill, outline="black", tags="hp")
