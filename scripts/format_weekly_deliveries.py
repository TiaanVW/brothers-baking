#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os
import re
from datetime import datetime, timedelta

def parse_week_string(week_str):
    """
    Parse a week string into a timestamp for sorting.
    Handles various formats:
    - "31 MAR - 6 APR 2025"
    - "7 - 13 APR 2025"
    - "28 APR - 4 MAY 2025"
    
    Returns the timestamp of the first day of the week for ordering.
    """
    # Strip any extra whitespace
    week_str = week_str.strip()
    
    # Try to extract year from the end
    year_match = re.search(r'(\d{4})$', week_str)
    if year_match:
        year = int(year_match.group(1))
    else:
        # Default to current year if not found
        year = 2025
    
    # Handle "31 MAR - 6 APR 2025" format
    pattern1 = re.compile(r'(\d+)\s+([A-Za-z]{3})\s*-\s*\d+\s+[A-Za-z]{3}\s+\d{4}')
    match1 = pattern1.search(week_str)
    if match1:
        day = int(match1.group(1))
        month_str = match1.group(2).upper()
        month_map = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
        month = month_map.get(month_str, 1)  # Default to January if not recognized
        return pd.Timestamp(year=year, month=month, day=day)
    
    # Handle "7 - 13 APR 2025" format
    pattern2 = re.compile(r'(\d+)\s*-\s*\d+\s+([A-Za-z]{3})\s+\d{4}')
    match2 = pattern2.search(week_str)
    if match2:
        day = int(match2.group(1))
        month_str = match2.group(2).upper()
        month_map = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                    'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
        month = month_map.get(month_str, 1)  # Default to January if not recognized
        return pd.Timestamp(year=year, month=month, day=day)
    
    # If we can't parse it, return a very early date to sort first
    print(f"Warning: Could not parse week string: {week_str}")
    return pd.Timestamp(year=1900, month=1, day=1)

# Define file paths
input_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw_deliveries.csv')
output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'deliveries_formatted.csv')

# Check if input file exists
if not os.path.exists(input_file):
    print(f"Error: Input file not found at {input_file}")
    print("Please run extract_weekly_deliveries.py first to generate the raw_deliveries.csv file.")
    exit(1)

try:
    # Read the raw deliveries data
    df = pd.read_csv(input_file)
    print(f"Data loaded. Rows: {len(df)}, Columns: {df.columns.tolist()}")
except Exception as e:
    print(f"Error reading input file: {e}")
    exit(1)

# Get all unique weeks from the data and filter out NaN values
unique_weeks = df['Week'].dropna().unique().tolist()
print(f"Found {len(unique_weeks)} unique weeks in the data:")
for week in unique_weeks:
    print(f"  - {week}")

# Create a mapping of weeks to their chronological index
# First, parse each week string to a timestamp
week_timestamps = [(week, parse_week_string(week)) for week in unique_weeks if isinstance(week, str)]

# Sort by timestamp
week_timestamps.sort(key=lambda x: x[1])

# Create a mapping from week string to index (1-based)
week_to_index = {week: i+1 for i, (week, _) in enumerate(week_timestamps)}

print("Chronological week ordering:")
for week, timestamp in week_timestamps:
    print(f"  {week_to_index[week]}: {week} => {timestamp}")

# Filter out rows with NaN week values
df = df.dropna(subset=['Week'])
print(f"After removing NaN week values, remaining records: {len(df)}")

# Add the WeekIndex to the dataframe
df['WeekIndex'] = df['Week'].map(week_to_index)

# Make sure all weeks have an index (check for any NaN values in WeekIndex)
if df['WeekIndex'].isna().any():
    print("Warning: Some weeks could not be mapped to an index:")
    for week in df.loc[df['WeekIndex'].isna(), 'Week'].unique():
        print(f"  - {week}")
    # Remove records with no week index
    df = df.dropna(subset=['WeekIndex'])
    print(f"After removing records with unmapped weeks, remaining records: {len(df)}")

# Sort the dataframe by WeekIndex, Store, CakeType for better organization
df = df.sort_values(['WeekIndex', 'Store', 'CakeType'])

# Save the formatted data
df.to_csv(output_file, index=False)
print(f"Formatted data saved to {output_file}")

# Display some statistics about the output data
print(f"Total records: {len(df)}")
print("Records per week:")
for week, count in df.groupby('Week').size().items():
    print(f"  {week}: {count} records")
