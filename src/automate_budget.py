from datetime import datetime
import pandas as pd
import os

# --- CONFIG ---
# adjust based on statement file
DATE_COL = 3
REMARKS_COL = 5
WITHDRAWAL_COL = 6
SALARY_COL = 7


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
                current_withdrawal = None  # reset for next transaction

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
