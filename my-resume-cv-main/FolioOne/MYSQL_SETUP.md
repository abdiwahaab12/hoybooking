# 🗄️ MySQL Database Setup Guide

## For Local Development:

### Step 1: Install MySQL
1. Download MySQL from [mysql.com](https://dev.mysql.com/downloads/mysql/)
2. Install MySQL Server
3. Set root password during installation

### Step 2: Create Database
```sql
CREATE DATABASE resume_db;
```

### Step 3: Update Configuration
Your `config.py` already has MySQL configuration:
```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/resume_db'
```

### Step 4: Run Database Setup
```bash
python database_setup.py
```

---

## For Production Deployment:

### Railway (Recommended):
1. **Add MySQL Service**:
   - Go to Railway dashboard
   - Click "New" → "Database" → "MySQL"
   - Railway will provide `DATABASE_URL` automatically

2. **Environment Variables**:
   - `SECRET_KEY`: `my-super-secret-key-12345-abdiwahab-resume-website-2025`
   - `DATABASE_URL`: Railway provides this automatically

### Render:
1. **Add PostgreSQL** (Render doesn't have free MySQL):
   - Go to Render dashboard
   - Click "New" → "PostgreSQL"
   - Use the provided `DATABASE_URL`

2. **Update requirements.txt** to include PostgreSQL:
   ```
   psycopg2-binary==2.9.7
   ```

### PythonAnywhere:
1. **Use MySQL** (included in free tier):
   - Go to "Databases" tab
   - Create MySQL database
   - Use connection string: `mysql+pymysql://username:password@mysql.server/resume_db`

---

## Database Connection Strings:

### MySQL:
```
mysql+pymysql://username:password@host:port/database_name
```

### PostgreSQL (for Render):
```
postgresql://username:password@host:port/database_name
```

### SQLite (fallback):
```
sqlite:///resume_db.db
```

---

## Environment Variables for Production:

### Railway:
- `SECRET_KEY`: `my-super-secret-key-12345-abdiwahab-resume-website-2025`
- `DATABASE_URL`: `mysql+pymysql://root:password@host:port/resume_db` (provided by Railway)

### Render:
- `SECRET_KEY`: `my-super-secret-key-12345-abdiwahab-resume-website-2025`
- `DATABASE_URL`: `postgresql://username:password@host:port/database` (provided by Render)

### PythonAnywhere:
- `SECRET_KEY`: `my-super-secret-key-12345-abdiwahab-resume-website-2025`
- `DATABASE_URL`: `mysql+pymysql://username:password@mysql.server/resume_db`
