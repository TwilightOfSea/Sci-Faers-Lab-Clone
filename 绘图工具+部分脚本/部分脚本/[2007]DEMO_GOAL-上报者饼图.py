import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300
# 学术图表全局设置
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'figure.dpi': 300,
    'font.size': 14,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'font.family': 'Arial',
    'axes.spines.right': False,
    'axes.spines.top': False
})
def plot(data_path, output_path):
    df = pd.read_csv(data_path)
    data = df['occp_cod'].dropna().value_counts()

    # 过滤极小值(防止标签重叠)
    threshold = 0.02 * data.sum()
    filtered = data[data >= threshold]
    other = pd.Series([data[data < threshold].sum()], index=['Others']) if (data < threshold).any() else pd.Series()
    combined = pd.concat([filtered, other])

    # 颜色配置(Tableau调色板)
    colors = plt.cm.tab20c(np.linspace(0, 1, len(combined)))

    # 绘制饼图
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        combined,
        labels=None,
        colors=colors,
        startangle=90,
        autopct=lambda p: f'{p:.1f}%' if p >= 5 else '',
        pctdistance=0.85,
        wedgeprops={'linewidth': 0.5, 'edgecolor': 'white'}
    )

    # 添加图例
    legend = ax.legend(
        wedges,
        combined.index,
        title='Occupation Codes',
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        frameon=False,
        title_fontsize=12
    )

    # 添加比例标签
    plt.setp(autotexts, size=10, color='white', weight='bold')

    # 添加统计注释
    ax.annotate(f'Total samples: {data.sum():,}',
                xy=(0.5, -0.05),
                xycoords='axes fraction',
                ha='center',
                fontsize=10)

    plt.savefig(output_path)
    plt.show()