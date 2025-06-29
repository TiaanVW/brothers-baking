"""
Reusable filter components for the Brothers Baking Analytics Dashboard
"""
import streamlit as st
from services.data_service import get_data_service


class FilterComponents:
    """Class containing reusable filter components"""
    
    def __init__(self):
        self.data_service = get_data_service()
    
    def year_filter(self, table_name, default_all=True):
        """Create a year filter widget"""
        years = self.data_service.get_distinct_values(table_name, "Year")
        default = years if default_all else []
        return st.multiselect("Select Year(s)", years, default=default)
    
    def month_filter(self, table_name, selected_years, default_all=True):
        """Create a month filter widget based on selected years"""
        if not selected_years:
            return []
        
        where_clause = f"Year IN {tuple(selected_years)}"
        months = self.data_service.get_distinct_values(table_name, "Month", where_clause)
        default = months if default_all else []
        return st.multiselect("Select Month(s)", months, default=default)
    
    def category_filter(self, table_name, default_all=True):
        """Create a category filter widget"""
        categories = self.data_service.get_distinct_values(table_name, "Category")
        default = categories if default_all else []
        return st.multiselect("Select Category(s)", categories, default=default)
    
    def category_group_filter(self, table_name, default_all=True):
        """Create a category group filter widget"""
        category_groups = self.data_service.get_distinct_values(table_name, "Category Group")
        default = category_groups if default_all else []
        return st.multiselect("Select Category Group(s)", category_groups, default=default)
    
    def store_filter(self, table_name, selected_years=None, default_all=False):
        """Create a store filter widget"""
        where_clause = ""
        if selected_years:
            where_clause = f"Year IN {tuple(selected_years)}"
        
        stores = self.data_service.get_distinct_values(table_name, "Store", where_clause)
        default = stores if default_all else []
        return st.multiselect("Select Store(s)", stores, default=default)
    
    def week_filter(self, table_name, selected_years=None, selected_stores=None, default_all=False):
        """Create a week filter widget with chronological ordering"""
        conditions = []
        if selected_years:
            conditions.append(f"Year IN {tuple(selected_years)}")
        if selected_stores:
            conditions.append(f"Store IN {tuple(map(str, selected_stores))}")
        
        where_clause = " AND ".join(conditions) if conditions else ""
        
        # Get weeks ordered by WeekIndex for chronological order
        query = f"SELECT DISTINCT Week FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += " ORDER BY WeekIndex"
        
        result = self.data_service.run_query(query)
        weeks = result["Week"].tolist() if not result.empty else []
        
        default = weeks if default_all else []
        return st.multiselect("Select Week(s)", weeks, default=default)
    
    def aggregation_level_filter(self, levels=None):
        """Create an aggregation level filter"""
        if levels is None:
            levels = ["Year", "Month", "Date"]
        return st.selectbox("Date Aggregation Level", levels)
    
    def expense_filters(self, table_name):
        """Create standard expense-related filters"""
        st.subheader("Filters")
        
        selected_years = self.year_filter(table_name)
        selected_months = self.month_filter(table_name, selected_years)
        selected_categories = self.category_filter(table_name)
        selected_category_groups = self.category_group_filter(table_name)
        
        return {
            'years': selected_years,
            'months': selected_months,
            'categories': selected_categories,
            'category_groups': selected_category_groups
        }
    
    def delivery_return_filters(self, table_name):
        """Create standard delivery/return-related filters"""
        st.subheader("Filters")
        
        selected_years = self.year_filter(table_name)
        selected_stores = self.store_filter(table_name, selected_years)
        selected_weeks = self.week_filter(table_name, selected_years, selected_stores)
        
        return {
            'years': selected_years,
            'stores': selected_stores,
            'weeks': selected_weeks
        } 