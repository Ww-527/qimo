import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 配置中文字体，避免图表中文乱码
plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Micro Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# 页面基础配置
st.set_page_config(page_title="学生成绩分析与预测系统", layout="wide")

# 加载数据（基础缓存优化）
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("student_data_adjusted_rounded.csv")
        # 仅新增：修复出勤率数据单位（最小化修改）
        if "上课出勤率" in df.columns and df["上课出勤率"].max() < 2:
            df["上课出勤率"] = df["上课出勤率"] * 100
        return df
    except FileNotFoundError:
        st.error("请确保数据文件 student_data_adjusted_rounded.csv 存在于当前目录！")
        return pd.DataFrame()

df = load_data()

# 侧边栏导航（基础radio组件）
st.sidebar.title("导航菜单📃")
page = st.sidebar.radio(
    "请选择功能页面",
    ["项目介绍", "专业数据分析", "成绩预测"]
)

# -------------------------- 1. 项目介绍页面（纯基础元素） --------------------------
if page == "项目介绍":
    st.title("🎓学生成绩分析与预测系统")
    st.markdown('***') 
    
    # 基础列布局
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
        # 直接指定图片路径（若图片不存在可注释此行，不影响核心功能）
        st.image("images/analysis_diagram.png", caption="学生数据分析示意图", width=400)

    st.markdown('***')
    
    # 项目目标（基础列+markdown）
    st.subheader("🎯 项目目标")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 目标一：分析影响因素")
        st.write("- 识别关键学习指标")
        st.write("- 探索成绩相关因素")
        st.write("- 提供数据支持决策")
    
    with col2:
        st.markdown("#### 🎯 目标二：可视化展示")
        st.write("- 专业对比分析")
        st.write("- 性别差异研究")
        st.write("- 学习模式识别")
    
    with col3:
        st.markdown("#### 🎯 目标三：成绩预测")
        st.write("- 机器学习模型")
        st.write("- 个性化预测")
        st.write("- 及时干预预警")

    st.markdown('***')

    # 技术架构（基础列布局）
    st.subheader("🔧 技术架构")
    tech_cols = st.columns(4)

    with tech_cols[0]:
        st.markdown("#### 前端框架: ")
        st.write("Streamlit")
    
    with tech_cols[1]:
        st.markdown("#### 数据处理:")
        st.write("Pandas")
        st.write("Numpy")
    
    with tech_cols[2]:
        st.markdown("#### 可视化:")
        st.write("Plotly")
        st.write("Matplotlib")
    
    with tech_cols[3]:
        st.markdown("#### 机器学习:")
        st.write("Scikit-learn")

# -------------------------- 2. 专业数据分析页面（仅最小化修改） --------------------------
elif page == "专业数据分析":
    st.title("📊专业数据分析")
    
    if not df.empty:
        # 1. 表格展示各专业每周平均学时、期中考试平均分和期末考试平均分
        if all(col in df.columns for col in ["专业", "期中考试分数", "期末考试分数", "每周学习时长（小时）"]):
            st.subheader("1. 各专业核心学习指标汇总")
            # 计算核心指标
            core_metrics = df.groupby("专业")[
                ["每周学习时长（小时）", "期中考试分数", "期末考试分数"]
            ].mean().round(2)
            # 重命名列名更直观
            core_metrics.columns = ["每周平均学时", "期中考试平均分", "期末考试平均分"]
            # 展示表格
            st.dataframe(core_metrics.reset_index(), use_container_width=True)
        
        # 2. 双层柱状图展示每个专业的男女性别比例
        if "专业" in df.columns and "性别" in df.columns:
            st.subheader("2. 各专业男女性别比例")
            col_plot1 = st.columns([1])[0]  # 单列展示
            # 计算性别数量（双层柱状图用数量更直观）
            gender_count = df.groupby(["专业", "性别"]).size().unstack(fill_value=0)
            # 确保列名是男/女（兼容数据）
            if "男" in gender_count.columns and "女" in gender_count.columns:
                gender_count = gender_count[["男", "女"]]
            
            with col_plot1:
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                # 双层堆叠柱状图
                gender_count.plot(kind="bar", ax=ax1, stacked=True, color=["#0099FF", "#99FFCC"], width=0.8)
                ax1.set_ylabel("学生人数")
                ax1.set_xlabel("专业")
                # 修复刻度标签匹配问题
                ax1.set_xticks(range(len(gender_count.index)))
                ax1.set_xticklabels(gender_count.index, rotation=45)
                ax1.legend(title="性别", bbox_to_anchor=(1.05, 1), loc='upper left')
                st.pyplot(fig1)
        
        # 3. 折线图展示每个专业的期中考试分数和期末考试分数
        if all(col in df.columns for col in ["专业", "期中考试分数", "期末考试分数"]):
            st.subheader("3. 各专业考试分数趋势")
            col_plot2 = st.columns([1])[0]
            # 计算平均分
            exam_scores = df.groupby("专业")[["期中考试分数", "期末考试分数"]].mean().round(2)
            
            with col_plot2:
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                # 纯折线图展示
                exam_scores.plot(kind="line", ax=ax2, marker="o", linewidth=2, 
                                 color=["#2ca02c", "#ffbb78"], markersize=8)
                ax2.set_ylabel("平均分")
                ax2.set_xlabel("专业")
                # 修复：先设置刻度位置，再设置标签
                ax2.set_xticks(range(len(exam_scores.index)))
                ax2.set_xticklabels(exam_scores.index, rotation=45)
                ax2.grid(True, alpha=0.3)
                ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                st.pyplot(fig2)
        
        # 4. 单层柱状图展示每个专业的平均上课出勤率
        if "专业" in df.columns and "上课出勤率" in df.columns:
            st.subheader("4. 各专业平均上课出勤率")
            col_plot3 = st.columns([1])[0]
            # 计算平均出勤率
            attend_rate = df.groupby("专业")["上课出勤率"].mean().round(2)
            
            with col_plot3:
                fig3, ax3 = plt.subplots(figsize=(10, 6))
                # 单层柱状图
                ax3.bar(attend_rate.index, attend_rate.values, color="#4CAF50", width=0.8)
                ax3.set_ylabel("平均上课出勤率（%）")
                ax3.set_xlabel("专业")
                # 修复刻度标签匹配问题
                ax3.set_xticks(range(len(attend_rate.index)))
                ax3.set_xticklabels(attend_rate.index, rotation=45)
                # 仅新增：固定Y轴范围，解决空白问题
                ax3.set_ylim(0, 100)
                # 给柱子添加数值标签
                for i, v in enumerate(attend_rate.values):
                    ax3.text(i, v + 1, f"{v}%", ha='center', va='bottom')  # 仅调整数值标签位置
                st.pyplot(fig3)
        
        # 5. 展示大数据管理专业的平均上课出勤率和期末考试
        target_major = "大数据管理"
        if target_major in df["专业"].values:
            st.subheader(f"5. {target_major}专业核心指标")
            col_plot4 = st.columns([1])[0]
            # 筛选数据并计算指标
            bigdata_df = df[df["专业"] == target_major]
            bigdata_metrics = {
                "平均上课出勤率": round(bigdata_df["上课出勤率"].mean(), 2),
                "期末考试平均分": round(bigdata_df["期末考试分数"].mean(), 2)
            }
            
            with col_plot4:
                fig4, ax4 = plt.subplots(figsize=(8, 5))
                # 双列柱状图展示两个指标
                x = list(bigdata_metrics.keys())
                y = list(bigdata_metrics.values())
                ax4.bar(x, y, color=["#FF9800", "#E91E63"], width=0.5)
                ax4.set_ylabel("数值")
                ax4.set_title(f"{target_major}专业核心指标")
                # 添加数值标签
                for i, v in enumerate(y):
                    ax4.text(i, v + 0.5, f"{v}", ha='center', va='bottom')
                st.pyplot(fig4)

    else:
        st.warning("暂无数据可展示")  # 基础提示组件

# -------------------------- 3. 成绩预测页面（完全保留你的原始代码） --------------------------
elif page == "成绩预测":
    st.title("🔍期末成绩预测")
    
    # 分数段说明（基础列+状态组件）
    st.subheader("分数段说明")
    col_excellent, col_pass, col_improve = st.columns(3)
    
    with col_excellent:
        st.success("✅ 优秀段（85分及以上）：保持当前学习状态，可拓展知识深度！")
    with col_pass:
        st.warning("⚠️ 合格段（60-84分）：巩固基础，定期错题复盘！")
    with col_improve:
        st.error("❌ 待提升段（60分以下）：加强投入，优先掌握核心内容！")
    
    st.write("请输入学生的学习信息，系统将预测其期末成绩并提供对应建议")
    
    # 输入表单（基础form组件）
    with st.form("predict_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            student_id = st.text_input("学号", value="1231231")  # 基础输入框
            gender = st.selectbox("性别", options=["男", "女"])  # 基础下拉框
            major_options = df["专业"].unique() if ("专业" in df.columns and not df.empty) else ["信息系统"]
            major = st.selectbox("专业", options=major_options)
        
        with col2:
            study_hours = st.slider("每周学习时长(小时)", min_value=0, max_value=50, value=29)  # 基础滑块
            attendance = st.slider("上课出勤率", min_value=0, max_value=100, value=100)
            midterm_score = st.slider("期中考试分数", min_value=0, max_value=100, value=63)
            homework_rate = st.slider("作业完成率", min_value=0, max_value=100, value=80)
        
        # 预测按钮（基础表单按钮）
        submit_btn = st.form_submit_button("预测期末成绩")
    
    # 预测逻辑+固定图片展示
    if submit_btn:
        # 简单预测算法
        predicted_score = midterm_score * 0.7 + study_hours * 0.5 + attendance * 0.1 + homework_rate * 0.2
        predicted_score = min(max(round(predicted_score, 1), 0), 100)
        
        # 显示预测结果（基础状态组件）
        st.subheader("🔍 预测结果")
        if predicted_score >= 80:
            st.success(f"预测期末成绩：{predicted_score} 分")
            advice = "学习建议：保持当前学习状态，可适当拓展知识深度，挑战更高难度的学习内容！"
            st.success(advice)
            # 若图片不存在可注释此行，不影响核心功能
            st.image("images/excellent.png",  width=500)
        
        elif predicted_score >= 60:
            st.warning(f"预测期末成绩：{predicted_score} 分")
            advice = "学习建议：巩固基础知识要点，定期进行错题复盘，针对薄弱环节加强练习！"
            st.warning(advice)
            # 若图片不存在可注释此行，不影响核心功能
            st.image("images/pass.png", width=500)
        
        else:
            st.error(f"预测期末成绩：{predicted_score} 分")
            advice = "学习建议：加油！需加强学习投入，优先掌握核心知识点，及时请教老师/同学！"
            st.error(advice)
            # 若图片不存在可注释此行，不影响核心功能
            st.image("images/improve.png",  width=500)
