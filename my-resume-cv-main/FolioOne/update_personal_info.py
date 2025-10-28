#!/usr/bin/env python3
"""
Update personal information in the database
"""

import sys
import os
from datetime import datetime, date
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Project, Skill, Experience, Education, Contact

def update_personal_info():
    """Update database with Abdiwahab's real information"""
    print("Updating personal information...")
    
    with app.app_context():
        # Clear existing data
        Skill.query.delete()
        Experience.query.delete()
        Education.query.delete()
        Project.query.delete()
        
        # Add Skills
        skills_data = [
            {'name': 'Graphic Design', 'category': 'Design', 'proficiency': 90, 'description': 'Professional graphic design skills', 'icon': 'bi bi-palette'},
            {'name': 'Word & Excel', 'category': 'Office', 'proficiency': 85, 'description': 'Microsoft Office applications', 'icon': 'bi bi-file-earmark-text'},
            {'name': 'Computer Repair', 'category': 'Technical', 'proficiency': 80, 'description': 'Hardware and software troubleshooting', 'icon': 'bi bi-tools'},
            {'name': 'Software Solutions', 'category': 'Development', 'proficiency': 75, 'description': 'Custom software development', 'icon': 'bi bi-code-slash'},
            {'name': 'Web Development', 'category': 'Development', 'proficiency': 85, 'description': 'Building websites and systems', 'icon': 'bi bi-globe'},
            {'name': 'English', 'category': 'Language', 'proficiency': 90, 'description': 'Fluent English communication', 'icon': 'bi bi-translate'}
        ]
        
        for skill_data in skills_data:
            skill = Skill(**skill_data)
            db.session.add(skill)
        
        # Add Education
        educations_data = [
            {
                'degree': 'Bachelor of Computer Science',
                'institution': 'Jomhuria University',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2021, 9, 1),
                'end_date': date(2025, 6, 1),
                'current': False,
                'description': 'Comprehensive computer science education with focus on software development and system design.',
                'gpa': 3.5
            },
            {
                'degree': 'Diploma in Accounting',
                'institution': 'Al-Imra University',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2023, 9, 1),
                'end_date': date(2024, 6, 1),
                'current': False,
                'description': 'Professional accounting and financial management training.',
                'gpa': 3.7
            }
        ]
        
        for edu_data in educations_data:
            education = Education(**edu_data)
            db.session.add(education)
        
        # Add Experience
        experiences_data = [
            {
                'title': 'Graphic Designer',
                'company': 'Freelance',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2024, 1, 1),
                'current': True,
                'description': 'Providing professional graphic design services to various clients.',
                'achievements': json.dumps([
                    'Created compelling visual designs for multiple projects',
                    'Developed brand identities and marketing materials',
                    'Collaborated with clients to deliver high-quality designs',
                    'Maintained consistent design standards across all projects'
                ])
            }
        ]
        
        for exp_data in experiences_data:
            experience = Experience(**exp_data)
            db.session.add(experience)
        
        # Add Projects
        projects_data = [
            {
                'title': 'Wanaag Travel and Logistic System',
                'description': 'I developed Wanaag Travel Agency and Logistic System, a modern and efficient platform designed to simplify travel booking and logistics management.',
                'long_description': 'A comprehensive travel and logistics management system that streamlines booking processes, manages transportation logistics, and provides real-time tracking capabilities. The system includes user management, booking systems, payment processing, and administrative dashboards.',
                'category': 'Web Development',
                'image_url': '',
                'project_url': '',
                'github_url': '',
                'technologies': json.dumps(['HTML', 'CSS', 'JavaScript', 'PHP', 'MySQL']),
                'featured': True
            },
            {
                'title': 'Computer Repair Service Management',
                'description': 'A system for managing computer repair services, tracking repairs, and customer management.',
                'long_description': 'A comprehensive system for computer repair shops to manage customer requests, track repair progress, maintain inventory, and generate reports.',
                'category': 'Software Solutions',
                'image_url': '',
                'project_url': '',
                'github_url': '',
                'technologies': json.dumps(['Python', 'SQLite', 'Tkinter']),
                'featured': True
            },
            {
                'title': 'Accounting Management System',
                'description': 'A professional accounting system for small businesses to manage finances and generate reports.',
                'long_description': 'A user-friendly accounting system that helps small businesses track income, expenses, generate invoices, and create financial reports.',
                'category': 'Software Solutions',
                'image_url': '',
                'project_url': '',
                'github_url': '',
                'technologies': json.dumps(['Python', 'MySQL', 'Flask']),
                'featured': False
            }
        ]
        
        for project_data in projects_data:
            project = Project(**project_data)
            db.session.add(project)
        
        db.session.commit()
        print("✅ Personal information updated successfully!")

if __name__ == '__main__':
    update_personal_info()
