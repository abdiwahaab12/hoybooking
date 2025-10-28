from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    long_description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200))  # Main/thumbnail image
    gallery_images = db.Column(db.Text)  # JSON array of gallery images
    project_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    _technologies = db.Column('technologies', db.Text)  # JSON string
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def technologies(self):
        """Get technologies as a list"""
        if self._technologies:
            try:
                return json.loads(self._technologies)
            except:
                return []
        return []
    
    @technologies.setter
    def technologies(self, value):
        """Set technologies from a list"""
        if isinstance(value, list):
            self._technologies = json.dumps(value)
        else:
            self._technologies = value
    
    @property
    def gallery_images_list(self):
        """Get gallery images as a list"""
        if self.gallery_images:
            try:
                return json.loads(self.gallery_images)
            except:
                return []
        return []
    
    @gallery_images_list.setter
    def gallery_images_list(self, value):
        """Set gallery images from a list"""
        if isinstance(value, list):
            self.gallery_images = json.dumps(value)
        else:
            self.gallery_images = value

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    proficiency = db.Column(db.Integer, nullable=False)  # 0-100
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    achievements = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(200), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    gpa = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    projects = Project.query.filter_by(featured=True).limit(6).all()
    skills = Skill.query.all()
    experiences = Experience.query.order_by(Experience.start_date.desc()).limit(3).all()
    return render_template('index.html', projects=projects, skills=skills, experiences=experiences)

@app.route('/about')
def about():
    skills = Skill.query.all()
    experiences = Experience.query.order_by(Experience.start_date.desc()).all()
    educations = Education.query.order_by(Education.start_date.desc()).all()
    return render_template('about.html', skills=skills, experiences=experiences, educations=educations)

@app.route('/resume')
def resume():
    experiences = Experience.query.order_by(Experience.start_date.desc()).all()
    educations = Education.query.order_by(Education.start_date.desc()).all()
    skills = Skill.query.all()
    
    # Parse achievements JSON for each experience
    for experience in experiences:
        if experience.achievements:
            try:
                experience.achievements = json.loads(experience.achievements)
            except:
                experience.achievements = []
    
    return render_template('resume.html', experiences=experiences, educations=educations, skills=skills)

@app.route('/portfolio')
def portfolio():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    categories = db.session.query(Project.category.distinct()).all()
    return render_template('portfolio.html', projects=projects, categories=[cat[0] for cat in categories])

@app.route('/portfolio/<int:project_id>')
def portfolio_details(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('portfolio-details.html', project=project)

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        new_message = Message(name=name, email=email, subject=subject, message=message)
        db.session.add(new_message)
        db.session.commit()
        
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

# Admin Routes
@app.route('/admin')
def admin_login():
    if 'admin_logged_in' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        session['admin_logged_in'] = True
        session['admin_user'] = user.username
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    projects_count = Project.query.count()
    skills_count = Skill.query.count()
    experiences_count = Experience.query.count()
    contacts_count = Message.query.count()
    unread_contacts = Message.query.filter_by(read=False).count()
    
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    recent_contacts = Message.query.order_by(Message.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         projects_count=projects_count,
                         skills_count=skills_count,
                         experiences_count=experiences_count,
                         contacts_count=contacts_count,
                         unread_contacts=unread_contacts,
                         recent_projects=recent_projects,
                         recent_contacts=recent_contacts)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    return redirect(url_for('admin_login'))

# API Routes for AJAX
@app.route('/api/projects', methods=['GET'])
def api_projects():
    projects = Project.query.all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'description': p.description,
        'long_description': p.long_description,
        'category': p.category,
        'image_url': p.image_url,
        'gallery_images': p.gallery_images_list,  # This will use the property
        'project_url': p.project_url,
        'github_url': p.github_url,
        'technologies': p.technologies,  # This will use the property
        'featured': p.featured,
        'created_at': p.created_at.isoformat()
    } for p in projects])

@app.route('/api/projects', methods=['POST'])
def api_create_project():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    project = Project(
        title=data['title'],
        description=data['description'],
        long_description=data.get('long_description', ''),
        category=data['category'],
        image_url=data.get('image_url', ''),
        project_url=data.get('project_url', ''),
        github_url=data.get('github_url', ''),
        technologies=json.dumps(data.get('technologies', [])),
        featured=data.get('featured', False)
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify({'message': 'Project created successfully', 'id': project.id})

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def api_update_project(project_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    
    # Update project fields
    project.title = data.get('title', project.title)
    project.description = data.get('description', project.description)
    project.long_description = data.get('long_description', project.long_description)
    project.category = data.get('category', project.category)
    project.image_url = data.get('image_url', project.image_url)
    project.project_url = data.get('project_url', project.project_url)
    project.github_url = data.get('github_url', project.github_url)
    project.featured = data.get('featured', project.featured)
    
    # Handle technologies
    if 'technologies' in data:
        project.technologies = data['technologies']
    
    # Handle gallery images
    if 'gallery_images' in data:
        project.gallery_images_list = data['gallery_images']
    
    db.session.commit()
    return jsonify({'message': 'Project updated successfully'})

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def api_delete_project(project_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    
    return jsonify({'message': 'Project deleted successfully'})

# Skills API endpoints
@app.route('/api/skills', methods=['GET'])
def api_skills():
    skills = Skill.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'category': s.category,
        'proficiency': s.proficiency,
        'description': s.description,
        'created_at': s.created_at.isoformat() if s.created_at else None
    } for s in skills])

@app.route('/api/skills', methods=['POST'])
def api_create_skill():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    skill = Skill(
        name=data['name'],
        category=data['category'],
        proficiency=data['proficiency'],
        description=data.get('description', '')
    )
    db.session.add(skill)
    db.session.commit()
    
    return jsonify({'message': 'Skill created successfully', 'id': skill.id})

@app.route('/api/skills/<int:skill_id>', methods=['PUT'])
def api_update_skill(skill_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    skill = Skill.query.get_or_404(skill_id)
    data = request.get_json()
    
    skill.name = data.get('name', skill.name)
    skill.category = data.get('category', skill.category)
    skill.proficiency = data.get('proficiency', skill.proficiency)
    skill.description = data.get('description', skill.description)
    
    db.session.commit()
    return jsonify({'message': 'Skill updated successfully'})

@app.route('/api/skills/<int:skill_id>', methods=['DELETE'])
def api_delete_skill(skill_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    
    return jsonify({'message': 'Skill deleted successfully'})

@app.route('/api/upload', methods=['POST'])
def api_upload_file():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({'message': 'File uploaded successfully', 'filename': filename})

# Experience API Routes
@app.route('/api/experiences', methods=['GET'])
def api_experiences():
    experiences = Experience.query.order_by(Experience.start_date.desc()).all()
    return jsonify([{
        'id': exp.id,
        'title': exp.title,
        'company': exp.company,
        'start_date': exp.start_date.isoformat(),
        'end_date': exp.end_date.isoformat() if exp.end_date else None,
        'description': exp.description,
        'achievements': exp.achievements
    } for exp in experiences])

@app.route('/api/experiences', methods=['POST'])
def api_create_experience():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    title = request.form.get('title')
    company = request.form.get('company')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date') if request.form.get('end_date') else None
    description = request.form.get('description')
    achievements = request.form.get('achievements')
    
    experience = Experience(
        title=title,
        company=company,
        start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
        description=description,
        achievements=achievements
    )
    
    db.session.add(experience)
    db.session.commit()
    
    return jsonify({'message': 'Experience created successfully', 'id': experience.id})

@app.route('/api/experiences/<int:experience_id>', methods=['GET'])
def api_get_experience(experience_id):
    experience = Experience.query.get_or_404(experience_id)
    return jsonify({
        'id': experience.id,
        'title': experience.title,
        'company': experience.company,
        'start_date': experience.start_date.isoformat(),
        'end_date': experience.end_date.isoformat() if experience.end_date else None,
        'description': experience.description,
        'achievements': experience.achievements
    })

@app.route('/api/experiences/<int:experience_id>', methods=['PUT'])
def api_update_experience(experience_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    experience = Experience.query.get_or_404(experience_id)
    
    # Check if this is an update (has ID in form data)
    if request.form.get('id'):
        experience.title = request.form.get('title')
        experience.company = request.form.get('company')
        experience.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        experience.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None
        experience.description = request.form.get('description')
        experience.achievements = request.form.get('achievements')
        
        db.session.commit()
        return jsonify({'message': 'Experience updated successfully'})
    else:
        # This is a create request, redirect to POST
        return api_create_experience()

@app.route('/api/experiences/<int:experience_id>', methods=['DELETE'])
def api_delete_experience(experience_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    experience = Experience.query.get_or_404(experience_id)
    db.session.delete(experience)
    db.session.commit()
    
    return jsonify({'message': 'Experience deleted successfully'})

# Messages API Routes
@app.route('/api/messages', methods=['GET'])
def api_messages():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return jsonify([{
        'id': msg.id,
        'name': msg.name,
        'email': msg.email,
        'subject': msg.subject,
        'message': msg.message,
        'read': msg.read,
        'created_at': msg.created_at.isoformat()
    } for msg in messages])

@app.route('/api/messages/<int:message_id>', methods=['GET'])
def api_get_message(message_id):
    message = Message.query.get_or_404(message_id)
    return jsonify({
        'id': message.id,
        'name': message.name,
        'email': message.email,
        'subject': message.subject,
        'message': message.message,
        'read': message.read,
        'created_at': message.created_at.isoformat()
    })

@app.route('/api/messages/<int:message_id>', methods=['PUT'])
def api_mark_message_read(message_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    message = Message.query.get_or_404(message_id)
    message.read = True
    db.session.commit()
    
    return jsonify({'message': 'Message marked as read successfully'})

@app.route('/api/messages/<int:message_id>', methods=['DELETE'])
def api_delete_message(message_id):
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'message': 'Message deleted successfully'})

@app.route('/api/messages', methods=['DELETE'])
def api_clear_all_messages():
    if 'admin_logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    Message.query.delete()
    db.session.commit()
    
    return jsonify({'message': 'All messages cleared successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")
    
    # Get port from environment (for Railway/Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
