import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['figure.dpi'] = 300

def plot(data_path, output_path):
    df = pd.read_csv(data_path)
    # 检查 'dur_days' 列是否存在
    if 'dur_days' in df.columns:
        # 移除空值
        clean_data = df['dur_days'].dropna()
        
        # 拟合 Weibull 分布
        shape, loc, scale = stats.weibull_min.fit(clean_data, floc=0)
        
        # 计算中位数
        median = scale * (np.log(2)) ** (1/shape)
        
        # 使用 bootstrap 方法计算置信区间
        n_iterations = 100
        bootstrap_shape = np.zeros(n_iterations)
        bootstrap_scale = np.zeros(n_iterations)
        bootstrap_median = np.zeros(n_iterations)
        
        for i in range(n_iterations):
            sample = np.random.choice(clean_data, size=len(clean_data), replace=True)
            params = stats.weibull_min.fit(sample, floc=0)
            bootstrap_shape[i] = params[0]
            bootstrap_scale[i] = params[2]
            bootstrap_median[i] = params[2] * (np.log(2)) ** (1/params[0])
        
        # 计算 95% 置信区间
        shape_ci = np.percentile(bootstrap_shape, [2.5, 97.5])
        scale_ci = np.percentile(bootstrap_scale, [2.5, 97.5])
        median_ci = np.percentile(bootstrap_median, [2.5, 97.5])
        
        # 创建结果表格
        results = pd.DataFrame({
            'Parameter': ['Median', 'Scale parameter: a', 'Shape parameter: β'],
            'Mean': [round(median, 2), round(scale, 2), round(shape, 2)],
            '95% CI': [
                f"({round(median_ci[0], 2)}, {round(median_ci[1], 2)})",
                f"({round(scale_ci[0], 2)}, {round(scale_ci[1], 2)})",
                f"({round(shape_ci[0], 2)}, {round(shape_ci[1], 2)})"
            ]
        })
        
        # 绘制数据分布和 Weibull 拟合曲线
        fig = plt.figure(figsize=(14, 10))  # 增加宽度以容纳表格
        ax = fig.add_subplot(111)
        
        # 绘制直方图和拟合曲线
        ax.hist(clean_data, bins=30, density=True, alpha=0.6, color='g', label='Observed Data')
        
        x = np.linspace(0, max(clean_data), 100)
        ax.plot(x, stats.weibull_min.pdf(x, shape, loc, scale),
                'r-', lw=2, label=f'Weibull Fit (β={shape:.2f}, a={scale:.2f})')
        
        ax.set_xlabel('Time-to-onset (days)')
        ax.set_ylabel('Density')
        ax.set_title('Weibull Distribution Fit for Time-to-onset Data')
        ax.legend()
        
        # 将表格添加到图表右侧
        table_text = "weibull distribution result argument:\n\n"
        table_text += results.to_string(index=False)
        
        # 在图表右侧添加文本框
        plt.text(1.05, 0.5, table_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='center', bbox=dict(facecolor='white', alpha=0.8))
        
        # 调整布局以避免裁剪
        plt.tight_layout()
        
        plt.savefig(output_path, bbox_inches='tight')
        plt.show()
    else:
        print("错误：数据框中不存在'dur_days'列")
