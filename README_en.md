<div align="center">

<img src="./pic/LOGO白底-round.png" alt="SciFaersLab" width="120">

<h1>SciFaersLab</h1>

**FAERS mining, statistical analysis, and publication-ready figures in one no-code workflow.**

Built for medical and pharmacy researchers, clinicians, and research teams. Clean data, detect safety signals, run subgroup analysis, build statistical models, and produce manuscript figures through a graphical interface, with no R, Python, or SQL setup.

<p>
<img alt="Windows 10 / 11" src="https://img.shields.io/badge/Windows-10%20%2F%2011-0078D4?style=flat-square">
<a href="#core-capabilities"><img alt="No-code" src="https://img.shields.io/badge/No--code-R%20%2F%20Python%20%2F%20SQL-2F6F6B?style=flat-square"></a>
<a href="./数据库范围和方法说明.md"><img alt="FAERS 2004Q1-2026Q3" src="https://img.shields.io/badge/FAERS-2004Q1--2026Q3-E86A5A?style=flat-square"></a>
<a href="./更新日志/v1.60版本更新日志.md"><img alt="v1.60-26Q3" src="https://img.shields.io/badge/version-v1.60--26Q3-475569?style=flat-square"></a>
</p>

<p>
<a href="README.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-README.md-lightgrey?style=flat-square"></a>
<a href="README_en.md"><img alt="English" src="https://img.shields.io/badge/English-current-blue?style=flat-square"></a>
</p>

[Quick Start](#quick-start) · [Core Capabilities](#core-capabilities) · [Figures](#paper-figures) · [Research Resources](#research-resources) · [Versions and Service](#versions-and-service) · [FAQ](#faq)

</div>

<p align="center">
<img src="./pic/新版界面2.png" alt="SciFaersLab drug safety signal detection screen with drug input, algorithm selection, progress, and logs" width="900">
</p>

<p align="center"><sub>Enter a target drug, select algorithms, and let the platform handle database loading, deduplication, signal calculation, and result export.</sub></p>

## Quick Start

| What you need | Start here |
|---|---|
| Learn FAERS analysis from scratch | [Bilibili course: FAERS for beginners](https://www.bilibili.com/video/BV1uifhYdEQn/) |
| Watch the platform in action | [Bilibili: full platform walkthrough](https://www.bilibili.com/video/BV1AHeozNEXt/) |
| Browse every feature | [Feature catalog](./功能模块详解.md) |
| Follow step-by-step instructions | [Software guide](./软件操作说明.md) |
| Design a study | [Research playbook](./文章套路.md) |
| Look for a research topic | [Topic information](./选题信息.md) |
| Check data coverage and methods | [Database scope and methods](./数据库范围和方法说明.md) |

**More resources:** [Free plotting tool v3.0](./绘图工具+部分脚本/绘图工具v3.0下载链接.md) · [FAERS paper method index](https://datapod.space/faers-paper/) · [Latest release notes](./更新日志/v1.60版本更新日志.md)

> The linked product documentation and video courses are currently provided in Chinese.

## From Data to Manuscript

<table>
<tr>
<td align="center" width="25%"><b>01 Prepare data</b><br><br>Quarterly databases included<br>Automatic merge, deduplication, and standardization</td>
<td align="center" width="25%"><b>02 Detect signals</b><br><br>ROR, PRR, MGPS, and BCPNN<br>Baseline statistics included</td>
<td align="center" width="25%"><b>03 Analyze further</b><br><br>Subgroups, regression, and ML<br>TTO, Weibull, and comorbidity analysis</td>
<td align="center" width="25%"><b>04 Produce outputs</b><br><br>Statistical tables and publication figures<br>Ready to export and refine</td>
</tr>
</table>

## Core Capabilities

| Module | What you can do |
|---|---|
| **Signal detection** | Search by generic name, brand name, or compound conditions; clean and deduplicate records, map PT/SOC terms, run common signal algorithms, and export statistics and source results. |
| **Subgroup analysis** | Compare age, sex, country, reporter, comedication, or custom groups; refine an existing dataset or build focused population databases from large data. |
| **Statistics and prediction** | Baseline tables, descriptive statistics, multivariable logistic regression, machine learning, comorbidity analysis, sensitivity analysis, time-to-onset, and cumulative incidence. |
| **Publication figures** | More than 160 templates for forest plots, volcano plots, violin plots, Weibull curves, comorbidity networks, and more; export to PNG, PDF, SVG, EPS, or TIFF. |
| **Additional databases** | [JADER](./拓展模块/Jader数据库挖掘工具.md) and [CVARD](./拓展模块/CVARD加拿大数据库挖掘工具.md) plug-ins, plus [DDI drug interaction analysis](./拓展模块/DDI药物相互作用计算说明文档.md), [network pharmacology](./拓展模块/网络药理学拓展模块.md), and multi-drug signal networks. |
| **Topics and AI support** | Historical publication information for 9,000 drugs, a FAERS paper method index, and an AI assistant with platform-specific prompts. |

## Paper-Ready Plotting

Choose a script, load the result table, and run it. Preview and export the figure directly from the plotting tool, which can also be used without the full analysis system.

<p align="left">
<img src="./pic/显示-新版绘图.png" alt="SciFaersLab plotting tool with script selection, figure preview, and multiple export formats" width="900">
</p>

<p align="left"><sub>Select scripts, preview figures, and export as PNG, PDF, SVG, EPS, or TIFF in one graphical tool.</sub></p>

## Paper Figures

<table>
<tr>
<td align="left" width="50%">
<img src="./pic/四算法森林图.png" alt="Forest plot comparing ROR, PRR, BCPNN, and MGPS" width="420"><br>
<sub>Multi-algorithm forest plot</sub>
</td>
<td align="left" width="50%">
<img src="./pic/多药累积发生率&小提琴对比.png" alt="Cumulative incidence, time-to-onset, and summary table for multiple drugs" width="420"><br>
<sub>Cumulative incidence, TTO, and summary table</sub>
</td>
</tr>
<tr>
<td align="left" width="50%">
<img src="./pic/信号森林图(复杂).png" alt="SOC-level adverse event signal forest plot" width="420"><br>
<sub>SOC-level signal forest plot</sub>
</td>
<td align="left" width="50%">
<img src="./pic/JADER亚组分析.png" alt="JADER subgroup analysis tool" width="420"><br>
<sub>JADER subgroup module</sub>
</td>
</tr>
</table>

## AI and Research Support

The built-in assistant carries FAERS analysis and SciFaersLab operating prompts. It is useful for organizing methods, checking workflows, and exploring study designs. AI output is generated by a language model and should always be checked against the source data, documentation, and literature.

<p align="left">
<img src="./pic/AI聊天助手-scifaerslab.png" alt="SciFaersLab AI chat assistant discussing subgroup analysis" width="820">
</p>

## Research Resources

Topic discovery, study structure, and hands-on analysis use a consistent set of terms, so you spend less time reconciling tutorials, papers, and software screens.

<table>
<tr>
<td align="left" width="50%">
<img src="./pic/药物发表情况.png" alt="Historical publication information for 9,000 drugs and related FAERS articles" width="420"><br>
<sub>Drug publication history for topic screening</sub>
</td>
<td align="left" width="50%">
<img src="./pic/论文方法索引库.png" alt="FAERS paper method index website" width="420"><br>
<sub>Filter papers by database, analysis type, and method</sub>
</td>
</tr>
</table>

<p align="left">
<img src="./pic/基本套路流程.png" alt="Basic FAERS research workflow from objective and data source to signal analysis and conclusions" width="1200">
</p>

<p align="left"><sub>Organize a study around the objective, data source, signal detection, subgroup analysis, time-to-onset, and conclusions.</sub></p>

See [Research playbook](./文章套路.md) for study frameworks and figure combinations, and [Database scope and methods](./数据库范围和方法说明.md) for coverage, cleaning logic, and method-writing examples.

## Free and Full Versions

| Edition | What is included |
|:--|:--|
| **Free** | Plotting tool, selected plotting scripts, sample data, and tutorials |
| **Full** | Complete analysis system, quarterly database package, full plotting scripts, extension modules, and topic updates |

The free plotting resources follow the repository [LICENSE](./LICENSE). The paid analysis system is licensed per device; the exact feature and update scope is confirmed at purchase.

## Versions and Service

Current version: **v1.60-26Q3** (released 2026-11-01). The database covers **2004Q1-2026Q3, 91 quarters**.

| Service period | Price | Included |
|:--|--:|:--|
| Six months | CNY 800 | Full analysis features, complete scripts, database, and updates during the service period |
| One year | CNY 1,200 | The same scope for one year |
| Perpetual | Quoted per request | Confirmed by feature scope, devices, and usage requirements |

Updated database packages are delivered by email, so there is no need to download each quarterly source file manually. JADER and CVARD can also use official source data imported through the provided guides.

<details>
<summary><b>System requirements and delivery</b></summary>

| Item | Requirement |
|---|---|
| Operating system | Windows 10 / 11 |
| Memory | 8 GB or more recommended |
| Storage | At least 5 GB available |
| Data delivery | Integrated package sent by email |
| Licensing | Analysis modules are bound to the device; contact us before changing devices |
| Support | Software usage guidance and troubleshooting |

</details>

## FAQ

<details>
<summary><b>Can I use it without programming experience?</b></summary>

Yes. Data import, signal detection, statistical analysis, and plotting are performed through graphical interfaces without writing code.

</details>

<details>
<summary><b>What is the difference between the free and full versions?</b></summary>

The free version provides the plotting tool, selected scripts, and learning materials. The full version adds the analysis system, complete scripts, quarterly database packages, and ongoing updates.

</details>

<details>
<summary><b>How often is the database updated?</b></summary>

Updates follow the official FDA data releases and are sent by email as new packages. The JADER and CVARD modules are updated with the product, and official source data can also be imported through the guides.

</details>

<details>
<summary><b>Is paper writing or ghostwriting included?</b></summary>

Support covers software usage and troubleshooting, not paper ghostwriting. For study design guidance, see the [Research playbook](./文章套路.md).

</details>

> **Data note:** Spontaneous reporting databases such as FAERS are suitable for detecting risk signals and generating research hypotheses. They cannot directly estimate adverse-event incidence or prove causality on their own. Conclusions should be interpreted together with the study design, clinical context, and other data sources.

## Get Started

1. Watch the [full platform walkthrough](https://www.bilibili.com/video/BV1AHeozNEXt/) to see whether the workflow fits your research.
2. Try the [free plotting tool v3.0](./绘图工具+部分脚本/绘图工具v3.0下载链接.md), or read the [software guide](./软件操作说明.md).
3. For the full analysis system, add us on WeChat and mention SciFaersLab.

<p align="left">
<img src="./pic/wechat.jpg" alt="SciFaersLab WeChat contact" width="240">
</p>

---

<div align="center">

China access: [Gitee](https://gitee.com/Twilight-of-sea/sci-faers-lab) · Mirror: [GitHub](https://github.com/TwilightOfSea/Sci-Faers-Lab-Clone) · Video: [Full platform walkthrough](https://www.bilibili.com/video/BV1AHeozNEXt/)

[简体中文 README](README.md) · Last updated: 2026-11-23

</div>
