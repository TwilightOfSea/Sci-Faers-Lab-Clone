import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置学术图表格式
plt.rcParams.update({
    'font.family': 'Times New Roman',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'figure.dpi': 300
})

def plot(data_path, output_path):
    data = pd.read_csv(data_path)
    # 数据预处理
    filtered_data = data['wt_group'].dropna()
    filtered_data = filtered_data[filtered_data != 'Missing']
    filtered_data = filtered_data[filtered_data != '--']

    # 计算频数和百分比
    counts = filtered_data.value_counts().sort_index()
    percentages = 100 * counts / counts.sum()

    # 创建画布
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='white')

    # 生成动态标签：仅显示≥5%的标签
    labels = [label if percentages.loc[label] >=5 else '' for label in counts.index]

    # 绘制饼图
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=labels,
        autopct=lambda p: f'{p:.1f}%' if p >=5 else '',
        startangle=90,
        colors=sns.color_palette("pastel"),
        pctdistance=0.8,
        labeldistance=1.05,
        wedgeprops={'linewidth': 0.5, 'edgecolor': 'black'},
        textprops={'fontsize': 12}
    )

    # 设置百分比格式
    for autotext in autotexts:
        if autotext.get_text() == '':
            autotext.set_visible(False)
        else:
            autotext.set_color('black')
            autotext.set_fontsize(11)
            autotext.set_fontstyle('normal')

    # 添加中心注释
    centre_circle = plt.Circle((0,0), 0.7, fc='white')
    ax.add_artist(centre_circle)
    # ax = plt.subplots(figsize=(7, 5))

    # 设置图例（右下角）
    ax.legend(
        wedges,
        [f"{l} (n={c}, {p:.1f}%)" for l, c, p in zip(counts.index, counts, percentages)],
        title="Weight Groups",
        loc='lower right',
        bbox_to_anchor=(1.1, 0.1),
        frameon=False,
        fontsize=10,
        title_fontsize=12
    )
    # 设置长宽比保证圆形
    # ax.axis('equal')

    # 保存图片
    plt.savefig(output_path)
    plt.show()