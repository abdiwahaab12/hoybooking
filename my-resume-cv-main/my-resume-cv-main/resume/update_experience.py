#!/usr/bin/env python3
"""
Update professional experience with Abdiwahab's services
"""

import sys
import os
from datetime import datetime, date
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Experience, Project

def update_experience():
    """Update professional experience"""
    print("Updating professional experience...")
    
    with app.app_context():
        # Clear existing experience
        Experience.query.delete()
        
        # Add Professional Experience
        experiences_data = [
            {
                'title': 'Full Stack Developer',
                'company': 'Freelance',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2023, 1, 1),
                'current': True,
                'description': 'Providing comprehensive full-stack development services including frontend, backend, and database solutions.',
                'achievements': json.dumps([
                    'Developed responsive web applications using HTML, CSS, Bootstrap, and JavaScript',
                    'Built backend systems with Python Flask framework',
                    'Designed and implemented MySQL databases for various projects',
                    'Created complete web solutions from concept to deployment',
                    'Collaborated with clients to deliver custom software solutions'
                ])
            },
            {
                'title': 'Mobile App Developer',
                'company': 'Freelance',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2023, 6, 1),
                'current': True,
                'description': 'Specializing in mobile application development for iOS and Android platforms.',
                'achievements': json.dumps([
                    'Developed cross-platform mobile applications',
                    'Implemented user-friendly interfaces and smooth user experiences',
                    'Integrated mobile apps with backend services and databases',
                    'Published applications on app stores',
                    'Provided ongoing maintenance and updates for mobile applications'
                ])
            },
            {
                'title': 'Computer Repair Specialist',
                'company': 'Freelance',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2022, 1, 1),
                'current': True,
                'description': 'Providing professional computer repair and maintenance services.',
                'achievements': json.dumps([
                    'Diagnosed and repaired hardware issues on desktop and laptop computers',
                    'Performed software troubleshooting and system optimization',
                    'Installed and configured operating systems and software',
                    'Provided data recovery and backup solutions',
                    'Offered preventive maintenance and system upgrades'
                ])
            },
            {
                'title': 'Mobile Repair Technician',
                'company': 'Freelance',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2022, 3, 1),
                'current': True,
                'description': 'Expert mobile device repair and maintenance services.',
                'achievements': json.dumps([
                    'Repaired smartphones and tablets with various issues',
                    'Replaced screens, batteries, and other components',
                    'Performed software updates and troubleshooting',
                    'Provided data recovery services for damaged devices',
                    'Offered device optimization and performance improvements'
                ])
            },
            {
                'title': 'Graphic Designer',
                'company': 'Freelance',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2024, 1, 1),
                'current': True,
                'description': 'Creating professional graphic designs and visual content for various clients.',
                'achievements': json.dumps([
                    'Designed logos, brochures, and marketing materials',
                    'Created social media graphics and promotional content',
                    'Developed brand identities and visual guidelines',
                    'Produced print-ready designs for various media',
                    'Collaborated with clients to achieve their vision'
                ])
            },
            {
                'title': 'Video Editor',
                'company': 'Freelance',
                'location': 'Mogadishu, Somalia',
                'start_date': date(2023, 9, 1),
                'current': True,
                'description': 'Professional video editing and post-production services.',
                'achievements': json.dumps([
                    'Edited promotional videos and marketing content',
                    'Created engaging social media video content',
                    'Performed color correction and audio enhancement',
                    'Added motion graphics and visual effects',
                    'Delivered high-quality video content for various platforms'
                ])
            }
        ]
        
        for exp_data in experiences_data:
            experience = Experience(**exp_data)
            db.session.add(experience)
        
        # Update Projects to reflect services
        Project.query.delete()
        projects_data = [
            {
                'title': 'Wanaag Travel and Logistic System',
                'description': 'A comprehensive travel and logistics management system built with full-stack development skills.',
                'long_description': 'Developed using HTML, CSS, Bootstrap for frontend, Python Flask for backend, and MySQL for database. Features include user management, booking systems, payment processing, and administrative dashboards.',
                'category': 'Full Stack Development',
                'image_url': '',
                'project_url': '',
                'github_url': '',
                'technologies': json.dumps(['HTML', 'CSS', 'Bootstrap', 'Python', 'Flask', 'MySQL']),
                'featured': True
            },
            {
                'title': 'Mobile App Development Portfolio',
                'description': 'Various mobile applications developed for different clients and purposes.',
                'long_description': 'Cross-platform mobile applications built for iOS and Android, featuring modern UI/UX design, backend integration, and database connectivity.',
                'category': 'Mobile App Development',
                'image_url': '',
                'project_url': '',
                'github_url': '',
                'technologies': json.dumps(['React Native', 'Flutter', 'JavaScript', 'Python']),
                'featured': True
            },
            {
                'title': 'Computer Repair Management System',
                'description': 'A system for managing computer repair services and customer tracking.',
                'long_description': 'A comprehensive system for computer repair shops to manage customer requests, track repair progress, maintain inventory, and generate reports.',
                'category': 'Software Solutions',
                'image_url': '',
                'project_url': '',
                'github_url': '',
                'technologies': json.dumps(['Python', 'Flask', 'MySQL', 'Bootstrap']),
                'featured': True
            },
            {
                'title': 'Graphic Design Portfolio',
                'description': 'Professional graphic design work including logos, brochures, and marketing materials.',
                'long_description': 'A collection of graphic design projects showcasing creativity and professional design skills across various media and platforms.',
                'category': 'Graphic Design',
                'image_url': '',
                'project_url': '',
                'github_url': '',
                'technologies': json.dumps(['Adobe Photoshop', 'Adobe Illustrator', 'Canva', 'CorelDRAW']),
                'featured': False
            },
            {
                'title': 'Video Editing Showcase',
                'description': 'Professional video editing projects including promotional videos and social media content.',
                'long_description': 'A portfolio of video editing work featuring promotional videos, social media content, and marketing materials with professional post-production effects.',
                'category': 'Video Editing',
                'image_url': '',
                'project_url': '',
                'github_url': '',
                'technologies': json.dumps(['Adobe Premiere Pro', 'After Effects', 'Final Cut Pro', 'DaVinci Resolve']),
                'featured': False
            }
        ]
        
        for project_data in projects_data:
            project = Project(**project_data)
            db.session.add(project)
        
        db.session.commit()
        print("✅ Professional experience updated successfully!")
        print("\n📋 Your Professional Services:")
        for exp in experiences_data:
            print(f"  • {exp['title']} ({exp['start_date'].year} - Present)")
        print("\n📋 Your Project Categories:")
        for proj in projects_data:
            print(f"  • {proj['title']} ({proj['category']})")

if __name__ == '__main__':
    update_experience()
