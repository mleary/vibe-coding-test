# 🚀 My Streamlit App

A lightweight Streamlit application with user authentication, permission-based access, and DuckDB backend. Features include a calendar view and image generator with a clean, modern UI.

## ✨ Features

- 🔐 **Secure Authentication** - DuckDB-powered user management
- 👑 **Admin Panel** - User management and permissions
- 📅 **Interactive Calendar** - Full calendar with ICS export
- 🎨 **Image Generator** - Basic image creation and editing
- 🛡️ **Permission System** - Role-based page access
- 💾 **Lightweight Database** - DuckDB for zero-cost storage

## 🏗️ Project Structure

```
my-streamlit-app
├── app.py                 # Main Streamlit application
├── login.py              # Authentication logic
├── db_auth.py            # DuckDB user management
├── pages/
│   ├── calendar.py       # Interactive calendar with events
│   ├── image_generator.py # Image creation tools
│   └── admin.py          # Admin user management
├── requirements.txt      # Python dependencies
├── users.db             # DuckDB database (auto-created, gitignored)
└── README.md
```

## 🚀 Quick Start

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd vibe-coding-test
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Access the app:** Open http://localhost:8501

### 🔑 Demo Credentials

| User | Password | Permissions |
|------|----------|-------------|
| `admin` | `admin123` | All pages + Admin Panel |
| `user1` | `password1` | Calendar only |
| `user2` | `password2` | Image Generator only |

## 🌍 Azure Deployment

### Option 1: Azure Container Apps (Recommended)

1. **Create a Dockerfile:**
   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Deploy to Azure:**
   ```bash
   # Build and push to Azure Container Registry
   az acr build --registry myregistry --image streamlit-app .
   
   # Deploy to Container Apps
   az containerapp create \
     --name streamlit-app \
     --resource-group myRG \
     --environment myEnv \
     --image myregistry.azurecr.io/streamlit-app \
     --target-port 8501 \
     --ingress external
   ```

### Option 2: Azure App Service

1. **Deploy directly:**
   ```bash
   az webapp up --name my-streamlit-app --runtime PYTHON:3.12
   ```

2. **Configure startup command in Azure:**
   ```
   python -m streamlit run app.py --server.port=8000 --server.address=0.0.0.0
   ```

### 💾 Database Persistence in Azure

**For production, set environment variable:**
```bash
# Point to persistent storage
export USER_DB_PATH="/mnt/data/users.db"
```

**Azure-specific options:**
- **Azure Files**: Mount persistent volume for database file
- **Azure Database**: Migrate to Azure SQL for scaling
- **Azure Storage**: Store database in blob storage (less recommended)

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USER_DB_PATH` | Path to DuckDB database file | `users.db` |
| `STREAMLIT_SERVER_PORT` | Port for Streamlit server | `8501` |

### Database Management

The app automatically creates a DuckDB database with default users. For production:

1. **Backup database:**
   ```bash
   cp users.db users_backup.db
   ```

2. **View database content:**
   ```python
   import duckdb
   conn = duckdb.connect("users.db")
   print(conn.execute("SELECT * FROM users").fetchall())
   ```

## 👑 Admin Features

Login as `admin` to access:
- ➕ Add new users
- 🔧 Modify user permissions  
- 🗑️ Delete users
- 📊 View user statistics
- 👥 Monitor login activity

## 🔒 Security Notes

- Passwords are SHA-256 hashed
- Database file is gitignored
- Session state manages authentication
- No hardcoded credentials in production

## 📦 Dependencies

- **streamlit**: Web app framework
- **streamlit-calendar**: Interactive calendar component  
- **duckdb**: Lightweight SQL database
- **pandas**: Data manipulation
- **Pillow**: Image processing

## 🐛 Troubleshooting

**Database Issues:**
```bash
# Reset database
rm users.db
# Restart app to recreate with defaults
```

**Permission Errors:**
- Check user permissions in Admin Panel
- Verify session state is preserved

**Deployment Issues:**
- Ensure `USER_DB_PATH` points to writable directory
- Check port configuration matches Azure settings

## 📄 License

MIT License - See LICENSE file for details.
   ```
   git clone <repository-url>
   cd my-streamlit-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

- Upon running the app, users will be presented with a login page.
- After successful login, users can navigate to the calendar or image generator pages based on their permissions.
- The calendar page currently contains placeholder content for demonstration purposes.
- The image generator page also contains dummy content to illustrate functionality.

## Contributing

Feel free to submit issues or pull requests for improvements or additional features.