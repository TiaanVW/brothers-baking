import pandas as pd
import numpy as np
from datetime import datetime
import re

# Configuration
input_file = 'data_sources/MAIN DOCUMENT 2025 (Autosaved).xlsx'
sheet_name = 'EXPENSE DAILY'  # Target the EXPENSE DAILY sheet
output_file = 'raw_outputs/expenses_daily.csv'

print(f"Processing {sheet_name} from {input_file}...")

try:
    # Read the entire EXPENSE DAILY sheet without a header to parse it manually
    raw_df = pd.read_excel(input_file, sheet_name='EXPENSE DAILY', header=None)
    print(f"Successfully loaded sheet 'EXPENSE DAILY' for manual parsing")
    
    # Initialize variables for parsing
    current_date = None
    expenses = []
    headers = ['SLIP NUMBER', 'AMOUNT', 'VAT', 'Shop']
    date_count = 0
    
    # Iterate through each row to detect dates and expense entries
    for idx in range(len(raw_df)):
        row = raw_df.iloc[idx]
        first_cell = str(row[0]).strip().upper() if pd.notna(row[0]) else ''
        
        # Check if this row indicates a date
        if first_cell == 'DATE' and pd.notna(row[1]):
            current_date = pd.to_datetime(row[1])
            date_count += 1
            print(f"Found date at row {idx}: {current_date}")
            continue
        
        # Check if this row contains headers (SLIP NUMBER, AMOUNT, etc.)
        if first_cell == 'SLIP NUMBER':
            continue  # Skip header rows
        
        # If we have a valid date and this looks like an expense entry (has a value in first or second column)
        if current_date is not None and pd.notna(row[0]) and str(row[0]).strip().upper() != 'EXPENSES':
            try:
                amount = pd.to_numeric(row[1], errors='coerce')
                if pd.notna(amount):  # Valid amount
                    shop = str(row[3]) if pd.notna(row[3]) else 'Unknown'
                    expenses.append({
                        'Date': current_date,
                        'Shop': shop,
                        'AMOUNT': amount
                    })
                    print(f"Added expense at row {idx} with date {current_date}, amount {amount}, shop {shop}")
            except Exception as e:
                print(f"Error parsing row {idx}: {e}")
                continue
    
    if not expenses:
        raise Exception("No valid expense data found in 'EXPENSE DAILY' sheet")
    
    print(f"Total dates detected: {date_count}")
    print(f"Parsed {len(expenses)} expense entries with multiple dates")
    # Convert the list of expenses to a DataFrame
    raw_df = pd.DataFrame(expenses)
except Exception as e:
    print(f"Error loading or processing 'EXPENSE DAILY' sheet: {e}")
    exit(1)

print("Cleaning and preparing data...")

# Use the correct columns directly
result_df = raw_df[['Date', 'Shop', 'AMOUNT']].copy()
result_df = result_df.rename(columns={'Shop': 'Category', 'AMOUNT': 'Amount'})

# Add additional enrichment if needed
result_df['Source'] = 'EXPENSE DAILY'

# Enhance the data for Power BI
print("Enhancing data for Power BI...")

# Ensure Date is in datetime format
result_df['Date'] = pd.to_datetime(result_df['Date'], errors='coerce')
result_df = result_df.dropna(subset=['Date'])  # Remove rows with invalid dates

# Add time dimensions for easier analysis in Power BI
result_df['Year'] = result_df['Date'].dt.year
result_df['Month'] = result_df['Date'].dt.month
result_df['Month Name'] = result_df['Date'].dt.strftime('%B')
result_df['Quarter'] = result_df['Date'].dt.quarter
result_df['Week Number'] = result_df['Date'].dt.isocalendar().week
result_df['Day of Week'] = result_df['Date'].dt.dayofweek + 1  # 1=Monday, 7=Sunday
result_df['Day Name'] = result_df['Date'].dt.strftime('%a').str.upper()

# Create a clean, standardized Category field
if 'Category' in result_df.columns:
    result_df['Category_Clean'] = result_df['Category'].astype(str).str.strip().str.upper()
    
    # Create a Category Group field for higher-level analysis
    def categorize(category):
        category = str(category).upper()
        if any(x in category for x in ['FUEL', 'TOLL']):
            return 'Transportation'
        elif any(x in category for x in ['ELECTRICITY']):
            return 'Utilities'
        elif any(x in category for x in ['WAGES']):
            return 'Labor'
        elif any(x in category for x in ['BAKELS', 'CHIPKINS', 'BAKERSBIN', 'WASI', 'HYPER', 'SWEETS']):
            return 'Raw Materials'
        elif any(x in category for x in ['SHOPRITE', 'MAKRO', 'T/BANTU']):
            return 'Supplies'
        elif any(x in category for x in ['INCOME']):
            return 'Income'
        else:
            return 'Other Expenses'
    
    result_df['Category Group'] = result_df['Category'].apply(categorize)

# Calculate running totals and other aggregate measures
if 'Category' in result_df.columns and 'Amount' in result_df.columns:
    result_df['Running Total'] = result_df.groupby(['Category'])['Amount'].cumsum()

# Sort by date for better readability
result_df = result_df.sort_values(['Date', 'Category' if 'Category' in result_df.columns else 'Amount'])

# Save to CSV in a format optimized for Power BI
result_df.to_csv(output_file, index=False)
print(f"Saved Power BI-ready data to {output_file}")

# Print summary statistics
if 'Category' in result_df.columns and 'Amount' in result_df.columns:
    print("\nExpense summary by category:")
    summary = result_df.groupby('Category')['Amount'].agg(['sum', 'count']).reset_index()
    summary = summary.sort_values('sum', ascending=False)
    print(summary.head(10).to_string(index=False))
    
    if 'Category Group' in result_df.columns:
        print("\nExpense summary by category group:")
        group_summary = result_df.groupby('Category Group')['Amount'].agg(['sum', 'count']).reset_index()
        group_summary = group_summary.sort_values('sum', ascending=False)
        print(group_summary.to_string(index=False))
    
    # Print total
    total = result_df['Amount'].sum()
    print(f"\nTotal expenses: R{total:,.2f}")

print("\nData is now ready for Power BI import:")
print("1. In Power BI Desktop, use 'Get Data' → 'Text/CSV'")
print("2. Select expense_daily_powerbi_ready.csv")
print("3. The data is already in a structured format ready for visualizations")
print("4. Create date hierarchy using the date dimensions provided")
print("5. Use Category and Category Group for meaningful breakdowns")