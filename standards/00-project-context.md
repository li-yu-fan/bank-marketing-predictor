# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的"身份档案"。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`bank-marketing-predictor`
- **一句话目标**:基于银行电话营销数据,提供交互式数据分析与在线认购预测的 Web 应用。
- **使用者/受益者**:银行营销分析师、数据科学家,用于探索营销数据规律并快速预测客户是否会认购定期存款。
- **核心功能**:
  - 数据分析交互页面:上传/加载营销数据,展示统计摘要、可视化图表、特征分布与相关性。
  - 在线预测系统:基于离线训练的分类模型,用户输入客户特征后返回「是否会认购」的预测结果与置信度。
- **输入/数据**:Bank Marketing 数据集(UCI 公开数据集,约 45K 条记录,20 个特征);数据文件不进 Git,通过 `.gitignore` 排除。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 课程统一版本,生态成熟 |
| Web/UI 框架 | Streamlit | 纯 Python 即可构建数据仪表盘与交互表单,免写前端 |
| 数据处理 | pandas, numpy | 表格数据标配 |
| 可视化 | plotly | 交互式图表(缩放/悬停),Streamlit 原生支持 |
| 机器学习 | scikit-learn | 经典分类模型(逻辑回归/随机森林),轻量无需 GPU |
| 测试 | pytest + pytest-cov | 课程统一,覆盖率门禁 |
| 格式/静态检查 | ruff | 快,替代 flake8+isort+black |
| 打包 | Docker | CI 构建检查,本地运行用 `streamlit run` |
| CI | GitHub Actions | PR 触发自动检查,云端 runner 自带 Docker |

## 3. 目录地图

```text
bank-marketing-predictor/
├── standards/                 # AI 项目记忆与通用规范
├── app.py                     # Streamlit 应用入口
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # 数据加载与缓存
│   ├── analysis.py            # 数据分析与统计计算
│   ├── visuals.py             # 可视化图表生成
│   ├── model_trainer.py       # 离线模型训练与保存
│   └── predictor.py           # 在线预测推理
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_analysis.py
│   ├── test_visuals.py
│   ├── test_model_trainer.py
│   └── test_predictor.py
├── models/                    # 训练产物(不进 Git)
├── .github/workflows/
│   └── ci.yml
├── requirements.txt           # 生产运行依赖
├── requirements-dev.txt       # 本地/CI 检查依赖
├── Dockerfile
├── .gitignore
└── README.md
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest --cov --cov-fail-under=80` |
| 覆盖率 | ≥ 80% |
| 构建 | `docker build` 成功(CI 执行,本地不强制) |
| 业务/模型指标 | 模型 AUC ≥ 0.75,准确率 ≥ 0.80 |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 数据文件(`.csv`)、训练产物(`models/*.pkl`)不进 Git,通过 `.gitignore` 排除。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 本地运行端口 8004。

## 6. CI 占位符取值

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `bank-marketing-predictor` | 应用名 |
| `<PORT>` | `8004` | 本地服务端口 |
| `<PYVER>` | `3.11` | Python 版本 |
