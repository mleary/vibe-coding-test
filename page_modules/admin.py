import streamlit as st
import pandas as pd
from utils.db_auth import get_user_db
from utils.login import is_admin, require_auth

def admin_page():
    """Admin page for user management"""
    require_auth()
    if not is_admin():
        st.error("🚫 Access denied. Admin privileges required.")
        return
    
    st.title("👑 Admin Panel")
    st.write("Manage users and permissions")
    
    user_db = get_user_db()
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["👥 View Users", "➕ Add User", "📊 Database Stats", "🔍 SQL Query"])
    
    with tab1:
        st.subheader("Current Users")
        
        # Get all users
        users = user_db.get_all_users()
        
        if users:
            # Create a nice display
            df_data = []
            for user in users:
                df_data.append({
                    "Username": user["username"],
                    "Permissions": ", ".join(user["permissions"]),
                    "Created": user["created_at"],
                    "Last Login": user["last_login"] or "Never"
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # User management
            st.subheader("Manage Users")
            selected_user = st.selectbox("Select user to modify:", 
                                       [u["username"] for u in users if u["username"] != "admin"])
            
            if selected_user:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Update permissions
                    st.write("**Update Permissions:**")
                    current_user = next(u for u in users if u["username"] == selected_user)
                    
                    calendar_perm = st.checkbox("Calendar", 
                                              value="calendar" in current_user["permissions"],
                                              key=f"calendar_{selected_user}")
                    image_perm = st.checkbox("Image Generator", 
                                           value="image_generator" in current_user["permissions"],
                                           key=f"image_{selected_user}")
                    
                    new_permissions = []
                    if calendar_perm:
                        new_permissions.append("calendar")
                    if image_perm:
                        new_permissions.append("image_generator")
                    
                    if st.button("Update Permissions", key=f"update_{selected_user}"):
                        if user_db.update_permissions(selected_user, new_permissions):
                            st.success(f"Updated permissions for {selected_user}")
                            st.rerun()
                        else:
                            st.error("Failed to update permissions")
                
                with col2:
                    # Delete user
                    st.write("**Danger Zone:**")
                    if st.button(f"🗑️ Delete {selected_user}", 
                               type="secondary", 
                               key=f"delete_{selected_user}"):
                        if user_db.delete_user(selected_user):
                            st.success(f"Deleted user {selected_user}")
                            st.rerun()
                        else:
                            st.error("Failed to delete user")
        else:
            st.write("No users found.")
    
    with tab2:
        st.subheader("Add New User")
        
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            st.write("**Permissions:**")
            calendar_perm = st.checkbox("Calendar", key="new_calendar")
            image_perm = st.checkbox("Image Generator", key="new_image")
            
            submitted = st.form_submit_button("Add User")
            
            if submitted:
                if not new_username or not new_password:
                    st.error("Username and password are required")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    permissions = []
                    if calendar_perm:
                        permissions.append("calendar")
                    if image_perm:
                        permissions.append("image_generator")
                    
                    if not permissions:
                        st.error("At least one permission must be selected")
                    elif user_db.add_user(new_username, new_password, permissions):
                        st.success(f"Successfully added user: {new_username}")
                    else:
                        st.error("Failed to add user (username might already exist)")
    
    with tab3:
        st.subheader("Database Statistics")
        
        users = user_db.get_all_users()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", len(users))
        
        with col2:
            users_with_calendar = sum(1 for u in users if "calendar" in u["permissions"])
            st.metric("Calendar Users", users_with_calendar)
        
        with col3:
            users_with_image = sum(1 for u in users if "image_generator" in u["permissions"])
            st.metric("Image Gen Users", users_with_image)
        
        # Recent activity
        st.subheader("Recent Activity")
        recent_logins = [u for u in users if u["last_login"]]
        recent_logins.sort(key=lambda x: x["last_login"] or "", reverse=True)
        
        if recent_logins:
            for user in recent_logins[:5]:  # Show last 5 logins
                st.write(f"👤 **{user['username']}** - Last login: {user['last_login']}")
        else:
            st.write("No recent login activity")
    
    with tab4:
        st.subheader("🔍 SQL Query Interface")
        st.write("Execute custom SQL queries against the DuckDB database")
        
        # Query input
        default_query = """-- Example queries:
-- SELECT * FROM users;
-- SELECT username, permissions, created_at FROM users ORDER BY created_at DESC;
-- SELECT COUNT(*) as total_users FROM users;
-- SELECT permissions, COUNT(*) as count FROM users GROUP BY permissions;

SELECT * FROM users;"""
        
        sql_query = st.text_area(
            "SQL Query:", 
            value=default_query,
            height=200,
            help="Write your SQL query here. Be careful with UPDATE/DELETE operations!"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            execute_query = st.button("▶️ Execute Query", type="primary")
        
        with col2:
            show_schema = st.button("📋 Show Schema")
        
        if show_schema:
            st.subheader("Database Schema")
            try:
                import duckdb
                import os
                db_path = os.getenv("USER_DB_PATH", "users.db")
                conn = duckdb.connect(db_path)
                
                # Get table info
                schema_info = conn.execute("DESCRIBE users").fetchall()
                schema_df = pd.DataFrame(schema_info, columns=["Column", "Type", "Null", "Key", "Default", "Extra"])
                st.dataframe(schema_df, use_container_width=True)
                
                # Show sample data
                st.subheader("Sample Data (First 3 rows)")
                sample_data = conn.execute("SELECT * FROM users LIMIT 3").fetchall()
                if sample_data:
                    columns = [desc[0] for desc in conn.description]
                    sample_df = pd.DataFrame(sample_data, columns=columns)
                    st.dataframe(sample_df, use_container_width=True)
                
                conn.close()
            except Exception as e:
                st.error(f"Error getting schema: {str(e)}")
        
        if execute_query and sql_query.strip():
            try:
                import duckdb
                import os
                db_path = os.getenv("USER_DB_PATH", "users.db")
                conn = duckdb.connect(db_path)
                
                # Clean up the query (remove comments and extra whitespace)
                clean_query = sql_query.strip()
                if clean_query.startswith('--'):
                    # Remove comment lines but keep the actual query
                    lines = clean_query.split('\n')
                    clean_lines = [line for line in lines if not line.strip().startswith('--')]
                    clean_query = '\n'.join(clean_lines).strip()
                
                if not clean_query:
                    st.warning("Please enter a valid SQL query")
                else:
                    # Execute the query
                    start_time = pd.Timestamp.now()
                    
                    # Check if it's a SELECT query (safe) or a modification query
                    is_select = clean_query.upper().strip().startswith('SELECT')
                    
                    if not is_select:
                        st.warning("⚠️ You're about to execute a non-SELECT query. This may modify your data!")
                        confirm = st.checkbox("I understand this may modify the database", key="confirm_modify")
                        if not confirm:
                            st.stop()
                    
                    result = conn.execute(clean_query).fetchall()
                    end_time = pd.Timestamp.now()
                    execution_time = (end_time - start_time).total_seconds()
                    
                    # Display results
                    if result:
                        # Get column names
                        columns = [desc[0] for desc in conn.description]
                        df_result = pd.DataFrame(result, columns=columns)
                        
                        st.success(f"✅ Query executed successfully in {execution_time:.3f} seconds")
                        st.subheader(f"Results ({len(result)} rows)")
                        
                        # Display the dataframe
                        st.dataframe(df_result, use_container_width=True)
                        
                        # Download option for results
                        csv_data = df_result.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=csv_data,
                            file_name=f"query_results_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                    else:
                        if is_select:
                            st.info("Query executed successfully but returned no results")
                        else:
                            st.success(f"✅ Query executed successfully in {execution_time:.3f} seconds")
                            st.info("Query completed (no results to display)")
                
                conn.close()
                
            except Exception as e:
                st.error(f"❌ Error executing query: {str(e)}")
                st.code(f"Query that failed:\n{sql_query}")
        
        # Quick query shortcuts
        st.subheader("Quick Queries")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👥 All Users", key="quick_all_users"):
                st.code("SELECT username, permissions, created_at, last_login FROM users ORDER BY created_at DESC;")
        
        with col2:
            if st.button("📊 User Stats", key="quick_stats"):
                st.code("SELECT permissions, COUNT(*) as user_count FROM users GROUP BY permissions;")
        
        with col3:
            if st.button("🕒 Recent Logins", key="quick_recent"):
                st.code("SELECT username, last_login FROM users WHERE last_login IS NOT NULL ORDER BY last_login DESC LIMIT 10;")
        
        # Safety warning
        st.warning("⚠️ **Safety Notice:** Be careful with UPDATE, DELETE, and DROP statements. Always backup your database before making structural changes.")

if __name__ == "__main__":
    admin_page()
