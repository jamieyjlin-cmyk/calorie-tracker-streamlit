"""
計算邏輯
"""
from datetime import datetime


def calculate_bmr(height_cm, weight_kg, age, gender):
    """
    計算基礎代謝率 (BMR)
    使用 Mifflin-St Jeor 公式
    """
    if not all([height_cm, weight_kg, age, gender]):
        return 0
    
    if gender == 'M':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    return max(0, bmr)


def calculate_tdee(bmr, activity_level):
    """
    計算每日總消耗熱量 (TDEE)
    """
    activity_multipliers = {
        'sedentary': 1.2,      # 久坐
        'light': 1.375,        # 輕度活動
        'moderate': 1.55,      # 中度活動
        'active': 1.725,       # 高度活動
        'very_active': 1.9     # 極高活動
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)
    return bmr * multiplier


def calculate_daily_budget(profile):
    """
    計算每日有效預算，考慮預算模式
    """
    if not profile:
        return 0
    
    base_budget = profile.get('tdee', 0)
    budget_mode = profile.get('budget_mode', 'none')
    
    if budget_mode == 'payday':
        # 發薪日模式
        today = datetime.now().weekday()  # 0=Monday, 6=Sunday
        payday_day = profile.get('payday_day_of_week', 6)
        
        if today == payday_day:
            return base_budget + profile.get('payday_bonus', 500)
    
    elif budget_mode == 'savings':
        # 定存提領模式
        today = datetime.now().weekday()
        
        if today >= 5:  # 週末 (Saturday=5, Sunday=6)
            return base_budget + profile.get('accumulated_savings', 0)
        else:
            return base_budget - profile.get('daily_savings', 100)
    
    return base_budget


def calculate_weight_change(calorie_balance, days=1):
    """
    根據熱量盈虧估計體重變化
    1 kg 體脂 ≈ 7700 kcal
    """
    kg_per_kcal = 1 / 7700
    return calorie_balance * days * kg_per_kcal


def format_calories(calories):
    """格式化熱量顯示"""
    return f"{int(calories)} kcal"


def format_weight(weight):
    """格式化體重顯示"""
    return f"{weight:.1f} kg"


def get_budget_status(consumed, budget):
    """
    獲取預算狀態
    返回 (餘額, 百分比, 狀態)
    """
    balance = budget - consumed
    percentage = (consumed / budget * 100) if budget > 0 else 0
    
    if percentage <= 80:
        status = '✅ 健康'
    elif percentage <= 100:
        status = '⚠️ 接近'
    else:
        status = '❌ 超標'
    
    return balance, percentage, status


def get_water_status(cups, goal):
    """
    獲取飲水狀態
    """
    percentage = (cups / goal * 100) if goal > 0 else 0
    
    if percentage >= 100:
        status = '✅ 達成'
    elif percentage >= 80:
        status = '🔶 接近'
    else:
        status = '⚠️ 未達'
    
    return percentage, status


def get_activity_level_name(level):
    """獲取活動量等級名稱"""
    names = {
        'sedentary': '久坐',
        'light': '輕度活動',
        'moderate': '中度活動',
        'active': '高度活動',
        'very_active': '極高活動'
    }
    return names.get(level, '中度活動')


def get_budget_mode_name(mode):
    """獲取預算模式名稱"""
    names = {
        'none': '無特殊預算',
        'payday': '發薪日模式',
        'savings': '定存提領模式'
    }
    return names.get(mode, '無特殊預算')


def get_day_name(day_of_week):
    """獲取星期名稱"""
    days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    return days[day_of_week] if 0 <= day_of_week < 7 else '未知'
