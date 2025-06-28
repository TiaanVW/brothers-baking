# Brothers Baking - Data Analytics Dashboard

This project provides a data analytics dashboard for Brothers Baking, using DuckDB for data storage and Streamlit for visualization.

## Project Structure

```
brothers_baking/
├── app.py                      # Main Streamlit app entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview and setup instructions

├── data/                       # Raw or processed CSV data files
│   └── *.csv                   # Various CSV data files

├── db/                         # Local database files
│   └── data.duckdb             # DuckDB database file

├── scripts/                    # Data processing or ETL scripts
│   ├── process_data.py         # Converts CSVs to DB or cleans data
│   └── load_to_db.py           # Loads pandas data into the DB

├── utils/                      # Reusable Python modules/utilities
│   └── db_utils.py             # DB connection, query functions, etc.

└── assets/                     # Optional: images, logos, or static files
    └── logo.png                # Company logo
```

## Setup Instructions

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Process the data**

```bash
python scripts/process_data.py
```

3. **Load data into the database**

```bash
python scripts/load_to_db.py
```

4. **Run the Streamlit app**

```bash
streamlit run app.py
```

The application will then be available at http://localhost:8501

## Data Sources

This dashboard uses several data sources:
- Daily expenses pivot table
- Daily income and expense data
- Weekly expense analysis

## Features

- Visualization of daily expenses
- Comparison of income vs expenses
- Analysis of weekly expense trends

## Requirements

- Python 3.9+
- DuckDB
- Streamlit
- Pandas
