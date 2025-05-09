import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import squarify
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import seaborn as sns
from matplotlib.colors import to_rgba

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'figure.dpi': 300,
    'font.size': 8,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'font.family': 'Arial',
    'axes.spines.right': False,
    'axes.spines.top': False
})


def plot(data_path, output_path):
    df = pd.read_excel(data_path)
    # 排除主反应并排序
    # 数据预处理
    # 生成标签
    df = df.sort_values('计数',ascending=False)
    df = df.head(10)
    labels = df.apply(lambda x: f"{x['drugname']}\n{x['role_cod']}\n{x['计数']}", axis=1)

    # 绘制树状图
    plt.figure(figsize=(12, 8))
    squarify.plot(sizes=df['计数'], label=labels, alpha=0.7)
    plt.axis('off')
    plt.title('Treemap of Drug Counts by Role Code')
    plt.show()


    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()  # 避免内存泄漏