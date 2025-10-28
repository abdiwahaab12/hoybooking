#!/usr/bin/env python3
"""
Simple run script for the Resume/CV Website
"""

import os
import sys
from app import app

if __name__ == '__main__':
    # Run database migration first
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
    
    # Check if database exists and is set up
    try:
        from app import db
        with app.app_context():
            # Try to query the database to see if it's set up
            from app import User
            User.query.first()
        print("✅ Database connection successful!")
    except Exception as e:
        print("❌ Database setup required!")
        print("Please run: python database_setup.py")
        print(f"Error: {str(e)}")
        sys.exit(1)
    
    # Run the application
    print("🚀 Starting Resume/CV Website...")
    print("📍 Website: http://localhost:5000")
    print("🔧 Admin Panel: http://localhost:5000/admin")
    print("👤 Admin Login: admin / admin123")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
