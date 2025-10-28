#!/usr/bin/env python3
"""
Script to reset the database with the correct schema
Use this if you encounter database schema issues
"""

from app import app, db, User
from werkzeug.security import generate_password_hash

def reset_database():
    with app.app_context():
        print("🔄 Resetting database...")
        
        # Drop all tables
        db.drop_all()
        print("✅ Dropped all tables")
        
        # Create all tables with current schema
        db.create_all()
        print("✅ Created all tables with current schema")
        
        # Create admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Created admin user (username: admin, password: admin123)")
        
        print("🎉 Database reset completed successfully!")
        print("📱 You can now run: python app.py")

if __name__ == '__main__':
    reset_database()
