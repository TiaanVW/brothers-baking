import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

# Path to the source data file (adjust if necessary)
source_file = os.path.join(os.path.dirname(__file__), '../data_sources/MAIN DOCUMENT 2025 (Autosaved).xlsx')
output_file = os.path.join(os.path.dirname(__file__), '../raw_outputs/weekly_deliveries_returns.csv')

# Check if source file exists
if not os.path.exists(source_file):
    print(f"Error: Source file not found at {source_file}")
    print("Please ensure the 'MAIN DOCUMENT 2025 (Autosaved).xlsx' file is placed in the data_sources directory.")
    exit(1)

try:
    # Read the Excel file - adjust sheet name if needed
    xls = pd.ExcelFile(source_file)
    sheet_name = 'WEEKLY DELIVEIES & RETURN'
    df = pd.read_excel(source_file, sheet_name=sheet_name)
    print(f"Sheet loaded. Rows: {len(df)}, Columns: {len(df.columns)}")
except Exception as e:
    print(f"Error reading Excel file: {e}")
    print("Please check if the file format is correct and the sheet name is 'WEEKLY DELIVEIES & RETURN'.")
    exit(1)

# Define all possible cake types to look for in the sheet
all_cake_types = ['CHOCOLATE', 'VANILLA', 'CARROT', 'COFFEE', 'DARKM']
print(f"Looking for these cake types: {all_cake_types}")

# This will store our final dataset
weeks = []
years = []
stores = []
cake_types = []
returns = []
return_amounts = []

# Function to identify cake type headers in a row
def is_cake_header_row(row):
    cake_types_found = 0
    for val in row:
        val = str(val).strip().upper()
        if val in all_cake_types:
            cake_types_found += 1
    return cake_types_found >= 3

# Function to extract cake types from a row
def extract_cake_types(row):
    cake_positions = {}
    for pos, val in enumerate(row):
        val = str(val).strip().upper()
        if val in all_cake_types:
            cake_positions[val] = pos
    return cake_positions

# Function to identify store names
def extract_store_name(row):
    # Check for store name in the second column (index 1)
    if len(row) >= 2 and row[1] and not pd.isna(row[1]):
        store = str(row[1]).strip()
        # Common identifiers for store names - expanded to include MALL
        store_indicators = ['CHECKERS', 'SPAR', 'PNP', 'SAVEWAYS', 'GROVE', 'HAZYVIEW', 'BARBERTON', 'PLAZA', 'KLIPFONTEIN', 'MALL']
        if any(indicator in store.upper() for indicator in store_indicators):
            return store
    return None

# New pivot-based approach for extraction
print("\nStarting new pivot-based extraction...")

# Process the dataframe to extract the returns data
# Extended pattern to match both "31 MAR - 6 APR 2025" and "1 - 7 MAY" formats
week_pattern = r'((?:\d+\s+[A-Z]{3,4}\s*-\s*\d+\s+[A-Z]{3,4}\s+2025)|(?:\d+\s*-\s*\d+\s+[A-Z]{3,4}))'

# Pre-scan for cake header rows in early part of the sheet
# This is needed specifically for data that appears before the first date marker
early_cake_positions = None
for i in range(10):  # Check first few rows
    if i < len(df):
        row_values = [str(df.iloc[i][col]).strip() if pd.notna(df.iloc[i][col]) else '' for col in range(len(df.columns))]
        if is_cake_header_row(row_values):
            early_cake_positions = extract_cake_types(row_values)
            print(f"Pre-scan found early cake header at row {i}: {early_cake_positions}")
            break

# Pre-scan for the first week in the sheet to handle data that appears before date headers
first_week = None
for i, row in df.iterrows():
    for col in range(len(row)):
        if pd.notna(row[col]):
            val = str(row[col]).strip()
            match = re.search(week_pattern, val)
            if match:
                first_week = match.group(1)
                if '2025' not in first_week:
                    first_week = f"{first_week} 2025"
                print(f"Pre-scan found first week: {first_week} at row {i}")
                break
    if first_week:
        break

# Initialize variables for tracking context
current_week = first_week  # Start with the first week found (may be None initially)
current_store = None
cake_type_positions = {}  # Map each cake type to its column position

# If we found cake positions in early rows, use them to initialize
if early_cake_positions:
    cake_type_positions = early_cake_positions

# Main extraction loop
for index, row in df.iterrows():
    row_values = [str(row[col]).strip() if pd.notna(row[col]) else '' for col in range(len(df.columns))]
    
    # Check if this is a date row
    for val in row_values:
        match = re.search(week_pattern, val)
        if match:
            current_week = match.group(1)
            # If the year is not in the date string, add it
            if '2025' not in current_week:
                current_week = f"{current_week} 2025"
            print(f"Row {index}: Found week: {current_week}")
            break
    
    # Check if this is a cake type header row
    if is_cake_header_row(row_values):
        cake_type_positions = extract_cake_types(row_values)
        print(f"Row {index}: Found cake header row with cake types at positions: {cake_type_positions}")
        continue
    
    # Check for store name
    store_name = extract_store_name(row_values)
    if store_name:
        current_store = store_name
        print(f"Row {index}: Found store: {current_store}")
    
    # Check for RETURNS row (but not RETURN TOTAL or other similar rows)
    is_returns_row = False
    for val in row_values[:3]:  # Check first few columns for the word RETURNS
        if 'RETURNS' in val.upper() and not any(exclude in val.upper() for exclude in ['RETURN TOTAL', 'TOTAL BEFORE', 'GRAND TOTAL']):
            is_returns_row = True
            break
    
    if is_returns_row and current_store and cake_type_positions and current_week:
        print(f"Row {index}: Processing RETURNS for store: {current_store}")
        
        # Index 3 is usually column D, where the cake type values start
        data_start_index = 3
        
        # Collect returns data from this row
        for cake_type, pos in cake_type_positions.items():
            if pos >= data_start_index:  # Skip non-data columns
                value = row.iloc[pos]
                if pd.notna(value) and str(value).strip() != '' and str(value).strip().upper() != 'TOTALS':
                    # Only add if it's a numeric value
                    try:
                        numeric_value = float(value)
                        weeks.append(current_week)
                        years.append('2025')  # Hardcoded for now
                        stores.append(current_store)
                        cake_types.append(cake_type)
                        returns.append(numeric_value)
                        return_amounts.append(0)  # Will be updated in RETURN TOTAL row
                        print(f"  Added return for {cake_type}: {numeric_value}")
                    except (ValueError, TypeError):
                        # Skip non-numeric values
                        pass
    
    # Check for RETURN TOTAL row
    is_return_total_row = False
    for val in row_values[:3]:  # Check first few columns for RETURN TOTAL
        if 'RETURN TOTAL' in val.upper():
            is_return_total_row = True
            break
    
    if is_return_total_row and current_store and cake_type_positions and current_week:
        print(f"Row {index}: Processing RETURN TOTAL for store: {current_store}")
        
        # Index 3 is usually column D, where the cake type values start
        data_start_index = 3
        
        # Collect return amount data
        for cake_type, pos in cake_type_positions.items():
            if pos >= data_start_index:  # Skip non-data columns
                value = row.iloc[pos]
                if pd.notna(value) and str(value).strip() != '' and str(value).strip().upper() != 'TOTALS':
                    # Only process if it's a numeric value
                    try:
                        numeric_value = float(value)
                        # Try to match with the corresponding returns entry
                        for i in range(len(weeks) - 1, -1, -1):
                            if stores[i] == current_store and cake_types[i] == cake_type and weeks[i] == current_week:
                                return_amounts[i] = numeric_value
                                print(f"  Updated return amount for {cake_type}: {numeric_value}")
                                break
                    except (ValueError, TypeError):
                        # Skip non-numeric values
                        pass

print(f"\nExtraction complete. Total records extracted: {len(weeks)}")

# Create a new dataframe with extracted data
returns_df = pd.DataFrame({
    'Week': weeks,
    'Year': years,
    'Store': stores,
    'CakeType': cake_types,
    'Returns': returns,
    'ReturnAmount': return_amounts
})

# Convert numeric columns
returns_df['Returns'] = pd.to_numeric(returns_df['Returns'], errors='coerce')
returns_df['ReturnAmount'] = pd.to_numeric(returns_df['ReturnAmount'], errors='coerce')

# Round to 2 decimal places to fix floating-point precision issues
returns_df['ReturnAmount'] = returns_df['ReturnAmount'].round(2)

# Remove any rows where either 'Returns' or 'ReturnAmount' contains non-numeric values
returns_df = returns_df.dropna(subset=['Returns', 'ReturnAmount'])

# Save to CSV
returns_df.to_csv(output_file, index=False)
print(f"Data saved to {output_file}")
if len(weeks) == 0:
    print("WARNING: No data was extracted. Check if the sheet structure matches expectations (DELIVERED, RETURNS, RETURN TOTAL rows).")
else:
    print(f"Successfully extracted {len(returns_df)} records with valid numeric values.")
    
# Print a sample of the data for verification
print("\nSample of extracted data:")
print(returns_df.head())
