import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# 页面配置 - 移除低版本不支持的theme参数
st.set_page_config(page_title="学生成绩分析与预测系统", layout="wide")

# 定义数据文件路径（适配Streamlit Cloud的文件结构）
LIGHT_FILE = "student_data_light.csv"
MAIN_FILE = "student_data_adjusted_rounded.csv"

# 加载数据（增加容错处理，适配云端环境）
@st.cache_data(show_spinner="正在加载数据...")
def load_data():
    # 优先加载轻量数据
    if os.path.isfile(LIGHT_FILE):
        try:
            return pd.read_csv(LIGHT_FILE)
        except Exception as e:
            st.warning(f"轻量数据文件读取失败：{e}")
    
    # 加载主数据文件
    try:
        df = pd.read_csv(MAIN_FILE)
    except FileNotFoundError:
        st.error(f"未找到数据文件 {MAIN_FILE}，请确保文件已上传到项目根目录！")
        # 创建示例数据（避免页面崩溃）
        sample_data = {
            "专业": ["大数据管理", "计算机科学", "信息系统", "软件工程"],
            "性别": ["男", "女", "男", "女"] * 25,
            "每周学习时长（小时）": [15, 20, 18, 22] * 25,
            "期中考试分数": [75, 80, 78, 85] * 25,
            "期末考试分数": [80, 85, 82, 88] * 25,
            "上课出勤率": [95, 98, 92, 99] * 25
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(MAIN_FILE, index=False)
        st.info("已创建示例数据文件，你可以替换为真实数据")
    
    # 数据预处理
    if "上课出勤率" in df.columns:
        # 统一出勤率为百分比格式
        if df["上课出勤率"].max() < 2:
            df["上课出勤率"] = df["上课出勤率"] * 100
        df["上课出勤率"] = df["上课出勤率"].round(2)
    
    # 筛选必要列
    keep_cols = {"专业", "性别", "每周学习时长（小时）", "期中考试分数", "期末考试分数", "上课出勤率"}
    df = df[list(keep_cols & set(df.columns))].copy()
    
    # 保存轻量数据
    df.to_csv(LIGHT_FILE, index=False)
    return df

# 加载数据
df = load_data()

# 侧边栏导航
st.sidebar.title("导航菜单📃")
page = st.sidebar.radio(
    "请选择功能页面", 
    ["项目介绍", "专业数据分析", "成绩预测"],
    index=1  # 默认显示专业数据分析页面
)

# -------------------------- 1. 项目介绍页面 --------------------------
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
        # 使用内置图表替代本地图片（避免图片路径问题）
        st.write("### 📈 数据分析示意图")
        sample_chart_data = pd.DataFrame({
            "专业": ["大数据管理", "计算机科学", "信息系统"],
            "平均分": [85, 82, 88],
            "出勤率": [95, 92, 98]
        })
        fig_sample = px.bar(sample_chart_data, x="专业", y=["平均分", "出勤率"], barmode="group")
        st.plotly_chart(fig_sample, use_container_width=True)
    
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

# -------------------------- 2. 专业数据分析页面（核心功能） --------------------------
elif page == "专业数据分析":
    st.title("📊专业数据分析")
    
    if not df.empty:
        # 计算各专业核心统计指标
        major_stats = df.groupby("专业").agg({
            "每周学习时长（小时）": "mean",
            "期中考试分数": "mean",
            "期末考试分数": "mean",
            "上课出勤率": "mean"
        }).round(2)
        
        major_stats = major_stats.rename(columns={
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
        
        st.markdown('***')
        
        # （2）双层柱状图展示每个专业的男女性别比例
        st.subheader("2. 各专业男女性别比例（双层柱状图）")
        # 计算各专业男女人数
        gender_data = df.groupby(["专业", "性别"]).size().unstack(fill_value=0).reset_index()
        # 确保男女列都存在
        for gender in ["男", "女"]:
            if gender not in gender_data.columns:
                gender_data[gender] = 0
        
        # 创建双层柱状图
        fig_gender = go.Figure()
        # 添加男生柱子
        fig_gender.add_trace(go.Bar(
            x=gender_data["专业"],
            y=gender_data["男"],
            name="男生",
            marker_color="#1E88E5",
            text=gender_data["男"],
            textposition='auto'
        ))
        # 添加女生柱子
        fig_gender.add_trace(go.Bar(
            x=gender_data["专业"],
            y=gender_data["女"],
            name="女生",
            marker_color="#26A69A",
            text=gender_data["女"],
            textposition='auto'
        ))
        # 布局设置
        fig_gender.update_layout(
            barmode='group',  # 双层/分组柱状图
            height=400,
            xaxis_title="专业",
            yaxis_title="人数",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_gender, use_container_width=True)
        
        st.markdown('***')
        
        # （3）折线图展示每个专业的期中/期末考试分数
        st.subheader("3. 各专业期中/期末考试分数对比（折线图）")
        # 转换数据格式
        score_data = major_stats.melt(
            id_vars="专业",
            value_vars=["期中考试平均分", "期末考试平均分"],
            var_name="考试类型",
            value_name="平均分"
        )
        
        # 创建折线图（使用Plotly避免Streamlit原生图表的兼容性问题）
        fig_score = px.line(
            score_data,
            x="专业",
            y="平均分",
            color="考试类型",
            markers=True,  # 标记点
            height=400,
            color_discrete_map={
                "期中考试平均分": "#FFA000",
                "期末考试平均分": "#4CAF50"
            }
        )
        # 优化样式
        fig_score.update_traces(line=dict(width=3), marker=dict(size=8))
        fig_score.update_layout(
            xaxis_title="专业",
            yaxis_title="平均分",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_score, use_container_width=True)
        
        st.markdown('***')
        
        # （4）单层柱状图展示每个专业的平均上课出勤率
        st.subheader("4. 各专业平均上课出勤率")
        fig_attendance = px.bar(
            major_stats,
            x="专业",
            y="平均上课出勤率",
            height=400,
            color="平均上课出勤率",
            color_continuous_scale=px.colors.sequential.Greens,
            text="平均上课出勤率"
        )
        fig_attendance.update_traces(
            texttemplate="%{text:.2f}%",
            textposition='outside'
        )
        fig_attendance.update_layout(
            xaxis_title="专业",
            yaxis_title="平均上课出勤率（%）",
            coloraxis_showscale=False,
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_attendance, use_container_width=True)
        
        st.markdown('***')
        
        # （5）大数据管理专业专项分析
        st.subheader("5. 大数据管理专业专项分析")
        target_major = "大数据管理"
        
        if target_major in major_stats["专业"].values:
            # 提取该专业数据
            bigdata_data = major_stats[major_stats["专业"] == target_major].iloc[0]
            
            # 创建专项分析图表
            fig_bigdata = go.Figure()
            metrics = ["平均上课出勤率", "期末考试平均分"]
            values = [bigdata_data["平均上课出勤率"], bigdata_data["期末考试平均分"]]
            
            fig_bigdata.add_trace(go.Bar(
                x=metrics,
                y=values,
                marker_color=["#2196F3", "#FF9800"],
                text=[f"{v:.2f}%" if i==0 else f"{v:.2f}分" for i, v in enumerate(values)],
                textposition='auto'
            ))
            
            fig_bigdata.update_layout(
                height=400,
                title=f"{target_major}专业核心指标",
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig_bigdata, use_container_width=True)
            
            # 指标卡片展示
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label=f"{target_major} - 平均上课出勤率",
                    value=f"{bigdata_data['平均上课出勤率']:.2f}%",
                    delta=f"{bigdata_data['平均上课出勤率'] - major_stats['平均上课出勤率'].mean():.2f}%",
                    delta_color="normal"
                )
            with col2:
                st.metric(
                    label=f"{target_major} - 期末考试平均分",
                    value=f"{bigdata_data['期末考试平均分']:.2f}分",
                    delta=f"{bigdata_data['期末考试平均分'] - major_stats['期末考试平均分'].mean():.2f}分",
                    delta_color="normal"
                )
        else:
            st.warning(f"未找到{target_major}专业的数据！")
            # 显示所有专业列表
            st.write("当前系统中的专业列表：")
            st.write(major_stats["专业"].tolist())
    else:
        st.warning("暂无数据可展示")

# -------------------------- 3. 成绩预测页面 --------------------------
elif page == "成绩预测":
    st.title("🔍期末成绩预测")
    
    st.subheader("分数段说明")
    col_excellent, col_pass, col_improve = st.columns(3)
    with col_excellent: 
        st.success("✅ 优秀段（85分及以上）：保持当前学习状态，可拓展知识深度！")
    with col_pass: 
        st.warning("⚠️ 合格段（60-84分）：巩固基础，定期错题复盘！")
    with col_improve: 
        st.error("❌ 待提升段（60分以下）：加强投入，优先掌握核心内容！")
    
    st.write("请输入学生的学习信息，系统将预测其期末成绩并提供对应建议")
    
    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_id = st.text_input("学号", value="1231231")
            gender = st.selectbox("性别", options=["男", "女"])
            # 获取专业列表（容错处理）
            major_options = df["专业"].unique() if ("专业" in df.columns and not df.empty) else ["大数据管理", "计算机科学"]
            major = st.selectbox("专业", options=major_options)
        
        with col2:
            study_hours = st.slider("每周学习时长(小时)", min_value=0, max_value=50, value=29)
            attendance = st.slider("上课出勤率(%)", min_value=0, max_value=100, value=100)
            midterm_score = st.slider("期中考试分数", min_value=0, max_value=100, value=63)
            homework_rate = st.slider("作业完成率(%)", min_value=0, max_value=100, value=80)
        
        submit_btn = st.form_submit_button("预测期末成绩")
    
    if submit_btn:
        # 简单的预测算法
        predicted = midterm_score * 0.7 + study_hours * 0.5 + attendance * 0.1 + homework_rate * 0.2
        predicted = min(max(round(predicted, 1), 0), 100)
        
        st.subheader("🔍 预测结果")
        if predicted >= 85:
            st.success(f"预测期末成绩：{predicted} 分")
            st.success("学习建议：保持当前学习状态，可适当拓展知识深度，挑战更高难度的学习内容！")
        elif predicted >= 60:
            st.warning(f"预测期末成绩：{predicted} 分")
            st.warning("学习建议：巩固基础知识要点，定期进行错题复盘，针对薄弱环节加强练习！")
        else:
            st.error(f"预测期末成绩：{predicted} 分")
            st.error("学习建议：加油！需加强学习投入，优先掌握核心知识点，及时请教老师/同学！")


