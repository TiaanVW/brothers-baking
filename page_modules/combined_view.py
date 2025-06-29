"""
Combined View page for Brothers Baking Analytics Dashboard
"""
import streamlit as st
from services.data_service import get_data_service
from components.filters import FilterComponents
from components.charts import ChartComponents


class CombinedViewPage:
    """Combined View page class"""
    
    def __init__(self):
        self.data_service = get_data_service()
        self.filters = FilterComponents()
        self.charts = ChartComponents()
    
    def render(self):
        """Render the Combined View page"""
        st.header("Combined View")
        
        # Filters in sidebar
        with st.sidebar:
            st.subheader("Filters for All Tables")
            
            # Get all unique years across tables
            years_daily = self.data_service.get_distinct_values("daily_expense", "Year")
            years_weekly = self.data_service.get_distinct_values("daily_weekly_expenses", "Year")
            years_expense = self.data_service.get_distinct_values("expense_daily", "Year")
            all_years = sorted(list(set(years_daily + years_weekly + years_expense)))
            
            selected_years = st.multiselect("Select Year(s)", all_years, default=all_years)
            agg_level = self.filters.aggregation_level_filter()
        
        # Get data for all three tables
        data_dict = self._get_all_filtered_data(selected_years)
        
        # Display side-by-side tables
        self._display_side_by_side_tables(data_dict)
        
        # Show combined chart
        self.charts.combined_expense_trends_chart(data_dict, agg_level, selected_years)
    
    def _get_all_filtered_data(self, selected_years):
        """Get filtered data for all expense tables"""
        data_dict = {}
        
        # Build year filter condition
        year_condition = ""
        if selected_years:
            year_condition = f" AND Year IN {tuple(selected_years)}"
        
        # Query each table
        tables = {
            'Daily Expenses': 'daily_expense',
            'Weekly Expenses': 'daily_weekly_expenses', 
            'Expense Daily': 'expense_daily'
        }
        
        for display_name, table_name in tables.items():
            query = f"SELECT * FROM {table_name} WHERE 1=1{year_condition}"
            data_dict[display_name] = self.data_service.run_query(query)
        
        return data_dict
    
    def _display_side_by_side_tables(self, data_dict):
        """Display tables side by side in columns"""
        col1, col2, col3 = st.columns(3)
        
        columns = [col1, col2, col3]
        table_names = list(data_dict.keys())
        
        for i, (col, table_name) in enumerate(zip(columns, table_names)):
            with col:
                st.subheader(table_name)
                df = data_dict[table_name]
                st.dataframe(df) 