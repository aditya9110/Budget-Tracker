# 💰 Budgeteer

A personal expense tracking desktop app built with PyQt6 and Python. Import your bank statements, auto-categorize transactions, visualize spending patterns, and manage your budget — all in one place, fully offline.

---

## ✨ Features

- **Import Bank Statements** — drag & drop or browse `.xlsx`/`.xls` files
- **Auto Categorization** — transactions are automatically matched to categories using keyword rules
- **Interactive Dashboard** — KPI metrics, bar chart, daily trend, cumulative spend, donut chart, and treemap
- **Transactions View** — browse, add, edit, and delete transactions by month
- **Budget Status** — compares salary to expenses across months
- **Fully Offline** — all data stored locally in a single SQLite file
- **No installation needed** — can be packaged as a standalone `.exe`

---

## 📁 Project Structure

```
Budgeteer/
├── main.py                  # Entry point — opens PyQt6 window
├── api.py                   # Python ↔ JS bridge (js_api)
├── db.py                    # SQLite setup and queries
├── requirements.txt
├── src/
│   └── automate_budget.py   # Bank statement parsing and categorization
├── frontend/
│   ├── index.html           # Main UI
│   ├── style.css            # Dark theme styles
│   ├── app.js               # JS logic and Plotly charts
│   └── plotly.min.js        # Local Plotly (no internet needed)
└── data/
    └── budgeteer.db            # SQLite database (auto-created on first run)
```

---

## ⚙️ Setup (First Time Only)

### 1. Install Python
Download Python 3.10+ from https://python.org
Check **"Add Python to PATH"** during installation.

### 2. Create virtual environment
```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies
```
python -m pip install -r requirements.txt
```

---

## ▶️ Run the App

```
python main.py
```

The app opens as a native Windows window — no browser, no terminal visible.

---

## 📂 Importing a Bank Statement

1. Export your bank statement as `.xlsx` or `.xls`
2. Open the app and go to **Import Statement**
3. Drag & drop the file or click **Browse File**
4. Click **Import & Categorize**
5. If data for that month already exists, you'll be asked to confirm overwrite
6. Transactions are auto-categorized and stored in the database
7. App redirects to **Transactions** view automatically

---

## 📊 Dashboard

Select a month and year from the top bar and click **Load** to view:

- **KPI Row** — Total Spent, Top Category, Avg Daily Spend, Transaction Count, Budget Status
- **Category Breakdown** — horizontal bar chart sorted by spend
- **Daily Spending Trend** — bar chart with 7-day rolling average
- **Cumulative Spend** — area chart showing total spend over the month
- **Parents vs Family** — donut chart splitting spend groups
- **Hierarchical View** — treemap of categories and transactions
- **Top Transactions** — table of 8 highest spend transactions

---

## 🧾 Transactions

Select a period and click **Load** to view all transactions for that month.

- **➕ Add** — manually add a new transaction
- **✎ Edit** — edit any existing transaction inline
- **✕ Delete** — delete a transaction (with confirmation)

---

## 🔧 Configuration

### Adjust Bank Statement Column Positions
If your bank uses different column positions, edit in `src/automate_budget.py`:

```python
DATE_COL       = 3   # Date column index
REMARKS_COL    = 5   # Description column index
WITHDRAWAL_COL = 6   # Withdrawal amount column index
SALARY_COL     = 7   # Salary/credit amount column index
```

### Add or Edit Categories
Edit the `CATEGORIES` dictionary in `src/automate_budget.py`:

```python
CATEGORIES = {
    "Food": ["food", "swiggy", "zomato"],
    "Travel": ["uber", "ola", "irctc"],
    ...
}
```

---

## 💾 Backup

All data is stored in a single file:
```
Budgeteer/data/budgeteer.db
```

Copy this file to Google Drive or any location to back up all your transactions. To restore, copy it back into the `data/` folder.

---

## 📦 Package as .exe (Optional)

To create a standalone Windows executable:

```
python -m pip install pyinstaller
pyinstaller --onefile --windowed --add-data "frontend;frontend" main.py
```

The `.exe` will be in the `dist/` folder. Copy `dist/main.exe` + `data/` folder to any Windows machine — no Python needed.

---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| No transactions imported | Verify column indices match your bank format in `src/automate_budget.py` |
| Transactions not categorized | Add keywords to `CATEGORIES` for your bank's terminology |
| Salary not detected | Ensure salary transaction has "salary" in description |
| Budget Status not showing | Previous month's data must be imported first |
| Charts not rendering | Ensure `frontend/plotly.min.js` exists |

---

## 📝 Notes

- Salary rows are stored separately and used only for budget status calculation
- All amounts are in Indian Rupees (₹)
- The app works fully offline — no internet connection required after setup

---

## 📄 License

Personal use only.

---

## 👨‍💻 Author Notes

This application is designed for personal expense tracking with automated categorization based on bank statement keywords. Regular maintenance of the `CATEGORIES` dictionary ensures accurate categorization as your banking patterns evolve.
