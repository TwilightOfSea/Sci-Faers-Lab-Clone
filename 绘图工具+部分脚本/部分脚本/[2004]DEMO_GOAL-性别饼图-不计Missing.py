import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

def plot(data_path, output_path):
    df = pd.read_csv(data_path)
    # 数据预处理（包含缺失值处理）
    valid_sex = df[df['sex'].isin(['F', 'M'])]
    counts = valid_sex['sex'].value_counts().reindex(['F', 'M']).fillna(0)
    total = counts.sum()  # 计算总样本数

    # 设置学术图表格式
    plt.rcParams.update({
        'font.family': 'Times New Roman',
        'font.size': 12,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'legend.fontsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'figure.figsize': (7, 4)  # 加宽画布容纳图例
    })

    # 创建饼图
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=counts.index,
        colors=['#4C72B0', '#DD8452'],
        autopct='%.2f%%',
        startangle=90,
        textprops={'color': 'black', 'weight': 'semibold'},
        pctdistance=0.8
    )

    # 设置百分比样式
    for autotext in autotexts:
        autotext.set_size(11)
        autotext.set_color('white')

    # 添加中心注释
    centre_circle = plt.Circle((0,0), 0.6, fc='white')
    ax.add_artist(centre_circle)
    ax.text(0, 0, f'Total Samples\n{total}', 
            ha='center', va='center', 
            fontsize=10, weight='bold',
            linespacing=1.5)  # 添加总样本数

    # 添加图例（显示绝对数量）
    legend_labels = [f'{label} (n={count})' for label, count in zip(counts.index, counts)]
    ax.legend(wedges, legend_labels, 
             title='Gender', 
             loc='center left',
             bbox_to_anchor=(1, 0.5))  # 将图例放在图表右侧

    # 设置标题和布局
    ax.set_title('Gender Distribution', pad=20)
    plt.tight_layout()

    # 保存输出（包含bbox参数确保完整保存）
    plt.savefig(output_path, bbox_inches='tight')
    plt.show()
