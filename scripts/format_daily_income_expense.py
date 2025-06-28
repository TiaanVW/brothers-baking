import pandas as pd
import os

# Input and output file paths
input_file = os.path.join(os.path.dirname(__file__), '../data/daily_income_expense_powerbi_ready.csv')
output_income_file = os.path.join(os.path.dirname(__file__), '../data/daily_income_expense_income_formatted.csv')
output_expense_file = os.path.join(os.path.dirname(__file__), '../data/daily_income_expense_expense_formatted.csv')

# Read the CSV file
try:
    df = pd.read_csv(input_file, dtype=str)
except Exception as e:
    print(f'Error reading file: {e}')
    raise

# Keep only the required columns
keep_cols = ['Date', 'Type', 'Amount', 'Year', 'Month']
df = df[keep_cols]

# Standardize the Date column to YYYY-MM-DD
def parse_date(val):
    try:
        return pd.to_datetime(val).strftime('%Y-%m-%d')
    except Exception:
        return ''

df['Date'] = df['Date'].apply(parse_date)

# Split into income and expense DataFrames
income_df = df[df['Type'].str.upper() == 'INCOME']
expense_df = df[df['Type'].str.upper() == 'EXPENSE']

# Write to separate output files
try:
    income_df.to_csv(output_income_file, index=False)
    print(f'Income file written to {output_income_file}')
except Exception as e:
    print(f'Error writing income file: {e}')
    raise

try:
    expense_df.to_csv(output_expense_file, index=False)
    print(f'Expense file written to {output_expense_file}')
except Exception as e:
    print(f'Error writing expense file: {e}')
    raise
