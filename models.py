"""
數據庫模型定義
"""
import sqlite3
from datetime import datetime
import hashlib
import os

DB_PATH = "calorie_tracker.db"


def init_db():
    """初始化數據庫"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 用戶表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 用戶資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            height_cm REAL,
            weight_kg REAL,
            gender TEXT,
            age INTEGER,
            activity_level TEXT DEFAULT 'moderate',
            target_weight_kg REAL,
            target_date DATE,
            daily_water_goal_cups INTEGER DEFAULT 8,
            budget_mode TEXT DEFAULT 'none',
            payday_day_of_week INTEGER,
            payday_bonus REAL DEFAULT 500,
            daily_savings REAL DEFAULT 100,
            accumulated_savings REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 食物表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            calories REAL NOT NULL,
            protein_g REAL DEFAULT 0,
            carbs_g REAL DEFAULT 0,
            sugar_g REAL DEFAULT 0,
            unit TEXT DEFAULT '份'
        )
    ''')
    
    # 飲食記錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            food_name TEXT NOT NULL,
            category TEXT NOT NULL,
            calories REAL NOT NULL,
            quantity REAL DEFAULT 1,
            unit TEXT DEFAULT '份',
            protein_g REAL DEFAULT 0,
            carbs_g REAL DEFAULT 0,
            sugar_g REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 自訂食物歷史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_food_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            calories REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 飲水記錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS water_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            cups REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()


def hash_password(password):
    """密碼哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """驗證密碼"""
    return hash_password(password) == password_hash


# 用戶操作
def create_user(username, password):
    """創建用戶"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, hash_password(password))
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_user(username):
    """獲取用戶"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_user_by_id(user_id):
    """通過 ID 獲取用戶"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


# 用戶資料操作
def save_user_profile(user_id, profile_data):
    """保存用戶資料"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 檢查是否存在
    cursor.execute('SELECT id FROM user_profiles WHERE user_id = ?', (user_id,))
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute('''
            UPDATE user_profiles SET
            height_cm = ?, weight_kg = ?, gender = ?, age = ?,
            activity_level = ?, target_weight_kg = ?, target_date = ?,
            daily_water_goal_cups = ?, budget_mode = ?,
            payday_day_of_week = ?, payday_bonus = ?, daily_savings = ?,
            updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        ''', (
            profile_data.get('height_cm'),
            profile_data.get('weight_kg'),
            profile_data.get('gender'),
            profile_data.get('age'),
            profile_data.get('activity_level', 'moderate'),
            profile_data.get('target_weight_kg'),
            profile_data.get('target_date'),
            profile_data.get('daily_water_goal_cups', 8),
            profile_data.get('budget_mode', 'none'),
            profile_data.get('payday_day_of_week'),
            profile_data.get('payday_bonus', 500),
            profile_data.get('daily_savings', 100),
            user_id
        ))
    else:
        cursor.execute('''
            INSERT INTO user_profiles
            (user_id, height_cm, weight_kg, gender, age, activity_level,
             target_weight_kg, target_date, daily_water_goal_cups, budget_mode,
             payday_day_of_week, payday_bonus, daily_savings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            profile_data.get('height_cm'),
            profile_data.get('weight_kg'),
            profile_data.get('gender'),
            profile_data.get('age'),
            profile_data.get('activity_level', 'moderate'),
            profile_data.get('target_weight_kg'),
            profile_data.get('target_date'),
            profile_data.get('daily_water_goal_cups', 8),
            profile_data.get('budget_mode', 'none'),
            profile_data.get('payday_day_of_week'),
            profile_data.get('payday_bonus', 500),
            profile_data.get('daily_savings', 100)
        ))
    
    conn.commit()
    conn.close()


def get_user_profile(user_id):
    """獲取用戶資料"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT height_cm, weight_kg, gender, age, activity_level,
               target_weight_kg, target_date, daily_water_goal_cups,
               budget_mode, payday_day_of_week, payday_bonus, daily_savings,
               accumulated_savings
        FROM user_profiles WHERE user_id = ?
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'height_cm': result[0],
            'weight_kg': result[1],
            'gender': result[2],
            'age': result[3],
            'activity_level': result[4],
            'target_weight_kg': result[5],
            'target_date': result[6],
            'daily_water_goal_cups': result[7],
            'budget_mode': result[8],
            'payday_day_of_week': result[9],
            'payday_bonus': result[10],
            'daily_savings': result[11],
            'accumulated_savings': result[12]
        }
    return None


# 食物操作
def init_foods():
    """初始化預設食物"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 檢查是否已有食物
    cursor.execute('SELECT COUNT(*) FROM foods')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    foods = [
        # 水果
        ('蘋果', 'fruit', 52, 0.3, 14, 10, '個'),
        ('香蕉', 'fruit', 89, 1.1, 23, 12, '個'),
        ('橙', 'fruit', 47, 0.9, 12, 9, '個'),
        ('葡萄', 'fruit', 67, 0.6, 17, 16, '份'),
        
        # 蔬菜
        ('番茄', 'vegetable', 18, 0.9, 3.9, 2.6, '個'),
        ('生菜', 'vegetable', 15, 1.2, 2.9, 0.6, '份'),
        ('胡蘿蔔', 'vegetable', 41, 0.9, 10, 4.7, '根'),
        ('花椰菜', 'vegetable', 34, 2.8, 7, 1.7, '份'),
        
        # 乳品
        ('牛奶', 'dairy', 61, 3.2, 4.8, 5, '杯'),
        ('優格', 'dairy', 59, 3.5, 3.3, 2.7, '杯'),
        ('起司', 'dairy', 402, 25, 1.3, 0.7, '片'),
        
        # 油脂與堅果
        ('花生醬', 'fat_nut', 588, 25, 20, 7, '湯匙'),
        ('杏仁', 'fat_nut', 579, 21, 22, 4.4, '份'),
        ('橄欖油', 'fat_nut', 884, 0, 0, 0, '湯匙'),
        
        # 豆魚蛋肉
        ('雞蛋', 'protein', 155, 13, 1.1, 1.1, '個'),
        ('雞胸肉', 'protein', 165, 31, 0, 0, '份'),
        ('豆腐', 'protein', 76, 8, 1.9, 0.1, '份'),
        ('鮭魚', 'protein', 208, 20, 0, 0, '份'),
        
        # 全穀雜糧
        ('白米飯', 'grain', 130, 2.7, 28, 0.1, '碗'),
        ('全麥麵包', 'grain', 265, 9, 49, 8, '片'),
        ('燕麥', 'grain', 389, 17, 66, 0, '杯'),
        ('意大利麵', 'grain', 131, 5, 25, 0.6, '份'),
    ]
    
    cursor.executemany(
        'INSERT INTO foods (name, category, calories, protein_g, carbs_g, sugar_g, unit) VALUES (?, ?, ?, ?, ?, ?, ?)',
        foods
    )
    
    conn.commit()
    conn.close()


def get_foods_by_category(category):
    """獲取指定類別的食物"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, name, calories, protein_g, carbs_g, sugar_g, unit FROM foods WHERE category = ? ORDER BY name',
        (category,)
    )
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': r[0],
            'name': r[1],
            'calories': r[2],
            'protein_g': r[3],
            'carbs_g': r[4],
            'sugar_g': r[5],
            'unit': r[6]
        }
        for r in results
    ]


# 飲食記錄操作
def add_food_log(user_id, date, food_name, category, calories, quantity, unit, protein_g=0, carbs_g=0, sugar_g=0):
    """添加飲食記錄"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO food_logs
        (user_id, date, food_name, category, calories, quantity, unit, protein_g, carbs_g, sugar_g)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, date, food_name, category, calories, quantity, unit, protein_g, carbs_g, sugar_g))
    conn.commit()
    conn.close()


def get_food_logs(user_id, date):
    """獲取指定日期的飲食記錄"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, food_name, category, calories, quantity, unit, protein_g, carbs_g, sugar_g
        FROM food_logs WHERE user_id = ? AND date = ? ORDER BY created_at DESC
    ''', (user_id, date))
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': r[0],
            'food_name': r[1],
            'category': r[2],
            'calories': r[3],
            'quantity': r[4],
            'unit': r[5],
            'protein_g': r[6],
            'carbs_g': r[7],
            'sugar_g': r[8]
        }
        for r in results
    ]


def delete_food_log(log_id):
    """刪除飲食記錄"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM food_logs WHERE id = ?', (log_id,))
    conn.commit()
    conn.close()


# 自訂食物操作
def add_custom_food(user_id, food_name, calories):
    """添加自訂食物"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO custom_food_history (user_id, food_name, calories) VALUES (?, ?, ?)',
        (user_id, food_name, calories)
    )
    conn.commit()
    conn.close()


def get_custom_foods(user_id):
    """獲取用戶的自訂食物"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT DISTINCT food_name, calories FROM custom_food_history WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    )
    results = cursor.fetchall()
    conn.close()
    
    return [{'name': r[0], 'calories': r[1]} for r in results]


# 飲水記錄操作
def save_water_log(user_id, date, cups):
    """保存飲水記錄"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM water_logs WHERE user_id = ? AND date = ?', (user_id, date))
    exists = cursor.fetchone()
    
    if exists:
        cursor.execute('UPDATE water_logs SET cups = ? WHERE user_id = ? AND date = ?', (cups, user_id, date))
    else:
        cursor.execute('INSERT INTO water_logs (user_id, date, cups) VALUES (?, ?, ?)', (user_id, date, cups))
    
    conn.commit()
    conn.close()


def get_water_log(user_id, date):
    """獲取飲水記錄"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT cups FROM water_logs WHERE user_id = ? AND date = ?', (user_id, date))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else 0


def get_monthly_water_logs(user_id, year, month):
    """獲取月度飲水記錄"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, cups FROM water_logs
        WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        ORDER BY date
    ''', (user_id, str(year).zfill(4), str(month).zfill(2)))
    results = cursor.fetchall()
    conn.close()
    
    return [{'date': r[0], 'cups': r[1]} for r in results]


def get_monthly_food_logs(user_id, year, month):
    """獲取月度飲食記錄"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, SUM(calories) as total_calories, SUM(protein_g) as total_protein,
               SUM(carbs_g) as total_carbs, SUM(sugar_g) as total_sugar
        FROM food_logs
        WHERE user_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
        GROUP BY date
        ORDER BY date
    ''', (user_id, str(year).zfill(4), str(month).zfill(2)))
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'date': r[0],
            'total_calories': r[1] or 0,
            'total_protein': r[2] or 0,
            'total_carbs': r[3] or 0,
            'total_sugar': r[4] or 0
        }
        for r in results
    ]
