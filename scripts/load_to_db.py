#!/usr/bin/env python3
"""
Database loader script for Brothers Baking.
Loads processed CSV data into DuckDB database.
"""
import os
import sys
import pandas as pd
import glob
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_utils import get_db_connection, insert_dataframe

# Define paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DB_DIR = os.path.join(PROJECT_DIR, "db")

def load_csv_to_db(conn, csv_path, if_exists='replace'):
    """
    Load a CSV file into the database.
    
    Args:
        conn: Database connection
        csv_path: Path to CSV file
        if_exists: What to do if table exists ('append', 'replace', 'fail')
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get table name from file name (without extension)
        file_name = os.path.basename(csv_path)
        table_name = Path(file_name).stem
        
        print(f"Loading {file_name} into table '{table_name}'...")
        
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        # Create SQL statement to create or replace table
        if if_exists == 'replace':
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Create table and load data
        # Use the DataFrame we already loaded rather than the file path
        # This avoids potential issues with path formatting
        conn.execute(f"DROP TABLE IF EXISTS temp_table")
        conn.execute("CREATE TABLE temp_table AS SELECT * FROM df")
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM temp_table")
        conn.execute(f"DROP TABLE IF EXISTS temp_table")
        
        # Get and print row count
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  Loaded {row_count} rows into table '{table_name}'")
        
        return True
    except Exception as e:
        print(f"Error loading {csv_path}: {e}")
        return False

def main():
    """
    Main function to load all CSV files into the database.
    """
    print("Loading data files into database...")
    
    # Create db directory if it doesn't exist
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Connect to database
    conn = get_db_connection()
    
    # Get list of all CSV files
    csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    
    if not csv_files:
        print("No CSV files found in the data directory.")
        return
    
    # Load each CSV file
    for csv_file in csv_files:
        load_csv_to_db(conn, csv_file)
    
    # List all tables
    print("\nAvailable tables in the database:")
    tables = conn.execute("SHOW TABLES").fetchall()
    for table in tables:
        print(f"  - {table[0]}")
    
    # Close the connection
    conn.close()
    
    print("\nData loading complete!")

if __name__ == "__main__":
    main()
