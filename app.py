"""bank-marketing-predictor — Bank Marketing Data Analysis & Prediction."""

import streamlit as st

st.set_page_config(page_title="Bank Marketing Predictor", layout="wide")

st.title("Bank Marketing Predictor")
st.markdown("银行电话营销数据分析与认购预测系统")

tab1, tab2 = st.tabs(["数据分析", "在线预测"])

with tab1:
    st.header("数据分析")
    st.info("上传 CSV 数据文件以开始分析。")

with tab2:
    st.header("在线预测")
    st.info("请先在「数据分析」页训练模型，然后在此进行预测。")
