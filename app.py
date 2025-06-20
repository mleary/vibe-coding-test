import streamlit as st
from dotenv import load_dotenv
from utils.login import authenticate_user, check_permission, logout, is_admin
from page_modules.calendar import calendar_page
from page_modules.image_generator import image_generator_page
from page_modules.admin import admin_page
from page_modules.calendar_events import calendar_events_page

# Load environment variables from .env file
load_dotenv()

def main():
    st.set_page_config(
        page_title="My Streamlit App",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Force single entry point - ensure this is the only way to access the app
    if __name__ != "__main__":
        st.error("🔒 Unauthorized access. Please run the application through the main entry point.")
        st.stop()
    
    # Initialize session state
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'permissions' not in st.session_state:
        st.session_state.permissions = []

    # Show login page if not authenticated
    if st.session_state.username is None:
        authenticate_user()
        return

    # Show main app if authenticated
    st.title("🚀 My Streamlit App")
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        st.write(f"Welcome, **{st.session_state.username}**!")
        
        # Available pages based on permissions
        available_pages = []
        if check_permission("calendar"):
            available_pages.append("Calendar")
        if check_permission("image_generator"):
            available_pages.append("Image Generator")
        if is_admin():
            available_pages.append("Admin Panel")
            available_pages.append("Calendar Events")
        
        if available_pages:
            page = st.radio("Go to", available_pages)
        else:
            st.error("You don't have permission to access any pages.")
            page = None
        
        st.divider()
        if st.button("🚪 Logout"):
            logout()
    
    # Display selected page
    if page == "Calendar":
        calendar_page()
    elif page == "Image Generator":
        image_generator_page()
    elif page == "Admin Panel":
        admin_page()
    elif page == "Calendar Events":
        calendar_events_page()
    elif not available_pages:
        st.error("You don't have permission to access any pages. Please contact an administrator.")

if __name__ == "__main__":
    main()

