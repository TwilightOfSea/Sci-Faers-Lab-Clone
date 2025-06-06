import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import seaborn as sns
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
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    age_sex = pd.read_excel(data_path, sheet_name='年龄性别分布Age_Sex')
    age_sex = age_sex[age_sex['sex'].isin(['F', 'M'])]
    age_sex['age_group'] = age_sex['age_group'].replace({'0-2':'0-02', '2-10':'02-10'})

    # 创建画布
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    # 定义颜色（ColorBrewer 2.0颜色集）
    colors = ['#1f77b4', '#ff7f0e']

    # 生成分组柱状图
    age_groups = age_sex['age_group'].unique()
    bar_width = 0.35
    x_pos = range(len(age_groups))

    for i, sex in enumerate(['F', 'M']):
        counts = age_sex[age_sex['sex'] == sex]['count'].values
        ax.bar(
            [x + i*bar_width for x in x_pos],
            counts,
            width=bar_width,
            color=colors[i],
            label=sex,
            edgecolor='black',
            linewidth=0.5
        )

    # 坐标轴设置
    ax.set_xticks([x + bar_width/2 for x in x_pos])
    ax.set_xticklabels(age_groups)
    ax.set_xlabel('Age Group', fontweight='bold')
    ax.set_ylabel('Count', fontweight='bold')
    ax.set_ylim(0, max(age_sex['count'])*1.15)

    # 添加水平辅助线（网格线）
    ax.grid(True, axis='y', linestyle='--', alpha=0.7, zorder=0)
    ax.set_axisbelow(True)  # 确保网格线在柱状图下方

    # 添加图例
    ax.legend(title='Sex', frameon=True, shadow=False, edgecolor='black')

    # 移除上右边框
    sns.despine()

    # 优化布局
    plt.tight_layout()

    # 保存输出（可选格式：PDF/PNG）
    plt.savefig(output_path)
    plt.show()