"""自动轨迹绘制（matplotlib 版，直接出图，不弹窗）"""

import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_FILE = "data.txt"

x, y, heading = 0.0, 0.0, 0.0        # 起点在 (0,0)，初始朝右
fig, ax = plt.subplots(figsize=(6, 6), dpi=150)

with open(DATA_FILE, encoding="utf-8") as file:
    for line in file:
        if not line.strip():
            continue
        distance, turn, angle, r, g, b = [float(v) for v in line.split(",")]
        nx = x + distance * math.cos(math.radians(heading))
        ny = y + distance * math.sin(math.radians(heading))
        ax.plot([x, nx], [y, ny], color=(r, g, b), lw=2)
        x, y = nx, ny
        heading += angle if turn == 0 else -angle   # 0 左转，1 右转

ax.set_aspect("equal")
ax.axis("off")
fig.savefig("trace.png", bbox_inches="tight")
print("已保存 trace.png")
