"""
Returns Summary page for Brothers Baking Analytics Dashboard
"""
import streamlit as st
from services.data_service import get_data_service
from components.filters import FilterComponents
from components.charts import ChartComponents


class ReturnsSummaryPage:
    """Returns Summary page class"""
    
    def __init__(self):
        self.data_service = get_data_service()
        self.filters = FilterComponents()
        self.charts = ChartComponents()
    
    def render(self):
        """Render the Returns Summary page"""
        st.header("Returns Summary")
        
        # Filters in sidebar
        with st.sidebar:
            filters = self.filters.delivery_return_filters("deliveries_returns_combined")
        
        # Build and execute query - only show records with returns > 0
        df = self._get_filtered_data(filters)
        
        # Display data
        st.dataframe(df)
        
        # Show charts
        if not df.empty:
            self.charts.returns_by_week_chart(df)
            self.charts.store_performance_line_chart(
                df, 
                'Returns', 
                "Returns by Store (Chronological Weeks)", 
                "Returns"
            )
        else:
            st.warning("No return data available for the selected filters.")
    
    def _get_filtered_data(self, filters):
        """Get filtered data based on selected filters"""
        query = """
        SELECT Week, Year, Store, CakeType, WeekIndex, Delivered, DeliveryAmount, Returns, ReturnAmount 
        FROM deliveries_returns_combined 
        WHERE Returns > 0
        """
        
        if filters['years']:
            query += f" AND Year IN {tuple(filters['years'])}"
        if filters['stores']:
            query += f" AND Store IN {tuple(map(str, filters['stores']))}"
        if filters['weeks']:
            query += f" AND Week IN {tuple(map(str, filters['weeks']))}"
        
        return self.data_service.run_query(query) 