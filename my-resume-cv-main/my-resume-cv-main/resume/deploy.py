#!/usr/bin/env python3
"""
Simple deployment script for Flask resume website
"""
import os
import sys

def main():
    print("🚀 Starting Flask Resume Website...")
    
    # Set environment variables if not set
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'my-super-secret-key-12345-abdiwahab-resume-website-2025'
    
    # Ensure upload directory exists
    upload_dir = 'static/uploads'
    os.makedirs(upload_dir, exist_ok=True)
    print(f"📁 Upload directory ensured: {upload_dir}")
    
    # Use persistent database path for production
    if not os.environ.get('DATABASE_URL'):
        # Use a persistent path for production deployments
        persistent_db_path = '/opt/render/project/src/instance/resume_db.db'
        os.environ['DATABASE_URL'] = f'sqlite:///{persistent_db_path}'
        print(f"🔍 Using persistent SQLite database: {persistent_db_path}")
    else:
        print(f"🔍 Using provided DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    
    # Run database migration
    print("🔄 Running database migration...")
    try:
        from migrate_database import migrate_database
        if migrate_database():
            print("✅ Database migration completed successfully!")
        else:
            print("❌ Database migration failed!")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Migration error: {e}")
        sys.exit(1)
    
    # Import and run the app
    from app import app
    
    # Get port from environment (for Railway/Render)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌍 Starting server on port {port}")
    print("📱 Your resume website is now live!")
    print("🔧 Admin panel: /admin (username: admin, password: admin123)")
    
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
