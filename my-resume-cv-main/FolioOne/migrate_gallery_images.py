#!/usr/bin/env python3
"""
Database migration script to add the 'gallery_images' column to the Project table
"""
import os
import sys
import sqlite3
from app import app, db

def migrate_gallery_images():
    """Add the gallery_images column to the Project table if it doesn't exist"""
    print("🔄 Starting gallery_images migration...")
    
    try:
        with app.app_context():
            # Get the database path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            if not os.path.exists(db_path):
                print(f"❌ Database not found at: {db_path}")
                return False
            
            print(f"📁 Database found at: {db_path}")
            
            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if the gallery_images column already exists
            cursor.execute("PRAGMA table_info(project)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'gallery_images' in columns:
                print("✅ Column 'gallery_images' already exists in the project table")
                conn.close()
                return True
            
            print("🔧 Adding 'gallery_images' column to project table...")
            
            # Add the gallery_images column with default value NULL
            cursor.execute("ALTER TABLE project ADD COLUMN gallery_images TEXT")
            
            # Commit the changes
            conn.commit()
            conn.close()
            
            print("✅ Successfully added 'gallery_images' column to the project table")
            
            # Test the migration
            print("🧪 Testing migration...")
            from app import Project
            projects = Project.query.all()
            print(f"📊 Total projects: {len(projects)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main function to run the migration"""
    print("🚀 Gallery Images Migration Script")
    print("=" * 50)
    
    success = migrate_gallery_images()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("🎉 Your application should now work without errors!")
    else:
        print("\n❌ Migration failed!")
        print("Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
