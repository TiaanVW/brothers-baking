"""
Daily Expenses page for Brothers Baking Analytics Dashboard
"""
import streamlit as st
from services.data_service import get_data_service
from components.filters import FilterComponents
from components.charts import ChartComponents


class DailyExpensesPage:
    """Daily Expenses page class"""
    
    def __init__(self):
        self.data_service = get_data_service()
        self.filters = FilterComponents()
        self.charts = ChartComponents()
    
    def render(self):
        """Render the Daily Expenses page"""
        st.header("Daily Expenses")
        
        # Filters in sidebar
        with st.sidebar:
            filters = self._get_basic_filters("daily_expense")
        
        # Build and execute query
        df = self._get_filtered_data(filters)
        
        # Display data
        st.dataframe(df)
        
        # Show chart
        self.charts.amount_by_date_chart(df, "Amount by Date Hierarchy")
    
    def _get_basic_filters(self, table_name):
        """Create basic filters for daily expense data (no Category column)"""
        st.subheader("Filters")
        
        selected_years = self.filters.year_filter(table_name)
        selected_months = self.filters.month_filter(table_name, selected_years)
        
        return {
            'years': selected_years,
            'months': selected_months
        }
    
    def _get_filtered_data(self, filters):
        """Get filtered data based on selected filters"""
        query = "SELECT * FROM daily_expense WHERE 1=1"
        
        if filters['years']:
            query += f" AND Year IN {tuple(filters['years'])}"
        if filters['months']:
            query += f" AND Month IN {tuple(filters['months'])}"
        
        return self.data_service.run_query(query) 