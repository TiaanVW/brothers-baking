"""
Combine tasks for Brothers Baking data pipeline
Handles all data combination operations
"""
import os
from invoke import task
from pathlib import Path


@task
def deliveries_returns(c):
    """Combine deliveries and returns data"""
    print("🔄 Combining deliveries and returns data...")
    c.run("python scripts/combine_deliveries_returns.py")
    print("✅ Deliveries and returns combination completed")


@task(pre=[deliveries_returns])
def all(c):
    """Run all combination tasks"""
    print("🎉 All combination tasks completed successfully!")


@task
def clean(c):
    """Clean combination outputs"""
    print("🧹 Cleaning combination outputs...")
    # Add cleanup logic here if needed
    print("✅ Combination cleanup completed") 