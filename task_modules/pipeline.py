"""
Pipeline tasks for Brothers Baking data pipeline
Orchestrates the complete data processing pipeline
"""
import os
from invoke import task
from . import extract, format, combine


@task(pre=[extract.all])
def extract_all(c):
    """Run all extraction tasks"""
    print("🎉 All extraction tasks completed!")


@task(pre=[format.all])
def format_all(c):
    """Run all formatting tasks"""
    print("🎉 All formatting tasks completed!")


@task(pre=[combine.all])
def combine_all(c):
    """Run all combination tasks"""
    print("🎉 All combination tasks completed!")


@task(pre=[extract_all, format_all, combine_all])
def all(c):
    """Run the complete data pipeline: extract -> format -> combine"""
    print("\n" + "="*60)
    print("🎉 COMPLETE PIPELINE EXECUTION SUCCESSFUL! 🎉")
    print("="*60)
    print("✅ All extraction tasks completed")
    print("✅ All formatting tasks completed")
    print("✅ All combination tasks completed")
    print("\n📊 Your data is now ready for analysis!")
    print("🚀 Run 'invoke app.run' to start the dashboard")


@task
def clean(c):
    """Clean all pipeline outputs"""
    print("🧹 Cleaning all pipeline outputs...")
    
    # Clean data directory (except source files)
    data_patterns = [
        "data/*_formatted.csv",
        "data/*_combined.csv",
        "raw_outputs/*"
    ]
    
    for pattern in data_patterns:
        c.run(f"rm -f {pattern}", warn=True)
        print(f"🗑️  Cleaned {pattern}")
    
    print("✅ Pipeline cleanup completed")


@task
def status(c):
    """Check pipeline status and data file availability"""
    print("📊 Pipeline Status Check")
    print("="*40)
    
    # Check extraction outputs
    extract_files = [
        "raw_outputs/daily_income_expense.csv",
        "raw_outputs/expenses_daily.csv",
        "raw_outputs/daily_weekly_expenses.csv",
        "raw_outputs/weekly_deliveries.csv",
        "raw_outputs/weekly_deliveries_returns.csv"
    ]
    
    print("\n📥 Extraction Outputs:")
    extract_complete = True
    for file_path in extract_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            extract_complete = False
    
    # Check formatting outputs
    format_files = [
        "data/daily_income_expense_expense_formatted.csv",
        "data/expense_daily_formatted.csv",
        "data/daily_weekly_expenses_formatted.csv",
        "data/deliveries_formatted.csv",
        "data/returns_formatted.csv"
    ]
    
    print("\n🔧 Formatting Outputs:")
    format_complete = True
    for file_path in format_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            format_complete = False
    
    # Check combination outputs
    combine_files = [
        "data/deliveries_returns_combined.csv"
    ]
    
    print("\n🔗 Combination Outputs:")
    combine_complete = True
    for file_path in combine_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            combine_complete = False
    
    # Summary
    print("\n" + "="*40)
    if extract_complete and format_complete and combine_complete:
        print("🎉 Pipeline is COMPLETE and ready!")
        print("🚀 Run 'invoke app.run' to start the dashboard")
    else:
        print("⚠️  Pipeline is INCOMPLETE")
        if not extract_complete:
            print("   Run 'invoke extract.all' to complete extraction")
        if not format_complete:
            print("   Run 'invoke format.all' to complete formatting")
        if not combine_complete:
            print("   Run 'invoke combine.all' to complete combination")
        print("   Or run 'invoke pipeline.all' to run the complete pipeline") 