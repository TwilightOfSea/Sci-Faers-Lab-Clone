import warnings

warnings.filterwarnings('ignore')
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

def plot(data_path, output_path):
    df = pd.read_excel(data_path)
    
    # 数据处理同上
    df_sorted = df.sort_values('a', ascending=False)
    top_8 = df_sorted.head(8)
    others_sum = df_sorted.iloc[8:]['a'].sum()

    plot_data = top_8.copy()
    if others_sum > 0:
        others_row = pd.DataFrame({'pt': ['Others'], 'a': [others_sum]})
        plot_data = pd.concat([plot_data, others_row], ignore_index=True)

    # 设置图形
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']

    # 绘制甜甜圈图（不显示标签）
    wedges, texts, autotexts = ax.pie(plot_data['a'], 
                                    colors=colors[:len(plot_data)],
                                    autopct='%1.1f%%',
                                    startangle=90,
                                    pctdistance=0.85,
                                    wedgeprops=dict(width=0.5, edgecolor='white', linewidth=1))

    # 设置百分比文字样式
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')

    # 添加中心圆形和文字
    centre_circle = plt.Circle((0,0), 0.50, fc='white', linewidth=1, edgecolor='gray')
    ax.add_artist(centre_circle)

    total_events = plot_data['a'].sum()
    ax.text(0, 0, f'Total Events\n{total_events}', ha='center', va='center', 
            fontsize=12, fontweight='bold', color='black')

    # 添加图例
    ax.legend(wedges, plot_data['pt'], title="Adverse Event Types",
            loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=10, title_fontsize=12)

    # 设置标题
    ax.set_title('Distribution of Adverse Events', 
                fontsize=16, fontweight='bold', pad=20)

    ax.axis('equal')
        
    # 调整布局
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.show()
    
