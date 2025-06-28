#!/usr/bin/env python3

import os
import pandas as pd
import re
import numpy as np


def get_week_start_timestamp(week_str):
    """
    Convert a week string to a sortable timestamp based on its first date
    Handles formats like:
    - '31 MAR - 6 APR 2025'
    - '7 - 13 APR 2025'
    - '28 APR - 4 MAY 2025'
    """
    month_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
        'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
        'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    
    try:
        # Remove year suffix if present for parsing (but keep original format in data)
        normalized_str = week_str
        if '2025' in normalized_str:
            normalized_str = normalized_str.replace(' 2025', '')
        
        # Handle various date formats
        if ' - ' in normalized_str or '-' in normalized_str:
            # Standardize separator
            parts = normalized_str.replace(' - ', '-').split('-')
            first_part = parts[0].strip()
            
            # Extract day and month from the first part
            if ' ' in first_part:
                # Format like "31 MAR"
                day_str, month_str = first_part.split()
                day = int(day_str)
                month = month_map.get(month_str.strip(), 0)
            else:
                # Format like "7" (day only, month in second part)
                day = int(first_part)
                
                # Extract month from second part (e.g., "13 APR")
                second_part = parts[1].strip()
                month_parts = second_part.split()
                
                # Month will be the last word in second part if it's not a number
                for part in month_parts:
                    if not part.isdigit() and part in month_map:
                        month = month_map.get(part, 0)
                        break
                else:
                    # If we can't find a month, use the month from another part of the data
                    print(f"Warning: Could not find month in '{second_part}', using current month")
                    month = 1  # Fallback
            
            # Year is always 2025 for this dataset
            year = 2025
            
            # Create a sortable timestamp (year * 10000 + month * 100 + day)
            timestamp = year * 10000 + month * 100 + day
            return timestamp
        
        print(f"Warning: Could not parse week format for '{week_str}', using default ordering")
        return 0  # Default fallback
        
    except Exception as e:
        print(f"Error parsing week '{week_str}': {e}")
        return 0


def main():
    # Define input and output paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    raw_returns_path = os.path.join(project_dir, 'data', 'raw_returns.csv')
    output_path = os.path.join(project_dir, 'data', 'returns_formatted.csv')
    
    # Read the raw returns data
    print(f"Reading raw returns data from {raw_returns_path}")
    raw_df = pd.read_csv(raw_returns_path)
    
    # Extract all unique weeks from the data
    unique_weeks = sorted(raw_df['Week'].unique())
    print(f"Found {len(unique_weeks)} unique weeks in raw data: {unique_weeks}")
    
    # Create a list of (week, timestamp) tuples for sorting
    week_dates = [(week, get_week_start_timestamp(week)) for week in unique_weeks]
    
    # Sort by timestamp to get chronological order
    week_dates.sort(key=lambda x: x[1])
    
    # Print ordered weeks with timestamps for verification
    print("\nOrdered weeks by start date:")
    for week, timestamp in week_dates:
        print(f"  {week}: {timestamp}")
    
    # Create dynamic week ordering mapping (1-based index)
    chronological_order = {week: i+1 for i, (week, _) in enumerate(week_dates)}
    print(f"\nDynamic week ordering: {chronological_order}")
    
    # Create a copy of the raw data for formatting
    formatted_df = raw_df.copy()
    
    # Add WeekIndex column based on the dynamic mapping
    formatted_df['WeekIndex'] = formatted_df['Week'].map(chronological_order)
    
    # Sort the DataFrame by WeekIndex for chronological display
    formatted_df = formatted_df.sort_values(by=['WeekIndex', 'Store', 'CakeType'])
    
    # Save the formatted data
    formatted_df.to_csv(output_path, index=False)
    print(f"\nFormatted data saved to {output_path}")
    print(f"Total records: {len(formatted_df)}")
    
    # Summary of data - show records per week
    print("\nRecords per week:")
    week_counts = formatted_df.groupby(['Week', 'WeekIndex']).size().reset_index(name='RecordCount')
    for _, row in week_counts.iterrows():
        print(f"  Week {row['WeekIndex']} ({row['Week']}): {row['RecordCount']} records")


if __name__ == "__main__":
    main()