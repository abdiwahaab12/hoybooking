# 🚀 PythonAnywhere Deployment Guide

## Step 1: Create PythonAnywhere Account
1. Go to [PythonAnywhere.com](https://pythonanywhere.com)
2. Create a free account
3. Verify your email

## Step 2: Upload Your Files
1. Go to "Files" tab
2. Navigate to `/home/yourusername/`
3. Upload your project files:
   - app.py
   - requirements.txt
   - config.py
   - templates/ folder
   - static/ folder
   - All other project files

## Step 3: Install Dependencies
1. Go to "Consoles" tab
2. Start a new Bash console
3. Run: `pip3.10 install --user -r requirements.txt`

## Step 4: Create Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Flask"
4. Choose Python 3.10
5. Set source code path to: `/home/yourusername/`
6. Set WSGI file to: `/home/yourusername/app.py`

## Step 5: Configure WSGI File
Replace the content with:
```python
import sys
path = '/home/yourusername'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

## Step 6: Reload Web App
1. Click "Reload" button
2. Your website will be live at: `https://yourusername.pythonanywhere.com`

## Admin Access:
- URL: `https://yourusername.pythonanywhere.com/admin`
- Username: `admin`
- Password: `admin123`

## Free Tier Limits:
- 750 hours/month
- 1 web app
- 1 console
- Perfect for personal resume website!
