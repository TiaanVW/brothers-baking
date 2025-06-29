"""
App tasks for Brothers Baking data pipeline
Handles application management operations
"""
import os
from invoke import task
from pathlib import Path


@task
def run(c, port=8501, host="localhost"):
    """Run the Streamlit application"""
    print(f"🚀 Starting Brothers Baking Analytics Dashboard on {host}:{port}...")
    c.run(f"streamlit run app.py --server.port={port} --server.address={host}")


@task
def run_headless(c, port=8501):
    """Run the Streamlit application in headless mode"""
    print(f"🚀 Starting Brothers Baking Analytics Dashboard (headless) on port {port}...")
    c.run(f"streamlit run app.py --server.headless=true --server.port={port}")


@task
def test(c):
    """Test the application imports and basic functionality"""
    print("🧪 Testing application imports...")
    c.run("python -c 'from app import main; print(\"✅ App imports successfully\")'")
    print("✅ Application test completed")


@task
def check_data(c):
    """Check if required data files exist"""
    print("📊 Checking data files...")
    
    required_files = [
        "data/deliveries_returns_combined.csv",
        "data/daily_income_expense_expense_formatted.csv",
        "data/daily_weekly_expenses_formatted.csv",
        "data/expense_daily_formatted.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Warning: {len(missing_files)} required data files are missing.")
        print("Run 'invoke pipeline.all' to generate missing data files.")
    else:
        print("\n🎉 All required data files are present!")


@task
def clean_cache(c):
    """Clean Streamlit cache and temporary files"""
    print("🧹 Cleaning Streamlit cache...")
    
    # Clean Streamlit cache directory
    cache_dirs = [
        ".streamlit",
        "__pycache__",
        "**/__pycache__"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            c.run(f"rm -rf {cache_dir}")
            print(f"🗑️  Removed {cache_dir}")
    
    print("✅ Cache cleanup completed") 