#!/usr/bin/env python3
"""
Brothers Baking - Data Analytics Dashboard
Main Streamlit application entry point.
"""
import streamlit as st
import pandas as pd
import duckdb
import os
import sys
import plotly.express as px

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page configuration
st.set_page_config(
    page_title="Brothers Baking Analytics",
    page_icon="🍞",
    layout="wide",
)

# App header
st.title("Brothers Baking - Data Analytics Dashboard")
st.markdown("---")

# Sidebar
try:
    st.sidebar.image("assets/logo.png", use_column_width=True)
except Exception:
    st.sidebar.write("Brothers Baking")
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select a page",
    ["Daily Expenses", "Daily Weekly Expenses", "Expense Daily", "Combined View", "Returns Summary", "Deliveries Summary"]
)

# Initialize database connection and load CSVs if needed
conn = duckdb.connect(database=':memory:', read_only=False)

# Paths to formatted CSVs
csv_paths = {
    'daily_expense': os.path.join(os.path.dirname(__file__), 'data/daily_income_expense_expense_formatted.csv'),
    'daily_weekly_expenses': os.path.join(os.path.dirname(__file__), 'data/daily_weekly_expenses_formatted.csv'),
    'expense_daily': os.path.join(os.path.dirname(__file__), 'data/expense_daily_formatted.csv'),
    'returns': os.path.join(os.path.dirname(__file__), 'data/returns_formatted.csv'),
    'deliveries': os.path.join(os.path.dirname(__file__), 'data/deliveries_formatted.csv')
}

# Load CSVs into DuckDB if they exist, with debug output
for table_name, path in csv_paths.items():
    try:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"Loading {path} into {table_name} table")
            # Ensure numeric type for Returns or Deliveries columns when loading data
            if table_name in ['returns', 'deliveries']:
                # First load data into pandas to ensure proper typing
                import pandas as pd
                df = pd.read_csv(path)
                if table_name == 'returns':
                    df['Returns'] = pd.to_numeric(df['Returns'], errors='coerce').fillna(0)
                elif table_name == 'deliveries':
                    df['Delivered'] = pd.to_numeric(df['Delivered'], errors='coerce').fillna(0)
                    df['DeliveryAmount'] = pd.to_numeric(df['DeliveryAmount'], errors='coerce').fillna(0)
                
                # Create temporary CSV with proper types
                temp_path = path + '.temp'
                df.to_csv(temp_path, index=False)
                
                # Load from temp file
                conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{temp_path}')")
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            else:
                conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_csv_auto('{path}')")
            print(f"Loaded {path} into {table_name} table")
        else:
            print(f"Warning: {path} does not exist or is empty")
    except Exception as e:
        print(f"Error loading {path}: {e}")

# Function to run queries
def run_query(query):
    try:
        return conn.execute(query).fetchdf()
    except Exception as e:
        st.error(f"DuckDB query error: {e}\nQuery: {query}")
        return pd.DataFrame()

# Display different content based on selected page
if page == "Daily Expenses":
    st.header("Daily Expenses")
    
    # Filters
    with st.sidebar:
        st.subheader("Filters")
        years = run_query("SELECT DISTINCT Year FROM daily_expense ORDER BY Year").values.flatten().tolist()
        selected_years = st.multiselect("Select Year(s)", years, default=years)
        if selected_years:
            months = run_query(f"SELECT DISTINCT Month FROM daily_expense WHERE Year IN {tuple(selected_years)} ORDER BY Month").values.flatten().tolist()
            selected_months = st.multiselect("Select Month(s)", months, default=months)
        else:
            selected_months = []
    
    # Build query based on filters
    query = "SELECT * FROM daily_expense WHERE 1=1"
    if selected_years:
        query += f" AND Year IN {tuple(selected_years)}"
    if selected_months:
        query += f" AND Month IN {tuple(selected_months)}"
    df = run_query(query)
    
    # Display data
    st.dataframe(df)
    
    # Show chart
    if not df.empty:
        st.subheader("Amount by Date Hierarchy")
        required_cols = {'Year', 'Month', 'Date', 'Amount'}
        if required_cols.issubset(set(df.columns)):
            chart_data = df.groupby(['Year', 'Month', 'Date'])['Amount'].sum().reset_index()
            chart_required_cols = {'Year', 'Month', 'Date', 'Amount'}
            if chart_required_cols.issubset(set(chart_data.columns)):
                chart_data['DateKey'] = chart_data.apply(lambda row: f"{row['Year']}-{str(row['Month']).zfill(2)}-{str(row['Date']).zfill(2)}", axis=1)
                st.line_chart(chart_data.set_index('DateKey')['Amount'])
            else:
                st.warning(f"Cannot plot: missing one or more required columns in chart_data.")
        else:
            st.warning(f"Cannot plot: missing one or more required columns.")

elif page == "Daily Weekly Expenses":
    st.header("Daily Weekly Expenses")
    
    # Filters
    with st.sidebar:
        st.subheader("Filters")
        years = run_query("SELECT DISTINCT Year FROM daily_weekly_expenses ORDER BY Year").values.flatten().tolist()
        selected_years = st.multiselect("Select Year(s)", years, default=years)
        if selected_years:
            months = run_query(f"SELECT DISTINCT Month FROM daily_weekly_expenses WHERE Year IN {tuple(selected_years)} ORDER BY Month").values.flatten().tolist()
            selected_months = st.multiselect("Select Month(s)", months, default=months)
        else:
            selected_months = []
        categories = run_query("SELECT DISTINCT Category FROM daily_weekly_expenses").values.flatten().tolist()
        selected_categories = st.multiselect("Select Category(s)", categories, default=categories)
        category_groups = run_query("SELECT DISTINCT \"Category Group\" FROM daily_weekly_expenses").values.flatten().tolist()
        selected_category_groups = st.multiselect("Select Category Group(s)", category_groups, default=category_groups)
    
    # Build query based on filters
    query = "SELECT * FROM daily_weekly_expenses WHERE 1=1"
    if selected_years:
        query += f" AND Year IN {tuple(selected_years)}"
    if selected_months:
        query += f" AND Month IN {tuple(selected_months)}"
    if selected_categories:
        query += f" AND Category IN {tuple(map(str, selected_categories))}"
    if selected_category_groups:
        query += f" AND \"Category Group\" IN {tuple(map(str, selected_category_groups))}"
    df = run_query(query)
    
    # Display data
    st.dataframe(df)
    
    # Show chart
    if not df.empty:
        st.subheader("Amount by Date and Category")
        required_cols = {'Year', 'Month', 'Date', 'Category', 'Category Group', 'Amount'}
        if required_cols.issubset(set(df.columns)):
            chart_data = df.groupby(['Year', 'Month', 'Date', 'Category', 'Category Group'])['Amount'].sum().reset_index()
            chart_required_cols = {'Year', 'Month', 'Date', 'Category', 'Category Group', 'Amount'}
            if chart_required_cols.issubset(set(chart_data.columns)):
                chart_data['DateKey'] = chart_data.apply(lambda row: f"{row['Year']}-{str(row['Month']).zfill(2)}-{str(row['Date']).zfill(2)}", axis=1)
                st.line_chart(chart_data.set_index('DateKey')['Amount'])
            else:
                st.warning("Cannot plot: missing required columns in chart_data.")
        else:
            st.warning("Cannot plot: missing required columns in data.")

elif page == "Expense Daily":
    st.header("Expense Daily")
    
    # Filters
    with st.sidebar:
        st.subheader("Filters")
        years = run_query("SELECT DISTINCT Year FROM expense_daily ORDER BY Year").values.flatten().tolist()
        selected_years = st.multiselect("Select Year(s)", years, default=years)
        if selected_years:
            months = run_query(f"SELECT DISTINCT Month FROM expense_daily WHERE Year IN {tuple(selected_years)} ORDER BY Month").values.flatten().tolist()
            selected_months = st.multiselect("Select Month(s)", months, default=months)
        else:
            selected_months = []
        categories = run_query("SELECT DISTINCT Category FROM expense_daily").values.flatten().tolist()
        selected_categories = st.multiselect("Select Category(s)", categories, default=categories)
        category_groups = run_query("SELECT DISTINCT \"Category Group\" FROM expense_daily").values.flatten().tolist()
        selected_category_groups = st.multiselect("Select Category Group(s)", category_groups, default=category_groups)
    
    # Build query based on filters
    query = "SELECT * FROM expense_daily WHERE 1=1"
    if selected_years:
        query += f" AND Year IN {tuple(selected_years)}"
    if selected_months:
        query += f" AND Month IN {tuple(selected_months)}"
    if selected_categories:
        query += f" AND Category IN {tuple(map(str, selected_categories))}"
    if selected_category_groups:
        query += f" AND \"Category Group\" IN {tuple(map(str, selected_category_groups))}"
    df = run_query(query)
    
    # Display data
    st.dataframe(df)
    
    # Show chart
    if not df.empty:
        st.subheader("Amount by Date and Category")
        required_cols = {'Year', 'Month', 'Date', 'Category', 'Category Group', 'Amount'}
        if required_cols.issubset(set(df.columns)):
            chart_data = df.groupby(['Year', 'Month', 'Date', 'Category', 'Category Group'])['Amount'].sum().reset_index()
            chart_required_cols = {'Year', 'Month', 'Date', 'Category', 'Category Group', 'Amount'}
            if chart_required_cols.issubset(set(chart_data.columns)):
                chart_data['DateKey'] = chart_data.apply(lambda row: f"{row['Year']}-{str(row['Month']).zfill(2)}-{str(row['Date']).zfill(2)}", axis=1)
                st.line_chart(chart_data.set_index('DateKey')['Amount'])
            else:
                st.warning("Cannot plot: missing required columns in chart_data.")
        else:
            st.warning("Cannot plot: missing required columns in data.")

elif page == "Combined View":
    st.header("Combined View")
    
    # Filters for combined view
    with st.sidebar:
        st.subheader("Filters for All Tables")
        years_daily = run_query("SELECT DISTINCT Year FROM daily_expense ORDER BY Year").values.flatten().tolist()
        years_weekly = run_query("SELECT DISTINCT Year FROM daily_weekly_expenses ORDER BY Year").values.flatten().tolist()
        years_expense = run_query("SELECT DISTINCT Year FROM expense_daily ORDER BY Year").values.flatten().tolist()
        all_years = sorted(list(set(years_daily + years_weekly + years_expense)))
        selected_years = st.multiselect("Select Year(s)", all_years, default=all_years)
        
        # Aggregation level for chart
        agg_level = st.selectbox("Date Aggregation Level", ["Year", "Month", "Date"])
    
    # Split into three columns for side-by-side tables
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Daily Expenses")
        query_daily = "SELECT * FROM daily_expense WHERE 1=1"
        if selected_years:
            query_daily += f" AND Year IN {tuple(selected_years)}"
        df_daily = run_query(query_daily)
        st.dataframe(df_daily)
    
    with col2:
        st.subheader("Daily Weekly Expenses")
        query_weekly = "SELECT * FROM daily_weekly_expenses WHERE 1=1"
        if selected_years:
            query_weekly += f" AND Year IN {tuple(selected_years)}"
        df_weekly = run_query(query_weekly)
        st.dataframe(df_weekly)
    
    with col3:
        st.subheader("Expense Daily")
        query_expense = "SELECT * FROM expense_daily WHERE 1=1"
        if selected_years:
            query_expense += f" AND Year IN {tuple(selected_years)}"
        df_expense = run_query(query_expense)
        st.dataframe(df_expense)
    
    # Chart showing amounts grouped by date
    st.subheader("Expense Trends Across Datasets")
    
    # Prepare data for combined chart
    if agg_level == "Year":
        daily_chart = run_query(f"SELECT Year, SUM(Amount) as Amount, 'Daily Expenses' as Dataset FROM daily_expense WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Year")
        weekly_chart = run_query(f"SELECT Year, SUM(Amount) as Amount, 'Weekly Expenses' as Dataset FROM daily_weekly_expenses WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Year")
        expense_chart = run_query(f"SELECT Year, SUM(Amount) as Amount, 'Expense Daily' as Dataset FROM expense_daily WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Year")
        combined_chart = pd.concat([daily_chart, weekly_chart, expense_chart])
        pivot_chart = combined_chart.pivot_table(index='Year', columns='Dataset', values='Amount', fill_value=0)
    elif agg_level == "Month":
        daily_chart = run_query(f"SELECT Year, Month, SUM(Amount) as Amount, 'Daily Expenses' as Dataset FROM daily_expense WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Year, Month")
        weekly_chart = run_query(f"SELECT Year, Month, SUM(Amount) as Amount, 'Weekly Expenses' as Dataset FROM daily_weekly_expenses WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Year, Month")
        expense_chart = run_query(f"SELECT Year, Month, SUM(Amount) as Amount, 'Expense Daily' as Dataset FROM expense_daily WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Year, Month")
        combined_chart = pd.concat([daily_chart, weekly_chart, expense_chart])
        combined_chart['Year-Month'] = combined_chart['Year'].astype(str) + '-' + combined_chart['Month'].astype(str).str.zfill(2)
        pivot_chart = combined_chart.pivot_table(index='Year-Month', columns='Dataset', values='Amount', fill_value=0)
    else:  # Date
        daily_chart = run_query(f"SELECT Date, SUM(Amount) as Amount, 'Daily Expenses' as Dataset FROM daily_expense WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Date")
        weekly_chart = run_query(f"SELECT Date, SUM(Amount) as Amount, 'Weekly Expenses' as Dataset FROM daily_weekly_expenses WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Date")
        expense_chart = run_query(f"SELECT Date, SUM(Amount) as Amount, 'Expense Daily' as Dataset FROM expense_daily WHERE Year IN {tuple(selected_years) if selected_years else '(-1)'} GROUP BY Date")
        combined_chart = pd.concat([daily_chart, weekly_chart, expense_chart])
        pivot_chart = combined_chart.pivot_table(index='Date', columns='Dataset', values='Amount', fill_value=0)
    
    if not pivot_chart.empty:
        st.line_chart(pivot_chart)
    else:
        st.write("No data to display for the selected filters.")

elif page == "Returns Summary":
    st.header("Returns Summary")
    
    # Filters
    with st.sidebar:
        st.subheader("Filters")
        # Get unique values for filters
        years = run_query("SELECT DISTINCT Year FROM returns ORDER BY Year").values.flatten().tolist()
        selected_years = st.multiselect("Select Year(s)", years, default=years)
        
        # Get stores based on selected years
        if selected_years:
            stores = run_query(f"SELECT DISTINCT Store FROM returns WHERE Year IN {tuple(selected_years)} ORDER BY Store").values.flatten().tolist()
            selected_stores = st.multiselect("Select Store(s)", stores, default=[])
            
            # Get weeks based on selected years and stores, ordered by WeekIndex
            filter_condition = f"WHERE Year IN {tuple(selected_years)}"
            if selected_stores:
                filter_condition += f" AND Store IN {tuple(map(str, selected_stores))}"
            # Ensure weeks are ordered by WeekIndex (dynamic chronological order)
            weeks = run_query(f"SELECT DISTINCT Week FROM returns {filter_condition} ORDER BY WeekIndex").values.flatten().tolist()
            selected_weeks = st.multiselect("Select Week(s)", weeks, default=[])
        else:
            selected_stores = []
            selected_weeks = []
    
    # Build query based on filters
    query = "SELECT * FROM returns WHERE 1=1"
    if selected_years:
        query += f" AND Year IN {tuple(selected_years)}"
    if selected_stores:
        query += f" AND Store IN {tuple(map(str, selected_stores))}"
    if selected_weeks:
        query += f" AND Week IN {tuple(map(str, selected_weeks))}"
    
    # Execute query and display data
    df = run_query(query)
    st.dataframe(df)
    
    # Show chart
    if not df.empty:
        st.subheader("Returns by Week and Cake Type")
        
        # Group by Week and CakeType to sum return counts
        chart_data = df.groupby(['Week', 'CakeType'])['Returns'].sum().reset_index()
        
        # Add WeekIndex to chart_data for ordering
        week_index_map = df[['Week', 'WeekIndex']].drop_duplicates().set_index('Week')['WeekIndex'].to_dict()
        chart_data['WeekIndex'] = chart_data['Week'].map(week_index_map)
        
        # Sort by WeekIndex to ensure proper ordering
        chart_data = chart_data.sort_values('WeekIndex')
        
        # Create line chart with Week on x-axis and Returns on y-axis, colored by CakeType
        if len(chart_data) > 0:
            
            # Create week-to-index mapping dictionary
            week_mapping = chart_data[['Week', 'WeekIndex']].drop_duplicates().sort_values('WeekIndex')
            
            # Create combined labels with index prefixes (e.g., "1: 31 MAR - 6 APR")
            week_mapping['Combined'] = week_mapping['WeekIndex'].astype(str) + ": " + week_mapping['Week']
            combined_labels = dict(zip(week_mapping['WeekIndex'], week_mapping['Combined']))
            
            # First pivot on WeekIndex for correct ordering
            numeric_pivot = chart_data.pivot(index='WeekIndex', columns='CakeType', values='Returns').fillna(0)
            numeric_pivot = numeric_pivot.sort_index()
            
            # Replace the index with combined labels while preserving order
            ordered_pivot = numeric_pivot.copy()
            ordered_pivot.index = [combined_labels[idx] for idx in ordered_pivot.index]
            
            # Display the chart with combined labels that maintain proper order
            st.line_chart(ordered_pivot)
            


        else:
            st.warning("No return data available for the selected filters.")

        # --- NEW VISUAL: Returns by Store over Weeks ---
        st.subheader("Returns by Store (Chronological Weeks)")
        # Prepare concatenated week label
        df['WeekLabel'] = df['WeekIndex'].astype(str) + ': ' + df['Week']
        # Aggregate returns by store and week (sum in case of multiple cake types per store/week)
        store_week_returns = df.groupby(['Store', 'WeekIndex', 'WeekLabel'])['Returns'].sum().reset_index()
        # Sort by week index
        store_week_returns = store_week_returns.sort_values('WeekIndex')
        # Plotly line chart
        fig = px.line(
            store_week_returns,
            x='WeekLabel',
            y='Returns',
            color='Store',
            markers=True,
            labels={'WeekLabel': 'Week', 'Returns': 'Returns', 'Store': 'Store'},
            title='Returns per Store by Week (Chronological Order)'
        )
        fig.update_layout(xaxis_title='Week (Chronological)', yaxis_title='Returns', legend_title='Store')
        st.plotly_chart(fig, use_container_width=True)

elif page == "Deliveries Summary":
    st.header("Deliveries Summary")
    
    # Filters
    with st.sidebar:
        st.subheader("Filters")
        years = run_query("SELECT DISTINCT Year FROM deliveries ORDER BY Year").values.flatten().tolist()
        selected_years = st.multiselect("Select Year(s)", years, default=years)
        
        if selected_years:
            # Filter stores based on selected years
            filter_condition = f"WHERE Year IN {tuple(selected_years)}"
            stores = run_query(f"SELECT DISTINCT Store FROM deliveries {filter_condition} ORDER BY Store").values.flatten().tolist()
            selected_stores = st.multiselect("Select Store(s)", stores, default=[])
            
            # Filter weeks based on selected years and stores
            filter_condition = f"WHERE Year IN {tuple(selected_years)}"
            if selected_stores:
                filter_condition += f" AND Store IN {tuple(map(str, selected_stores))}"
            # Ensure weeks are ordered by WeekIndex (dynamic chronological order)
            weeks = run_query(f"SELECT DISTINCT Week FROM deliveries {filter_condition} ORDER BY WeekIndex").values.flatten().tolist()
            selected_weeks = st.multiselect("Select Week(s)", weeks, default=[])
        else:
            selected_stores = []
            selected_weeks = []
    
    # Build query based on filters
    query = "SELECT * FROM deliveries WHERE 1=1"
    if selected_years:
        query += f" AND Year IN {tuple(selected_years)}"
    if selected_stores:
        query += f" AND Store IN {tuple(map(str, selected_stores))}"
    if selected_weeks:
        query += f" AND Week IN {tuple(map(str, selected_weeks))}"
    
    # Execute query and display data
    df = run_query(query)
    st.dataframe(df)
    
    # Show chart
    if not df.empty:
        st.subheader("Deliveries by Week and Cake Type")
        
        # Group by Week and CakeType to sum delivery counts
        chart_data = df.groupby(['Week', 'CakeType'])['Delivered'].sum().reset_index()
        
        # Add WeekIndex to chart_data for ordering
        week_index_map = df[['Week', 'WeekIndex']].drop_duplicates().set_index('Week')['WeekIndex'].to_dict()
        chart_data['WeekIndex'] = chart_data['Week'].map(week_index_map)
        
        # Sort by WeekIndex to ensure proper ordering
        chart_data = chart_data.sort_values('WeekIndex')
        
        # Create line chart with Week on x-axis and Delivered on y-axis, colored by CakeType
        if len(chart_data) > 0:
            
            # Create week-to-index mapping dictionary
            week_mapping = chart_data[['Week', 'WeekIndex']].drop_duplicates().sort_values('WeekIndex')
            
            # Create combined labels with index prefixes (e.g., "1: 31 MAR - 6 APR")
            week_mapping['Combined'] = week_mapping['WeekIndex'].astype(str) + ": " + week_mapping['Week']
            combined_labels = dict(zip(week_mapping['WeekIndex'], week_mapping['Combined']))
            
            # First pivot on WeekIndex for correct ordering
            numeric_pivot = chart_data.pivot(index='WeekIndex', columns='CakeType', values='Delivered').fillna(0)
            numeric_pivot = numeric_pivot.sort_index()
            
            # Replace the index with combined labels while preserving order
            ordered_pivot = numeric_pivot.copy()
            ordered_pivot.index = [combined_labels[idx] for idx in ordered_pivot.index]
            
            # Display the chart with combined labels that maintain proper order
            st.line_chart(ordered_pivot)
        else:
            st.warning("No delivery data available for the selected filters.")

        # --- NEW VISUAL: Deliveries by Store over Weeks ---
        st.subheader("Deliveries by Store (Chronological Weeks)")
        # Prepare concatenated week label
        df['WeekLabel'] = df['WeekIndex'].astype(str) + ': ' + df['Week']
        # Aggregate deliveries by store and week (sum in case of multiple cake types per store/week)
        store_week_deliveries = df.groupby(['Store', 'WeekIndex', 'WeekLabel'])['Delivered'].sum().reset_index()
        # Sort by week index
        store_week_deliveries = store_week_deliveries.sort_values('WeekIndex')
        # Plotly line chart
        fig = px.line(
            store_week_deliveries,
            x='WeekLabel',
            y='Delivered',
            color='Store',
            markers=True,
            labels={'WeekLabel': 'Week', 'Delivered': 'Deliveries', 'Store': 'Store'},
            title='Deliveries per Store by Week (Chronological Order)'
        )
        fig.update_layout(xaxis_title='Week (Chronological)', yaxis_title='Deliveries', legend_title='Store')
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(" 2025 Brothers Baking")
