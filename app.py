"""bank-marketing-predictor — Bank Marketing Data Analysis & Prediction."""

import os

import streamlit as st

from src.analysis import get_missing_summary, get_numeric_stats
from src.config import TARGET_COLUMN
from src.data_loader import get_data_summary, load_csv, validate_columns
from src.model_trainer import (
    evaluate_models,
    get_best_model,
    meets_threshold,
    preprocess_data,
    save_model,
    train_models,
)
from src.predictor import load_model as load_model_bundle, predict
from src.visuals import (
    plot_correlation_heatmap,
    plot_numeric_histogram,
    plot_target_distribution,
)

_MODEL_PATH = "models/best_model.pkl"
_NUMERIC_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr.employed",
]
_CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

st.set_page_config(page_title="Bank Marketing Predictor", layout="wide")
st.title("Bank Marketing Predictor")
st.markdown("银行电话营销数据分析与认购预测系统")

tab1, tab2 = st.tabs(["数据分析", "在线预测"])

# ── Tab 1: Data Analysis ────────────────────────────────────────────────────
with tab1:
    st.header("数据分析")

    uploaded_file = st.file_uploader("上传 CSV 数据文件", type=["csv"])
    if uploaded_file is None:
        st.info("请上传 bank-additional-full.csv 开始分析。")
        st.stop()

    # Load with Streamlit caching — pass raw bytes for reliable hashing
    @st.cache_data
    def _load_bytes(data: bytes) -> dict:
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        df = load_csv(tmp_path)
        os.unlink(tmp_path)
        missing = validate_columns(df)
        summary = get_data_summary(df)
        return {"df": df, "missing_cols": missing, "summary": summary}

    result = _load_bytes(uploaded_file.read())
    df = result["df"]
    missing_cols = result["missing_cols"]
    summary = result["summary"]

    if missing_cols:
        st.error(f"数据缺少以下列: {missing_cols}")
        st.stop()

    # Store in session for Tab 2
    st.session_state["df"] = df

    # Overview
    st.subheader("数据总览")
    c1, c2, c3 = st.columns(3)
    c1.metric("行数", summary["rows"])
    c2.metric("列数", summary["columns"])
    total_missing = sum(v for v in summary["missing"].values())
    c3.metric("缺失值总数", total_missing)

    with st.expander("缺失值详情"):
        miss_df = get_missing_summary(df)
        if len(miss_df) == 0:
            st.success("数据无缺失值")
        else:
            st.dataframe(miss_df, use_container_width=True)

    with st.expander("数据类型分布"):
        dtype_counts = {}
        for dtype_name in summary["dtypes"].values():
            dtype_counts[dtype_name] = dtype_counts.get(dtype_name, 0) + 1
        dc1, dc2 = st.columns(2)
        dc1.metric(
            "数值型", dtype_counts.get("int64", 0) + dtype_counts.get("float64", 0)
        )
        dc2.metric("分类型", dtype_counts.get("object", 0) + dtype_counts.get("str", 0))
        # Build a DataFrame for the dtype table
        import pandas as pd

        dtype_df = pd.DataFrame(
            [{"列名": col, "数据类型": dt} for col, dt in summary["dtypes"].items()]
        )
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

    with st.expander("数据预览 (前 100 行)"):
        st.dataframe(df.head(100), use_container_width=True)

    # Sidebar filters
    st.subheader("筛选器")
    filter_cols = st.columns(4)
    selected_job = filter_cols[0].multiselect(
        "职业", df["job"].dropna().unique().tolist()
    )
    selected_month = filter_cols[1].multiselect(
        "月份", df["month"].dropna().unique().tolist()
    )
    selected_edu = filter_cols[2].multiselect(
        "教育", df["education"].dropna().unique().tolist()
    )
    selected_y = filter_cols[3].multiselect(
        "是否认购", df[TARGET_COLUMN].dropna().unique().tolist()
    )

    filtered = df.copy()
    if selected_job:
        filtered = filtered[filtered["job"].isin(selected_job)]
    if selected_month:
        filtered = filtered[filtered["month"].isin(selected_month)]
    if selected_edu:
        filtered = filtered[filtered["education"].isin(selected_edu)]
    if selected_y:
        filtered = filtered[filtered[TARGET_COLUMN].isin(selected_y)]

    st.caption(f"筛选后: {len(filtered)} / {len(df)} 条记录")

    # Statistics
    st.subheader("描述性统计")
    st.dataframe(get_numeric_stats(filtered), use_container_width=True)

    # Charts
    st.subheader("可视化")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(plot_target_distribution(filtered), use_container_width=True)
    with chart_col2:
        num_col = st.selectbox("选择数值列", _NUMERIC_COLS, key="hist_col")
        st.plotly_chart(
            plot_numeric_histogram(filtered, num_col), use_container_width=True
        )

    st.subheader("相关性热力图")
    st.plotly_chart(plot_correlation_heatmap(filtered), use_container_width=True)

# ── Tab 2: Online Prediction ─────────────────────────────────────────────────
with tab2:
    st.header("在线预测")

    if "df" not in st.session_state:
        st.warning("请先在「数据分析」页上传数据并训练模型。")
        st.stop()

    df = st.session_state["df"]

    col_left, col_right = st.columns([1, 2])

    # ── Left: Training ──
    with col_left:
        st.subheader("模型训练")

        if st.button("训练模型", type="primary", use_container_width=True):
            with st.spinner("正在训练..."):
                data = preprocess_data(df)
                models = train_models(data["X_train"], data["y_train"])
                metrics = evaluate_models(models, data["X_test"], data["y_test"])
                name, best = get_best_model(models, metrics)
                save_model(best, data["preprocessor"], _MODEL_PATH)

                st.session_state["metrics"] = metrics
                st.session_state["best_name"] = name
                st.session_state["model_ready"] = True

            if meets_threshold(metrics):
                st.success(f"训练完成！最佳模型: {name}")
            else:
                st.warning("模型 AUC 低于阈值 0.75，建议检查数据质量。")

        if "metrics" in st.session_state:
            st.dataframe(st.session_state["metrics"], use_container_width=True)

        st.divider()
        # Load existing model
        if os.path.exists(_MODEL_PATH) and not st.session_state.get("model_ready"):
            st.session_state["model_ready"] = True

        if st.session_state.get("model_ready"):
            st.success("模型已就绪，可在右侧进行预测。")
        else:
            st.info("点击上方按钮训练模型。")

    # ── Right: Prediction Form ──
    with col_right:
        st.subheader("预测表单")

        if not st.session_state.get("model_ready"):
            st.info("请先训练或加载模型。")
            st.stop()

        with st.form("prediction_form"):
            inputs = {}
            num_cols = st.columns(5)
            for i, col_name in enumerate(_NUMERIC_COLS):
                default = (
                    0 if col_name not in df.columns else float(df[col_name].median())
                )
                inputs[col_name] = num_cols[i % 5].number_input(
                    col_name, value=default, format="%.2f", key=f"pred_{col_name}"
                )

            cat_cols = st.columns(5)
            for i, col_name in enumerate(_CATEGORICAL_COLS):
                options = ["unknown"] + sorted(df[col_name].dropna().unique().tolist())
                inputs[col_name] = cat_cols[i % 5].selectbox(
                    col_name, options, key=f"pred_{col_name}"
                )

            submitted = st.form_submit_button(
                "预测", type="primary", use_container_width=True
            )

        if submitted:
            bundle = load_model_bundle(_MODEL_PATH)
            result = predict(bundle, inputs)
            if result["error"]:
                st.error(result["error"])
            else:
                if result["prediction"] == "yes":
                    st.success(
                        f"预测结果: **会认购** (概率: {result['probability']:.2%})"
                    )
                else:
                    st.info(
                        f"预测结果: **不会认购** (概率: {result['probability']:.2%})"
                    )
