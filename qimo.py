import os
import pandas as pd
import streamlit as st

# 页面配置（仅保留Streamlit原生支持的参数）
st.set_page_config(page_title="学生成绩分析与预测系统", layout="wide")

# 数据文件路径（适配qimo.py文件名，路径逻辑不变）
LIGHT_FILE = "student_data_light.csv"
MAIN_FILE = "student_data_adjusted_rounded.csv"

# 加载数据（容错处理，确保无数据也能运行）
@st.cache_data(show_spinner="加载数据中...")
def load_data():
    # 优先加载轻量数据
    if os.path.isfile(LIGHT_FILE):
        try:
            return pd.read_csv(LIGHT_FILE)
        except:
            pass
    
    # 加载主数据/创建示例数据（避免文件缺失报错）
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
    
    # 数据预处理（统一出勤率为百分比格式）
    if "上课出勤率" in df.columns and df["上课出勤率"].max() < 2:
        df["上课出勤率"] *= 100
    df["上课出勤率"] = df["上课出勤率"].round(2)
    
    # 筛选必要列
    keep_cols = {"专业", "性别", "每周学习时长（小时）", "期中考试分数", "期末考试分数", "上课出勤率"}
    df = df[list(keep_cols & set(df.columns))].copy()
    df.to_csv(LIGHT_FILE, index=False)
    return df

# 加载数据
df = load_data()

# 侧边栏导航
st.sidebar.title("导航菜单📃")
page = st.sidebar.radio("选择功能页面", ["项目介绍", "专业数据分析", "成绩预测"], index=1)

# -------------------------- 1. 项目介绍页面 --------------------------
if page == "项目介绍":
    st.title("🎓学生成绩分析与预测系统")
    st.markdown("---")
    
    # 分栏展示
    col_text, col_chart = st.columns([2, 1.2])
    with col_text:
        st.subheader("📋 项目概述")
        st.write("本系统基于Streamlit搭建，专注于学生学业数据的分析与期末成绩预测，为学习规划提供数据支撑。")
        st.subheader("✨ 核心功能")
        st.markdown("""
        - 📊 多维度展示各专业学业数据
        - 📈 专业间成绩、出勤率、性别比例对比
        - 🤖 基于学习行为的期末成绩预测
        - 💡 个性化学习建议
        """)
    
    with col_chart:
        st.subheader("数据可视化示例")
        # 示例图表
        sample_df = pd.DataFrame({
            "专业": ["大数据管理", "计算机科学", "信息系统"],
            "期中考试平均分": [78, 82, 79],
            "期末考试平均分": [83, 85, 81]
        }).set_index("专业")
        st.line_chart(sample_df, use_container_width=True)
    
    st.markdown("---")
    
    # 项目目标
    st.subheader("🎯 项目目标")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 分析影响因素")
        st.write("- 识别学习关键指标")
        st.write("- 探索成绩关联因素")
    with col2:
        st.markdown("#### 可视化展示")
        st.write("- 专业对比分析")
        st.write("- 性别差异研究")
    with col3:
        st.markdown("#### 成绩预测")
        st.write("- 个性化分数预测")
        st.write("- 学习建议生成")

# -------------------------- 2. 专业数据分析页面（优化中文显示） --------------------------
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

        # （1）表格展示各专业核心指标
        st.subheader("1. 各专业核心指标统计")
        st.dataframe(
            major_stats,
            use_container_width=True,
            hide_index=True,
            column_config={
                "专业": st.column_config.TextColumn("专业名称", width="medium"),
                "每周平均学时": st.column_config.NumberColumn("每周平均学时（小时）", format="%.2f"),
                "期中考试平均分": st.column_config.NumberColumn(format="%.2f"),
                "期末考试平均分": st.column_config.NumberColumn(format="%.2f"),
                "平均上课出勤率": st.column_config.NumberColumn(format="%.2f%%")
            }
        )
        st.markdown("---")

        # （2）双层柱状图展示男女性别比例（优化中文）
        st.subheader("2. 各专业男女性别比例")
        gender_data = df.groupby(["专业", "性别"]).size().unstack(fill_value=0)
        for gender in ["男", "女"]:
            if gender not in gender_data.columns:
                gender_data[gender] = 0
        # 手动调整图表高度+强制中文适配
        st.bar_chart(
            gender_data,
            use_container_width=True,
            height=500  # 增加高度，让中文标签显示完整
        )
        st.markdown("---")

        # （3）折线图展示期中/期末分数（优化中文）
        st.subheader("3. 各专业期中/期末考试分数对比")
        score_data = major_stats.set_index("专业")[["期中考试平均分", "期末考试平均分"]]
        # 增加高度+调整布局
        st.line_chart(
            score_data,
            use_container_width=True,
            height=500
        )
        # 补充说明（避免标签重叠）
        st.caption("注：蓝色线为期中考试平均分，浅蓝色线为期末考试平均分")
        st.markdown("---")

        # （4）单层柱状图展示平均出勤率（优化中文）
        st.subheader("4. 各专业平均上课出勤率")
        attend_data = major_stats.set_index("专业")["平均上课出勤率"]
        st.bar_chart(
            attend_data,
            use_container_width=True,
            height=500
        )
        st.markdown("---")

        # （5）大数据管理专业专项分析
        st.subheader("5. 大数据管理专业专项分析")
        target_major = "大数据管理"
        if target_major in major_stats["专业"].values:
            bigdata_info = major_stats[major_stats["专业"] == target_major].iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label=f"{target_major} - 平均上课出勤率",
                    value=f"{bigdata_info['平均上课出勤率']:.2f}%",
                    delta=f"{bigdata_info['平均上课出勤率'] - major_stats['平均上课出勤率'].mean():.2f}%",
                    delta_color="normal"
                )
            with col2:
                st.metric(
                    label=f"{target_major} - 期末考试平均分",
                    value=f"{bigdata_info['期末考试平均分']:.2f}分",
                    delta=f"{bigdata_info['期末考试平均分'] - major_stats['期末考试平均分'].mean():.2f}分",
                    delta_color="normal"
                )
            bigdata_chart = pd.DataFrame({
                "指标": ["平均上课出勤率(%)", "期末考试平均分(分)"],
                "数值": [bigdata_info["平均上课出勤率"], bigdata_info["期末考试平均分"]]
            }).set_index("指标")
            st.bar_chart(
                bigdata_chart,
                use_container_width=True,
                height=400
            )
        else:
            st.warning(f"未找到「{target_major}」专业的数据！")
            st.write(f"当前系统中的专业列表：{major_stats['专业'].tolist()}")
    else:
        st.warning("暂无数据可展示，请检查数据文件是否正确！")

# -------------------------- 3. 成绩预测页面 --------------------------
elif page == "成绩预测":
    st.title("🔍期末成绩预测")
    
    # 分数段说明
    st.subheader("分数段说明")
    col_excellent, col_pass, col_improve = st.columns(3)
    with col_excellent:
        st.success("✅ 优秀段（85分及以上）：保持当前学习状态，可拓展知识深度！")
    with col_pass:
        st.warning("⚠️ 合格段（60-84分）：巩固基础，定期错题复盘！")
    with col_improve:
        st.error("❌ 待提升段（60分以下）：加强投入，优先掌握核心内容！")
    
    # 预测表单
    st.write("请输入学生的学习信息，系统将预测期末成绩并给出学习建议")
    with st.form("predict_form"):
        col_left, col_right = st.columns(2)
        with col_left:
            student_id = st.text_input("学号", value="20240001")
            gender = st.selectbox("性别", options=["男", "女"])
            # 获取专业列表（容错处理）
            major_options = df["专业"].unique() if ("专业" in df.columns and not df.empty) else ["大数据管理"]
            major = st.selectbox("专业", options=major_options)
        with col_right:
            study_hours = st.slider("每周学习时长(小时)", min_value=0, max_value=50, value=25)
            attendance = st.slider("上课出勤率(%)", min_value=0, max_value=100, value=95)
            midterm_score = st.slider("期中考试分数", min_value=0, max_value=100, value=75)
            homework_rate = st.slider("作业完成率(%)", min_value=0, max_value=100, value=85)
        
        # 提交按钮
        submit_btn = st.form_submit_button("预测期末成绩")
    
    # 预测逻辑
    if submit_btn:
        # 简单的预测算法
        predicted_score = midterm_score * 0.7 + study_hours * 0.5 + attendance * 0.1 + homework_rate * 0.2
        # 限制分数范围在0-100之间
        predicted_score = min(max(round(predicted_score, 1), 0), 100)
        
        # 展示预测结果
        st.subheader("🔍 成绩预测结果")
        if predicted_score >= 85:
            st.success(f"预测期末成绩：{predicted_score} 分")
            st.success("📝 学习建议：保持当前优秀的学习状态，可适当拓展知识深度，挑战更高难度的学习内容！")
        elif predicted_score >= 60:
            st.warning(f"预测期末成绩：{predicted_score} 分")
            st.warning("📝 学习建议：巩固基础知识，定期复盘错题，针对薄弱环节加强专项练习！")
        else:
            st.error(f"预测期末成绩：{predicted_score} 分")
            st.error("📝 学习建议：需要加大学习投入，优先掌握核心知识点，及时向老师/同学请教问题！")

# 页脚信息
st.markdown("---")
st.caption("© 2025 学生成绩分析与预测系统 | 运行文件：qimo.py")
