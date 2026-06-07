# PROGRESS · bank-marketing-predictor 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-06-07 · by Claude)

- **阶段**:`初始化` — 第 ① 步完成,等待确认进入第 ② 步
- **上一步完成**:✅ 建仓 `https://github.com/li-yu-fan/bank-marketing-predictor`,SSH 推送 main。
- **下一步 (TODO 第一条)**:确认后进入第 ② 步,从 main 切 `feature/1-project-init`。
- **阻塞项**:无(无需 CD,跳过 Secrets 配置)。

---

## 待办清单 (TODO,按优先级)

### 第①步 · 建仓
- [ ] 用 `gh repo create` 创建 GitHub 仓库 `bank-marketing-predictor`
- [ ] 添加 `.gitignore`(Python 模板 + data/*.csv + models/*.pkl)
- [ ] 初始化本地 git,提交初始 commit,推送到 main

### 第②步 · 开 feature 分支
- [ ] 从 main 切出 `feature/1-project-init` 分支,完成工程骨架(见 US-1)
- [ ] 从 main 切出 `feature/2-data-analysis` 分支,实现数据分析页面(见 US-2)
- [ ] 从 main 切出 `feature/3-online-prediction` 分支,实现模型训练与在线预测(见 US-3)

### 第③步 · 本地模块化开发
- [ ] 模块 1: 项目骨架 — `app.py` + `requirements.txt` + `requirements-dev.txt` + `Dockerfile` + CI workflow
- [ ] 模块 2: 数据加载 — `src/data_loader.py` + `tests/test_data_loader.py`
- [ ] 模块 3: 数据分析 — `src/analysis.py` + `tests/test_analysis.py`
- [ ] 模块 4: 可视化 — `src/visuals.py` + `tests/test_visuals.py`
- [ ] 模块 5: 模型训练 — `src/model_trainer.py` + `tests/test_model_trainer.py`
- [ ] 模块 6: 在线预测 — `src/predictor.py` + `tests/test_predictor.py`
- [ ] 模块 7: Streamlit 页面整合 — `app.py` 组装分析页与预测页

### 第④步 · 本地 CI 自检
- [ ] `ruff format --check .` 通过
- [ ] `ruff check .` 通过
- [ ] `pytest --cov --cov-fail-under=80` 通过
- [ ] 模型 AUC ≥ 0.75 验证通过

### 第⑤步 · 触发 PR
- [ ] git push 分支 → `gh pr create` 发起 PR → 汇报 CI 状态

### 第⑥步 · 人工审核 → 合并 → 本地验证
- [ ] **✋ 等人工 Review 并 Merge**
- [ ] 本地 `streamlit run app.py --server.port 8004` 验证功能正常

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

- *(暂无,项目刚初始化)*

---

## 里程碑 (DONE)

- [ ] *(暂无)*
