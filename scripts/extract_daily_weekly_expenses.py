import pandas as pd
import numpy as np
from datetime import datetime
import re

# Configuration
input_file = 'data_sources/MAIN DOCUMENT 2025 (Autosaved).xlsx'
sheet_name = 'DAILY WEEKLY EXPENSES'
output_file = 'raw_outputs/daily_weekly_expenses.csv'

print(f"Processing {sheet_name} from {input_file}...")

# Load the raw data
raw_df = pd.read_excel(input_file, sheet_name=sheet_name, header=None)

# Step 1: Find and extract the week periods (they appear in row 2)
week_periods = {}
for col in range(raw_df.shape[1]):
    val = raw_df.iloc[1, col]
    if pd.notna(val) and isinstance(val, str) and ' - ' in val:
        week_periods[col] = val.strip()

print(f"Found {len(week_periods)} week periods")

# Step 2: Extract categories from row 3 (index 2)
categories = {}
for col in range(raw_df.shape[1]):
    val = raw_df.iloc[2, col]
    if pd.notna(val):
        categories[col] = str(val).strip()

print(f"Found {len(categories)} expense categories")

# Step 3: Process all rows to extract expense data
# Structure for normalized, machine-readable output
all_expenses = []

# Additional function to help determine the appropriate week for a column
def get_applicable_week(col_idx):
    for week_col in sorted(week_periods.keys(), reverse=True):
        if week_col <= col_idx:
            return week_periods[week_col]
    return None

# Debug the data extraction process
print(f"Starting data extraction process...")

# Iterate through all rows
for row_idx in range(3, raw_df.shape[0]):  # Process all rows
    # Check if this row contains a date in column B (index 1)
    cell_b = raw_df.iloc[row_idx, 1]
    
    print(f"Row {row_idx+1}: Checking for date in column B, value = {cell_b}, type = {type(cell_b).__name__}")
    
    if pd.notna(cell_b) and (isinstance(cell_b, datetime) or (isinstance(cell_b, str) and len(cell_b) == 10 and cell_b.count('-') == 2)):
        if isinstance(cell_b, str):
            date_value = datetime.strptime(cell_b, '%Y-%m-%d').date()
        else:
            date_value = cell_b.date()
        print(f"  - PROCESSING DATE ROW: {date_value}")
        
        # Try to get day from the next row
        day_value = None
        if row_idx + 1 < raw_df.shape[0]:
            next_cell_b = raw_df.iloc[row_idx + 1, 1]
            print(f"  - Checking for day in next row, value = {next_cell_b}, type = {type(next_cell_b).__name__}")
            if isinstance(next_cell_b, str) and any(day in next_cell_b.upper() for day in ['MON', 'TUE', 'TUES', 'WED', 'THU', 'THURS', 'FRI', 'SAT', 'SUN']):
                day_value = next_cell_b.strip().upper()
                print(f"    - FOUND DAY: {day_value}")
        
        # For each expense category column, extract values
        print(f"  - Checking for expenses in columns 6 to {raw_df.shape[1]}...")
        for col in range(5, raw_df.shape[1]):  # Start from column F (index 5), where expenses usually begin
            # Skip if this column doesn't have a category
            if col not in categories:
                print(f"    - Col {col+1}: No category defined, skipping")
                continue
                
            category = categories[col]
            value = raw_df.iloc[row_idx, col]
            
            print(f"    - Col {col+1} ({category}): Value = {value}, Type = {type(value).__name__}")
            
            # Only process non-zero numeric values
            if pd.notna(value) and isinstance(value, (int, float, np.integer, np.floating)) and value != 0:
                print(f"      - FOUND EXPENSE: {category} = {value}")
                # Get description (if any) from the next row
                description = ""
                if row_idx + 1 < raw_df.shape[0]:
                    desc_cell = raw_df.iloc[row_idx + 1, col]
                    if pd.notna(desc_cell) and not isinstance(desc_cell, (int, float, np.integer, np.floating)):
                        description = str(desc_cell).strip()
                        print(f"        - Description: {description}")
                
                # For "OTHER" category, get additional description from column X (index 23)
                if category == "OTHER" and col == 22 and pd.notna(raw_df.iloc[row_idx, 23]):
                    other_desc = str(raw_df.iloc[row_idx, 23]).strip()
                    if description:
                        description += f" - {other_desc}"
                    else:
                        description = other_desc
                    print(f"        - Additional 'OTHER' Description: {other_desc}")
                
                # Get the applicable week period
                week = get_applicable_week(col)
                print(f"      - Week Period: {week}")
                
                # Add to our normalized data structure
                all_expenses.append({
                    'Date': date_value,
                    'Day': day_value,
                    'Week Period': week,
                    'Category': category,
                    'Description': description,
                    'Amount': value
                })
                print(f"      - Added to dataset")
    else:
        print(f"  - Not a date row")

# Convert to DataFrame
print(f"Extracted {len(all_expenses)} expense records")
result_df = pd.DataFrame(all_expenses)

if not result_df.empty:
    # Step 4: Clean and enhance the data for Power BI
    
    # Ensure Date is in datetime format
    result_df['Date'] = pd.to_datetime(result_df['Date'])
    
    # Add time dimensions for easier analysis in Power BI
    result_df['Year'] = result_df['Date'].dt.year
    result_df['Month'] = result_df['Date'].dt.month
    result_df['Month Name'] = result_df['Date'].dt.strftime('%B')
    result_df['Quarter'] = result_df['Date'].dt.quarter
    result_df['Week Number'] = result_df['Date'].dt.isocalendar().week
    result_df['Day of Week'] = result_df['Date'].dt.dayofweek + 1  # 1=Monday, 7=Sunday
    
    # Extract week start/end dates for better time filtering
    def extract_date_range(week_str):
        try:
            if pd.isna(week_str) or not isinstance(week_str, str):
                return pd.NA, pd.NA
                
            parts = week_str.split(' - ')
            if len(parts) != 2:
                return pd.NA, pd.NA
                
            return parts[0], parts[1]
        except:
            return pd.NA, pd.NA
    
    if 'Week Period' in result_df.columns:
        result_df[['Week Start', 'Week End']] = result_df['Week Period'].apply(
            lambda x: pd.Series(extract_date_range(x))
        )
    
    # Clean up descriptions
    result_df['Description'] = result_df['Description'].fillna('')
    
    # Create a clean, standardized Category field
    result_df['Category_Clean'] = result_df['Category'].str.strip().str.upper()
    
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
    result_df['Running Total'] = result_df.groupby(['Category'])['Amount'].cumsum()
    
    # Sort by date for better readability
    result_df = result_df.sort_values(['Date', 'Category'])
    
    # Save to CSV in a format optimized for Power BI
    result_df.to_csv(output_file, index=False)
    print(f"Saved Power BI-ready data to {output_file}")
    
    # Create a pivot table version for alternative analysis
    print("Creating pivot table version...")
    pivot_df = result_df.pivot_table(
        index=['Date', 'Day', 'Week Period', 'Year', 'Month', 'Month Name'],
        columns='Category',
        values='Amount',
        aggfunc='sum',
        fill_value=0
    ).reset_index()
    
    pivot_output = 'daily_expenses_pivot.csv'
    pivot_df.to_csv(pivot_output)
    print(f"Saved pivot table to {pivot_output}")
    
    # Print summary statistics
    print("\nExpense summary by category:")
    summary = result_df.groupby('Category')['Amount'].agg(['sum', 'count']).reset_index()
    summary = summary.sort_values('sum', ascending=False)
    print(summary.head(10).to_string(index=False))
    
    # Print summary by category group
    print("\nExpense summary by category group:")
    group_summary = result_df.groupby('Category Group')['Amount'].agg(['sum', 'count']).reset_index()
    group_summary = group_summary.sort_values('sum', ascending=False)
    print(group_summary.to_string(index=False))
    
    # Print total
    total = result_df['Amount'].sum()
    print(f"\nTotal expenses: R{total:,.2f}")
    
    print("\nData is now ready for Power BI import:")
    print("1. In Power BI Desktop, use 'Get Data' → 'Text/CSV'")
    print("2. Select daily_expenses_powerbi_ready.csv")
    print("3. The data is already in a structured format ready for visualizations")
    print("4. Create date hierarchy using the date dimensions provided")
    print("5. Use Category and Category Group for meaningful breakdowns")
else:
    print("No expense data was extracted. Please check the Excel file structure.")
