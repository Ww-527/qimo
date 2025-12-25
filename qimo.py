import os
import pandas as pd
import streamlit as st

# 页面配置
st.set_page_config(page_title="学生成绩分析与预测系统", layout="wide")

# 数据文件路径
LIGHT_FILE = "student_data_light.csv"
MAIN_FILE = "student_data_adjusted_rounded.csv"

# 加载数据（容错处理）
@st.cache_data(show_spinner="加载数据中...")
def load_data():
    if os.path.isfile(LIGHT_FILE):
        try:
            return pd.read_csv(LIGHT_FILE)
        except:
            pass
    
    try:
        df = pd.read_csv(MAIN_FILE)
    except FileNotFoundError:
        # 生成示例数据
        sample_data = {
            "专业": ["大数据管理", "计算机科学", "信息系统", "软件工程"] * 25,
            "性别": ["男", "女", "男", "女"] * 25,
            "每周学习时长（小时）": [15, 20, 18, 22] * 25,
            "期中考试分数": [75, 80, 78, 85] * 25,
            "期末考试分数": [80, 85, 82, 88] * 25,
            "上课出勤率": [95, 98, 92, 99] * 25
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(MAIN_FILE, index=False)
        df.to_csv(LIGHT_FILE, index=False)
    
    if "上课出勤率" in df.columns and df["上课出勤率"].max() < 2:
        df["上课出勤率"] *= 100
    df["上课出勤率"] = df["上课出勤率"].round(2)
    
    keep_cols = {"专业", "性别", "每周学习时长（小时）", "期中考试分数", "期末考试分数", "上课出勤率"}
    df = df[list(keep_cols & set(df.columns))].copy()
    df.to_csv(LIGHT_FILE, index=False)
    return df

df = load_data()

# 侧边栏导航
st.sidebar.title("导航菜单📃")
page = st.sidebar.radio("请选择功能页面", ["项目介绍", "专业数据分析", "成绩预测"])

# -------------------------- 1. 项目介绍页面（真实数据图表） --------------------------
if page == "项目介绍":
    st.title("🎓学生成绩分析与预测系统")
    st.markdown('***')
    col_text, col_chart = st.columns([2, 1.2])
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
    with col_chart:
        st.subheader("专业数据分析（真实数据）")
        # 生成真实的专业性别比例柱状图
        if not df.empty:
            gender_data = df.groupby(["专业", "性别"]).size().unstack(fill_value=0)
            for g in ["男", "女"]:
                if g not in gender_data.columns:
                    gender_data[g] = 0
            st.bar_chart(gender_data, use_container_width=True, height=300)
        st.caption("学生专业性别分布示意图")
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
    with tech_cols[2]: st.markdown("#### 可视化:"); st.write("Plotly"); st.write("Streamlit原生图表")
    with tech_cols[3]: st.markdown("#### 机器学习:"); st.write("Scikit-learn")

# -------------------------- 2. 专业数据分析页面（恢复delta箭头） --------------------------
elif page == "专业数据分析":
    st.title("📊专业数据分析")
    if not df.empty:
        # 计算各专业核心统计指标
        major_stats = df.groupby("专业").agg({
            "每周学习时长（小时）": "mean",
            "期中考试分数": "mean",
            "期末考试分数": "mean",
            "上课出勤率": "mean"
        }).round(2).rename(columns={
            "每周学习时长（小时）": "每周平均学时",
            "期中考试分数": "期中考试平均分",
            "期末考试分数": "期末考试平均分",
            "上课出勤率": "平均上课出勤率"
        }).reset_index()

        # （1）表格展示核心指标
        st.subheader("1. 各专业核心指标")
        st.dataframe(
            major_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                "平均上课出勤率": st.column_config.NumberColumn(format="%.2f%%")
            }
        )
        st.markdown("---")

        # （2）双层柱状图（性别比例）
        st.subheader("2. 各专业男女性别比例")
        gender_data = df.groupby(["专业", "性别"]).size().unstack(fill_value=0)
        for g in ["男", "女"]:
            if g not in gender_data.columns:
                gender_data[g] = 0
        st.bar_chart(gender_data, use_container_width=True, height=500)
        st.markdown("---")

        # （3）折线图（期中/期末分数）
        st.subheader("3. 各专业考试分数趋势")
        score_data = major_stats.set_index("专业")[["期中考试平均分", "期末考试平均分"]]
        st.line_chart(score_data, use_container_width=True, height=500)
        st.markdown("---")

        # （4）单层柱状图（出勤率）
        st.subheader("4. 各专业平均上课出勤率")
        attend_data = major_stats.set_index("专业")["平均上课出勤率"]
        st.bar_chart(attend_data, use_container_width=True, height=500)
        st.markdown("---")

        # （5）大数据管理专业专项分析（恢复delta箭头）
        st.subheader("5. 大数据管理专业专项")
        target = "大数据管理"
        if target in major_stats["专业"].values:
            bigdata = major_stats[major_stats["专业"] == target].iloc[0]
            # 计算与所有专业平均值的差值（显示上下箭头）
            avg_attend = major_stats["平均上课出勤率"].mean()
            avg_score = major_stats["期末考试平均分"].mean()
            attend_delta = bigdata["平均上课出勤率"] - avg_attend
            score_delta = bigdata["期末考试平均分"] - avg_score
            
            # 带delta箭头的指标卡片
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="平均出勤率",
                    value=f"{bigdata['平均上课出勤率']:.2f}%",
                    delta=f"{attend_delta:.2f}%",
                    delta_color="normal"
                )
            with col2:
                st.metric(
                    label="期末平均分",
                    value=f"{bigdata['期末考试平均分']:.2f}分",
                    delta=f"{score_delta:.2f}分",
                    delta_color="normal"
                )
            # 专项图表
            st.bar_chart(
                pd.DataFrame({
                    "指标": ["出勤率", "期末平均分"],
                    "数值": [bigdata["平均上课出勤率"], bigdata["期末考试平均分"]]
                }).set_index("指标"),
                height=300
            )
        else:
            st.info(f"当前无「{target}」专业数据，现有专业：{major_stats['专业'].tolist()}")
    else:
        st.warning("暂无数据")

# -------------------------- 3. 成绩预测页面（完整保留原始内容） --------------------------
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


