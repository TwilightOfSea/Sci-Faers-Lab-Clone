import warnings

warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from venn import venn 
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

def plot(data_path, output_path):
    df = pd.read_excel(data_path)
    
    # 计算百分比
    df['percent'] = df['a'] / df['a'].sum() * 100

    # 设置画图风格
    sns.set(style="whitegrid", context="paper", font_scale=1.5)
    
    # 选择一个调色板
    palette = sns.color_palette("muted", len(df))

    # 画条形图
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = sns.barplot(
        x="percent", y="soc", 
        data=df.sort_values('percent', ascending=False),
        palette=palette,  # 使用调色板
        edgecolor='black'
    )
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=5, fontweight='bold')
    # 添加数据标签
    for i, (p, soc) in enumerate(zip(df.sort_values('percent', ascending=False)['percent'], 
                                    df.sort_values('percent', ascending=False)['soc'])):
        ax.text(p + 0.5, i, f"{p:.1f}%", va="center", fontsize=5)
    plt.xticks(fontsize=8)
    # 优化美观
    ax.set_xlabel("Proportion of adverse event reports(%)", fontsize=8)
    ax.set_ylabel("")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()
