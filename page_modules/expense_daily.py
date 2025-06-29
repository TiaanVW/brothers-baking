"""
Expense Daily page for Brothers Baking Analytics Dashboard
"""
import streamlit as st
from services.data_service import get_data_service
from components.filters import FilterComponents
from components.charts import ChartComponents


class ExpenseDailyPage:
    """Expense Daily page class"""
    
    def __init__(self):
        self.data_service = get_data_service()
        self.filters = FilterComponents()
        self.charts = ChartComponents()
    
    def render(self):
        """Render the Expense Daily page"""
        st.header("Expense Daily")
        
        # Filters in sidebar
        with st.sidebar:
            filters = self.filters.expense_filters("expense_daily")
        
        # Build and execute query
        df = self._get_filtered_data(filters)
        
        # Display data
        st.dataframe(df)
        
        # Show chart
        self.charts.amount_by_date_and_category_chart(df, "Amount by Date and Category")
    
    def _get_filtered_data(self, filters):
        """Get filtered data based on selected filters"""
        query = "SELECT * FROM expense_daily WHERE 1=1"
        
        if filters['years']:
            query += f" AND Year IN {tuple(filters['years'])}"
        if filters['months']:
            query += f" AND Month IN {tuple(filters['months'])}"
        if filters['categories']:
            query += f" AND Category IN {tuple(map(str, filters['categories']))}"
        if filters['category_groups']:
            query += f" AND \"Category Group\" IN {tuple(map(str, filters['category_groups']))}"
        
        return self.data_service.run_query(query) 