#!/usr/bin/env python3
"""
Combine deliveries and returns data by creating a hash of common columns
and joining on that hash to create a unified dataset.
"""
import pandas as pd
import hashlib
import os

def create_hash(row):
    """Create a hash from Week, Year, Store, CakeType, WeekIndex columns"""
    # Convert all values to strings and concatenate
    hash_string = f"{row['Week']}|{row['Year']}|{row['Store']}|{row['CakeType']}|{row['WeekIndex']}"
    # Create MD5 hash
    return hashlib.md5(hash_string.encode()).hexdigest()

def main():
    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    deliveries_path = os.path.join(project_dir, 'data', 'deliveries_formatted.csv')
    returns_path = os.path.join(project_dir, 'data', 'returns_formatted.csv')
    output_path = os.path.join(project_dir, 'data', 'deliveries_returns_combined.csv')
    
    # Check if input files exist
    if not os.path.exists(deliveries_path):
        print(f"Error: Deliveries file not found at {deliveries_path}")
        return
    
    if not os.path.exists(returns_path):
        print(f"Error: Returns file not found at {returns_path}")
        return
    
    # Read the formatted data
    print("Reading deliveries data...")
    deliveries_df = pd.read_csv(deliveries_path)
    print(f"Loaded {len(deliveries_df)} delivery records")
    
    print("Reading returns data...")
    returns_df = pd.read_csv(returns_path)
    print(f"Loaded {len(returns_df)} return records")
    
    # Create hash columns for both dataframes
    print("Creating hash columns...")
    deliveries_df['hash'] = deliveries_df.apply(create_hash, axis=1)
    returns_df['hash'] = returns_df.apply(create_hash, axis=1)
    
    print(f"Created {deliveries_df['hash'].nunique()} unique hashes in deliveries data")
    print(f"Created {returns_df['hash'].nunique()} unique hashes in returns data")
    
    # Prepare returns data for joining - keep only hash and the returns columns
    returns_join = returns_df[['hash', 'Returns', 'ReturnAmount']].copy()
    
    # Perform left join on hash - keeping all deliveries records
    print("Joining data on hash...")
    combined_df = deliveries_df.merge(
        returns_join, 
        on='hash', 
        how='left'
    )
    
    # Fill NaN values in returns columns with 0 (for deliveries that have no returns)
    combined_df['Returns'] = combined_df['Returns'].fillna(0)
    combined_df['ReturnAmount'] = combined_df['ReturnAmount'].fillna(0)
    
    # Select and reorder columns for the final output
    final_columns = [
        'Week', 'Year', 'Store', 'CakeType', 'WeekIndex',
        'Delivered', 'DeliveryAmount', 'Returns', 'ReturnAmount'
    ]
    
    combined_df = combined_df[final_columns]
    
    # Sort by WeekIndex, Store, CakeType for consistent ordering
    combined_df = combined_df.sort_values(['WeekIndex', 'Store', 'CakeType'])
    
    # Save the combined data
    combined_df.to_csv(output_path, index=False)
    print(f"Combined data saved to {output_path}")
    print(f"Total records in combined dataset: {len(combined_df)}")
    
    # Show summary statistics
    print("\nSummary of combined data:")
    print(f"  - Unique weeks: {combined_df['Week'].nunique()}")
    print(f"  - Unique stores: {combined_df['Store'].nunique()}")
    print(f"  - Unique cake types: {combined_df['CakeType'].nunique()}")
    print(f"  - Records with deliveries: {len(combined_df[combined_df['Delivered'] > 0])}")
    print(f"  - Records with returns: {len(combined_df[combined_df['Returns'] > 0])}")
    print(f"  - Records with both deliveries and returns: {len(combined_df[(combined_df['Delivered'] > 0) & (combined_df['Returns'] > 0)])}")
    
    # Show sample of the data
    print("\nSample of combined data:")
    print(combined_df.head(10))
    
    # Check for any Ermelo stores specifically
    ermelo_data = combined_df[combined_df['Store'].str.contains('ERMELO', na=False)]
    if not ermelo_data.empty:
        print(f"\nErmelo stores in combined data:")
        print(f"  - ERMELO CHECKERS: {len(ermelo_data[ermelo_data['Store'] == 'ERMELO CHECKERS'])} records")
        print(f"  - ERMELO MERINO MALL: {len(ermelo_data[ermelo_data['Store'] == 'ERMELO MERINO MALL'])} records")

if __name__ == "__main__":
    main() 