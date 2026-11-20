"""作业：蒙特卡罗方法手搓圆形（纯标准库，不依赖 matplotlib）"""

import math
import random


# ==================== 1. 核心算法 ====================

def monte_carlo_pi(total=100_000, seed=None):
    """在单位正方形里撒点，落进 1/4 圆的比例 ≈ π/4 → π ≈ 4*命中/总数"""
    rng = random.Random(seed)
    inside = 0
    for _ in range(total):
        px, py = rng.random(), rng.random()
        if px * px + py * py <= 1.0:
            inside += 1
    return 4 * inside / total, inside


# ==================== 2. 字符版圆形 ====================

def draw_ascii_circle(points=500, rows=31, seed=7):
    """● 圆内，· 圆外，│ 圆弧"""
    rng = random.Random(seed)
    cols = rows * 2
    grid = [[" "] * cols for _ in range(rows)]

    inside = 0
    for _ in range(points):
        px, py = rng.random(), rng.random()
        row = rows - 1 - min(int(py * rows), rows - 1)
        col = min(int(px * cols), cols - 1)
        if px * px + py * py <= 1.0:
            grid[row][col] = "●"
            inside += 1
        else:
            grid[row][col] = "·"

    # 圆弧最后画，免得被点盖住
    for row in range(rows):
        yy = 1 - (row + 0.5) / rows
        col = round(math.sqrt(max(0.0, 1 - yy * yy)) * cols) - 1
        if 0 <= col < cols:
            grid[row][col] = "│"

    print("\n".join("".join(line) for line in grid))
    print(f"撒点 {points} 个，圆内 {inside} 个 → π ≈ {4 * inside / points:.4f}")


# ==================== 3. 出图：手写 SVG，不用第三方库 ====================

class SvgCanvas:
    """极简 SVG 画布，把图形拼成 xml 文本"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.parts = []

    def rect(self, x, y, w, h, stroke="#333", stroke_width=1.0, fill="none"):
        self.parts.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>')

    def circle(self, cx, cy, radius, fill="#333", opacity=1.0):
        self.parts.append(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" '
            f'fill="{fill}" fill-opacity="{opacity}"/>')

    def line(self, x1, y1, x2, y2, stroke="#999", stroke_width=0.8, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}"{extra}/>')

    def polyline(self, pts, stroke="#333", stroke_width=1.0, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        text = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        self.parts.append(
            f'<polyline points="{text}" fill="none" stroke="{stroke}" '
            f'stroke-width="{stroke_width}"{extra}/>')

    def text(self, x, y, content, size=12, anchor="start", fill="#333"):
        self.parts.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}">{content}</text>')

    def save(self, path):
        body = "\n  ".join(self.parts)
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
                f'height="{self.height}" viewBox="0 0 {self.width} {self.height}">')
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"{head}\n  {body}\n</svg>\n")


def save_svg(total=3000, seed=7, path="mc_pi.svg"):
    """左：撒点 + 1/4 圆；右：估计值收敛曲线"""
    rng = random.Random(seed)
    spot_x, spot_y, spot_hit, curve = [], [], [], []
    inside = 0
    for idx in range(total):
        px, py = rng.random(), rng.random()
        ok = px * px + py * py <= 1.0
        inside += ok
        spot_x.append(px)
        spot_y.append(py)
        spot_hit.append(ok)
        curve.append(4 * inside / (idx + 1))

    canvas = SvgCanvas(900, 440)

    # ---------- 左图 ----------
    ox, oy, box = 70, 80, 300
    canvas.rect(ox, oy, box, box, "#333", 1.2)
    for px, py, ok in zip(spot_x, spot_y, spot_hit):
        canvas.circle(ox + px * box, oy + (1 - py) * box, 1.6,
                      "#2f6fd0" if ok else "#f0a35e", 0.85)
    arc = [(ox + math.cos(math.radians(deg)) * box,
            oy + (1 - math.sin(math.radians(deg))) * box)
           for deg in range(0, 91, 2)]
    canvas.polyline(arc, "#111111", 1.8)
    canvas.text(ox + box / 2, oy - 18,
                f"在正方形里撒 {total} 个点：圆内占比 ≈ π/4", 13, "middle")
    canvas.text(ox + box / 2, oy + box + 26, "x", 12, "middle")
    canvas.text(ox - 16, oy + box / 2, "y", 12, "middle")

    # ---------- 右图（横轴取对数，不然开头全挤在左边） ----------
    gx, gy, gw, gh = 500, 80, 340, 300
    low = min(min(curve), math.pi) * 0.995
    high = max(max(curve), math.pi) * 1.005
    log_total = math.log10(total)

    for k in range(6):
        value = low + (high - low) * k / 5
        pos_y = gy + gh - (value - low) / (high - low) * gh
        canvas.line(gx, pos_y, gx + gw, pos_y, "#dddddd", 0.8)
        canvas.text(gx - 8, pos_y + 4, f"{value:.2f}", 10, "end")

    curve_pts = [(gx + math.log10(i + 1) / log_total * gw,
                  gy + gh - (v - low) / (high - low) * gh) for i, v in enumerate(curve)]
    canvas.polyline([(gx, gy), (gx, gy + gh), (gx + gw, gy + gh)][1:], "#333", 1.0)
    canvas.line(gx, gy, gx, gy + gh, "#333", 1.0)
    canvas.polyline(curve_pts, "#2f6fd0", 1.4)

    pi_y = gy + gh - (math.pi - low) / (high - low) * gh
    canvas.line(gx, pi_y, gx + gw, pi_y, "#d0342c", 1.2, dash="6,4")
    canvas.text(gx + 8, pi_y - 8, f"真实 π = {math.pi:.4f}", 10, "start", "#d0342c")

    tick_labels = ["1", "10", "100", "1000", "10000", "100000"]
    for power in range(0, int(log_total) + 1):
        pos_x = gx + power / log_total * gw
        canvas.line(pos_x, gy + gh, pos_x, gy + gh + 5, "#333", 0.8)
        canvas.text(pos_x, gy + gh + 18, tick_labels[power], 9, "middle")

    canvas.text(gx + gw / 2, gy - 18,
                f"估计值收敛：最终 π ≈ {curve[-1]:.4f}", 13, "middle")
    canvas.text(gx + gw / 2, gy + gh + 40, "撒点个数（对数刻度）", 11, "middle")

    canvas.save(path)
    print("已保存:", path)


if __name__ == "__main__":
    print("=== 不同撒点数下的估计（每组 3 次） ===")
    for total in (1_000, 10_000, 100_000, 1_000_000):
        values = [monte_carlo_pi(total, seed=s)[0] for s in (1, 2, 3)]
        avg = sum(values) / 3
        print(f"n = {total:>8} : " + "  ".join(f"{v:.4f}" for v in values) +
              f"   平均 {avg:.6f}   误差 {abs(avg - math.pi) / math.pi * 100:.3f}%")
    print(f"真实 π = {math.pi:.6f}")

    print("\n=== 字符版圆 ===")
    draw_ascii_circle()

    print("\n=== 出图 ===")
    save_svg()
