import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

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
    # 数据预处理
    # 增强型数据清洗
    df = df.dropna(subset=['reporter_country'])  # 移除缺失值
    df['reporter_country'] = df['reporter_country'].astype(str).str.strip().str.upper()  # 标准化格式
    df = df[df['reporter_country'].str.len() == 2]  # 筛选长度为2的代码
    country_counts = df['reporter_country'].value_counts().head(8)

    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    # plt.style.use('seaborn-whitegrid')  # 设置科研风格

    # 绘制条形图
    bar_plot = ax.bar(
        country_counts.index,
        country_counts.values,
        color='#2b7bba',  # 专业蓝色调
        edgecolor='black',
        linewidth=0.8,
        width=0.7
    )

    # 设置坐标轴
    ax.set_xlabel('Country Code', fontsize=14, fontweight='bold', labelpad=12)
    ax.set_ylabel('Count', fontsize=14, fontweight='bold', labelpad=12)
    ax.tick_params(axis='both', which='major', labelsize=12, direction='out')

    # 添加数值标签
    ax.bar_label(
        bar_plot,
        labels=country_counts.values,
        padding=3,
        fontsize=11,
        fmt='%d'
    )

    # 优化布局
    plt.ylim(0, country_counts.max() * 1.15)  # 自动调整y轴范围
    plt.tight_layout(pad=2.0)

    # 保存图像（矢量格式适合出版）
    plt.savefig(output_path)
    plt.show()