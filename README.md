# 💰 Budgeteer - Personal Expense Tracker

A Streamlit-based personal expense dashboard that automatically parses bank statements, categorizes transactions, and provides interactive visualizations for budget analysis.

---

## 📋 Project Overview

This application helps you:
- **Automatically import** bank statements from Excel files
- **Categorize transactions** using intelligent keyword matching
- **Visualize spending patterns** with interactive charts
- **Track budget status** with real-time metrics
- **Compare expenses** across salary periods

---

## 📁 Project Structure

```
Budgeteer/
├── dashboard.py              # Main Streamlit UI application
├── visualize_budget.py       # Visualization and metrics functions
├── automate_budget.py        # Bank statement parsing & Excel generation
├── year/
│   ├── Bank Statements/      # Folder for bank statement Excel files
│   ├── January Expense Tracker.xlsx
│   └── February Expense Tracker.xlsx
└── README.md
```

---

## 🔧 File Descriptions

### 1. **dashboard.py** - Main Application
**Purpose:** Streamlit frontend and user interface

**Key Features:**
- Year and month selection dropdowns
- Generate new expense tracker button
- Visualize dashboard button
- File overwrite confirmation dialog

**Main Flow:**
```
User selects Year & Month
         ↓
Click "Generate" → Create expense tracker from bank statement
         ↓
Click "Visualize" → Display interactive dashboard
```

---

### 2. **visualize_budget.py** - Visualizations & Metrics
**Purpose:** Creates all dashboard charts and metrics

**Key Features:**

#### **Top KPI Metrics**
Displays 5 metrics in columns:
1. **💸 Total Spent** - Sum of all expenses
2. **🔥 Top Category** - Highest spending category
3. **📅 Avg Daily Spend** - Average daily expenses
4. **🧾 Transactions** - Total transaction count
5. **💰 Budget Status** - Salary vs Expenses (with ▲/▼ and color coding)
   - 🟢 Green ▲ = Under budget (surplus)
   - 🔴 Red ▼ = Over budget (deficit)

#### **Hierarchical View**
Shows spending breakdown by category and description in a treemap visualization.

#### **Horizontal Bar Chart**
Bar chart sorted by spend amount showing each category's total expenses.

#### **Daily Trend Analysis**
Overlaid bar chart (daily spend) with 7-day moving average line.

#### **Source Distribution**
Pie chart showing where expenses came from (e.g., Bank Statement).

#### **Family Spending Split**
Donut chart comparing spending between:
- **Parents**
- **Family**

#### **High-Value Transactions**
Table of top 8 transactions with date, description, category, source, and amount.

---

### 3. **automate_budget.py** - Bank Statement Processing
**Purpose:** Parses bank statements and generates Excel trackers

**Key Features:**

#### **File Discovery**
- Finds file matching the month name (case-sensitive)
- Raises error if file not found

#### **Excel Parsing**
- Multi-line transaction remarks (overflow rows)
- Salary transaction detection (separate column)
- Withdrawal amount validation

#### **Smart Categorization**
- Matches transaction remarks against category keywords (case-insensitive)
- Falls back to "Others" if no match

#### **Excel Generation**
Creates a formatted Excel workbook with 3 sheets:

**Sheet 1: Transactions**
- Columns: #, Date, Description, Source, Type, Spend, Remarks
- All withdrawal transactions auto-categorized
- Salary transactions in "Remarks" column (for comparison)
- Auto-filter enabled on headers
- Currency formatting (₹)

**Sheet 2: Categories**
- Uses SUMIF formula to aggregate spending by category
- Auto-calculates percentage of total
- Total row with 100% verification

**Sheet 3: Dashboard**
- Sample chart (for reference)

---

## 🚀 How to Use

### **Step 1: Prepare Bank Statement**
1. Export bank statement as Excel from your bank
2. Save to: `2026/Bank Statements/{Month}.xlsx`
3. Ensure columns are at standard positions (adjustable in `automate_budget.py`)

### **Step 2: Generate Tracker**
1. Open dashboard: `streamlit run dashboard.py`
2. Select Year and Month
3. Click **"📥 Generate"**
4. Confirm if file exists (overwrite if needed)
5. Wait for "Excel tracker created" message

### **Step 3: Review Transactions**
1. Open the generated Excel file
2. Verify that all transactions are correctly categorized
3. Adjust categories if necessary

- PS: Put the category keywords during payments to ensure accurate categorization.

### **Step 4: Visualize**
1. Click **"📊 Visualize"**
2. View interactive dashboard with:
   - Top 5 KPI metrics
   - Category breakdown charts
   - Daily spending trend
   - Spending heatmap
   - Top transactions table
   - Raw data view

---

## 🛠️ Configuration

### **Bank Statement Column Indices**
In `automate_budget.py`, adjust these if your bank uses different columns:

```python
DATE_COL = 3          # Date column position
REMARKS_COL = 5       # Description column position
WITHDRAWAL_COL = 6    # Withdrawal amount column position
SALARY_COL = 7        # Salary amount column position
```

### **Add Custom Categories**
Edit `CATEGORIES` dictionary:

```python
CATEGORIES = {
    "Your Category": ["keyword1", "keyword2", ...],
    ...
}
```

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| File not found error | Check bank statement is in `2026/Bank Statements/` |
| No transactions imported | Verify column indices match your bank's format in `automate_budget.py` |
| Transactions not categorized | Add keywords to `CATEGORIES` dictionary for your bank's terminology |
| Salary not detected | Ensure salary transaction has "salary" in description (case-insensitive) |
| Budget Status not showing | Previous month's file must exist to calculate salary vs expenses |

---

## 📝 Notes

- **Salary Detection:** Transactions with "salary" in description are flagged separately
- **Budget Comparison:** Compares expenses from current salary to next salary
- **Auto-filter:** All transaction sheets have auto-filter enabled for easy sorting
- **Currency:** All amounts displayed in Indian Rupees (₹) with 2 decimal places

---

## 📄 License

Personal use only.

---

## 👨‍💻 Author Notes

This application is designed for personal expense tracking with automated categorization based on bank statement keywords. Regular maintenance of the `CATEGORIES` dictionary ensures accurate categorization as your banking patterns evolve.
