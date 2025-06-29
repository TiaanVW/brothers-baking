"""
Extract tasks for Brothers Baking data pipeline
Handles all data extraction operations
"""
import os
from invoke import task
from pathlib import Path


@task
def daily_income_expense(c):
    """Extract daily income expense data"""
    print("🔄 Extracting daily income expense data...")
    c.run("python scripts/extract_daily_income_expense.py")
    print("✅ Daily income expense extraction completed")


@task
def expenses_daily(c):
    """Extract daily expenses data"""
    print("🔄 Extracting daily expenses data...")
    c.run("python scripts/extract_expenses_daily.py")
    print("✅ Daily expenses extraction completed")


@task
def daily_weekly_expenses(c):
    """Extract daily weekly expenses data"""
    print("🔄 Extracting daily weekly expenses data...")
    c.run("python scripts/extract_daily_weekly_expenses.py")
    print("✅ Daily weekly expenses extraction completed")


@task
def weekly_deliveries(c):
    """Extract weekly deliveries data"""
    print("🔄 Extracting weekly deliveries data...")
    c.run("python scripts/extract_weekly_deliveries.py")
    print("✅ Weekly deliveries extraction completed")


@task
def weekly_deliveries_returns(c):
    """Extract weekly deliveries and returns data"""
    print("🔄 Extracting weekly deliveries and returns data...")
    c.run("python scripts/extract_weekly_deliveries_returns.py")
    print("✅ Weekly deliveries and returns extraction completed")


@task(pre=[daily_income_expense, expenses_daily, daily_weekly_expenses, weekly_deliveries, weekly_deliveries_returns])
def all(c):
    """Run all extraction tasks"""
    print("🎉 All extraction tasks completed successfully!")


@task
def clean(c):
    """Clean extraction outputs"""
    print("🧹 Cleaning extraction outputs...")
    # Add cleanup logic here if needed
    print("✅ Extraction cleanup completed") 