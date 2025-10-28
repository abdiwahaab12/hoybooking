#!/usr/bin/env python3
"""
Add Flutter to Abdiwahab's technical skills
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Skill

def update_flutter_skills():
    """Add Flutter to technical skills"""
    print("Adding Flutter to technical skills...")
    
    with app.app_context():
        # Add Flutter skill
        flutter_skill = Skill(
            name='Flutter',
            category='Mobile Development',
            proficiency=75,
            description='Cross-platform mobile app development with Flutter framework',
            icon='bi bi-phone'
        )
        
        # Check if Flutter already exists
        existing_flutter = Skill.query.filter_by(name='Flutter').first()
        if not existing_flutter:
            db.session.add(flutter_skill)
            db.session.commit()
            print("✅ Flutter added to your skills!")
        else:
            print("✅ Flutter already exists in your skills!")
        
        # Show all current skills
        skills = Skill.query.all()
        print("\n📋 Your Complete Technical Skills:")
        for skill in skills:
            print(f"  • {skill.name} ({skill.category}) - {skill.proficiency}%")

if __name__ == '__main__':
    update_flutter_skills()
