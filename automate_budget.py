from datetime import datetime
import pandas as pd
import os
import xlsxwriter
import streamlit as st

# --- CONFIG ---
CATEGORIES = {
    "Cash Withdrawal": ["cash wdl"],
    "EMI": ["emi", "hdb financial", "loan", "personal loan"],
    "Rent": ["rent"],
    "Food": ["food", "hazel", "brambles", "theobroma", "mimi"],
    "Entertainment": ["entertainment", "district", "bookmyshow", "bms"],
    "Groceries": ["groceries", "grocery", "dmart", "avenue"],
    "Bills": ["bills"],
    "Bills (P)": ["radha naga", "bennett"],
    "Personal": ["personal"],
    "Shopping": [],
    "Parents": ["home", "parents", "parent"],
    "Investment": ["investment", " fd ", "invest", "groww"],
    "Insurance": ["insurance", "tataaia", "aia", "lic"],
    "Fuel": ["fuel", "petrol"],
    "Travel": ["travel", "railway", "rail", "irctc", "auto", "cab"],
    "Medicines": ["medicine", "wellness"],
    "Medicines (P)": ["medicinep", "revival", "wellness", "hospitalp"]
}

# adjust based on statement file
DATE_COL = 3
REMARKS_COL = 5
WITHDRAWAL_COL = 6
SALARY_COL = 7


def get_statement_file(statement_folder, month):    
    if not os.path.exists(statement_folder):
        raise FileNotFoundError(f"Statement folder '{statement_folder}' not found")
    
    month_lower = month.lower()
    for filename in os.listdir(statement_folder):
        if month_lower in filename.lower():
            file_path = os.path.join(statement_folder, filename)
            if os.path.isfile(file_path):
                return file_path
    
    raise FileNotFoundError(f"No statement file found for month '{month}' in '{statement_folder}'")

def fetch_transactions_from_bank_statement(statement_file):
    df = pd.read_excel(statement_file, header=None)

    transactions = []
    current_remarks = ""
    current_withdrawal = None

    for _, row in df.iterrows():
        date = row[DATE_COL]
        remarks = row[REMARKS_COL]
        withdrawal = row[WITHDRAWAL_COL]
        
        # Case 1: New transaction starts
        if pd.notna(withdrawal) and "Withdrawal" not in withdrawal:
            # save previous transaction
            if current_withdrawal is not None:
                transactions.append({
                    "Date": datetime.strptime(current_date, "%d,%m,%Y").strftime("%d-%m-%Y"),
                    "Transaction Remarks": current_remarks.strip(),
                    "Withdrawal Amount (INR)": current_withdrawal
                })

            if withdrawal != "0.00":
                # start new transaction
                current_date = date
                current_remarks = str(remarks) if pd.notna(remarks) else ""
                current_withdrawal = withdrawal

            elif "salary" in str(remarks).lower():
                # Handle salary transactions
                current_date = date
                current_remarks = str(remarks) if pd.notna(remarks) else ""
                current_withdrawal = row[SALARY_COL]

        # Case 2: Remarks overflow (continuation row)
        else:
            if pd.notna(remarks) and current_withdrawal is not None:
                current_remarks += " " + str(remarks)

    # Save last transaction
    if current_withdrawal is not None:
        transactions.append({
            "Date": datetime.strptime(current_date, "%d,%m,%Y").strftime("%d-%m-%Y"),
            "Transaction Remarks": current_remarks.strip(),
            "Withdrawal Amount (INR)": current_withdrawal
        })

    # Final clean DataFrame
    transactions_df = pd.DataFrame(transactions)
    return transactions_df

def classify_transaction(remarks):
    remarks_lower = remarks.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in remarks_lower:
                return category, keyword.strip()
    return "Others", ""

def create_expense_tracker(year, month):
    st.info("Excel file generation started...")

    try:
        statement_folder = f"{year}/Bank Statements"
        file_name = f"{year}/{month} Expense Tracker.xlsx"
        file_name = f"{year}/{month} Expense Tracker test.xlsx"

        statement_file = get_statement_file(statement_folder, month)
        transactions_df = fetch_transactions_from_bank_statement(statement_file)

        workbook = xlsxwriter.Workbook(file_name)

        # Formats
        header = workbook.add_format({
            "bold": True,
            "font_color": "white",
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#7030A0",
            "border": 1
        })
        border = workbook.add_format({"border": 1})
        date_format = workbook.add_format({"num_format": "dd-mm-yyyy", "border": 1})
        money = workbook.add_format({"num_format": "₹#,##0.00", "border": 1})
        percent = workbook.add_format({"num_format": "0.00%", "border": 1})

        # TRANSACTIONS SHEET
        trans_sheet = workbook.add_worksheet("Transactions")

        headers = [
            "#",
            "Date",
            "Description",
            "Source",
            "Type",
            "Spend",
            "Remarks"
        ]

        # headers
        for col, h in enumerate(headers):
            trans_sheet.write(0, col, h, header)

        # track row number and serial number
        row_ptr = 1
        sr_no = 1

        for _, row in transactions_df.iterrows():

            if "salary" in str(row["Transaction Remarks"]).lower():
                trans_sheet.write(row_ptr, 0, sr_no, border)
                trans_sheet.write(row_ptr, 1, datetime.strptime(row["Date"], "%d-%m-%Y"), date_format)
                trans_sheet.write(row_ptr, 2, row["Transaction Remarks"][:90].strip(), border)
                trans_sheet.write(row_ptr, 3, None, border)
                trans_sheet.write(row_ptr, 4, None, border)
                trans_sheet.write(row_ptr, 5, None, border)
                trans_sheet.write(row_ptr, 6, float(row["Withdrawal Amount (INR)"]), border) # Salary amount in Remarks column

            else:
                category, remarks = classify_transaction(row["Transaction Remarks"])

                values = [
                    sr_no,
                    datetime.strptime(row["Date"], "%d-%m-%Y"),
                    row["Transaction Remarks"][:90].strip(),
                    "Bank Statement",
                    category,
                    float(row["Withdrawal Amount (INR)"]),
                    remarks
                ]

                for col, val in enumerate(values):
                    # Date column
                    if col == 1:
                        trans_sheet.write_datetime(row_ptr, col, val, date_format)
                    # Spend column
                    elif col == 5:
                        trans_sheet.write_number(row_ptr, col, val, money)
                    else:
                        trans_sheet.write(row_ptr, col, val, border)

            row_ptr += 1
            sr_no += 1
        
        # Apply column width
        trans_sheet.set_column("A:A", 5)
        trans_sheet.set_column("B:B", 12)
        trans_sheet.set_column("C:C", 95)
        trans_sheet.set_column("D:D", 20)
        trans_sheet.set_column("E:E", 13)
        trans_sheet.set_column("F:F", 12)
        trans_sheet.set_column("G:G", 20)

        # Add filter to header row
        trans_sheet.autofilter(0, 0, row_ptr - 1, len(headers) - 1)

        # CATEGORIES SHEET
        cat_sheet = workbook.add_worksheet("Categories")

        cat_headers = ["Type", "Spend", "Percent"]

        # headers
        for col, h in enumerate(cat_headers):
            cat_sheet.write(0, col, h, header)

        categories = list(CATEGORIES.keys()) + ["Others"]

        # first two column with category names and SUMIF formulas for spend
        for row, cat in enumerate(categories, start=1):
            cat_sheet.write(row, 0, cat, border)

            # SUMIF formula
            cat_sheet.write_formula(row, 1, f'=SUMIF(Transactions!E:E,A{row+1},Transactions!F:F)', money)

        # Total row (last row)
        total_row = len(categories) + 1
        cat_sheet.write(total_row, 0, "Total", header)
        cat_sheet.write_formula(total_row, 1, f"=SUM(B2:B{total_row})", money)

        # third column - Percent calculation
        for row in range(1, total_row):
            cat_sheet.write_formula(row, 2, f"=B{row+1}/B{total_row+1}", percent)

        # last row percent (100%)
        cat_sheet.write_formula(total_row, 2, f"=SUM(C2:C{total_row})", percent)

        # Apply column width
        cat_sheet.set_column("A:A", 20)
        cat_sheet.set_column("B:C", 15)

        # DASHBOARD SHEET
        dash = workbook.add_worksheet("Dashboard")

        chart = workbook.add_chart({"type": "column", "subtype": "clustered"})

        for i in range(len(categories)):
            row = i + 2
            chart.add_series({
                "name": f"=Categories!A{row}",
                "categories": "=Categories!A1",
                "values": f"=Categories!B{row}",
                "data_labels": {"value": True},
            })

        chart.set_title({"name": "Expense Distribution"})
        chart.set_x_axis({"name": "Category", "label_position": "low"})
        chart.set_y_axis({"name": "Amount", "major_gridlines": {"visible": True}})
        chart.set_plotarea({
            "layout": {"x": 0.13, "y": 0.15, "width": 0.75, "height": 0.7}
        })
        chart.set_style(26)

        dash.insert_chart("B2", chart, {"x_scale": 2.2, "y_scale": 2})

        workbook.close()

        st.success(f"Excel tracker created: {file_name}")
        st.info(f"{len(transactions_df)} transactions added.")
    
    except Exception as e:
        st.error(f"Error generating Excel file: {e}")
