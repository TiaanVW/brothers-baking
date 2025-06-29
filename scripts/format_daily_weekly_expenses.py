import pandas as pd
import os

# Input and output file paths
input_file = os.path.join(os.path.dirname(__file__), '../raw_outputs/daily_weekly_expenses.csv')
output_file = os.path.join(os.path.dirname(__file__), '../data/daily_weekly_expenses_formatted.csv')

# Read the CSV file
try:
    df = pd.read_csv(input_file, dtype=str)
except Exception as e:
    print(f'Error reading file: {e}')
    raise

# Filter out rows where Category is 'TOTALS' or 'Category Group'
df = df[(df['Category'].str.upper() != 'TOTALS') & (df['Category'].str.upper() != 'CATEGORY GROUP')]

# Keep only the required columns
keep_cols = ['Date', 'Category', 'Category Group', 'Amount', 'Year', 'Month']
df = df[keep_cols]

# Write to output file
try:
    df.to_csv(output_file, index=False)
    print(f'Formatted file written to {output_file}')
except Exception as e:
    print(f'Error writing file: {e}')
    raise
