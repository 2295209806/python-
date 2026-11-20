"""P196 5.1 字符田字格绘制 + 科赫雪花（0~4 阶）"""

import math
import os

# ==================== 1. 字符田字格 ====================

def draw_tian(cell_w=6, cell_h=3, texts=None):
    """用字符画田字格：外框 + 中间十字，分成四个小格
       cell_w 每个小格的字符宽度，cell_h 每个小格的行数
       texts  可选，4 个字，按 左上/右上/左下/右下 填进格子
    """
    total_w = 2 * cell_w + 3
    total_h = 2 * cell_h + 3
    mid_c = cell_w + 1          # 中间竖线所在列
    mid_r = cell_h + 1          # 中间横线所在行

    grid = [[" "] * total_w for _ in range(total_h)]

    # 三条横线
    for r in (0, mid_r, total_h - 1):
        for c in range(1, total_w - 1):
            grid[r][c] = "─"

    # 三条竖线
    for c in (0, mid_c, total_w - 1):
        for r in range(1, total_h - 1):
            grid[r][c] = "│"

    # 交点连接符
    grid[0][0], grid[0][total_w - 1] = "┌", "┐"
    grid[total_h - 1][0], grid[total_h - 1][total_w - 1] = "└", "┘"
    grid[0][mid_c], grid[total_h - 1][mid_c] = "┬", "┴"
    grid[mid_r][0], grid[mid_r][total_w - 1] = "├", "┤"
    grid[mid_r][mid_c] = "┼"

    # 在四个格子中央写字
    if texts:
        blocks = [(1, 1), (1, mid_c + 1), (mid_r + 1, 1), (mid_r + 1, mid_c + 1)]
        for ch, (r0, c0) in zip(texts, blocks):
            grid[r0 + cell_h // 2][c0 + cell_w // 2] = ch

    print("\n".join("".join(row) for row in grid))


# ==================== 2. 科赫雪花 ====================
# 0 阶：一条直线段；雪花的 0 阶 = 等边三角形
# 每一阶把每条边换成 4 段：短 / 短（拐出去再回来）/ 短

def koch_curve(t, n, length):
    """turtle 版：画一条 n 阶科赫曲线"""
    if n == 0:
        t.forward(length)
        return
    length /= 3
    koch_curve(t, n - 1, length)     # 前 1/3
    t.left(60)
    koch_curve(t, n - 1, length)     # 外侧斜边
    t.right(120)
    koch_curve(t, n - 1, length)     # 回落的斜边
    t.left(60)
    koch_curve(t, n - 1, length)     # 后 1/3


def draw_koch_turtle(n, size=300):
    """turtle 版：画一朵 n 阶雪花（图形界面下运行）"""
    import turtle as t
    t.setup(600, 600)
    t.speed(0)
    t.penup()
    t.goto(-size / 2, -size * math.sqrt(3) / 6)   # 左下角出发
    t.setheading(60)                              # 保证尖朝上
    t.pendown()
    for _ in range(3):
        koch_curve(t, n, size)                    # 每条边换成一条科赫曲线
        t.right(120)                              # 换个方向画下一条边
    t.hideturtle()
    t.done()


def koch_points(n, p1, p2):
    """复数版：返回 p1→p2 的 n 阶科赫折线的顶点列表"""
    if n == 0:
        return [p1, p2]
    d = (p2 - p1) / 3
    a = p1 + d                        # 第一个三等分点
    b = a + d                         # 第二个三等分点
    # 把 d 顺时针转 60°，凸起朝外
    tip = a + d * complex(math.cos(-math.pi / 3), math.sin(-math.pi / 3))
    return (koch_points(n - 1, p1, a)[:-1]
            + koch_points(n - 1, a, tip)[:-1]
            + koch_points(n - 1, tip, b)[:-1]
            + koch_points(n - 1, b, p2))


def koch_snowflake_points(n, size=1.0, center=0j):
    """返回一整朵 n 阶雪花的闭合顶点列表"""
    verts = [center + size * complex(math.cos(a), math.sin(a))
             for a in (math.pi / 2, math.pi / 2 + 2 * math.pi / 3,
                       math.pi / 2 + 4 * math.pi / 3)]   # 尖朝上的三角形
    pts = []
    for i in range(3):
        pts += koch_points(n, verts[i], verts[(i + 1) % 3])[:-1]
    pts.append(pts[0])                # 闭合
    return pts


def save_koch_png(out_dir="koch", orders=range(5)):
    """matplotlib 版：0~4 阶各存一张 PNG，博客里直接用"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(out_dir, exist_ok=True)
    for n in orders:
        pts = koch_snowflake_points(n)
        xs = [p.real for p in pts]
        ys = [p.imag for p in pts]
        fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
        ax.fill(xs, ys, color="#5b6ee1", alpha=0.9, linewidth=0)
        ax.set_aspect("equal")        # 等比，不然雪花会被压扁
        ax.axis("off")
        ax.set_title(f"{n} 阶科赫雪花（边数 {len(pts) - 1}）")
        path = os.path.join(out_dir, f"koch_{n}.png")
        fig.savefig(path, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print("已保存:", path)


if __name__ == "__main__":
    print("=== 田字格（空） ===")
    draw_tian()

    print("\n=== 田字格（带 4 个字） ===")
    draw_tian(cell_w=8, cell_h=3, texts="春夏秋冬")

    print("\n=== 0~4 阶雪花 ===")
    save_koch_png()

    # 想直接看动画就放开下面这行（需要图形界面）
    # draw_koch_turtle(4)
