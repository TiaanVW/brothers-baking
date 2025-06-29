import pandas as pd
import numpy as np
from datetime import datetime
import re

# Configuration
input_file = 'data_sources/MAIN DOCUMENT 2025 (Autosaved).xlsx'
sheet_name = 'DAILY INCOME EXPENSE'
output_file = 'raw_outputs/daily_income_expense.csv'

print(f"Processing {sheet_name} from {input_file}...")

try:
    # Read the entire DAILY INCOME EXPENSE sheet without a header to parse it manually
    raw_df = pd.read_excel(input_file, sheet_name=sheet_name, header=None)
    print(f"Successfully loaded sheet '{sheet_name}' for manual parsing")
    
    # Initialize variables for parsing
    records = []
    month_count = 0
    current_col = 0
    max_cols = len(raw_df.columns)
    max_rows = len(raw_df)
    
    # Iterate through columns to find month blocks
    while current_col < max_cols:
        # Look for a month identifier (like 2025-01-01) in the first few rows of the column
        current_month = None
        for row_idx in range(min(5, max_rows)):
            cell_value = raw_df.iloc[row_idx, current_col]
            if pd.notna(cell_value) and isinstance(cell_value, datetime):
                current_month = cell_value
                month_count += 1
                print(f"Found month at column {current_col}, row {row_idx}: {current_month}")
                break
        
        if current_month is None:
            current_col += 1
            continue
        
        # Look for header row (DATE, INCOME, etc.) in the rows just below the month
        header_row_idx = None
        for row_idx in range(row_idx + 1, min(row_idx + 5, max_rows)):
            cell_value = str(raw_df.iloc[row_idx, current_col]).strip().upper() if pd.notna(raw_df.iloc[row_idx, current_col]) else ''
            if cell_value == 'DATE':
                header_row_idx = row_idx
                break
        
        if header_row_idx is None:
            print(f"No header row found for month at column {current_col}, skipping")
            current_col += 1
            continue
        
        # Identify column indices for DATE, INCOME, EXPENSES, etc., in this block
        date_col = current_col
        income_col = None
        income_vat_col = None
        expenses_col = None
        expenses_vat_col = None
        
        for col_offset in range(min(5, max_cols - current_col)):
            col_val = str(raw_df.iloc[header_row_idx, current_col + col_offset]).strip().upper() if pd.notna(raw_df.iloc[header_row_idx, current_col + col_offset]) else ''
            if col_val == 'INCOME':
                income_col = current_col + col_offset
            elif col_val == 'INCOME VAT':
                income_vat_col = current_col + col_offset
            elif col_val == 'EXPENSES':
                expenses_col = current_col + col_offset
            elif col_val == 'EXPENSES VAT':
                expenses_vat_col = current_col + col_offset
        
        print(f"Month {current_month}: Identified columns - Date: {date_col}, Income: {income_col}, Income VAT: {income_vat_col}, Expenses: {expenses_col}, Expenses VAT: {expenses_vat_col}")
        
        # If no income or expense columns found, skip to next potential month block
        if income_col is None and expenses_col is None:
            print(f"No Income or Expenses columns found for month at column {current_col}, skipping")
            current_col += 1
            continue
        
        # Parse data rows for this month (rows below header)
        for row_idx in range(header_row_idx + 1, max_rows):
            date_val_str = str(raw_df.iloc[row_idx, date_col]) if pd.notna(raw_df.iloc[row_idx, date_col]) else ''
            if date_val_str == '' or date_val_str.upper() == 'WEEKLY TOTALS':
                continue  # Skip empty or summary rows
            
            try:
                day = int(float(date_val_str))  # Handle cases where day might be a float
                if 1 <= day <= 31:
                    entry_date = pd.to_datetime(f"{current_month.year}-{current_month.month}-{day}")
                    
                    # Extract Income if column exists
                    if income_col is not None and income_col < max_cols:
                        income = pd.to_numeric(raw_df.iloc[row_idx, income_col], errors='coerce')
                        if pd.notna(income) and income > 0:
                            income_vat = pd.to_numeric(raw_df.iloc[row_idx, income_vat_col], errors='coerce') if income_vat_col is not None and income_vat_col < max_cols else 0
                            records.append({
                                'Date': entry_date,
                                'Type': 'Income',
                                'Amount': income,
                                'VAT': income_vat if pd.notna(income_vat) else 0
                            })
                            print(f"Added income for {entry_date} at row {row_idx}, amount {income}, VAT {income_vat if pd.notna(income_vat) else 0}")
                    
                    # Extract Expenses if column exists
                    if expenses_col is not None and expenses_col < max_cols:
                        expense = pd.to_numeric(raw_df.iloc[row_idx, expenses_col], errors='coerce')
                        if pd.notna(expense) and expense > 0:
                            expense_vat = pd.to_numeric(raw_df.iloc[row_idx, expenses_vat_col], errors='coerce') if expenses_vat_col is not None and expenses_vat_col < max_cols else 0
                            records.append({
                                'Date': entry_date,
                                'Type': 'Expense',
                                'Amount': expense,
                                'VAT': expense_vat if pd.notna(expense_vat) else 0
                            })
                            print(f"Added expense for {entry_date} at row {row_idx}, amount {expense}, VAT {expense_vat if pd.notna(expense_vat) else 0}")
                else:
                    print(f"Skipping row {row_idx} for month {current_month}: Day {day} out of valid range")
            except (ValueError, TypeError) as e:
                print(f"Error parsing date at row {row_idx}, column {date_col}: {e}")
                break  # Likely end of data for this month
        
        # Move to the next potential month block (skip a few columns to avoid overlap)
        current_col = current_col + 5 if expenses_vat_col is None else expenses_vat_col + 1
        print(f"Moving to next month block at column {current_col}")
    
    if not records:
        raise Exception(f"No valid data found in '{sheet_name}' sheet")
    
    print(f"Total months detected: {month_count}")
    print(f"Parsed {len(records)} data entries")
    # Convert the list of records to a DataFrame
    result_df = pd.DataFrame(records)
except Exception as e:
    print(f"Error loading or processing '{sheet_name}' sheet: {e}")
    exit(1)

print("Cleaning and preparing data...")

# Add additional enrichment for Power BI
result_df['Source'] = sheet_name
result_df['Year'] = result_df['Date'].dt.year
result_df['Month'] = result_df['Date'].dt.month
result_df['Month Name'] = result_df['Date'].dt.strftime('%B')
result_df['Quarter'] = result_df['Date'].dt.quarter
result_df['Week Number'] = result_df['Date'].dt.isocalendar().week
result_df['Day of Week'] = result_df['Date'].dt.dayofweek + 1
result_df['Day Name'] = result_df['Date'].dt.strftime('%a').str.upper()

# Calculate running total by type
result_df = result_df.sort_values(by=['Type', 'Date'])
result_df['Running Total'] = result_df.groupby('Type')['Amount'].cumsum()

print("Saving enriched data...")
result_df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")

# Summary for user
income_total = result_df[result_df['Type'] == 'Income']['Amount'].sum()
expense_total = result_df[result_df['Type'] == 'Expense']['Amount'].sum()

print("\nSummary of Income and Expenses:")
print(f"Total Income: R{income_total:,.2f}")
print(f"Total Expenses: R{expense_total:,.2f}")
print(f"Net Income: R{(income_total - expense_total):,.2f}")

print(f"\nData is now ready for Power BI import:")
print(f"1. In Power BI Desktop, use 'Get Data' → 'Text/CSV'")
print(f"2. Select {output_file}")
print(f"3. The data is already in a structured format ready for visualizations")
print(f"4. Create date hierarchy using the date dimensions provided")
print(f"5. Use Type to differentiate between Income and Expense records")
