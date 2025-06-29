"""
Format tasks for Brothers Baking data pipeline
Handles all data formatting operations
"""
import os
from invoke import task
from pathlib import Path


@task
def daily_income_expense(c):
    """Format daily income expense data"""
    print("🔄 Formatting daily income expense data...")
    c.run("python scripts/format_daily_income_expense.py")
    print("✅ Daily income expense formatting completed")


@task
def expense_daily(c):
    """Format daily expenses data"""
    print("🔄 Formatting daily expenses data...")
    c.run("python scripts/format_expense_daily.py")
    print("✅ Daily expenses formatting completed")


@task
def daily_weekly_expenses(c):
    """Format daily weekly expenses data"""
    print("🔄 Formatting daily weekly expenses data...")
    c.run("python scripts/format_daily_weekly_expenses.py")
    print("✅ Daily weekly expenses formatting completed")


@task
def weekly_deliveries(c):
    """Format weekly deliveries data"""
    print("🔄 Formatting weekly deliveries data...")
    c.run("python scripts/format_weekly_deliveries.py")
    print("✅ Weekly deliveries formatting completed")


@task
def weekly_deliveries_returns(c):
    """Format weekly deliveries and returns data"""
    print("🔄 Formatting weekly deliveries and returns data...")
    c.run("python scripts/format_weekly_deliveries_returns.py")
    print("✅ Weekly deliveries and returns formatting completed")


@task(pre=[daily_income_expense, expense_daily, daily_weekly_expenses, weekly_deliveries, weekly_deliveries_returns])
def all(c):
    """Run all formatting tasks"""
    print("🎉 All formatting tasks completed successfully!")


@task
def clean(c):
    """Clean formatting outputs"""
    print("🧹 Cleaning formatting outputs...")
    # Add cleanup logic here if needed
    print("✅ Formatting cleanup completed") 