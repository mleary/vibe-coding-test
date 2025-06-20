import duckdb
import hashlib
import os
import streamlit as st
from typing import List, Optional, Dict

class UserDB:
    def __init__(self, db_path: str = "users.db"):
        """Initialize the user database"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with users table"""
        conn = duckdb.connect(self.db_path)
        
        # Create users table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR PRIMARY KEY,
                password_hash VARCHAR NOT NULL,
                permissions VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        # Create admin user from environment variable if it doesn't exist
        self._ensure_admin_user(conn)
        
        conn.close()
    
    def _ensure_admin_user(self, conn):
        """Ensure admin user exists, create from environment variable if needed"""
        # Check if admin user exists
        admin_exists = conn.execute("SELECT username FROM users WHERE username = 'admin'").fetchone()
        
        if not admin_exists:
            # Get admin password from environment variable
            admin_password = os.getenv("ADMIN_PASSWORD")
            
            if admin_password:
                password_hash = self._hash_password(admin_password)
                conn.execute(
                    "INSERT INTO users (username, password_hash, permissions) VALUES (?, ?, ?)",
                    ("admin", password_hash, "calendar,image_generator")
                )
                print("✅ Admin user created from ADMIN_PASSWORD environment variable")
            else:
                print("⚠️  Warning: No admin user found and ADMIN_PASSWORD environment variable not set.")
                print("   Set ADMIN_PASSWORD environment variable to create admin user automatically.")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info if successful"""
        conn = duckdb.connect(self.db_path)
        
        try:
            password_hash = self._hash_password(password)
            result = conn.execute(
                "SELECT username, permissions FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            ).fetchone()
            
            if result:
                # Update last login
                conn.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
                    (username,)
                )
                
                return {
                    "username": result[0],
                    "permissions": result[1].split(",") if result[1] else []
                }
            return None
        finally:
            conn.close()
    
    def add_user(self, username: str, password: str, permissions: List[str]) -> bool:
        """Add a new user to the database"""
        conn = duckdb.connect(self.db_path)
        
        try:
            # Check if user already exists
            existing = conn.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
            if existing:
                return False
            
            password_hash = self._hash_password(password)
            permissions_str = ",".join(permissions)
            
            conn.execute(
                "INSERT INTO users (username, password_hash, permissions) VALUES (?, ?, ?)",
                (username, password_hash, permissions_str)
            )
            return True
        except Exception:
            return False
        finally:
            conn.close()
    
    def update_permissions(self, username: str, permissions: List[str]) -> bool:
        """Update user permissions"""
        conn = duckdb.connect(self.db_path)
        
        try:
            permissions_str = ",".join(permissions)
            result = conn.execute(
                "UPDATE users SET permissions = ? WHERE username = ?",
                (permissions_str, username)
            )
            return result.fetchone() is not None
        except Exception:
            return False
        finally:
            conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (for admin purposes)"""
        conn = duckdb.connect(self.db_path)
        
        try:
            results = conn.execute(
                "SELECT username, permissions, created_at, last_login FROM users ORDER BY username"
            ).fetchall()
            
            users = []
            for result in results:
                users.append({
                    "username": result[0],
                    "permissions": result[1].split(",") if result[1] else [],
                    "created_at": result[2],
                    "last_login": result[3]
                })
            return users
        finally:
            conn.close()
    
    def delete_user(self, username: str) -> bool:
        """Delete a user (admin only)"""
        if username == "admin":  # Protect admin user
            return False
        
        conn = duckdb.connect(self.db_path)
        
        try:
            conn.execute("DELETE FROM users WHERE username = ?", (username,))
            return True
        except Exception:
            return False
        finally:
            conn.close()

# Initialize global database instance
@st.cache_resource
def get_user_db():
    """Get cached database instance"""
    # Use environment variable for database path in production
    db_path = os.getenv("USER_DB_PATH", "users.db")
    return UserDB(db_path)
