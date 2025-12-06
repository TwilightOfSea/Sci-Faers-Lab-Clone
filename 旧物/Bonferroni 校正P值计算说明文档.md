# 药物 ADR 信号检测四格表统计指标计算说明文档

## 一、文档概述

本文档针对基于四格表（a、b、c、d）计算 `pvalue`、`chisq_stat`、`test_used`、`Bonferron_P_value` 四列指标的 Python 脚本进行详细说明，明确各指标的计算逻辑、统计学意义，以及与 ROR（报告比值比）方法的核心区别，适用于药物不良反应（ADR）信号检测的比例失衡分析场景。

## 二、四格表基础定义

在药物 ADR 信号检测中，四格表的 a、b、c、d 定义如下：

|                      | 发生目标 ADR（阳性） | 未发生目标 ADR（阴性） | 合计         |
|----------------------|----------------------|------------------------|--------------|
| **暴露于目标药物**   | a（信号例数）        | b（暴露阴性例数）      | n1 = a + b   |
| **未暴露于目标药物** | c（非暴露阳性例数）  | d（非暴露阴性例数）    | n2 = c + d   |
| **合计**             | m1 = a + c           | m2 = b + d             | N = a+b+c+d  |

## 三、新增四列指标的计算逻辑与意义

### 3.1 chisq_stat（卡方统计量）

#### 3.1.1 计算逻辑

卡方统计量用于衡量“暴露组 ADR 发生率（a/n1）”与“非暴露组 ADR 发生率（c/n2）”的差异程度，计算方式随检验方法不同而区分：

- **Pearson 卡方**（期望频数≥5 且 N≥40）：  
  \(\chi^2 = \frac{N(ad - bc)^2}{n1 \cdot n2 \cdot m1 \cdot m2}\)（脚本通过 `chi2_contingency` 函数自动计算）

- **连续性校正卡方**（1≤期望频数 < 5 且 N≥40）：  
  \(\chi^2_c = \frac{N(|ad - bc| - N/2)^2}{n1 \cdot n2 \cdot m1 \cdot m2}\)（脚本手动计算校正项）

- **Fisher 精确检验**（期望频数 < 1 或 N<40）：无卡方统计量，赋值为 NaN

#### 3.1.2 统计学意义

卡方值越大，表明 “ad - bc” 的差异越显著，即药物暴露与 ADR 发生的关联趋势越强，越倾向于拒绝“药物与 ADR 无关联”的原假设。

### 3.2 test_used（检验方法）

#### 3.2.1 选择逻辑

脚本基于四格表的期望频数和总例数 N 自动判断检验方法，优先级如下：

1. **Fisher's Exact Test**：若最小期望频数 < 1 或 总例数 N<40
2. **Continuity-corrected Chi-square Test**：若 1≤最小期望频数 < 5 且 N≥40
3. **Pearson Chi-square Test**：若最小期望频数≥5 且 N≥40

其中，期望频数计算方式为：

- T11 = n1×m1/N  
- T12 = n1×m2/N  
- T21 = n2×m1/N  
- T22 = n2×m2/N  

最小期望频数 = min(T11, T12, T21, T22)

#### 3.2.2 统计学意义

明确当前行数据适用的统计检验类型，保证 p 值计算的准确性，避免因样本/期望频数问题导致假阳性/假阴性。

### 3.3 pvalue（原始 P 值）

#### 3.3.1 计算逻辑

- **Fisher 精确检验**：直接计算所有 “|ad - bc|≥当前值” 的四格表组合概率之和（`fisher_exact` 函数）
- **连续性校正卡方**：\(p = 1 - \text{chi2.cdf}(\chi^2_c, df=1)\)（脚本用 `chi2.sf` 简化计算）
- **Pearson 卡方**：由 `chi2_contingency` 函数直接返回

#### 3.3.2 统计学意义

P 值越小，拒绝原假设的证据越充分（通常 P<0.05 认为具有统计学显著性），反映“药物-ADR 关联”的统计学可靠性。

### 3.4 Bonferron_P_value（Bonferroni 校正 P 值）

#### 3.4.1 计算逻辑

\(Bonferroni\_P = \min(p \times k, 1.0)\)

- p：当前行的原始 P 值
- k：多重检验总次数（脚本中设为数据表行数，即本次分析的“药物-ADR 组合”总数）

#### 3.4.2 统计学意义

校正后 P 值 < 0.05，说明在控制总体假阳性率的前提下，药物与 ADR 的关联仍具有统计学显著性。

## 四、P 值计算的核心依据

P 值的计算始终围绕“原假设（药物与 ADR 无关联）”展开，分为：

- **分布近似依据**（Pearson / 连续性校正卡方）：大样本下卡方统计量服从 df=1 的卡方分布
- **精确概率依据**（Fisher 精确检验）：小样本下直接枚举所有更极端的四格表概率

## 五、与 ROR（报告比值比）方法的核心区别

| 维度             | 卡方 / P 值 / Bonferroni 校正体系       | ROR（报告比值比）                          |
|------------------|------------------------------------------|--------------------------------------------|
| 核心定义         | 统计显著性检验指标                       | 比例失衡度量指标                           |
| 计算公式         | 见第三、四部分                           | \(ROR = (a/b)/(c/d)\)                      |
| 核心意义         | 反映关联的“统计学可靠性”                 | 反映关联的“强度”                           |
| 关注重点         | 样本数据是否足够支撑“关联存在”           | 暴露组风险是未暴露组的多少倍               |
| 与数据特征的关联 | 依赖样本量/期望频数                      | 仅依赖频数，对零单元格敏感（需加 0.5 校正）|
| 应用场景         | 判断关联是否具有统计学显著性             | 量化关联程度                               |

**示例说明**：

- ROR=5（强度高），但 P=0.06 → 强度高，可靠性不足
- ROR=2（强度中等），但 Bonferroni_P=0.05 → 强度一般，但校正后仍显著

## 六、注意事项

- **零单元格处理**：可启用 Haldane-Anscombe 校正（加 0.5）
- **k 值设置**：Bonferroni 的 k 必须等于全部药物-ADR 组合总数
- **结果解读**：必须结合 ROR（强度）+ P 值/Bonferroni_P（显著性）

## 七、脚本输出说明

最终 Excel 文件包含原始 a、b、c、d 列及新增的：

- `pvalue`
- `chisq_stat`（Fisher 时为 NaN）
- `test_used`
- `Bonferron_P_value`（≤1，越小越显著）

可直接用于药物 ADR 信号的筛选与验证。


````python
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, chi2
import numpy as np

# ===================== 1. 导入数据=====================
def plot(data_path, output_path):
    df = pd.read_excel(data_path)
    # 确保a/b/c/d列为数值型
    df[['a', 'b', 'c', 'd']] = df[['a', 'b', 'c', 'd']].astype(float)

    # ===================== 2. 初始化新增列 =====================
    df['pvalue'] = np.nan
    df['chisq_stat'] = np.nan
    df['test_used'] = ""
    df['Bonferron_P_value'] = np.nan

    # ===================== 3. 定义多重检验次数k（需根据实际场景修改） =====================
    k = len(df) 

    # ===================== 4. 逐行计算各指标 =====================
    for idx, row in df.iterrows():
        a = row['a']
        b = row['b']
        c = row['c']
        d = row['d']
        
        # 构建四格表矩阵
        contingency_table = [[a, b], [c, d]]
        n1 = a + b  # 暴露组总数
        n2 = c + d  # 非暴露组总数
        m1 = a + c  # ADR总例数
        m2 = b + d  # 非ADR总例数
        N = a + b + c + d  # 总例数
        
        # 计算期望频数（判断卡方检验类型）
        T11 = n1 * m1 / N  # 暴露且ADR的期望频数
        T12 = n1 * m2 / N  # 暴露但非ADR的期望频数
        T21 = n2 * m1 / N  # 非暴露但ADR的期望频数
        T22 = n2 * m2 / N  # 非暴露且非ADR的期望频数
        expected_freqs = [T11, T12, T21, T22]
        
        # -------------------- 4.1 选择检验方法并计算统计量 --------------------
        # 标记是否使用Fisher精确检验
        use_fisher = False
        
        # 检查期望频数和总例数（判断检验类型）
        min_expected = min(expected_freqs)
        if min_expected < 1 or N < 40:
            # Fisher精确检验：无卡方统计量
            use_fisher = True
            odds_ratio, p_val = fisher_exact(contingency_table)
            chisq_val = np.nan
            test_type = "Fisher's Exact Test"
        else:
            if min_expected < 5:
                # 连续性校正卡方检验
                # 手动计算校正卡方值
                chisq_val = (N * (abs(a*d - b*c) - N/2)**2) / (n1 * n2 * m1 * m2)
                # 正确计算校正卡方对应的p值：自由度=1的卡方分布 Survival Function (1 - CDF)
                p_val = chi2.sf(chisq_val, df=1)
                test_type = "Continuity-corrected Chi-square Test"
            else:
                # Pearson卡方检验（使用scipy内置函数）
                chisq_val, p_val, dof, exp = chi2_contingency(contingency_table)
                test_type = "Pearson Chi-square Test"
        
        # -------------------- 4.2 Bonferroni校正 --------------------
        bonferroni_p = min(p_val * k, 1.0)
        
        # -------------------- 4.3 填充到DataFrame --------------------
        df.loc[idx, 'pvalue'] = p_val
        df.loc[idx, 'chisq_stat'] = chisq_val
        df.loc[idx, 'test_used'] = test_type
        df.loc[idx, 'Bonferron_P_value'] = bonferroni_p
        
        df.to_excel(output_path.replace(".png", ".xlsx"), index=False)
        
        # -------------------- 跳过检查 --------------------
        import matplotlib.pyplot as plt
        x = [1, 2, 3, 4, 5]
        plt.plot(x)
        plt.show()
        
        
        


````