#!/usr/bin/env python3
"""
Database setup script for Resume/CV Website
Run this script to create the database and populate it with sample data
"""

import os
import sys
from datetime import datetime, date
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Project, Skill, Experience, Education, Message
from werkzeug.security import generate_password_hash

def create_database():
    """Create database tables"""
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
        print("✓ Database tables created successfully!")

def create_admin_user():
    """Create admin user"""
    print("Creating admin user...")
    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Admin user created: username='admin', password='admin123'")
        else:
            print("✓ Admin user already exists")

def create_sample_data():
    """Create sample data for the portfolio"""
    print("Creating sample data...")
    with app.app_context():
        # Sample Skills
        skills_data = [
            {'name': 'HTML', 'category': 'Frontend', 'proficiency': 95, 'description': 'Semantic HTML5 markup', 'icon': 'bi bi-code-slash'},
            {'name': 'CSS', 'category': 'Frontend', 'proficiency': 90, 'description': 'Responsive CSS3 and modern layouts', 'icon': 'bi bi-palette'},
            {'name': 'JavaScript', 'category': 'Frontend', 'proficiency': 85, 'description': 'ES6+ and modern JavaScript', 'icon': 'bi bi-filetype-js'},
            {'name': 'Python', 'category': 'Backend', 'proficiency': 90, 'description': 'Flask, Django, and data science', 'icon': 'bi bi-filetype-py'},
            {'name': 'React', 'category': 'Frontend', 'proficiency': 80, 'description': 'Modern React with hooks', 'icon': 'bi bi-filetype-jsx'},
            {'name': 'Node.js', 'category': 'Backend', 'proficiency': 75, 'description': 'Server-side JavaScript', 'icon': 'bi bi-filetype-js'},
            {'name': 'MySQL', 'category': 'Database', 'proficiency': 85, 'description': 'Relational database management', 'icon': 'bi bi-database'},
            {'name': 'Git', 'category': 'Tools', 'proficiency': 90, 'description': 'Version control and collaboration', 'icon': 'bi bi-git'}
        ]
        
        for skill_data in skills_data:
            existing_skill = Skill.query.filter_by(name=skill_data['name']).first()
            if not existing_skill:
                skill = Skill(**skill_data)
                db.session.add(skill)
        
        # No default projects - users will add their own projects via admin panel
        
        # Sample Experience
        experiences_data = [
            {
                'title': 'Senior Full Stack Developer',
                'company': 'TechCorp Solutions',
                'location': 'San Francisco, CA',
                'start_date': date(2022, 1, 1),
                'current': True,
                'description': 'Lead development of web applications and mobile solutions for enterprise clients.',
                'achievements': json.dumps([
                    'Led a team of 5 developers in building scalable web applications',
                    'Improved application performance by 40% through optimization',
                    'Implemented CI/CD pipelines reducing deployment time by 60%',
                    'Mentored junior developers and conducted code reviews'
                ])
            },
            {
                'title': 'Full Stack Developer',
                'company': 'Digital Innovations Inc.',
                'location': 'New York, NY',
                'start_date': date(2020, 6, 1),
                'end_date': date(2021, 12, 31),
                'current': False,
                'description': 'Developed and maintained web applications using modern JavaScript frameworks.',
                'achievements': json.dumps([
                    'Built responsive web applications serving 100K+ users',
                    'Collaborated with design team to implement pixel-perfect UIs',
                    'Integrated third-party APIs and payment systems',
                    'Participated in agile development processes'
                ])
            },
            {
                'title': 'Frontend Developer',
                'company': 'StartupXYZ',
                'location': 'Austin, TX',
                'start_date': date(2019, 3, 1),
                'end_date': date(2020, 5, 31),
                'current': False,
                'description': 'Focused on creating engaging user interfaces and improving user experience.',
                'achievements': json.dumps([
                    'Developed mobile-first responsive designs',
                    'Implemented modern CSS frameworks and preprocessors',
                    'Optimized website loading times and performance',
                    'Collaborated with UX designers on user research'
                ])
            }
        ]
        
        for exp_data in experiences_data:
            existing_exp = Experience.query.filter_by(
                title=exp_data['title'], 
                company=exp_data['company']
            ).first()
            if not existing_exp:
                experience = Experience(**exp_data)
                db.session.add(experience)
        
        # Sample Education
        educations_data = [
            {
                'degree': 'Master of Science in Computer Science',
                'institution': 'Stanford University',
                'location': 'Stanford, CA',
                'start_date': date(2017, 9, 1),
                'end_date': date(2019, 6, 1),
                'current': False,
                'description': 'Specialized in software engineering and machine learning.',
                'gpa': 3.8
            },
            {
                'degree': 'Bachelor of Science in Computer Science',
                'institution': 'University of California, Berkeley',
                'location': 'Berkeley, CA',
                'start_date': date(2013, 9, 1),
                'end_date': date(2017, 6, 1),
                'current': False,
                'description': 'Focused on algorithms, data structures, and software development.',
                'gpa': 3.6
            }
        ]
        
        for edu_data in educations_data:
            existing_edu = Education.query.filter_by(
                degree=edu_data['degree'],
                institution=edu_data['institution']
            ).first()
            if not existing_edu:
                education = Education(**edu_data)
                db.session.add(education)
        
        db.session.commit()
        print("✓ Sample data created successfully!")

def main():
    """Main setup function"""
    print("🚀 Setting up Resume/CV Website Database...")
    print("=" * 50)
    
    try:
        create_database()
        create_admin_user()
        create_sample_data()
        
        print("=" * 50)
        print("✅ Database setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update your database credentials in config.py")
        print("2. Run: python app.py")
        print("3. Visit: http://localhost:5000")
        print("4. Admin login: http://localhost:5000/admin")
        print("   Username: admin")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check your database credentials")
        print("3. Ensure the database 'resume_db' exists")
        print("4. Install required packages: pip install -r requirements.txt")

if __name__ == '__main__':
    main()
