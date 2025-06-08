#!/usr/bin/env python3
"""
Simple setup script for creating .env file and admin user
"""

import os
import shutil
import getpass

def setup_env_file():
    """Create .env file from .env.example"""
    if os.path.exists('.env'):
        print("📁 .env file already exists")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            return False
    
    if not os.path.exists('.env.example'):
        print("❌ .env.example file not found!")
        return False
    
    # Copy .env.example to .env
    shutil.copy('.env.example', '.env')
    print("✅ Created .env file from .env.example")
    return True

def set_admin_password():
    """Set admin password in .env file"""
    while True:
        password = getpass.getpass("Enter admin password (min 8 characters): ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters long")
            continue
        
        confirm_password = getpass.getpass("Confirm admin password: ")
        if password != confirm_password:
            print("❌ Passwords don't match")
            continue
        break
    
    # Update .env file
    env_lines = []
    password_set = False
    
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    
    # Update or add ADMIN_PASSWORD
    new_lines = []
    for line in env_lines:
        if line.startswith('ADMIN_PASSWORD='):
            new_lines.append(f'ADMIN_PASSWORD={password}\n')
            password_set = True
        else:
            new_lines.append(line)
    
    if not password_set:
        new_lines.append(f'ADMIN_PASSWORD={password}\n')
    
    with open('.env', 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Admin password set in .env file")
    return True

def main():
    print("🔐 Streamlit App Setup")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the project root directory")
        return
    
    print("Setting up environment configuration...")
    
    # Create .env file
    if setup_env_file():
        # Set admin password
        set_admin_password()
        
        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Log in with username 'admin' and your password")
        print("3. Use the admin panel to create additional users")
        print("\n💡 Tip: You can add more users through the admin panel or by manually editing the database")
    
    else:
        print("❌ Setup failed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")
