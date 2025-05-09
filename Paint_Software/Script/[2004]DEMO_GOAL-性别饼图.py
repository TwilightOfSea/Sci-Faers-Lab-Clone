import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

def plot(data_path, output_path):
    df = pd.read_csv(data_path)
    # 数据预处理
    valid_sex = df[df['sex'].isin(['F', 'M'])]
    counts = valid_sex['sex'].value_counts().reindex(['F', 'M'])

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
        'figure.figsize': (6, 4)
    })

    # 创建饼图
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=counts.index,
        colors=['#4C72B0', '#DD8452'],  # 经过学术验证的色系
        autopct='%.1f%%',
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

    # 设置标题和布局
    ax.set_title('Gender Distribution', pad=20)
    plt.tight_layout()

    # 保存输出
    plt.savefig(output_path)
    plt.show()