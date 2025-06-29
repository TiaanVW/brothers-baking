"""
Page router for Brothers Baking Analytics Dashboard
Manages navigation between different pages
"""
import streamlit as st
from config.app_config import PAGES
from page_modules.daily_expenses import DailyExpensesPage
from page_modules.daily_weekly_expenses import DailyWeeklyExpensesPage
from page_modules.expense_daily import ExpenseDailyPage
from page_modules.combined_view import CombinedViewPage
from page_modules.returns_summary import ReturnsSummaryPage
from page_modules.deliveries_summary import DeliveriesSummaryPage
from page_modules.deliveries_returns_combined import DeliveriesReturnsCombinedPage


class PageRouter:
    """Manages page routing and navigation"""
    
    def __init__(self):
        """Initialize page instances"""
        self.pages = {
            "Daily Expenses": DailyExpensesPage(),
            "Daily Weekly Expenses": DailyWeeklyExpensesPage(),
            "Expense Daily": ExpenseDailyPage(),
            "Combined View": CombinedViewPage(),
            "Returns Summary": ReturnsSummaryPage(),
            "Deliveries Summary": DeliveriesSummaryPage(),
            "Deliveries & Returns Combined": DeliveriesReturnsCombinedPage()
        }
    
    def show_navigation(self):
        """Show navigation sidebar and return selected page"""
        st.sidebar.title("Navigation")
        selected_page = st.sidebar.selectbox("Select a page", PAGES)
        return selected_page
    
    def render_page(self, page_name):
        """Render the selected page"""
        if page_name in self.pages:
            self.pages[page_name].render()
        else:
            st.error(f"Page '{page_name}' not found!") 