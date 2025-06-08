import streamlit as st
import os
from .db_auth import get_user_db

def authenticate_user():
    """Display login form and handle authentication using DuckDB"""
    st.title("🔐 Login")
    
    # Get database instance
    user_db = get_user_db()
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if username and password:
                user_info = user_db.authenticate(username, password)
                if user_info:
                    st.session_state.username = user_info["username"]
                    st.session_state.permissions = user_info["permissions"]
                    st.success("Successfully logged in!")
                    st.rerun()
                    return user_info["username"]
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")
            return None
    
    # Show setup information
    with st.expander("Setup Information"):
        st.write("**First Time Setup:**")
        st.write("1. Copy `.env.example` to `.env`")
        st.write("2. Set your admin password in the `.env` file")
        st.write("3. Restart the app - admin user will be created automatically")
        st.write("")
        st.write("**Environment Setup:**")
        st.code("""# Copy the example file
cp .env.example .env

# Edit .env file and set:
ADMIN_PASSWORD=your_secure_password""")
        st.write("")
        st.write("**Current Status:**")
        # Check if admin user exists
        user_db = get_user_db()
        users = user_db.get_all_users()
        admin_exists = any(user["username"] == "admin" for user in users)
        
        if admin_exists:
            st.success("✅ Admin user exists - you can log in!")
        else:
            admin_password_set = bool(os.getenv("ADMIN_PASSWORD"))
            if admin_password_set:
                st.info("🔄 ADMIN_PASSWORD is set - restart app to create admin user")
            else:
                st.warning("⚠️ No admin user found and ADMIN_PASSWORD not set")
        
        st.info("💡 **Note:** User data is stored in a local DuckDB database")
    
    return None

def check_permission(page_name):
    """Check if current user has permission for a page"""
    if 'permissions' not in st.session_state:
        return False
    return page_name.lower().replace(" ", "_") in st.session_state.permissions

def logout():
    """Clear session state to log out user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def is_admin():
    """Check if current user is admin"""
    return st.session_state.get("username") == "admin"