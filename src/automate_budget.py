from datetime import datetime
import pandas as pd
import os

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

def classify_transaction(categories, remarks):
    remarks_lower = remarks.lower()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in remarks_lower:
                return category, keyword.strip()
    return "Others", ""
