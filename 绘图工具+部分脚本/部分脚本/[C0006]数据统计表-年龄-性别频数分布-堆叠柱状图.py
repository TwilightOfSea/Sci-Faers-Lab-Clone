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
    # 读取数据（假设数据为CSV或Excel格式，根据实际文件类型调整）
    age_sex = pd.read_excel(data_path, sheet_name='年龄性别分布Age_Sex')
    
    # 过滤掉 'Missing' 值
    age_sex = age_sex[age_sex['sex'].isin(['F', 'M'])]
    age_sex['age_group'] = age_sex['age_group'].replace({'0-2':'0-02', '2-10':'02-10'})

    # 汇总数据，按 age_group 和 sex 分组
    df = age_sex.groupby(['age_group', 'sex'])['count'].sum().unstack()

    # 设置绘图风格
    sns.set_style("whitegrid", {'grid.linestyle': '--', 'axes.edgecolor': '0.4'})
    plt.rcParams['font.family'] = 'Arial'  # 学术论文常用字体
    plt.rcParams['pdf.fonttype'] = 42      # 避免文字保存为矢量图时的字体问题

    # 创建画布
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    # 定义颜色（色盲友好且符合性别惯例）
    colors = {'F': '#4C72B0', 'M': '#DD8452'}

    # 计算每个堆叠柱的顶部高度
    stack_tops = []
    bottom = None
    
    # 绘制堆叠柱状图并记录每个柱子的顶部高度
    for sex in ['F', 'M']:
        heights = df[sex].values
        ax.bar(
            x=range(len(df.index)),
            height=heights,
            bottom=bottom,
            width=0.6,
            color=colors[sex],
            label=sex,
            edgecolor='white',
            linewidth=0.5
        )
        if bottom is None:
            bottom = heights.copy()
            stack_tops = heights.copy()
        else:
            bottom += heights
            stack_tops = bottom.copy()  # 更新为当前堆叠的总高度

    # 坐标轴设置
    ax.set_xticks(range(len(df.index)))
    ax.set_xticklabels(df.index, fontsize=10)
    ax.set_xlabel('Age Group', fontsize=11, labelpad=10)
    ax.set_ylabel('Count', fontsize=11, labelpad=10)
    ax.tick_params(axis='y', which='major', labelsize=9)

    # 添加图例
    ax.legend(
        title='Sex',
        frameon=True,
        edgecolor='0.8',
        title_fontsize=10,
        fontsize=9,
        loc='upper right'
    )

    # 计算y轴上限，确保比最高柱子高20%
    max_stack_top = max(stack_tops)
    y_upper_limit = max_stack_top * 1.2  # 比最高柱子高20%
    ax.set_ylim(0, y_upper_limit)

    # 计算标签位置（在最高柱子顶部之上一个合适的距离）
    label_offset = max_stack_top * 0.02  # 标签距离柱顶2%的距离

    # 添加数值标签（总计）
    for i, stack_top in enumerate(stack_tops):
        total = df.sum(axis=1).iloc[i]
        ax.text(
            x=i,
            y=stack_top + label_offset,
            s=str(int(total)),
            ha='center',
            va='bottom',
            fontsize=8,
            color='0.3'
        )

    # 调整布局
    plt.tight_layout()
    plt.savefig(output_path)
    plt.show()
