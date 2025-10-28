#!/usr/bin/env python3
"""
Database migration script to add the 'read' column to the Message table
This script handles both local and production database migrations
"""
import os
import sys
import sqlite3
from app import app, db

def migrate_database():
    """Add the read column to the Message table if it doesn't exist"""
    print("🔄 Starting database migration...")
    
    try:
        with app.app_context():
            # Get the database path - handle different SQLite URL formats
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"🔍 Database URI: {db_uri}")
            
            # Check if the URI is valid
            if not db_uri or 'SECRET_KEY' in db_uri:
                print("⚠️  Invalid database URI detected, using fallback")
                db_uri = 'sqlite:///instance/resume_db.db'
                print(f"🔍 Using fallback URI: {db_uri}")
            
            # Handle different SQLite URL formats
            if db_uri.startswith('sqlite:///'):
                db_path = db_uri.replace('sqlite:///', '')
            elif db_uri.startswith('sqlite://'):
                db_path = db_uri.replace('sqlite://', '')
            elif db_uri.startswith('sqlite:'):
                db_path = db_uri.replace('sqlite:', '')
            else:
                # For other database types, we can't migrate directly
                print(f"⚠️  Database type not supported for migration: {db_uri}")
                return True
            
            print(f"📁 Database path: {db_path}")
            
            if not os.path.exists(db_path):
                print(f"📁 Creating database at: {db_path}")
                # Create the database directory if it doesn't exist
                db_dir = os.path.dirname(db_path)
                if db_dir:
                    os.makedirs(db_dir, exist_ok=True)
                # Create all tables
                db.create_all()
                print("✅ Database and tables created successfully!")
                
                # Only create admin user and sample data if this is a completely new database
                print("🔧 Setting up initial data...")
                from database_setup import create_admin_user, create_sample_data
                create_admin_user()
                create_sample_data()
                print("✅ Initial data setup completed!")
                return True
            
            print(f"📁 Database found at: {db_path}")
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if the read column already exists
            cursor.execute("PRAGMA table_info(message)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'read' in columns:
                print("✅ Column 'read' already exists in the message table")
            else:
                print("🔧 Adding 'read' column to message table...")
                # Add the read column with default value False
                cursor.execute("ALTER TABLE message ADD COLUMN read BOOLEAN DEFAULT 0")
                # Update existing messages to have read=False (they should already be False by default)
                cursor.execute("UPDATE message SET read = 0 WHERE read IS NULL")
                print("✅ Successfully added 'read' column to the message table")
            
            # Check if the gallery_images column exists in project table
            cursor.execute("PRAGMA table_info(project)")
            project_columns = [column[1] for column in cursor.fetchall()]
            
            if 'gallery_images' in project_columns:
                print("✅ Column 'gallery_images' already exists in the project table")
            
            # Check if the last_login column exists in user table
            cursor.execute("PRAGMA table_info(user)")
            user_columns = [column[1] for column in cursor.fetchall()]
            
            if 'last_login' in user_columns:
                print("✅ Column 'last_login' already exists in the user table")
            else:
                print("🔧 Adding 'last_login' column to user table...")
                cursor.execute("ALTER TABLE user ADD COLUMN last_login DATETIME")
                print("✅ Successfully added 'last_login' column to the user table")
            
            if 'gallery_images' not in project_columns:
                print("🔧 Adding 'gallery_images' column to project table...")
                # Add the gallery_images column with default value NULL
                cursor.execute("ALTER TABLE project ADD COLUMN gallery_images TEXT")
                print("✅ Successfully added 'gallery_images' column to the project table")
            
            # Commit the changes
            conn.commit()
            conn.close()
            
            print("✅ Successfully added 'read' column to the message table")
            
            # Test the migration
            print("🧪 Testing migration...")
            from app import Message
            unread_count = Message.query.filter_by(read=False).count()
            total_count = Message.query.count()
            print(f"📊 Total messages: {total_count}")
            print(f"📊 Unread messages: {unread_count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main function to run the migration"""
    print("🚀 Database Migration Script")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🎉 Your application should now work without errors!")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
