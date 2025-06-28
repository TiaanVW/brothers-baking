#!/usr/bin/env python3
"""
Database utility functions for Brothers Baking application.
Handles connections and queries to the DuckDB database.
"""
import os
import pandas as pd
import duckdb
from typing import Optional, List, Dict, Any, Union

# Path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "data.duckdb")

def get_db_connection():
    """
    Create and return a connection to the DuckDB database.
    
    Returns:
        DuckDB connection object
    """
    # Create the connection (read-only is False to allow writes)
    conn = duckdb.connect(database=DB_PATH, read_only=False)
    return conn

def run_query(conn, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Execute a SQL query and return the results as a pandas DataFrame.
    
    Args:
        conn: DuckDB connection
        query: SQL query string
        params: Optional parameters for the query
    
    Returns:
        pandas DataFrame with query results
    """
    try:
        if params:
            result = conn.execute(query, params).fetchdf()
        else:
            result = conn.execute(query).fetchdf()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()

def get_table_names(conn) -> List[str]:
    """
    Get a list of all tables in the database.
    
    Args:
        conn: DuckDB connection
    
    Returns:
        List of table names
    """
    result = conn.execute("SHOW TABLES").fetchall()
    return [row[0] for row in result]

def get_table_schema(conn, table_name: str) -> pd.DataFrame:
    """
    Get the schema information for a specific table.
    
    Args:
        conn: DuckDB connection
        table_name: Name of the table
    
    Returns:
        DataFrame with column information
    """
    # PRAGMA query gets column info
    result = conn.execute(f"PRAGMA table_info('{table_name}')").fetchdf()
    return result

def insert_dataframe(conn, df: pd.DataFrame, table_name: str, if_exists: str = "append") -> bool:
    """
    Insert a pandas DataFrame into a DuckDB table.
    
    Args:
        conn: DuckDB connection
        df: DataFrame to insert
        table_name: Target table name
        if_exists: What to do if table exists ('append', 'replace', 'fail')
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if table exists
        table_exists = conn.execute(f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{table_name}'").fetchone()[0] > 0
        
        if table_exists and if_exists == "replace":
            conn.execute(f"DROP TABLE {table_name}")
            table_exists = False
        elif table_exists and if_exists == "fail":
            raise Exception(f"Table {table_name} already exists")
        
        # Create table if it doesn't exist
        if not table_exists:
            # Create relation from dataframe
            conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM df")
        else:
            # Append data
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
        
        return True
    except Exception as e:
        print(f"Error inserting dataframe: {e}")
        return False
