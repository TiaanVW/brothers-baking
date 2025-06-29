#!/usr/bin/env python3
"""
Brothers Baking - Data Analytics Dashboard
Refactored modular Streamlit application entry point.
"""
import streamlit as st
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.app_config import APP_TITLE, APP_ICON, LAYOUT, ASSETS_DIR
from components.page_router import PageRouter


def setup_page_config():
    """Set up Streamlit page configuration"""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded"
    )


def show_header():
    """Display app header"""
    st.title(APP_TITLE)
    st.markdown("---")


def show_sidebar_logo():
    """Display logo in sidebar"""
    try:
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        st.sidebar.image(logo_path, use_column_width=True)
    except Exception:
        st.sidebar.write("Brothers Baking")


def show_footer():
    """Display app footer"""
    st.markdown("---")
    st.markdown("© 2025 Brothers Baking")


def main():
    """Main application entry point"""
    # Setup page configuration
    setup_page_config()
    
    # Show header
    show_header()
    
    # Show sidebar logo
    show_sidebar_logo()
    
    # Initialize page router
    router = PageRouter()
    
    # Show navigation and get selected page
    selected_page = router.show_navigation()
    
    # Render the selected page
    router.render_page(selected_page)
    
    # Show footer
    show_footer()


if __name__ == "__main__":
    main() 