# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 课程任务 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI · 状态: Done

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试与 CI,
以便 后续每次开发都能自动检查代码质量。

验收标准:
- AC1: 从 `main` 开 feature 分支完成初始化,不直接 push main。
- AC2: PR 触发 CI,至少包含 ruff format、ruff check、pytest(覆盖率≥80%)、docker build。
- AC3: CI 全绿后合并 main。
- AC4: 本地 `streamlit run app.py --server.port 8004` 可正常启动,浏览器访问页面正常。
- AC5: 完成后更新 `standards/PROGRESS.md`。

技术备注:
- 本地不强制 docker build,交给 CI runner 执行。
- 无需配置 GitHub Secrets,无远程部署。

---

### US-2 数据分析交互页面 · 状态: Done

作为 **银行营销分析师**,
我想要 在浏览器中上传并探索营销数据,
以便 快速了解数据分布、特征关系与潜在规律,为建模做准备。

验收标准:
- AC1: Given 应用已启动,When 用户访问 `http://localhost:8004`,Then 页面显示数据分析仪表盘标题与数据上传组件。
- AC2: Given 用户上传了有效的 CSV 文件,When 文件加载完成,Then 展示数据总览(行数、列数、缺失值统计、数据类型分布)。
- AC3: Given 数据已加载,When 用户选择分析维度,Then 展示描述性统计(均值、中位数、标准差、分位数)和至少 3 种可视化图表(如目标变量分布、数值特征直方图、相关性热力图)。
- AC4: Given 页面展示图表,When 用户切换筛选条件(如按月份/职业过滤),Then 图表与统计实时更新。

技术备注:
- 数据文件 `bank-additional-full.csv` 不进 Git,本地放在 `data/` 目录。
- 使用 Streamlit caching(`@st.cache_data`)避免每次交互重新加载数据。
- 图表用 plotly 实现可交互缩放、悬停提示。
- 数据集列名使用下划线命名:`emp_var_rate`, `cons_price_index`, `cons_conf_index`, `lending_rate3m`;目标列 `subscribe`。

---

### US-3 离线训练 + 在线预测系统 · 状态: Done

作为 **银行营销分析师**,
我想要 基于历史数据训练分类模型,并在页面中输入新客户特征后得到认购预测,
以便 对新的营销线索进行快速筛选与决策。

验收标准:
- AC1: Given 数据已加载,When 用户触发「训练模型」,Then 自动完成数据预处理(编码、归一化、划分)、训练至少 2 种分类模型、输出对比指标(AUC、准确率、F1),并保存最佳模型。
- AC2: Given 模型已训练,When 用户进入「在线预测」页面,Then 显示与训练特征对应的输入表单(数值输入框、下拉选择框)。
- AC3: Given 用户填写了所有必填特征,When 点击「预测」,Then 显示预测结果(会认购/不会认购)及预测概率/置信度。
- AC4: Given 用户输入不合法(类型错误、必填缺失),When 点击「预测」,Then 显示具体校验错误提示,不崩溃。
- AC5: Given 模型文件不存在,When 用户进入预测页面,Then 提示「请先训练模型」并提供跳转。

技术备注:
- 模型保存为 `models/best_model.pkl`,不进 Git。
- 默认训练随机森林与逻辑回归,选 AUC 更高的作为最佳模型。
- 输入表单字段与数据集特征列一一对应:age, job, marital, education, default, housing, loan, contact, month, day_of_week, duration, campaign, pdays, previous, poutcome, emp.var.rate, cons.price.idx, cons.conf.idx, euribor3m, nr.employed。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git;数据文件与模型文件不进 Git。
- **可维护**:一需求一小 PR,PR 尽量小于 400 行;每个模块对应源码文件与测试文件。
- **可测试**:核心逻辑必须有单元测试,覆盖率 ≥ 80%;模型训练逻辑需覆盖数据预处理与指标计算。
- **本地可运行**:`streamlit run app.py --server.port 8004` 一键启动,无需额外配置。
- **可用性**:Streamlit 页面响应时间 < 3 秒(不含模型训练);预测接口输入校验即时反馈。
