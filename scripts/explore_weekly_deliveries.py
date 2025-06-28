import pandas as pd
import os

# Path to the source data file
source_file = os.path.join(os.path.dirname(__file__), '../data_sources/MAIN DOCUMENT 2025 (Autosaved).xlsx')

# Check if source file exists
if not os.path.exists(source_file):
    print(f"Error: Source file not found at {source_file}")
    print("Please ensure the 'MAIN DOCUMENT 2025 (Autosaved).xlsx' file is placed in the data_sources directory.")
    exit(1)

try:
    # Read the Excel file
    xl = pd.ExcelFile(source_file)
    print("Available sheets in the Excel file:")
    for sheet in xl.sheet_names:
        print(f"- {sheet}")
    
    # Read the specific sheet
    sheet_name = 'WEEKLY DELIVEIES & RETURN'
    if sheet_name in xl.sheet_names:
        df = pd.read_excel(source_file, sheet_name=sheet_name)
        print(f"\nSheet '{sheet_name}' found. Exploring content:")
        print(f"- Number of rows: {len(df)}")
        print(f"- Number of columns: {len(df.columns)}")
        print(f"- Column names: {list(df.columns)}")
        print("\nFirst 5 rows of data:")
        print(df.head(5).to_string())
    else:
        print(f"Sheet '{sheet_name}' not found in the Excel file.")
except Exception as e:
    print(f"Error reading Excel file: {e}")
    print("Please check if the file format is correct.")
