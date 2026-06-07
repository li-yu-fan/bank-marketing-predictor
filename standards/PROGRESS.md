# PROGRESS · bank-marketing-predictor 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by Claude)

- **阶段**:`US-3 完成` — PR #3 CI 全绿,等待人工审核合并。
- **上一步完成**:✅ 在线预测系统完善 — prob_yes 健壮性修复 + 模型信息卡片 + AC5 提示指引,CI 全绿。
- **下一步 (TODO 第一条)**:✋ **人工 Review 并 Merge PR #3**。
- **阻塞项**:等待人工操作合并。

---

## 待办清单 (TODO,按优先级)

### 第①步 · 建仓
- [x] 用 `gh repo create` 创建 GitHub 仓库 `bank-marketing-predictor`
- [x] 添加 `.gitignore`(Python 模板 + data/*.csv + models/*.pkl)
- [x] 初始化本地 git,提交初始 commit,推送到 main

### 第②步 · 开 feature 分支
- [x] 从 main 切出 `feature/1-project-init` 分支,完成工程骨架(见 US-1)
- [x] 从 main 切出 `feature/2-data-analysis` 分支,实现数据分析页面(见 US-2)
- [x] 从 main 切出 `feature/3-online-prediction` 分支,实现模型训练与在线预测(见 US-3)

### 第③步 · 本地模块化开发
- [x] 模块 1: 项目骨架 — `app.py` + `requirements.txt` + `requirements-dev.txt` + `Dockerfile` + CI workflow
- [x] 模块 2: 数据加载 — `src/data_loader.py` + `tests/test_data_loader.py`
- [x] 模块 3: 数据分析 — `src/analysis.py` + `tests/test_analysis.py`
- [x] 模块 4: 可视化 — `src/visuals.py` + `tests/test_visuals.py`
- [x] 模块 5: 模型训练 — `src/model_trainer.py` + `tests/test_model_trainer.py`
- [x] 模块 6: 在线预测 — `src/predictor.py` + `tests/test_predictor.py`
- [x] 模块 7: Streamlit 页面整合 — `app.py` 组装分析页与预测页

### 第④步 · 本地 CI 自检
- [x] `ruff format --check .` 通过
- [x] `ruff check .` 通过
- [x] `pytest --cov --cov-fail-under=80` 通过 (56/56 passed, 100%)
- [x] 模型 AUC ≥ 0.75 验证通过 (合成数据训练)

### 第⑤步 · 触发 PR
- [x] git push 分支 → `gh pr create` 发起 PR → CI 全绿(3 次迭代修复)

### 第⑥步 · 人工审核 → 合并 → 本地验证
- [x] **✋ 等人工 Review 并 Merge** — `gh pr merge 1 --merge`,分支保留
- [x] 本地 `streamlit run app.py --server.port 8004` 验证功能正常

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-06-07 | 端口使用 8004 | Streamlit 本地默认端口,避免与其他服务冲突 |
| 2026-06-07 | 模型选 scikit-learn(逻辑回归 + 随机森林),不引入深度学习 | 数据集规模小(~45K),无需 GPU;sklearn 轻量且可解释 |
| 2026-06-07 | 可视化选 plotly 而非 matplotlib | 交互式图表(缩放/悬停)更适合数据分析场景 |
| 2026-06-07 | 数据文件不进 Git,本地放 `data/` 目录 | 数据集约 11MB,且为公开数据,不进仓库保持轻量 |

---

## 已知坑 (GOTCHAS)

- **NumPy 2.x 与 pandas 不兼容**:环境中 NumPy 2.2.6 导致 `numpy.core.multiarray failed to import`(pandas 基于 NumPy 1.x 编译)。解决:`requirements.txt` 锁定 `numpy>=1.24.0,<2.0`。

- **pandas 版本跨平台 dtype 差异**:CI runner(Linux,新版 pandas)字符串列为 `str` dtype,本地 Windows(旧版)为 `object`。测试断言 `"object"` 在 CI 失败。解决:测试改为 `assert dtype in ("object", "str")`。

- **Dockerfile COPY 顺序错误**:`RUN pip install` 在 `COPY requirements.txt` 之前导致 CI `docker build` 找不到文件。解决:将 `COPY requirements.txt .` 移到 `RUN pip install` 之前。

---

## 里程碑 (DONE)

- [x] **2026-06-07** 建仓 + 项目骨架 | `feature/1-project-init` 分支,ruff+pytest 全绿
- [x] **2026-06-07** 数据分析模块 | `get_numeric_stats` + `get_target_distribution` + `get_correlation_matrix` + `get_missing_summary`,27 tests
- [x] **2026-06-07** US-1 合并到 main | PR #1 merged (`gh pr merge 1 --merge`),分支保留,本地验证通过
- [x] **2026-06-07** US-2 合并到 main | PR #2 merged,数据分析页完善(列名对齐 + 数据类型分布 + 数据预览)
- [x] **2026-06-07** US-3 在线预测系统完善 | prob_yes 健壮性修复 + 模型信息卡片 + AC5 指引,PR #3 CI 全绿
