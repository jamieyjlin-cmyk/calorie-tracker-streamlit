"""
飲食熱量管理系統 - Streamlit 版本
全 Python 實現
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import models
import calculations

# 頁面配置
st.set_page_config(
    page_title="🥗 飲食熱量管理系統",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化數據庫
models.init_db()
models.init_foods()

# 自訂 CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .success-text {
        color: #2ecc71;
        font-weight: bold;
    }
    .warning-text {
        color: #f39c12;
        font-weight: bold;
    }
    .danger-text {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化會話狀態"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None


def login_page():
    """登入頁面"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🥗 飲食熱量管理系統")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["登入", "註冊"])
        
        with tab1:
            st.subheader("登入")
            username = st.text_input("用戶名", key="login_username")
            password = st.text_input("密碼", type="password", key="login_password")
            
            if st.button("登入", use_container_width=True):
                user = models.get_user(username)
                if user and models.verify_password(password, user[1]):
                    st.session_state.user_id = user[0]
                    st.session_state.username = username
                    st.success("登入成功！")
                    st.rerun()
                else:
                    st.error("用戶名或密碼錯誤")
        
        with tab2:
            st.subheader("註冊")
            new_username = st.text_input("新用戶名", key="register_username")
            new_password = st.text_input("新密碼", type="password", key="register_password")
            confirm_password = st.text_input("確認密碼", type="password", key="confirm_password")
            
            if st.button("註冊", use_container_width=True):
                if not new_username or not new_password:
                    st.error("用戶名和密碼不能為空")
                elif new_password != confirm_password:
                    st.error("密碼不一致")
                else:
                    user_id = models.create_user(new_username, new_password)
                    if user_id:
                        st.success("註冊成功！請登入")
                    else:
                        st.error("用戶名已存在")


def profile_page():
    """基本資料設定頁面"""
    st.header("👤 基本資料設定")
    
    profile = models.get_user_profile(st.session_state.user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("身體資訊")
        height = st.number_input("身高 (cm)", min_value=100, max_value=250, 
                                value=int(profile['height_cm']) if profile and profile['height_cm'] else 170)
        weight = st.number_input("體重 (kg)", min_value=30.0, max_value=200.0, value=float(profile['weight_kg']) if profile and profile['weight_kg'] else 70.0)
        age = st.number_input("年齡", min_value=10, max_value=100,
                             value=int(profile['age']) if profile and profile['age'] else 30)
        gender = st.selectbox("性別", ["M", "F"],
                             index=0 if not profile or profile['gender'] == 'M' else 1)
    
    with col2:
        st.subheader("活動量與目標")
        activity_level = st.selectbox(
            "活動量等級",
            ["sedentary", "light", "moderate", "active", "very_active"],
            format_func=calculations.get_activity_level_name,
            index=2 if not profile else ["sedentary", "light", "moderate", "active", "very_active"].index(profile['activity_level'])
        )
        target_weight = st.number_input("目標體重 (kg)", min_value=30.0, max_value=200.0, value=float(profile['target_weight_kg']) if profile and profile['target_weight_kg'] else 65.0)
        target_date = st.date_input("目標日期",
                                   value=datetime.strptime(profile['target_date'], '%Y-%m-%d').date() if profile and profile['target_date'] else date.today() + timedelta(days=90))
    
    # 計算 BMR 和 TDEE
    bmr = calculations.calculate_bmr(height, weight, age, gender)
    tdee = calculations.calculate_tdee(bmr, activity_level)
    
    st.markdown("---")
    st.subheader("📊 代謝指標")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("基礎代謝率 (BMR)", f"{int(bmr)} kcal")
    with col2:
        st.metric("每日消耗 (TDEE)", f"{int(tdee)} kcal")
    with col3:
        weight_diff = weight - target_weight
        st.metric("目標差距", f"{weight_diff:.1f} kg")
    with col4:
        days_left = (target_date - date.today()).days
        st.metric("剩餘天數", f"{max(0, days_left)} 天")
    
    # 飲水目標
    st.markdown("---")
    st.subheader("💧 飲水管理")
    daily_water_goal = st.slider("每日飲水目標 (杯)", 1, 15, 
                                 value=int(profile['daily_water_goal_cups']) if profile else 8,
                                 help="✅ 1杯 = 250ml")
    
    # 預算管理
    st.markdown("---")
    st.subheader("💰 預算管理模式")
    
    budget_mode = st.selectbox(
        "選擇預算模式",
        ["none", "payday", "savings"],
        format_func=calculations.get_budget_mode_name,
        index=0 if not profile else ["none", "payday", "savings"].index(profile['budget_mode'])
    )
    
    payday_day = None
    payday_bonus = 500
    daily_savings = 100
    
    if budget_mode == "payday":
        col1, col2 = st.columns(2)
        with col1:
            payday_day = st.selectbox("發薪日", 
                                     range(7),
                                     format_func=calculations.get_day_name,
                                     index=profile['payday_day_of_week'] if profile and profile['payday_day_of_week'] else 5)
        with col2:
            payday_bonus = st.number_input("特別預算 (kcal)", min_value=0, max_value=2000,
                                          value=int(profile['payday_bonus']) if profile else 500)
        
        st.info(f"📌 在{calculations.get_day_name(payday_day)}，您的每日預算將增加 {payday_bonus} kcal")
    
    elif budget_mode == "savings":
        col1, col2 = st.columns(2)
        with col1:
            daily_savings = st.number_input("每日定存 (kcal)", min_value=0, max_value=500,
                                           value=int(profile['daily_savings']) if profile else 100)
        with col2:
            st.metric("累積定存", f"{int(profile['accumulated_savings']) if profile else 0} kcal")
        
        st.info(f"🏦 平日預算 = TDEE - {daily_savings} kcal，週末可提領累積金額")
    
    # 保存按鈕
    if st.button("💾 保存設定", use_container_width=True):
        profile_data = {
            'height_cm': height,
            'weight_kg': weight,
            'gender': gender,
            'age': age,
            'activity_level': activity_level,
            'target_weight_kg': target_weight,
            'target_date': target_date.isoformat(),
            'daily_water_goal_cups': daily_water_goal,
            'budget_mode': budget_mode,
            'payday_day_of_week': payday_day,
            'payday_bonus': payday_bonus,
            'daily_savings': daily_savings
        }
        models.save_user_profile(st.session_state.user_id, profile_data)
        st.success("✅ 設定已保存")


def daily_log_page():
    """每日飲食記帳頁面"""
    st.header("📋 每日飲食記帳")
    
    profile = models.get_user_profile(st.session_state.user_id)
    if not profile:
        st.warning("請先設定基本資料")
        return
    
    # 計算每日預算
    bmr = calculations.calculate_bmr(profile['height_cm'], profile['weight_kg'], 
                                     profile['age'], profile['gender'])
    tdee = calculations.calculate_tdee(bmr, profile['activity_level'])
    
    profile_with_tdee = {**profile, 'tdee': tdee}
    daily_budget = calculations.calculate_daily_budget(profile_with_tdee)
    
    # 選擇日期
    selected_date = st.date_input("選擇日期", value=date.today())
    
    # 獲取該日飲食記錄
    food_logs = models.get_food_logs(st.session_state.user_id, selected_date)
    water_log = models.get_water_log(st.session_state.user_id, selected_date)
    
    # 計算總數據
    total_calories = sum(log['calories'] for log in food_logs)
    total_protein = sum(log['protein_g'] for log in food_logs)
    total_carbs = sum(log['carbs_g'] for log in food_logs)
    total_sugar = sum(log['sugar_g'] for log in food_logs)
    
    # 顯示每日摘要
    st.subheader("📊 每日摘要")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        balance, percentage, status = calculations.get_budget_status(total_calories, daily_budget)
        st.metric("熱量攝取", f"{int(total_calories)} kcal", delta=f"{int(balance):+d} kcal")
    with col2:
        st.metric("蛋白質", f"{total_protein:.1f}g")
    with col3:
        st.metric("碳水化合物", f"{total_carbs:.1f}g")
    with col4:
        st.metric("糖分", f"{total_sugar:.1f}g")
    with col5:
        water_percentage, water_status = calculations.get_water_status(water_log, profile['daily_water_goal_cups'])
        st.metric("飲水進度", f"{int(water_percentage)}%", delta=water_status)
    
    # 預算進度條
    st.markdown("---")
    st.subheader("💰 預算進度")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        balance, percentage, status = calculations.get_budget_status(total_calories, daily_budget)
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=percentage,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "預算使用百分比"},
            delta={'reference': 100},
            gauge={'axis': {'range': [0, 150]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 80], 'color': "#2ecc71"},
                       {'range': [80, 100], 'color': "#f39c12"},
                       {'range': [100, 150], 'color': "#e74c3c"}
                   ],
                   'threshold': {
                       'line': {'color': "red", 'width': 4},
                       'thickness': 0.75,
                       'value': 100}}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.metric("每日預算", f"{int(daily_budget)} kcal")
        st.metric("已攝取", f"{int(total_calories)} kcal")
        st.metric("餘額", f"{int(balance)} kcal")
    
    # 添加食物
    st.markdown("---")
    st.subheader("➕ 新增食物")
    
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox("食物類別",
                               ["fruit", "vegetable", "dairy", "fat_nut", "protein", "grain"],
                               format_func=lambda x: {"fruit": "🍎 水果", "vegetable": "🥬 蔬菜",
                                                      "dairy": "🥛 乳品", "fat_nut": "🥜 油脂與堅果",
                                                      "protein": "🍗 豆魚蛋肉", "grain": "🌾 全穀雜糧"}.get(x))
    
    with col2:
        food_type = st.radio("食物類型", ["預設食物", "自訂食物"], horizontal=True)
    
    if food_type == "預設食物":
        foods = models.get_foods_by_category(category)
        if foods:
            food_names = [f['name'] for f in foods]
            selected_food_idx = st.selectbox("選擇食物", range(len(foods)),
                                            format_func=lambda i: f"{foods[i]['name']} ({int(foods[i]['calories'])} kcal)")
            selected_food = foods[selected_food_idx]
            
            quantity = st.number_input("份量", min_value=0.1, value=1.0, step=0.1)
            
            if st.button("新增食物", use_container_width=True):
                total_cal = selected_food['calories'] * quantity
                models.add_food_log(
                    st.session_state.user_id,
                    selected_date,
                    selected_food['name'],
                    category,
                    total_cal,
                    quantity,
                    selected_food['unit'],
                    selected_food['protein_g'] * quantity,
                    selected_food['carbs_g'] * quantity,
                    selected_food['sugar_g'] * quantity
                )
                st.success(f"✅ 已新增 {selected_food['name']}")
                st.rerun()
    
    else:  # 自訂食物
        custom_name = st.text_input("食物名稱")
        custom_calories = st.number_input("熱量 (kcal)", min_value=0, value=100)
        custom_quantity = st.number_input("份量", min_value=0.1, value=1.0, step=0.1)
        
        if st.button("新增自訂食物", use_container_width=True):
            if custom_name:
                total_cal = custom_calories * custom_quantity
                models.add_food_log(
                    st.session_state.user_id,
                    selected_date,
                    custom_name,
                    category,
                    total_cal,
                    custom_quantity,
                    "份",
                    0, 0, 0
                )
                models.add_custom_food(st.session_state.user_id, custom_name, custom_calories)
                st.success(f"✅ 已新增自訂食物 {custom_name}")
                st.rerun()
            else:
                st.error("請輸入食物名稱")
    
    # 顯示飲食記錄
    st.markdown("---")
    st.subheader("📝 今日飲食記錄")
    
    if food_logs:
        df = pd.DataFrame(food_logs)
        df = df[['food_name', 'category', 'calories', 'quantity', 'unit', 'protein_g', 'carbs_g', 'sugar_g']]
        
        # 創建可刪除的表格
        for idx, log in enumerate(food_logs):
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                st.write(f"**{log['food_name']}** ({log['quantity']}{log['unit']})")
            with col2:
                st.write(f"{int(log['calories'])} kcal")
            with col3:
                st.write(f"{log['protein_g']:.1f}g P")
            with col4:
                st.write(f"{log['carbs_g']:.1f}g C")
            with col5:
                if st.button("🗑️", key=f"delete_{log['id']}"):
                    models.delete_food_log(log['id'])
                    st.success("已刪除")
                    st.rerun()
    else:
        st.info("今日還沒有飲食記錄")
    
    # 飲水管理
    st.markdown("---")
    st.subheader("💧 飲水管理")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        new_water = st.slider("飲水量 (杯)", 0, profile['daily_water_goal_cups'] * 2, 
                             value=int(water_log), help="✅ 1杯 = 250ml")
    with col2:
        if st.button("💾 保存飲水", use_container_width=True):
            models.save_water_log(st.session_state.user_id, selected_date, new_water)
            st.success("✅ 飲水已保存")
            st.rerun()


def monthly_report_page():
    """月度報表頁面"""
    st.header("📊 月度報表")
    
    profile = models.get_user_profile(st.session_state.user_id)
    if not profile:
        st.warning("請先設定基本資料")
        return
    
    # 計算 TDEE
    bmr = calculations.calculate_bmr(profile['height_cm'], profile['weight_kg'], 
                                     profile['age'], profile['gender'])
    tdee = calculations.calculate_tdee(bmr, profile['activity_level'])
    
    # 選擇月份
    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input("年份", min_value=2020, max_value=2100, value=datetime.now().year)
    with col2:
        month = st.number_input("月份", min_value=1, max_value=12, value=datetime.now().month)
    
    # 獲取月度數據
    food_logs = models.get_monthly_food_logs(st.session_state.user_id, year, month)
    water_logs = models.get_monthly_water_logs(st.session_state.user_id, year, month)
    
    if not food_logs:
        st.info("該月份沒有飲食記錄")
        return
    
    # 轉換為 DataFrame
    df_food = pd.DataFrame(food_logs)
    df_food['date'] = pd.to_datetime(df_food['date'])
    df_food['balance'] = df_food['total_calories'] - tdee
    
    # 月度統計
    st.subheader("📈 月度統計")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_calories = df_food['total_calories'].sum()
        st.metric("總熱量", f"{int(total_calories)} kcal")
    with col2:
        total_balance = df_food['balance'].sum()
        st.metric("月度盈虧", f"{int(total_balance):+d} kcal")
    with col3:
        weight_change = calculations.calculate_weight_change(total_balance, 30)
        st.metric("預計體重變化", f"{weight_change:+.2f} kg")
    with col4:
        if water_logs:
            avg_water = sum(w['cups'] for w in water_logs) / len(water_logs)
            water_achievement = (avg_water / profile['daily_water_goal_cups'] * 100)
            st.metric("平均飲水達成率", f"{water_achievement:.1f}%")
    
    # 熱量盈虧圖表
    st.subheader("📊 每日熱量盈虧")
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_food['date'],
        y=df_food['balance'],
        name='熱量盈虧',
        marker_color=['#2ecc71' if x >= 0 else '#e74c3c' for x in df_food['balance']]
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(
        title="每日熱量盈虧",
        xaxis_title="日期",
        yaxis_title="熱量 (kcal)",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 飲水達成率
    if water_logs:
        st.subheader("💧 飲水達成率")
        df_water = pd.DataFrame(water_logs)
        df_water['date'] = pd.to_datetime(df_water['date'])
        df_water['achievement'] = (df_water['cups'] / profile['daily_water_goal_cups'] * 100).clip(upper=100)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_water['date'],
            y=df_water['achievement'],
            name='達成率',
            marker_color='#3498db'
        ))
        fig.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="目標")
        fig.update_layout(
            title="飲水達成率",
            xaxis_title="日期",
            yaxis_title="達成率 (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def main():
    """主函數"""
    init_session_state()
    
    # 側邊欄
    with st.sidebar:
        st.title("🥗 飲食熱量管理")
        
        if st.session_state.user_id:
            st.write(f"👤 {st.session_state.username}")
            st.markdown("---")
            
            page = st.radio(
                "選擇頁面",
                ["每日記帳", "基本資料", "月度報表"],
                key="page_selector"
            )
            
            st.markdown("---")
            if st.button("登出", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.username = None
                st.rerun()
        else:
            page = None
    
    # 主內容
    if not st.session_state.user_id:
        login_page()
    else:
        if page == "每日記帳":
            daily_log_page()
        elif page == "基本資料":
            profile_page()
        elif page == "月度報表":
            monthly_report_page()


if __name__ == "__main__":
    main()
