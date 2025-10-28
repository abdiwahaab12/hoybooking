#!/usr/bin/env python3
"""
Update skills with Abdiwahab's technical skills
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Skill

def update_skills():
    """Update skills with technical skills"""
    print("Updating technical skills...")
    
    with app.app_context():
        # Clear existing skills
        Skill.query.delete()
        
        # Add Technical Skills
        skills_data = [
            {'name': 'HTML', 'category': 'Frontend', 'proficiency': 90, 'description': 'Semantic HTML5 markup and structure', 'icon': 'bi bi-code-slash'},
            {'name': 'CSS', 'category': 'Frontend', 'proficiency': 85, 'description': 'Responsive CSS3 and modern styling', 'icon': 'bi bi-palette'},
            {'name': 'Bootstrap', 'category': 'Frontend', 'proficiency': 80, 'description': 'Bootstrap framework for responsive design', 'icon': 'bi bi-grid-3x3-gap'},
            {'name': 'Python', 'category': 'Backend', 'proficiency': 85, 'description': 'Python programming and development', 'icon': 'bi bi-filetype-py'},
            {'name': 'Flask', 'category': 'Backend', 'proficiency': 80, 'description': 'Flask web framework development', 'icon': 'bi bi-server'},
            {'name': 'MySQL', 'category': 'Database', 'proficiency': 75, 'description': 'MySQL database management and queries', 'icon': 'bi bi-database'},
            {'name': 'Graphic Design', 'category': 'Design', 'proficiency': 90, 'description': 'Professional graphic design skills', 'icon': 'bi bi-palette2'},
            {'name': 'Word & Excel', 'category': 'Office', 'proficiency': 85, 'description': 'Microsoft Office applications', 'icon': 'bi bi-file-earmark-text'},
            {'name': 'Computer Repair', 'category': 'Technical', 'proficiency': 80, 'description': 'Hardware and software troubleshooting', 'icon': 'bi bi-tools'},
            {'name': 'English', 'category': 'Language', 'proficiency': 90, 'description': 'Fluent English communication', 'icon': 'bi bi-translate'}
        ]
        
        for skill_data in skills_data:
            skill = Skill(**skill_data)
            db.session.add(skill)
        
        db.session.commit()
        print("✅ Technical skills updated successfully!")
        print("\n📋 Your Skills:")
        for skill in skills_data:
            print(f"  • {skill['name']} ({skill['category']}) - {skill['proficiency']}%")

if __name__ == '__main__':
    update_skills()
