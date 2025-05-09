import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

def plot(data_path, output_path):
    sheets = pd.read_excel(data_path, sheet_name=None)
    
    # 获取所有'pt'列的交集
    common_pts = None
    for name, df in sheets.items():
        pts = set(df['pt'].unique())  # 获取当前表的唯一pt值
        if common_pts is None:
            common_pts = pts
        else:
            common_pts &= pts  # 取交集

    # 确定第一个工作表的顺序
    first_sheet_name = list(sheets.keys())[0]
    first_sheet_df = sheets[first_sheet_name]
    first_sheet_pt_order = first_sheet_df[first_sheet_df['pt'].isin(common_pts)]['pt']

    # 创建基础DataFrame（按pt排序）
    merged_df = pd.DataFrame({'pt': sorted(common_pts)})

    # 为每个工作表添加对应的ror列
    for sheet_name, df in sheets.items():
        # 过滤数据并去重（保留第一个出现的pt）
        filtered = df[df['pt'].isin(common_pts)] \
            .drop_duplicates('pt') \
            [['pt', 'ror']] \
            .rename(columns={'ror': sheet_name})
        
        # 合并到主表
        merged_df = pd.merge(merged_df, filtered, on='pt', how='left')

    # 根据第一个工作表的pt顺序排序
    merged_df['pt'] = pd.Categorical(merged_df['pt'], categories=first_sheet_pt_order, ordered=True)
    merged_df = merged_df.sort_values('pt')
    
    merged_df = merged_df.head(20)
    for col in merged_df.columns:
        if col != 'pt':
            # 使用 np.where 来应用条件逻辑
            merged_df[col] = np.where(merged_df[col] > 0, np.log2(merged_df[col]), 0)
    
    # 动态获取药物列名
    drug_columns = merged_df.columns[merged_df.columns != 'pt']

    # 数据重塑为长格式
    df_long = merged_df.melt(
        id_vars='pt',
        value_vars=drug_columns,
        var_name='Drug',
        value_name='Value'
    )

    # 设置可视化样式
    sns.set_theme(style="whitegrid", font_scale=0.9)
    plt.figure(figsize=(8, 6), dpi=300)

    # 创建气泡矩阵图
    scatter = sns.scatterplot(
        data=df_long,
        x='Drug',
        y='pt',
        size='Value',
        hue='Value',
        sizes=(30, 300),  # 调整气泡大小范围
        palette='viridis',  # 使用科学期刊推荐的色系
        alpha=0.8,
        linewidth=0.5,
        edgecolor='w'
    )

    # 美化图形元素
    plt.title("Association Matrix of Adverse Events and Drug Responses", fontsize=12, pad=20)
    plt.xlabel("Drug Treatments", fontsize=10, labelpad=10)
    plt.ylabel("Preferred Terms (Adverse Events)", fontsize=10, labelpad=10)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    plt.yticks(fontsize=9)

    # 调整图例
    handles, labels = scatter.get_legend_handles_labels()
    plt.legend(
        handles[1:5],
        labels[1:5],
        title="Log2(ROR Value)",
        bbox_to_anchor=(1.05, 1),
        frameon=True,
        title_fontsize=7,
        fontsize=6,
        handleheight=3  # 增加行间距
    )
    plt.yticks(fontsize=8)
    # 添加网格线增强可读性
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    # 调整布局并保存
    plt.tight_layout()
    plt.show()
    plt.savefig(output_path)
    
