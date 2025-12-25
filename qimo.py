import os
import pandas as pd
import streamlit as st

# 无需Matplotlib字体配置！直接用Streamlit原生图表
st.set_page_config(page_title="学生成绩分析与预测系统", layout="wide")

LIGHT_FILE = "student_data_light.csv"

@st.cache_data(show_spinner=False)
def load_data():
    if os.path.isfile(LIGHT_FILE):
        return pd.read_csv(LIGHT_FILE)
    try:
        df = pd.read_csv("student_data_adjusted_rounded.csv")
    except FileNotFoundError:
        st.error("请确保数据文件 student_data_adjusted_rounded.csv 存在于当前目录！")
        return pd.DataFrame()
    if "上课出勤率" in df.columns and df["上课出勤率"].max() < 2:
        df["上课出勤率"] = df["上课出勤率"] * 100
    keep_cols = {"专业", "性别", "每周学习时长（小时）", "期中考试分数", "期末考试分数", "上课出勤率"}
    df = df[list(keep_cols & set(df.columns))].copy()
    df.to_csv(LIGHT_FILE, index=False)
    return df

df = load_data()

# 侧边栏导航
st.sidebar.title("导航菜单📃")
page = st.sidebar.radio("请选择功能页面", ["项目介绍", "专业数据分析", "成绩预测"])

if page == "项目介绍":
    st.title("🎓学生成绩分析与预测系统")
    st.markdown('***')
    col_text, col_img = st.columns([2, 1.2])
    with col_text:
        st.subheader("📋 项目概述")
        st.write("本项目基于Streamlit搭建，通过数据可视化和简单算法，分析学生学业表现并预测期末成绩。")
        st.subheader("✨ 主要特点")
        st.markdown("""
        - 📊 多维度展示学业数据
        - 📈 按专业统计分析
        - 🤖 智能成绩预测
        - 💡 个性化学习建议
        """)
    with col_img:
        st.subheader("专业数据分析")
        st.image("images/analysis_diagram.png", caption="学生数据分析示意图", width=400)
    st.markdown('***')
    st.subheader("🎯 项目目标")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🎯 目标一：分析影响因素")
        st.write("- 识别关键学习指标"); st.write("- 探索成绩相关因素"); st.write("- 提供数据支持决策")
    with col2:
        st.markdown("#### 🎯 目标二：可视化展示")
        st.write("- 专业对比分析"); st.write("- 性别差异研究"); st.write("- 学习模式识别")
    with col3:
        st.markdown("#### 🎯 目标三：成绩预测")
        st.write("- 机器学习模型"); st.write("- 个性化预测"); st.write("- 及时干预预警")
    st.markdown('***')
    st.subheader("🔧 技术架构")
    tech_cols = st.columns(4)
    with tech_cols[0]: st.markdown("#### 前端框架: "); st.write("Streamlit")
    with tech_cols[1]: st.markdown("#### 数据处理:"); st.write("Pandas"); st.write("Numpy")
    with tech_cols[2]: st.markdown("#### 可视化:"); st.write("Streamlit原生图表")
    with tech_cols[3]: st.markdown("#### 机器学习:"); st.write("Scikit-learn")

elif page == "专业数据分析":
    st.title("📊专业数据分析")
    if not df.empty:
        # 1. 核心指标表
        if all(c in df.columns for c in ["专业", "期中考试分数", "期末考试分数", "每周学习时长（小时）"]):
            st.subheader("1. 各专业核心学习指标汇总")
            core = df.groupby("专业")[["每周学习时长（小时）", "期中考试分数", "期末考试分数"]].mean().round(2)
            core.columns = ["每周平均学时", "期中考试平均分", "期末考试平均分"]
            st.dataframe(core.reset_index(), use_container_width=True)

        # 2. 性别堆叠柱（Streamlit原生st.bar_chart）
        if {"专业", "性别"} <= set(df.columns):
            st.subheader("2. 各专业男女性别比例")
            gender_cnt = df.groupby(["专业", "性别"]).size().unstack(fill_value=0)
            if "男" in gender_cnt and "女" in gender_cnt:
                gender_cnt = gender_cnt[["男", "女"]]
            # 原生堆叠柱状图（自动支持中文）
            st.bar_chart(gender_cnt, use_container_width=True, stack=True)

        # 3. 考试分数折线（Streamlit原生st.line_chart）
        if {"专业", "期中考试分数", "期末考试分数"} <= set(df.columns):
            st.subheader("3. 各专业考试分数趋势")
            exam = df.groupby("专业")[["期中考试分数", "期末考试分数"]].mean().round(2)
            st.line_chart(exam, use_container_width=True, marker="o")

        # 4. 出勤率柱（Streamlit原生st.bar_chart，带数值标签）
        if {"专业", "上课出勤率"} <= set(df.columns):
            st.subheader("4. 各专业平均上课出勤率")
            attend = df.groupby("专业")["上课出勤率"].mean().round(2).reset_index()
            attend.columns = ["专业", "平均上课出勤率（%）"]
            # 原生柱状图+显示数据标签
            st.bar_chart(attend.set_index("专业"), use_container_width=True)
            # 显示数值（避免中文问题）
            st.dataframe(attend, use_container_width=True, hide_index=True)

        # 5. 大数据管理双柱（Streamlit原生st.bar_chart）
        target = "大数据管理"
        if target in df["专业"].values:
            st.subheader(f"5. {target}专业核心指标")
            tmp = df[df["专业"] == target]
            metrics = pd.DataFrame({
                "指标": ["平均上课出勤率", "期末考试平均分"],
                "数值": [round(tmp["上课出勤率"].mean(), 2), round(tmp["期末考试分数"].mean(), 2)]
            })
            st.bar_chart(metrics.set_index("指标"), use_container_width=True)

    else:
        st.warning("暂无数据可展示")

elif page == "成绩预测":
    st.title("🔍期末成绩预测")
    st.subheader("分数段说明")
    col_excellent, col_pass, col_improve = st.columns(3)
    with col_excellent: st.success("✅ 优秀段（85分及以上）：保持当前学习状态，可拓展知识深度！")
    with col_pass: st.warning("⚠️ 合格段（60-84分）：巩固基础，定期错题复盘！")
    with col_improve: st.error("❌ 待提升段（60分以下）：加强投入，优先掌握核心内容！")
    st.write("请输入学生的学习信息，系统将预测其期末成绩并提供对应建议")
    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("学号", value="1231231")
            gender = st.selectbox("性别", options=["男", "女"])
            major_options = df["专业"].unique() if ("专业" in df.columns and not df.empty) else ["信息系统"]
            major = st.selectbox("专业", options=major_options)
        with col2:
            study_hours = st.slider("每周学习时长(小时)", min_value=0, max_value=50, value=29)
            attendance = st.slider("上课出勤率", min_value=0, max_value=100, value=100)
            midterm_score = st.slider("期中考试分数", min_value=0, max_value=100, value=63)
            homework_rate = st.slider("作业完成率", min_value=0, max_value=100, value=80)
        submit_btn = st.form_submit_button("预测期末成绩")
    if submit_btn:
        predicted = midterm_score * 0.7 + study_hours * 0.5 + attendance * 0.1 + homework_rate * 0.2
        predicted = min(max(round(predicted, 1), 0), 100)
        st.subheader("🔍 预测结果")
        if predicted >= 80:
            st.success(f"预测期末成绩：{predicted} 分"); st.success("学习建议：保持当前学习状态，可适当拓展知识深度，挑战更高难度的学习内容！")
            st.image("images/excellent.png", width=500)
        elif predicted >= 60:
            st.warning(f"预测期末成绩：{predicted} 分"); st.warning("学习建议：巩固基础知识要点，定期进行错题复盘，针对薄弱环节加强练习！")
            st.image("images/pass.png", width=500)
        else:
            st.error(f"预测期末成绩：{predicted} 分"); st.error("学习建议：加油！需加强学习投入，优先掌握核心知识点，及时请教老师/同学！")
            st.image("images/improve.png", width=500)
