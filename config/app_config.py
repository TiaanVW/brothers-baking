"""
Configuration settings for Brothers Baking Analytics Dashboard
"""
import os

# App Configuration
APP_TITLE = "Brothers Baking - Data Analytics Dashboard"
APP_ICON = "🍞"
LAYOUT = "wide"

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")

# CSV File Paths
CSV_PATHS = {
    'daily_expense': os.path.join(DATA_DIR, 'daily_income_expense_expense_formatted.csv'),
    'daily_weekly_expenses': os.path.join(DATA_DIR, 'daily_weekly_expenses_formatted.csv'),
    'expense_daily': os.path.join(DATA_DIR, 'expense_daily_formatted.csv'),
    'returns': os.path.join(DATA_DIR, 'returns_formatted.csv'),
    'deliveries': os.path.join(DATA_DIR, 'deliveries_formatted.csv'),
    'deliveries_returns_combined': os.path.join(DATA_DIR, 'deliveries_returns_combined.csv')
}

# Page Configuration
PAGES = [
    "Daily Expenses", 
    "Daily Weekly Expenses", 
    "Expense Daily", 
    "Combined View", 
    "Returns Summary", 
    "Deliveries Summary", 
    "Deliveries & Returns Combined"
]

# Database Configuration
DB_CONFIG = {
    'database': ':memory:',
    'read_only': False
} 