"""
Deliveries & Returns Combined page for Brothers Baking Analytics Dashboard
"""
import streamlit as st
import plotly.express as px
from services.data_service import get_data_service
from components.filters import FilterComponents
from components.charts import ChartComponents


class DeliveriesReturnsCombinedPage:
    """Deliveries & Returns Combined page class"""
    
    def __init__(self):
        self.data_service = get_data_service()
        self.filters = FilterComponents()
        self.charts = ChartComponents()
    
    def render(self):
        """Render the Deliveries & Returns Combined page"""
        st.header("Deliveries & Returns Combined View")
        
        # Filters in sidebar
        with st.sidebar:
            filters = self.filters.delivery_return_filters("deliveries_returns_combined")
        
        # Build and execute query
        df = self._get_filtered_data(filters)
        
        # Display data
        st.dataframe(df)
        
        # Show financial and performance metrics
        if not df.empty:
            self._display_financial_metrics(df)
            self._display_quantity_metrics(df)
            self._display_charts(df)
            self._display_store_performance(df)
        else:
            st.warning("No data available for the selected filters.")
    
    def _get_filtered_data(self, filters):
        """Get filtered data based on selected filters"""
        query = "SELECT * FROM deliveries_returns_combined WHERE 1=1"
        
        if filters['years']:
            query += f" AND Year IN {tuple(filters['years'])}"
        if filters['stores']:
            query += f" AND Store IN {tuple(map(str, filters['stores']))}"
        if filters['weeks']:
            query += f" AND Week IN {tuple(map(str, filters['weeks']))}"
        
        return self.data_service.run_query(query)
    
    def _display_financial_metrics(self, df):
        """Display financial metrics"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_delivery_amount = df['DeliveryAmount'].sum()
            st.metric("Deliveries Total (R)", f"R {total_delivery_amount:,.2f}")
        
        with col2:
            total_return_amount = df['ReturnAmount'].sum()
            st.metric("Total Returns (R)", f"R {total_return_amount:,.2f}")
        
        with col3:
            revenue_after_returns = total_delivery_amount - total_return_amount
            st.metric("Revenue After Returns", f"R {revenue_after_returns:,.2f}")
        
        st.markdown("---")
    
    def _display_quantity_metrics(self, df):
        """Display quantity metrics"""
        col4, col5, col6, col7 = st.columns(4)
        
        with col4:
            st.metric("Total Deliveries", f"{df['Delivered'].sum():.0f}")
        
        with col5:
            st.metric("Total Returns", f"{df['Returns'].sum():.0f}")
        
        with col6:
            return_rate = (df['Returns'].sum() / df['Delivered'].sum() * 100) if df['Delivered'].sum() > 0 else 0
            st.metric("Return Rate", f"{return_rate:.1f}%")
        
        with col7:
            st.metric("Net Deliveries", f"{(df['Delivered'].sum() - df['Returns'].sum()):.0f}")
    
    def _display_charts(self, df):
        """Display various charts"""
        # Deliveries vs Returns by week
        st.subheader("Deliveries vs Returns by Week")
        weekly_summary = df.groupby(['Week', 'WeekIndex']).agg({
            'Delivered': 'sum',
            'Returns': 'sum'
        }).reset_index().sort_values('WeekIndex')
        
        weekly_summary['WeekLabel'] = self.charts.create_week_label(weekly_summary)
        chart_data = weekly_summary[['WeekLabel', 'Delivered', 'Returns']].set_index('WeekLabel')
        st.line_chart(chart_data)
        
        # Return Rate Over Time
        st.subheader("Return Rate Over Time")
        weekly_return_rate = weekly_summary.copy()
        weekly_return_rate['Return Rate %'] = (
            weekly_return_rate['Returns'] / weekly_return_rate['Delivered'] * 100
        ).round(2)
        
        return_rate_chart = weekly_return_rate[['WeekLabel', 'Return Rate %']].set_index('WeekLabel')
        st.line_chart(return_rate_chart)
        
        # Return Rate Per Store
        self._display_store_return_rate_chart(df)
    
    def _display_store_return_rate_chart(self, df):
        """Display return rate per store chart"""
        st.subheader("Return Rate Per Store")
        store_return_rate = df.groupby(['Store', 'Week', 'WeekIndex']).agg({
            'Delivered': 'sum',
            'Returns': 'sum'
        }).reset_index()
        
        store_return_rate['Return Rate %'] = (
            store_return_rate['Returns'] / store_return_rate['Delivered'] * 100
        ).round(2)
        store_return_rate['WeekLabel'] = self.charts.create_week_label(store_return_rate)
        store_return_rate = store_return_rate.sort_values('WeekIndex')
        
        fig_store_return_rate = px.line(
            store_return_rate,
            x='WeekLabel',
            y='Return Rate %',
            color='Store',
            markers=True,
            labels={'WeekLabel': 'Week', 'Return Rate %': 'Return Rate (%)', 'Store': 'Store'},
            title='Return Rate per Store Over Time'
        )
        fig_store_return_rate.update_layout(
            xaxis_title='Week (Chronological)', 
            yaxis_title='Return Rate (%)', 
            legend_title='Store'
        )
        st.plotly_chart(fig_store_return_rate, use_container_width=True)
    
    def _display_store_performance(self, df):
        """Display store performance comparison"""
        st.subheader("Store Performance Comparison")
        store_summary = df.groupby('Store').agg({
            'Delivered': 'sum',
            'Returns': 'sum',
            'DeliveryAmount': 'sum',
            'ReturnAmount': 'sum'
        }).reset_index()
        
        store_summary['Return Rate %'] = (
            store_summary['Returns'] / store_summary['Delivered'] * 100
        ).round(1)
        store_summary['Net Deliveries'] = store_summary['Delivered'] - store_summary['Returns']
        store_summary['Net Revenue'] = store_summary['DeliveryAmount'] - store_summary['ReturnAmount']
        
        st.dataframe(store_summary.sort_values('Return Rate %', ascending=False)) 