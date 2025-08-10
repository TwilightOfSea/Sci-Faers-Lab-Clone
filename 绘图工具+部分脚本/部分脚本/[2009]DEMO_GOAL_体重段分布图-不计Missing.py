import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'figure.dpi': 300,
    'font.size': 11,  # 略微增大基础字号
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'font.family': 'Arial',
    'axes.spines.right': False,
    'axes.spines.top': False,
    'axes.linewidth': 1.2,  # 增强坐标轴可见性
    'xtick.major.size': 4,  # 调整刻度标记尺寸
    'xtick.major.width': 1.2,
    'ytick.major.size': 4,
    'ytick.major.width': 1.2,
})

def plot(data_path, output_path):
    data = pd.read_csv(data_path)
    
    # 数据预处理
    filtered_data = data['wt_group'].dropna()
    filtered_data = filtered_data[filtered_data != 'Missing']
    filtered_data = filtered_data[filtered_data != '--']

    # 计算频数和百分比
    counts = filtered_data.value_counts().sort_index()
    total = counts.sum()
    percentages = 100 * counts / total

    # 学术风格调色板（低饱和度蓝灰色系）
    colors = [
        '#4F6DA8', '#6B8CAB', '#88A9C3',  # 主色系
        '#A5C6DD', '#C2E3F6', '#5A7B9E',  # 辅助色
        '#3E5F8A', '#2D4666'
    ]

    # 标签格式优化：使用千位分隔符，仅显示≥3%的标签
    labels = [
        f"{label} {count:,} ({pct:.1f}%)" if pct >= 3 else ''
        for label, count, pct in zip(counts.index, counts, percentages)
    ]

    fig, ax = plt.subplots(figsize=(8, 8))

    # 增强文本对比度设置
    text_kwargs = {
        'fontsize': 12,
        'color': '#333333',  # 深灰色提升可读性
        'weight': 'normal'  # 取消加粗显示
    }

    wedges, texts, autotexts = ax.pie(
        counts,
        labels=labels,
        colors=colors[:len(counts)],  # 动态匹配颜色数量
        autopct=lambda p: f'{p:.1f}%' if p >= 5 else '',
        startangle=90,
        textprops=text_kwargs,
        wedgeprops={
            'edgecolor': '#666666',  # 中性灰分隔线
            'linewidth': 1.0,        # 适当减细线宽
            'linestyle': '-'         # 明确线型
        },
        pctdistance=0.8  # 将百分比向内移动
    )

    # 优化标签显示效果
    for text in texts:
        text.set_alpha(0.9)  # 轻微透明处理
    
    # 统一百分比文本样式
    for autotext in autotexts:
        autotext.set_color('#333333')
        autotext.set_alpha(0.9)

    # 添加副标题说明
    plt.suptitle('Distribution by Weight Groups', 
                y=0.93, fontsize=13, color='#444444')
    
    # 添加数据来源说明
    ax.text(0.5, -0.1, f"Total N = {total:,}\nData source: Survey Dataset",
           transform=ax.transAxes, ha='center', fontsize=10,
           color='#666666')

    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()  # 避免内存泄漏
