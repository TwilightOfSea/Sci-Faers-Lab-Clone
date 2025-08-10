import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

LR_PROPORTION = 3   # 用来改变左右柱状图显示比例

# 排序数据以便更好的可视化
def process_value(x):
    if pd.isna(x):  # 如果值为空，则返回一个非常大的数，确保排在最后
        return float('inf')
    if "360 d+" in x:  # 如果包含 "360 d+"，返回一个特定的非常大的数
        return float('inf') - 1
    # 提取 '-' 前面的内容并转为数值
    try:
        return float(x.split('-')[0].strip())
    except ValueError:  # 如果转换失败，返回一个非常大的数
        return float('inf')


def plot(data_path, output_path):
    bsc_info_event_onset_days = pd.read_excel(data_path)
    
    # 排除NaN组
    data = bsc_info_event_onset_days[bsc_info_event_onset_days['dur_group']  != 'Missing' ].copy()

    # 计算比例
    total = data['count'].sum()
    data['percentage'] = data['count'] / total * 100


    # 应用函数处理 'dur_group' 列，并按处理后的值进行正序排序
    data['sort_key'] = data['dur_group'].apply(process_value)
    data = data.sort_values(by='sort_key', ascending=True).drop(columns=['sort_key'])


    # 创建图形
    fig, ax = plt.subplots(figsize=(10,5))

    # 设置y轴位置
    y = np.arange(len(data))

    # 计算原始轴范围
    max_count = data['count'].max()
    # 判断右侧数据的最大值，用以自适应（即用右边标签的最大值的四分之一来当作左边标签的100%处）
    left_max_ax = max_count / LR_PROPORTION
    left_max_ax_percent = left_max_ax / 100

    data['percentage'] = data['percentage'] * left_max_ax_percent  # ##########
    max_percentage = data['percentage'].max()

    left_limit_original = -max_percentage * 2  # 原始左边界计算
    right_limit_original = max_count * 1.1     # 原始右边界计算
    total_width_original = right_limit_original - left_limit_original

    # 计算中轴位置（保持原始计算逻辑不变）
    new_axis_original = left_limit_original + (total_width_original / 3)
    new_axis = new_axis_original + 20  # 保持原始偏移量

    # 设置新的坐标轴范围
    # left_limit_new = new_axis - 100     # 左侧固定显示100%范围 ################
    left_limit_new = new_axis - left_max_ax
    right_limit_new = new_axis + max_count * 1.1  # 右侧自动扩展
    ax.set_xlim(left_limit_new, right_limit_new)

    # 绘制左侧比例条形图（向左延伸）
    ax.barh(y, -data['percentage'], height=0.6, left=new_axis,
            color='#3DB388', edgecolor='grey')

    # 绘制右侧频数条形图（向右延伸）
    ax.barh(y, data['count'], height=0.6, left=new_axis,
            color='#B43D68', edgecolor='grey')

    # 添加中轴线（保持位置不变）
    ax.axvline(x=new_axis, color='black', linestyle='-', linewidth=1)

    # 设置y轴标签
    ax.set_yticks(y)
    ax.set_yticklabels(data['dur_group'])

    # 生成刻度系统
    # 左侧百分比刻度（固定25%, 50%, 75%, 100%）
    percentage_values = [25, 50, 75, 100]  # 固定百分比
    percentage_ticks = [new_axis - (val / 100) * left_max_ax for val in percentage_values]  # 计算对应的刻度位置
    # 右侧计数刻度（100整倍数）
    s = str(max_count * 2)
    length = len(s)
    highest = int(s[0])
    max_integer = highest * (10 ** (length - 1))
    count_ticks = np.arange(0, right_limit_new-new_axis, max_integer / 20)
    count_positions = new_axis + count_ticks


    # 合并刻度并设置标签
    all_ticks = np.concatenate([percentage_ticks, count_positions])
    ax.set_xticks(all_ticks)
    # 修改后（去掉100 -）
    ax.set_xticklabels([
        f"{int(((tick - new_axis) / -left_max_ax) * 100)}%" if tick <= new_axis
        else f"{int(tick - new_axis)}"
        for tick in all_ticks
    ])

    # 添加数据标签
    for i, (perc, count) in enumerate(zip(data['percentage'], data['count'])):
        # 左侧百分比标签（调整位置，确保在条形图内）
        ax.text(new_axis - perc, i, f'{perc / left_max_ax_percent:.1f}%',    # ##########
                ha='right', va='center', color='black', fontsize=8)
        # 右侧计数标签（调整位置，确保在条形图内）
        ax.text(new_axis + count, i, f'{count:,}',
                ha='left', va='center', color='black', fontsize=8)

    # 添加标题和轴标签
    ax.set_title('Time to event onset (days)', size = 14, fontweight='bold')
    ax.set_xlabel('Percentage (Left) / Count (Right)', size = 12, fontweight='bold')
    # ax.set_ylabel('Duration Groups')
    plt.yticks(fontsize=8)
    plt.xticks(fontsize=8)

    ax.grid(False, which='major', axis='y')

    ax.spines['top'].set_visible(True)  # 显示上边框
    ax.spines['right'].set_visible(True)  # 显示右边框
    ax.spines['left'].set_visible(True)  # 确保左边框显示
    ax.spines['bottom'].set_visible(True)  # 确保下边框显示
    plt.savefig(output_path)
    plt.tight_layout()
    plt.show()
