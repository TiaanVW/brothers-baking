"""
Reusable chart components for the Brothers Baking Analytics Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px


class ChartComponents:
    """Class containing reusable chart components"""
    
    @staticmethod
    def create_date_key(df, year_col='Year', month_col='Month', date_col='Date'):
        """Create a formatted date key for charting"""
        return df.apply(
            lambda row: f"{row[year_col]}-{str(row[month_col]).zfill(2)}-{str(row[date_col]).zfill(2)}", 
            axis=1
        )
    
    @staticmethod
    def create_week_label(df, week_index_col='WeekIndex', week_col='Week'):
        """Create a formatted week label for charting"""
        return df[week_index_col].astype(str) + ": " + df[week_col]
    
    @staticmethod
    def amount_by_date_chart(df, title="Amount by Date"):
        """Create a line chart showing amounts by date"""
        if df.empty:
            st.warning("No data available for chart.")
            return
        
        required_cols = {'Year', 'Month', 'Date', 'Amount'}
        if not required_cols.issubset(set(df.columns)):
            st.warning("Cannot plot: missing required columns.")
            return
        
        chart_data = df.groupby(['Year', 'Month', 'Date'])['Amount'].sum().reset_index()
        chart_data['DateKey'] = ChartComponents.create_date_key(chart_data)
        
        st.subheader(title)
        st.line_chart(chart_data.set_index('DateKey')['Amount'])
    
    @staticmethod
    def amount_by_date_and_category_chart(df, title="Amount by Date and Category"):
        """Create a line chart showing amounts by date and category"""
        if df.empty:
            st.warning("No data available for chart.")
            return
        
        required_cols = {'Year', 'Month', 'Date', 'Category', 'Amount'}
        if not required_cols.issubset(set(df.columns)):
            st.warning("Cannot plot: missing required columns.")
            return
        
        chart_data = df.groupby(['Year', 'Month', 'Date', 'Category'])['Amount'].sum().reset_index()
        chart_data['DateKey'] = ChartComponents.create_date_key(chart_data)
        
        st.subheader(title)
        st.line_chart(chart_data.set_index('DateKey')['Amount'])
    
    @staticmethod
    def returns_by_week_chart(df, title="Returns by Week and Cake Type"):
        """Create a line chart showing returns by week and cake type"""
        if df.empty:
            st.warning("No return data available for chart.")
            return
        
        st.subheader(title)
        
        # Group by Week and CakeType
        chart_data = df.groupby(['Week', 'CakeType'])['Returns'].sum().reset_index()
        
        # Add WeekIndex for ordering
        week_index_map = df[['Week', 'WeekIndex']].drop_duplicates().set_index('Week')['WeekIndex'].to_dict()
        chart_data['WeekIndex'] = chart_data['Week'].map(week_index_map)
        chart_data = chart_data.sort_values('WeekIndex')
        
        if len(chart_data) > 0:
            # Create combined labels
            week_mapping = chart_data[['Week', 'WeekIndex']].drop_duplicates().sort_values('WeekIndex')
            week_mapping['Combined'] = ChartComponents.create_week_label(week_mapping)
            combined_labels = dict(zip(week_mapping['WeekIndex'], week_mapping['Combined']))
            
            # Pivot and display
            numeric_pivot = chart_data.pivot(index='WeekIndex', columns='CakeType', values='Returns').fillna(0)
            numeric_pivot = numeric_pivot.sort_index()
            numeric_pivot.index = [combined_labels[idx] for idx in numeric_pivot.index]
            
            st.line_chart(numeric_pivot)
        else:
            st.warning("No return data available for the selected filters.")
    
    @staticmethod
    def deliveries_by_week_chart(df, title="Deliveries by Week and Cake Type"):
        """Create a line chart showing deliveries by week and cake type"""
        if df.empty:
            st.warning("No delivery data available for chart.")
            return
        
        st.subheader(title)
        
        # Group by Week and CakeType
        chart_data = df.groupby(['Week', 'CakeType'])['Delivered'].sum().reset_index()
        
        # Add WeekIndex for ordering
        week_index_map = df[['Week', 'WeekIndex']].drop_duplicates().set_index('Week')['WeekIndex'].to_dict()
        chart_data['WeekIndex'] = chart_data['Week'].map(week_index_map)
        chart_data = chart_data.sort_values('WeekIndex')
        
        if len(chart_data) > 0:
            # Create combined labels
            week_mapping = chart_data[['Week', 'WeekIndex']].drop_duplicates().sort_values('WeekIndex')
            week_mapping['Combined'] = ChartComponents.create_week_label(week_mapping)
            combined_labels = dict(zip(week_mapping['WeekIndex'], week_mapping['Combined']))
            
            # Pivot and display
            numeric_pivot = chart_data.pivot(index='WeekIndex', columns='CakeType', values='Delivered').fillna(0)
            numeric_pivot = numeric_pivot.sort_index()
            numeric_pivot.index = [combined_labels[idx] for idx in numeric_pivot.index]
            
            st.line_chart(numeric_pivot)
        else:
            st.warning("No delivery data available for the selected filters.")
    
    @staticmethod
    def store_performance_line_chart(df, y_column, title, y_label):
        """Create a plotly line chart showing store performance over time"""
        if df.empty:
            st.warning("No data available for chart.")
            return
        
        st.subheader(title)
        
        # Prepare data with week labels
        df['WeekLabel'] = ChartComponents.create_week_label(df)
        
        # Aggregate by store and week
        chart_data = df.groupby(['Store', 'WeekIndex', 'WeekLabel'])[y_column].sum().reset_index()
        chart_data = chart_data.sort_values('WeekIndex')
        
        # Create plotly line chart
        fig = px.line(
            chart_data,
            x='WeekLabel',
            y=y_column,
            color='Store',
            markers=True,
            labels={'WeekLabel': 'Week', y_column: y_label, 'Store': 'Store'},
            title=title
        )
        fig.update_layout(
            xaxis_title='Week (Chronological)', 
            yaxis_title=y_label, 
            legend_title='Store'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def combined_expense_trends_chart(data_dict, agg_level, selected_years):
        """Create a combined chart showing expense trends across datasets"""
        st.subheader("Expense Trends Across Datasets")
        
        combined_chart_data = []
        
        for dataset_name, df in data_dict.items():
            if df.empty:
                continue
            
            if agg_level == "Year":
                chart_data = df.groupby('Year')['Amount'].sum().reset_index()
                chart_data['Dataset'] = dataset_name
                combined_chart_data.append(chart_data)
            elif agg_level == "Month":
                chart_data = df.groupby(['Year', 'Month'])['Amount'].sum().reset_index()
                chart_data['Year-Month'] = chart_data['Year'].astype(str) + '-' + chart_data['Month'].astype(str).str.zfill(2)
                chart_data['Dataset'] = dataset_name
                combined_chart_data.append(chart_data[['Year-Month', 'Amount', 'Dataset']])
            else:  # Date
                chart_data = df.groupby('Date')['Amount'].sum().reset_index()
                chart_data['Dataset'] = dataset_name
                combined_chart_data.append(chart_data)
        
        if combined_chart_data:
            combined_df = pd.concat(combined_chart_data, ignore_index=True)
            
            if agg_level == "Year":
                pivot_chart = combined_df.pivot_table(index='Year', columns='Dataset', values='Amount', fill_value=0)
            elif agg_level == "Month":
                pivot_chart = combined_df.pivot_table(index='Year-Month', columns='Dataset', values='Amount', fill_value=0)
            else:  # Date
                pivot_chart = combined_df.pivot_table(index='Date', columns='Dataset', values='Amount', fill_value=0)
            
            if not pivot_chart.empty:
                st.line_chart(pivot_chart)
            else:
                st.write("No data to display for the selected filters.")
        else:
            st.write("No data to display for the selected filters.") 