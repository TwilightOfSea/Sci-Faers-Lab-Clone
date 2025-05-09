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

    # 绘制堆叠柱状图
    bottom = None
    for sex in ['F', 'M']:
        ax.bar(
            x=range(len(df.index)),
            height=df[sex],
            bottom=bottom,
            width=0.6,
            color=colors[sex],
            label=sex,
            edgecolor='white',
            linewidth=0.5
        )
        if bottom is None:
            bottom = df[sex].values
        else:
            bottom += df[sex].values

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

    # 计算最大总计值并设置 y 轴上限
    max_total = df.sum(axis=1).max()
    ax.set_ylim(0, max_total * 1.1)  # 增加 10% 的空间以容纳标签

    # 添加数值标签（总计）
    for i, total in enumerate(df.sum(axis=1)):
        ax.text(
            x=i,
            y=total + max_total * 0.02 -200,  # 标签位置稍微调整
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