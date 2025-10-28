# 🚀 Free Website Deployment Guide

## Option 1: Railway (Recommended)

### Step 1: Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Create a new repository
3. Upload your project files
4. Commit and push your code

### Step 2: Deploy to Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway will automatically detect Python and deploy

### Step 3: Configure Environment Variables
In Railway dashboard, add these environment variables:
- `SECRET_KEY`: Generate a random secret key
- `DATABASE_URL`: Use MySQL connection string (Railway will provide this automatically if you add MySQL service)

### Step 4: Access Your Website
- Railway will give you a URL like: `https://your-project.railway.app`
- Your website will be live!

---

## Option 2: Render

### Step 1: Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Create a new repository
3. Upload your project files

### Step 2: Deploy to Render
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
   - **Environment**: Python 3

### Step 3: Configure Environment Variables
Add these in Render dashboard:
- `SECRET_KEY`: Generate a random secret key
- `DATABASE_URL`: Use MySQL connection string (Render provides free PostgreSQL, but we'll use MySQL)

### Step 4: Access Your Website
- Render will give you a URL like: `https://your-project.onrender.com`

---

## Option 3: PythonAnywhere

### Step 1: Create Account
1. Go to [PythonAnywhere.com](https://pythonanywhere.com)
2. Create a free account

### Step 2: Upload Files
1. Go to "Files" tab
2. Upload your project files
3. Install requirements: `pip3.10 install --user -r requirements.txt`

### Step 3: Configure Web App
1. Go to "Web" tab
2. Create new web app
3. Choose "Flask" and Python 3.10
4. Set source code path to your project
5. Set WSGI file to your app.py

### Step 4: Access Your Website
- Your URL will be: `https://yourusername.pythonanywhere.com`

---

## 🔧 Important Notes

### Database Configuration
- **Railway/Render**: Use their provided PostgreSQL
- **PythonAnywhere**: Use SQLite (already configured)

### File Uploads
- Make sure `static/uploads` folder exists
- Uploaded files will be stored in this folder

### Admin Access
- Username: `admin`
- Password: `admin123`
- Change these in production!

### Custom Domain (Optional)
- All platforms support custom domains
- You can buy a domain and connect it

---

## 🎯 Quick Start (Railway)

1. **Upload to GitHub**: Push your code to GitHub
2. **Connect Railway**: Sign up at Railway.app with GitHub
3. **Deploy**: Click "Deploy from GitHub"
4. **Done**: Your website is live!

Your resume website will be accessible worldwide! 🌍
