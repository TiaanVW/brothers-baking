# Brothers Baking Data Pipeline - Invoke Guide

## Overview

This project uses [Invoke](https://www.pyinvoke.org/) for task orchestration and automation. Invoke provides a clean, Pythonic way to define and run tasks for data processing, application management, and development workflows.

## Installation

Make sure Invoke is installed in your virtual environment:

```bash
# Activate your virtual environment
source venv/bin/activate

# Install dependencies (includes Invoke)
pip install -r requirements.txt
```

## Task Structure

The tasks are organized into modular collections following best practices:

```
tasks/
├── __init__.py              # Tasks module initialization
├── extract.py               # Data extraction tasks
├── format.py                # Data formatting tasks  
├── combine.py               # Data combination tasks
├── pipeline.py              # Complete pipeline orchestration
└── app.py                   # Application management tasks
```

## Available Commands

### 📋 List All Tasks
```bash
invoke --list
```

### 🔄 Pipeline Operations

#### Run Complete Pipeline
```bash
invoke pipeline.all          # Extract → Format → Combine
# or
invoke run-pipeline         # Convenience alias
```

#### Run Individual Stages
```bash
invoke extract.all          # Run all extraction tasks
invoke format.all           # Run all formatting tasks  
invoke combine.all          # Run all combination tasks
```

#### Check Pipeline Status
```bash
invoke pipeline.status      # Check what files exist
# or
invoke status              # Convenience alias
```

#### Clean Pipeline Outputs
```bash
invoke pipeline.clean       # Remove all generated files
```

### 📊 Data Extraction Tasks

```bash
invoke extract.daily-income-expense      # Extract daily income/expense data
invoke extract.expenses-daily            # Extract daily expenses data
invoke extract.daily-weekly-expenses     # Extract weekly expenses data
invoke extract.weekly-deliveries         # Extract delivery data
invoke extract.weekly-deliveries-returns # Extract delivery/return data
invoke extract.all                       # Run all extraction tasks
invoke extract.clean                     # Clean extraction outputs
```

### 🔧 Data Formatting Tasks

```bash
invoke format.daily-income-expense       # Format daily income/expense data
invoke format.expense-daily              # Format daily expenses data
invoke format.daily-weekly-expenses      # Format weekly expenses data
invoke format.weekly-deliveries          # Format delivery data
invoke format.weekly-deliveries-returns  # Format delivery/return data
invoke format.all                        # Run all formatting tasks
invoke format.clean                      # Clean formatting outputs
```

### 🔗 Data Combination Tasks

```bash
invoke combine.deliveries-returns        # Combine deliveries and returns
invoke combine.all                       # Run all combination tasks
invoke combine.clean                     # Clean combination outputs
```

### 🚀 Application Management

#### Run the Dashboard
```bash
invoke app.run                          # Start on localhost:8501
invoke app.run --port=8502              # Start on custom port
invoke app.run --host=0.0.0.0           # Start on all interfaces
# or
invoke run-app                          # Convenience alias
```

#### Run in Headless Mode
```bash
invoke app.run-headless                 # For server deployments
invoke app.run-headless --port=8502     # Custom port
```

#### Test and Maintenance
```bash
invoke app.test                         # Test app imports
invoke app.check-data                   # Check required data files
# or
invoke check-data                       # Convenience alias

invoke app.clean-cache                  # Clean Streamlit cache
```

## Typical Workflows

### 🏁 First Time Setup
```bash
# 1. Check current status
invoke status

# 2. Run complete pipeline
invoke pipeline.all

# 3. Start the dashboard
invoke app.run
```

### 🔄 Daily Data Update
```bash
# 1. Clean previous outputs
invoke pipeline.clean

# 2. Run pipeline
invoke pipeline.all

# 3. Check everything is ready
invoke check-data
```

### 🐛 Debugging Pipeline Issues
```bash
# 1. Check status to see what's missing
invoke status

# 2. Run individual stages
invoke extract.all
invoke format.all
invoke combine.all

# 3. Test app
invoke app.test
```

### 🚀 Production Deployment
```bash
# 1. Ensure all data is ready
invoke pipeline.all

# 2. Test the application
invoke app.test

# 3. Start in headless mode
invoke app.run-headless --port=8501
```

## Task Dependencies

The pipeline follows this dependency chain:

```
extract.all
    ↓
format.all (depends on extract.all)
    ↓  
combine.all (depends on format.all)
    ↓
pipeline.all (orchestrates all stages)
```

Individual tasks within each stage can run in parallel, but stages must complete in order.

## Configuration

### Default Settings

The `invoke.yaml` file contains default configuration:

```yaml
# Global settings
run:
  echo: true                    # Show command output
  env:
    PYTHONPATH: "."            # Ensure proper imports
    STREAMLIT_BROWSER_GATHER_USAGE_STATS: "false"

# Task-specific settings  
tasks:
  app:
    default_port: 8501         # Default Streamlit port
    default_host: "localhost"  # Default host
```

### Environment Variables

You can override settings with environment variables:

```bash
export STREAMLIT_SERVER_PORT=8502
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
invoke app.run
```

## Error Handling

### Common Issues

1. **Missing Data Files**
   ```bash
   invoke check-data          # See what's missing
   invoke pipeline.all        # Regenerate all data
   ```

2. **Import Errors**
   ```bash
   invoke app.test           # Test imports
   # Check PYTHONPATH in invoke.yaml
   ```

3. **Port Already in Use**
   ```bash
   invoke app.run --port=8502  # Use different port
   ```

4. **Permission Errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   invoke --version           # Verify Invoke is available
   ```

## Advanced Usage

### Custom Task Parameters

```bash
# Run with custom parameters
invoke app.run --port=8080 --host=0.0.0.0

# Chain multiple tasks
invoke pipeline.clean pipeline.all app.run
```

### Parallel Execution

Tasks within the same stage can run in parallel:

```bash
# These run simultaneously within extract.all
invoke extract.daily-income-expense &
invoke extract.expenses-daily &
invoke extract.daily-weekly-expenses &
wait  # Wait for all to complete
```

### Custom Environment

```bash
# Set custom environment for tasks
PYTHONPATH=/custom/path invoke pipeline.all
```

## Integration with Development Workflow

### Git Hooks Integration

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
invoke app.test || exit 1
```

### CI/CD Integration

```yaml
# .github/workflows/pipeline.yml
- name: Run Data Pipeline
  run: |
    source venv/bin/activate
    invoke pipeline.all
    invoke app.test
```

## Troubleshooting

### Debug Mode

Add `--echo` flag for verbose output:

```bash
invoke --echo pipeline.all
```

### Check Task Dependencies

```bash
invoke --list --verbose       # Show task details
```

### Manual Script Execution

If Invoke tasks fail, you can run scripts manually:

```bash
python scripts/extract_daily_income_expense.py
python scripts/format_daily_income_expense.py
# etc.
```

## Best Practices

1. **Always check status first**: `invoke status`
2. **Use the complete pipeline**: `invoke pipeline.all` for consistency
3. **Test after changes**: `invoke app.test`
4. **Clean between runs**: `invoke pipeline.clean` if needed
5. **Use convenience aliases**: `invoke run-app` instead of `invoke app.run`

## Getting Help

```bash
invoke --help                 # General help
invoke pipeline.all --help    # Task-specific help
invoke --list                 # List all available tasks
``` 