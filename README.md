# Brothers Baking Analytics Dashboard

A comprehensive data analytics dashboard for Brothers Baking, built with Streamlit and featuring a modular architecture with automated data pipeline orchestration.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)

### Installation

1. **Clone and setup environment:**
   ```bash
   cd brothers_baking
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Check pipeline status:**
   ```bash
   invoke status
   ```

3. **Run complete data pipeline:**
   ```bash
   invoke pipeline.all
   ```

4. **Start the dashboard:**
   ```bash
   invoke app.run
   ```

## 🏗️ Architecture

This project follows a clean, modular architecture:

```
brothers_baking/
├── app.py                          # Main Streamlit application
├── config/                         # Configuration settings
├── services/                       # Data service layer
├── components/                     # Reusable UI components
├── page_modules/                   # Individual page modules
├── task_modules/                   # Invoke task definitions
├── scripts/                        # Data processing scripts
└── data/                          # Processed data files
```

## 📊 Data Pipeline

The data processing pipeline consists of three stages:

1. **Extract** - Extract data from Excel sources
2. **Format** - Clean and format the extracted data
3. **Combine** - Merge related datasets

### Pipeline Commands

```bash
# Run complete pipeline
invoke pipeline.all

# Run individual stages
invoke extract.all
invoke format.all
invoke combine.all

# Check pipeline status
invoke status

# Clean pipeline outputs
invoke pipeline.clean
```

## 🎛️ Available Tasks

### Pipeline Operations
- `invoke pipeline.all` - Run complete pipeline
- `invoke pipeline.status` - Check pipeline status
- `invoke pipeline.clean` - Clean all outputs

### Data Processing
- `invoke extract.all` - Run all extraction tasks
- `invoke format.all` - Run all formatting tasks
- `invoke combine.all` - Run all combination tasks

### Application Management
- `invoke app.run` - Start the dashboard
- `invoke app.test` - Test application imports
- `invoke app.check-data` - Verify required data files

### Convenience Commands
- `invoke status` - Quick status check
- `invoke run-app` - Start dashboard (alias)
- `invoke run-pipeline` - Run complete pipeline (alias)

## 📈 Dashboard Features

### Available Pages
- **Daily Expenses** - Daily expense analysis
- **Daily Weekly Expenses** - Weekly expense trends
- **Expense Daily** - Daily expense breakdowns
- **Combined View** - Multi-dataset comparison
- **Returns Summary** - Product return analysis
- **Deliveries Summary** - Delivery performance
- **Deliveries & Returns Combined** - Comprehensive delivery/return metrics

### Key Metrics
- Revenue tracking
- Return rate analysis
- Store performance comparison
- Delivery efficiency metrics
- Financial summaries

## 🔧 Development

### Adding New Pages
1. Create page class in `page_modules/`
2. Add to `config/app_config.py`
3. Register in `components/page_router.py`

### Adding New Tasks
1. Create task in appropriate `task_modules/` file
2. Tasks automatically available via Invoke

### Data Sources
- Place Excel files in `data_sources/` directory
- Update script paths if needed
- Run `invoke pipeline.all` to process

## 📋 Task Reference

For detailed task documentation, see [INVOKE_GUIDE.md](INVOKE_GUIDE.md)

## 🛠️ Troubleshooting

### Common Issues

1. **Missing data files:**
   ```bash
   invoke check-data
   invoke pipeline.all
   ```

2. **Import errors:**
   ```bash
   invoke app.test
   ```

3. **Port conflicts:**
   ```bash
   invoke app.run --port=8502
   ```

### Debug Mode
```bash
invoke --echo pipeline.all  # Verbose output
```

## 📚 Documentation

- [Invoke Guide](INVOKE_GUIDE.md) - Complete task orchestration guide
- [Refactoring Notes](REFACTORING_NOTES.md) - Architecture details

## 🔄 Typical Workflows

### Daily Data Update
```bash
invoke pipeline.clean
invoke pipeline.all
invoke app.run
```

### Development
```bash
invoke app.test
invoke status
invoke app.run --port=8502
```

### Production Deployment
```bash
invoke pipeline.all
invoke app.test
invoke app.run-headless
```

## 📊 Data Flow

```
Excel Sources → Extract Scripts → Raw CSV → Format Scripts → Formatted CSV → Combine Scripts → Final Data → Dashboard
```

## 🎯 Benefits

- **Modular Architecture** - Easy to maintain and extend
- **Automated Pipeline** - One-command data processing
- **Clean Separation** - Data, UI, and orchestration layers
- **Developer Friendly** - Clear structure and documentation
- **Production Ready** - Robust error handling and logging

---

**Built with:** Streamlit, Pandas, DuckDB, Plotly, Invoke
