# -*- coding: utf-8 -*-
"""作业：统计“十五五”发展规划报告的热词频率"""

import collections
import re

import jieba
import jieba.posseg as pseg

# ---------- 可调参数 ----------
REPORT_FILE = "十五五报告.txt"     # 报告全文，UTF-8 编码，和脚本放同一目录
TOP_N = 30                        # 取前多少名热词

# 自定义词：jieba 分不完整的专有名词手工补进去
CUSTOM_WORDS = [
    "十五五", "新质生产力", "高质量发展", "中国式现代化", "共同富裕",
    "全过程人民民主", "全国统一大市场", "乡村振兴", "双碳", "数字中国",
    "人民至上", "科技自立自强", "乡村全面振兴", "区域协调发展战略",
]

# 停用词：高频但没信息量的虚词和套话，按需增删
STOPWORDS = set("""
的 地 得 了 着 和 与 及 或 是 在 有 为 以 对 从 到 把 被 让 使 将
要 应 可 能 会 也 就 都 还 又 更 最 很 太 再 才 只 但 而 且 如 若 因
这 那 其 之 等 中 上 下 内 外 前 后 左 右 个 些 种 项 次 一 二 三 四 五
我们 你们 他们 自己 大家 什么 怎么 以及 并且 因此 但是 如果 由于 通过
方面 有关 相关 各项 各类 各种 一定 必须 需要 应该 可以 能够 不能
积极 切实 努力 着力 充分 更加 更好 更多 不断 持续 进一步 继续
工作 任务 要求 举措 措施 内容 情况 问题 形式 过程 时期 阶段
""".split())

# 只统计名词和动名词（想连动词一起算，就改成 KEEP_FLAGS = ("n", "vn", "v")）
KEEP_FLAGS = ("n", "vn")

SAMPLE_TEXT = """
坚持创新驱动发展，加快实现高水平科技自立自强。以科技创新引领新质生产力发展，
推动高质量发展取得新成效。深入实施科教兴国战略、人才强国战略、创新驱动发展战略。
加快建设现代化产业体系，培育壮大新兴产业，前瞻布局未来产业。全面推进乡村振兴，
促进区域协调发展，扎实推进共同富裕。坚持人民至上，增进民生福祉，提高人民生活品质。
统筹发展和安全，防范化解重大风险，建设更高水平的平安中国。繁荣发展社会主义文化，
增强文化自信。推动绿色发展，积极稳妥推进碳达峰碳中和，建设美丽中国。
"""


def read_report(path=REPORT_FILE):
    """读报告全文；没有文件就退回内置示例，方便先跑通"""
    try:
        with open(path, encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"[提示] 没找到 {path}，先用内置示例文本演示。\n")
        return SAMPLE_TEXT


def count_words(text, topn=TOP_N):
    """分词 → 过滤 → 计数，返回 (词频表, 有效词总数, 词条种类数)"""
    counts = collections.Counter()
    for pair in pseg.cut(text):
        piece = pair.word.strip()             # 不同版本的 jieba 不一定支持 (词, 词性) 解包，统一取属性
        flag = pair.flag
        if len(piece) < 2:                    # 扔掉单字
            continue
        if piece in STOPWORDS:                # 扔掉停用词
            continue
        if not re.search(r"[\u4e00-\u9fa5]", piece):   # 扔掉纯数字/符号
            continue
        if not flag.startswith(KEEP_FLAGS):   # 只留名词类
            continue
        counts[piece] += 1
    total = sum(counts.values())
    return counts.most_common(topn), total, len(counts)


def show_table(items, total, kind_count, char_count, topn=TOP_N):
    """控制台打印：名次 / 词 / 次数 / 占比 / 条形图"""
    print(f"总字数：{char_count}，有效词条：{total}，不同词条：{kind_count}\n")
    print(f"{'排名':<4}{'热词':<10}{'次数':>6}{'占比':>9}   分布")
    print("-" * 72)
    peak = items[0][1] if items else 1
    for rank, (word, num) in enumerate(items, start=1):
        ratio = num / total * 100
        bar = "█" * max(1, round(num / peak * 30))
        print(f"{rank:<4}{word:<10}{num:>6}{ratio:>8.2f}%   {bar}")
    covered = sum(num for _, num in items) / total * 100
    print(f"\n前 {topn} 个词覆盖了全部有效词的 {covered:.1f}%")


def plot_bar(items, path="hotwords.png", topn=15):
    """横向柱状图，博客配图用（需要 matplotlib）"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei",
                                       "PingFang SC", "Noto Sans CJK SC",
                                       "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False    # 中文环境下负号会乱码

    head = items[:topn][::-1]                     # 倒序，最大的画最上面
    labels = [word for word, _ in head]
    values = [num for _, num in head]

    fig, ax = plt.subplots(figsize=(7, 0.35 * len(head) + 1.2), dpi=150)
    ax.barh(labels, values, color="#2f6fd0", height=0.65)
    for label, value in zip(labels, values):
        ax.text(value + max(values) * 0.01, label, str(value),
                va="center", fontsize=9)
    ax.set_xlabel("出现次数")
    ax.set_title(f"十五五规划报告热词 Top {len(head)}")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("柱状图已保存:", path)


def plot_wordcloud(items, path="hotwords_cloud.png", font="simhei.ttf"):
    """词云（需要 pip install wordcloud）"""
    from wordcloud import WordCloud

    cloud = WordCloud(font_path=font, width=1200, height=700,
                      background_color="white", colormap="Blues",
                      max_words=200).generate_from_frequencies(dict(items))
    cloud.to_file(path)
    print("词云已保存:", path)


if __name__ == "__main__":
    for word in CUSTOM_WORDS:             # 先把专有名词加进分词词典
        jieba.add_word(word, freq=1000)

    text = read_report()
    char_count = len(re.sub(r"[\s\W]", "", text))     # 去掉空白和标点后的字数
    items, total, kind_count = count_words(text)
    show_table(items, total, kind_count, char_count)

    plot_bar(items)                       # 没装 matplotlib 就把这行注释掉
    # plot_wordcloud(items, font="C:/Windows/Fonts/simhei.ttf")
