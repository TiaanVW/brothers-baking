"""
Data service layer for Brothers Baking Analytics Dashboard
Handles database connections, data loading, and query execution
"""
import duckdb
import pandas as pd
import os
import streamlit as st
from config.app_config import CSV_PATHS, DB_CONFIG


class DataService:
    """Service class for handling data operations"""
    
    def __init__(self):
        """Initialize database connection and load data"""
        self.conn = duckdb.connect(
            database=DB_CONFIG['database'], 
            read_only=DB_CONFIG['read_only']
        )
        self._load_csv_data()
    
    def _load_csv_data(self):
        """Load CSV files into DuckDB tables"""
        for table_name, path in CSV_PATHS.items():
            try:
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    print(f"Loading {path} into {table_name} table")
                    
                    # Handle special data type conversions for specific tables
                    if table_name in ['returns', 'deliveries', 'deliveries_returns_combined']:
                        df = pd.read_csv(path)
                        df = self._ensure_numeric_columns(df, table_name)
                        
                        # Create temporary CSV with proper types
                        temp_path = path + '.temp'
                        df.to_csv(temp_path, index=False)
                        
                        # Load from temp file
                        self.conn.execute(
                            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{temp_path}')"
                        )
                        
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    else:
                        self.conn.execute(
                            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{path}')"
                        )
                    print(f"Successfully loaded {path} into {table_name} table")
                else:
                    print(f"Warning: {path} does not exist or is empty")
            except Exception as e:
                print(f"Error loading {path}: {e}")
    
    def _ensure_numeric_columns(self, df, table_name):
        """Ensure numeric columns are properly typed"""
        if table_name == 'returns':
            df['Returns'] = pd.to_numeric(df['Returns'], errors='coerce').fillna(0)
            df['ReturnAmount'] = pd.to_numeric(df['ReturnAmount'], errors='coerce').fillna(0)
        elif table_name == 'deliveries':
            df['Delivered'] = pd.to_numeric(df['Delivered'], errors='coerce').fillna(0)
            df['DeliveryAmount'] = pd.to_numeric(df['DeliveryAmount'], errors='coerce').fillna(0)
        elif table_name == 'deliveries_returns_combined':
            df['Delivered'] = pd.to_numeric(df['Delivered'], errors='coerce').fillna(0)
            df['DeliveryAmount'] = pd.to_numeric(df['DeliveryAmount'], errors='coerce').fillna(0)
            df['Returns'] = pd.to_numeric(df['Returns'], errors='coerce').fillna(0)
            df['ReturnAmount'] = pd.to_numeric(df['ReturnAmount'], errors='coerce').fillna(0)
        
        return df
    
    def run_query(self, query):
        """Execute a SQL query and return results as DataFrame"""
        try:
            return self.conn.execute(query).fetchdf()
        except Exception as e:
            st.error(f"DuckDB query error: {e}\nQuery: {query}")
            return pd.DataFrame()
    
    def get_distinct_values(self, table, column, where_clause=""):
        """Get distinct values from a table column with optional WHERE clause"""
        # Handle column names with spaces by quoting them
        if ' ' in column:
            column_quoted = f'"{column}"'
        else:
            column_quoted = column
            
        query = f"SELECT DISTINCT {column_quoted} FROM {table}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += f" ORDER BY {column_quoted}"
        
        result = self.run_query(query)
        return result[column].tolist() if not result.empty else []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Global data service instance
@st.cache_resource
def get_data_service():
    """Get cached data service instance"""
    return DataService() 