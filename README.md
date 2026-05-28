# 🥗 飲食熱量管理系統 - Streamlit 版本

全 Python 實現的智能飲食熱量追蹤和管理應用，使用 Streamlit 框架構建。

## ✨ 主要功能

### 📋 每日飲食記帳
- 支援 6 大食物類別（水果、蔬菜、乳品、油脂與堅果、豆魚蛋肉、全穀雜糧）
- **自訂食物功能**：可新增並編輯自訂食物的熱量
- 自訂食物歷史記錄，方便快速選擇
- 份量調整自動計算熱量
- 每日摘要統計（總熱量、蛋白質、碳水、糖分）
- 熱量餘額實時顯示

### 👤 基本資料設定
- 身高、體重、性別、年齡設定
- 活動量等級選擇
- 目標體重和目標日期設定
- 每日飲水目標設定（1杯 = 250ml）
- **💰 預算管理模式**
  - **發薪日模式**：在指定星期幾自動加 500 kcal 特別預算
  - **定存提領模式**：平日每天存 100 kcal，週末提領累積金額
  - 自動計算 BMR、TDEE 和每日預算

### 💧 飲水管理
- 每日飲水量記錄
- 進度條視覺化顯示
- 同時顯示杯數和毫升數
- 月度飲水達成率統計

### 📊 月度報表
- 每日熱量盈虧長條圖
- 月度統計（總熱量、月度盈虧、體重變化估計）
- 飲水達成率分析
- 交互式圖表展示

## 🚀 快速開始

### 環境要求
- Python 3.8+
- Streamlit 1.28+
- Pandas 2.0+
- Plotly 5.17+

### 安裝步驟

1. **克隆或下載項目**
```bash
git clone <repository-url>
cd calorie-tracker-streamlit
```

2. **創建虛擬環境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **運行應用**
```bash
streamlit run app.py
```

5. **訪問應用**
打開瀏覽器訪問 `http://localhost:8501`

## 📁 項目結構

```
calorie-tracker-streamlit/
├── app.py               # Streamlit 主應用
├── models.py            # 數據庫模型和操作
├── calculations.py      # 計算邏輯（BMR, TDEE 等）
├── requirements.txt     # Python 依賴
├── calorie_tracker.db   # SQLite 數據庫（自動生成）
├── .gitignore           # Git 忽略文件
├── README.md            # 本文件
└── LICENSE              # MIT 許可證
```

## 🔧 核心模塊說明

### app.py
- **login_page()** - 用戶登入和註冊
- **profile_page()** - 基本資料設定和預算管理
- **daily_log_page()** - 每日飲食記帳
- **monthly_report_page()** - 月度報表

### models.py
- **init_db()** - 初始化數據庫
- **init_foods()** - 初始化預設食物
- **用戶操作** - create_user, get_user, get_user_by_id
- **資料操作** - save_user_profile, get_user_profile
- **食物操作** - get_foods_by_category, add_custom_food
- **記錄操作** - add_food_log, get_food_logs, delete_food_log
- **飲水操作** - save_water_log, get_water_log, get_monthly_water_logs

### calculations.py
- **calculate_bmr()** - 基礎代謝率（Mifflin-St Jeor 公式）
- **calculate_tdee()** - 每日總消耗熱量
- **calculate_daily_budget()** - 考慮預算模式的每日預算
- **calculate_weight_change()** - 根據熱量盈虧估計體重變化
- **get_budget_status()** - 預算狀態和進度
- **get_water_status()** - 飲水狀態

## 💡 使用說明

### 設定預算管理

1. **進入「基本資料設定」頁面**
2. **選擇預算模式**：
   - **無特殊預算**：每日預算 = TDEE
   - **發薪日模式**：選擇星期幾，該天預算 = TDEE + 500 kcal
   - **定存提領模式**：平日預算 = TDEE - 100 kcal，週末預算 = TDEE + 累積金額

3. **自訂預算金額**（可選）
4. **保存設定**

### 記錄飲食

1. **進入「每日記帳」頁面**
2. **選擇食物類別**
3. **選擇或自訂食物名稱**
4. **調整份量**（自動計算熱量）
5. **點擊「新增食物」**
6. **查看每日摘要和熱量餘額**

### 查看報表

1. **進入「月度報表」頁面**
2. **選擇年份和月份**
3. **查看熱量盈虧圖表和月度統計**
4. **查看飲水達成率**

## 🔐 安全性

- 使用 Streamlit Session State 進行用戶認證
- 密碼使用 SHA-256 安全哈希
- 所有 API 操作都需要登入驗證
- SQLite 數據庫存儲本地

## 📊 數據庫模型

### users
- `id` - 主鍵
- `username` - 用戶名（唯一）
- `password_hash` - 密碼哈希
- `created_at` - 創建時間

### user_profiles
- `id` - 主鍵
- `user_id` - 用戶 ID（外鍵）
- `height_cm` - 身高（cm）
- `weight_kg` - 體重（kg）
- `gender` - 性別（M/F）
- `age` - 年齡
- `activity_level` - 活動量等級
- `target_weight_kg` - 目標體重
- `target_date` - 目標日期
- `daily_water_goal_cups` - 每日飲水目標（杯）
- `budget_mode` - 預算模式（none/payday/savings）
- `payday_day_of_week` - 發薪日（0-6）
- `payday_bonus` - 發薪日特別預算（kcal）
- `daily_savings` - 每日定存金額（kcal）
- `accumulated_savings` - 累積定存金額（kcal）

### foods
- `id` - 主鍵
- `name` - 食物名稱
- `category` - 食物類別
- `calories` - 熱量（kcal）
- `protein_g` - 蛋白質（g）
- `carbs_g` - 碳水化合物（g）
- `sugar_g` - 糖分（g）
- `unit` - 單位

### food_logs
- `id` - 主鍵
- `user_id` - 用戶 ID（外鍵）
- `date` - 日期
- `food_name` - 食物名稱
- `category` - 食物類別
- `calories` - 熱量（kcal）
- `quantity` - 份量
- `unit` - 單位
- `protein_g` - 蛋白質（g）
- `carbs_g` - 碳水化合物（g）
- `sugar_g` - 糖分（g）

### custom_food_history
- `id` - 主鍵
- `user_id` - 用戶 ID（外鍵）
- `food_name` - 食物名稱
- `calories` - 熱量（kcal）
- `created_at` - 創建時間

### water_logs
- `id` - 主鍵
- `user_id` - 用戶 ID（外鍵）
- `date` - 日期
- `cups` - 飲水量（杯）

## 🛠️ 開發

### 運行測試
```bash
# 如果有測試文件
pytest
```

### 代碼風格
- 遵循 PEP 8 規範
- 使用 4 空格縮進

### 貢獻指南
1. Fork 本項目
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 許可證

本項目採用 MIT 許可證。詳見 [LICENSE](LICENSE) 文件。

## 🤝 支持

如有問題或建議，請提交 Issue 或 Pull Request。

## 🎯 未來計劃

- [ ] 支援多語言（英文、日文等）
- [ ] 添加運動記錄功能
- [ ] 支援營養素目標設定
- [ ] 添加食物照片識別功能
- [ ] 支援數據導出（CSV、PDF）
- [ ] 移動應用版本
- [ ] 社群分享功能
- [ ] 雲端同步功能

---

**最後更新**：2026 年 5 月 26 日
