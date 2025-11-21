from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, UserMixin, login_required
from sqlalchemy import func
import os
import requests

app = Flask(__name__)

# CONFIGURATION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillsync.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secure_key' 

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'register_page'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- MODELS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    skills = db.relationship('StudentSkill', backref='user', lazy=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    industry_need_level = db.Column(db.Integer, nullable=False)
    roadmap_group = db.Column(db.String(100), nullable=True)

class StudentSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), nullable=False)
    current_level = db.Column(db.Integer, nullable=False)
    completed_activities_count = db.Column(db.Integer, default=0) 

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)

# --- DATA SEEDING ---
def seed_database():
    ROADMAP_DATA = {
        'Web Developer': [{'name': 'HTML & CSS', 'industryNeed': 4}, {'name': 'JavaScript', 'industryNeed': 5}, {'name': 'Git & GitHub', 'industryNeed': 4}, {'name': 'Frontend Framework (React/Vue)', 'industryNeed': 5}, {'name': 'Backend Language (Python/Node)', 'industryNeed': 4}, {'name': 'Database (SQL/NoSQL)', 'industryNeed': 3}, {'name': 'APIs (RESTful)', 'industryNeed': 4}, {'name': 'Deployment (Cloud/Hosting)', 'industryNeed': 3}],
        'Data Scientist': [{'name': 'Probability & Statistics', 'industryNeed': 4}, {'name': 'Python (Pandas, NumPy)', 'industryNeed': 5}, {'name': 'SQL', 'industryNeed': 4}, {'name': 'Data Cleaning & Preprocessing', 'industryNeed': 4}, {'name': 'Machine Learning', 'industryNeed': 5}, {'name': 'Data Visualization', 'industryNeed': 3}, {'name': 'Big Data (Spark/Hadoop)', 'industryNeed': 2}, {'name': 'Deployment (APIs/Cloud)', 'industryNeed': 3}],
        'Cybersecurity Analyst': [{'name': 'Computer Fundamentals', 'industryNeed': 3}, {'name': 'Linux & Networking', 'industryNeed': 4}, {'name': 'Python for Automation', 'industryNeed': 3}, {'name': 'Security Tools (Nmap, Wireshark)', 'industryNeed': 4}, {'name': 'Web Security (OWASP)', 'industryNeed': 5}, {'name': 'Penetration Testing Basics', 'industryNeed': 4}, {'name': 'SOC/Blue Team Basics', 'industryNeed': 3}],
        'App Developer': [{'name': 'Java or Kotlin', 'industryNeed': 4}, {'name': 'Android Studio', 'industryNeed': 4}, {'name': 'UI/UX basics', 'industryNeed': 3}, {'name': 'Android components', 'industryNeed': 4}, {'name': 'Databases (Room, SQLite)', 'industryNeed': 3}, {'name': 'API integration', 'industryNeed': 4}, {'name': 'Firebase', 'industryNeed': 3}],
        'Cloud Engineer': [{'name': 'Linux basics', 'industryNeed': 3}, {'name': 'Networking (VPC, Subnets)', 'industryNeed': 4}, {'name': 'Cloud provider (AWS/Azure/GCP)', 'industryNeed': 5}, {'name': 'IAM', 'industryNeed': 4}, {'name': 'Compute (EC2, VM)', 'industryNeed': 5}, {'name': 'Storage (S3/Blob)', 'industryNeed': 3}, {'name': 'Databases (RDS, DynamoDB)', 'industryNeed': 3}, {'name': 'Monitoring & Security', 'industryNeed': 4}],
        'AI/ML Engineer': [{'name': 'Python (Adv. Libraries)', 'industryNeed': 4}, {'name': 'Stats & Probability', 'industryNeed': 4}, {'name': 'ML Algorithms', 'industryNeed': 5}, {'name': 'Deep Learning (TensorFlow/PyTorch)', 'industryNeed': 5}, {'name': 'Data Engineering basics', 'industryNeed': 3}, {'name': 'NLP / CV', 'industryNeed': 4}, {'name': 'Deployment (Docker, APIs)', 'industryNeed': 4}],
        'UI/UX Designer': [{'name': 'Design principles', 'industryNeed': 4}, {'name': 'Figma', 'industryNeed': 5}, {'name': 'Typography & Color Theory', 'industryNeed': 3}, {'name': 'Wireframes', 'industryNeed': 3}, {'name': 'Prototypes', 'industryNeed': 4}, {'name': 'User research', 'industryNeed': 4}, {'name': 'Portfolio building', 'industryNeed': 3}],
        'Ethical Hacker': [{'name': 'Linux fundamentals', 'industryNeed': 4}, {'name': 'Networking basics', 'industryNeed': 4}, {'name': 'Security concepts (CIA triad, attacks)', 'industryNeed': 5}, {'name': 'Kali Linux tools', 'industryNeed': 5}, {'name': 'Vulnerability scanning', 'industryNeed': 4}, {'name': 'Metasploit basics', 'industryNeed': 3}, {'name': 'Reporting & documentation', 'industryNeed': 3}],
        'Data Analyst': [{'name': 'Excel fundamentals', 'industryNeed': 4}, {'name': 'SQL basics (joins, subqueries)', 'industryNeed': 5}, {'name': 'Visualization tools (Power BI/Tableau)', 'industryNeed': 4}, {'name': 'Reports & dashboards', 'industryNeed': 3}, {'name': 'Basic analytics case studies', 'industryNeed': 3}],
        'Full Stack Developer': [{'name': 'HTML & CSS', 'industryNeed': 4}, {'name': 'JavaScript', 'industryNeed': 5}, {'name': 'Frontend Framework (React/Vue)', 'industryNeed': 5}, {'name': 'Backend Language (Node.js / Python)', 'industryNeed': 4}, {'name': 'Database (SQL/NoSQL)', 'industryNeed': 4}, {'name': 'APIs + Authentication', 'industryNeed': 4}, {'name': 'Deployment (Render, Vercel, AWS)', 'industryNeed': 4}]
    }
    with app.app_context():
        for role, skills in ROADMAP_DATA.items():
            for skill_data in skills:
                existing = Skill.query.filter_by(name=skill_data['name']).first()
                if not existing:
                    db.session.add(Skill(name=skill_data['name'], category='Technical', industry_need_level=skill_data['industryNeed'], roadmap_group=role))
        
        soft_skills = ['Communication Skills', 'Time Management', 'Public Speaking', 'Teamwork Skills', 'Critical Thinking', 'Leadership Skills', 'Creativity', 'Problem Solving', 'Emotional Intelligence']
        for name in soft_skills:
            if not Skill.query.filter_by(name=name).first():
                db.session.add(Skill(name=name, category='Soft', industry_need_level=5, roadmap_group='General'))
        db.session.commit()

# --- ROUTES ---
@app.route('/')
def home():
    try:
        feedbacks = Feedback.query.order_by(Feedback.id.desc()).limit(3).all()
    except:
        feedbacks = []
    return render_template('index.html', feedbacks=feedbacks)

@app.route('/register.html')
def register_page():
    return redirect(url_for('dashboard')) if current_user.is_authenticated else render_template('review.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    if User.query.filter((User.email == email) | (User.username == username)).first():
        return redirect(url_for('register_page'))
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, username=username, password_hash=hashed_pw)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('dashboard')) 

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(email=request.form.get('email')).first()
    if user and bcrypt.check_password_hash(user.password_hash, request.form.get('password')):
        login_user(user) 
        return redirect(url_for('dashboard'))
    return redirect(url_for('register_page'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required 
def dashboard():
    progress_query = db.session.query(
        Skill.category,
        (Skill.industry_need_level - func.avg(StudentSkill.current_level)).label('avg_gap')
    ).join(StudentSkill).filter(StudentSkill.user_id == current_user.id).group_by(Skill.category).all()
    
    gaps = {'Technical': {'total_gap': 5, 'level': 0}, 'Soft': {'total_gap': 5, 'level': 0}, 'status_message': f'Welcome, {current_user.username}. Start your assessment.'}
    
    for category, avg_gap in progress_query:
        current_lvl = max(0, 5 - round(avg_gap))
        gaps[category] = {'total_gap': round(avg_gap, 1), 'level': current_lvl}
    
    return render_template('dashboard.html', user_email=current_user.email, gaps=gaps, username=current_user.username)

@app.route('/technical-roadmap.html')
@login_required
def technical_roadmap():
    all_skills = Skill.query.filter_by(category='Technical').all()
    skill_data = []
    for s in all_skills:
        u_skill = StudentSkill.query.filter_by(user_id=current_user.id, skill_id=s.id).first()
        skill_data.append({
            'id': s.id, 'name': s.name, 'industryNeed': s.industry_need_level,
            'currentLevel': u_skill.current_level if u_skill else 1,
            'completedCount': u_skill.completed_activities_count if u_skill else 0,
            'roadmapGroup': s.roadmap_group 
        })
    ROADMAP_GROUPS = ["Web Developer", "Cybersecurity Analyst", "Ethical Hacker", "AI/ML Engineer", "Data Scientist", "Data Analyst", "Cloud Engineer", "UI/UX Designer", "Full Stack Developer"]
    return render_template('technical-roadmap.html', roadmap_groups=ROADMAP_GROUPS, skill_data=skill_data)

@app.route('/save_skills', methods=['POST'])
@login_required
def save_skills():
    for key, value in request.form.items():
        if key.startswith('skill_'):
            try:
                skill_id = int(key.split('_')[1])
                level = int(value)
                entry = StudentSkill.query.filter_by(user_id=current_user.id, skill_id=skill_id).first()
                if entry: entry.current_level = level
                else: db.session.add(StudentSkill(user_id=current_user.id, skill_id=skill_id, current_level=level))
            except ValueError: continue
    db.session.commit()
    return redirect(url_for('technical_roadmap'))

@app.route('/mark_activity_complete', methods=['POST'])
@login_required
def mark_activity_complete():
    data = request.json
    skill_name = data.get('skill_name')
    skill = Skill.query.filter_by(name=skill_name).first() 
    if not skill: return jsonify({"success": False, "message": "Skill not found"}), 404
    entry = StudentSkill.query.filter_by(user_id=current_user.id, skill_id=skill.id).first()
    if not entry:
        entry = StudentSkill(user_id=current_user.id, skill_id=skill.id, current_level=1, completed_activities_count=1)
        db.session.add(entry)
    else:
        entry.completed_activities_count += 1
        if entry.current_level < 5 and entry.completed_activities_count % 3 == 0:
             entry.current_level += 1
    db.session.commit()
    return jsonify({"success": True, "new_level": entry.current_level, "count": entry.completed_activities_count})

@app.route('/non-technical-activities.html')
@login_required
def non_tech():
    soft_skills = Skill.query.filter_by(category='Soft').all()
    soft_skill_data = []
    for s in soft_skills:
        u_skill = StudentSkill.query.filter_by(user_id=current_user.id, skill_id=s.id).first()
        soft_skill_data.append({
            'id': s.id, 'name': s.name, 'industryNeed': s.industry_need_level,
            'currentLevel': u_skill.current_level if u_skill else 1,
            'completedCount': u_skill.completed_activities_count if u_skill else 0
        })
    ACTIVITIES = {
        'Communication Skills': ['Record a 1-minute self-intro', 'Read aloud for 3 minutes', 'Talk to one new person', 'Write a professional email', 'Explain a concept in simple words'],
        'Time Management': ['Track your day for 24 hours', 'Make a to-do list', 'Complete 1 task using Pomodoro', 'Set top 3 priorities for tomorrow', 'Track actual study hours'],
        'Public Speaking': ['Speak in front of a mirror for 1 minute', 'Record a short speech', 'Ask 1 question in public', 'Present something to a friend', 'Watch a TED talk'],
        'Teamwork Skills': ['Complete 1 task with a partner', 'Give positive feedback', 'Delegate a task', 'Resolve a small conflict', 'Do a group mini-project'],
        'Critical Thinking': ['Solve 1 puzzle/riddle', 'Do a root-cause analysis', 'Break a problem into steps', 'Compare two solutions', 'Solve a small case study'],
        'Leadership Skills': ['Lead a small project', 'Assign tasks based on strengths', 'Give corrective feedback', 'Take responsibility for an outcome', 'Mentor a junior student'],
        'Creativity': ['Generate 5 ideas for a problem', 'Make a mind map', 'Sketch a rough design', 'Try a rapid prototype', 'Combine 2 random concepts'],
        'Problem Solving': ['Solve a logic puzzle', 'Break a real-life issue into steps', 'Test a solution and improve', 'Analyze why something failed', 'Compare outcomes of approaches'],
        'Emotional Intelligence': ['Maintain a mood journal', 'Do a 5-min breathing session', 'Practice active listening', 'Write a reflection on emotions', 'Observe someone’s emotion']
    }
    ICONS = {'Communication Skills': '🗣', 'Time Management': '🕒', 'Public Speaking': '🎤', 'Teamwork Skills': '👥', 'Critical Thinking': '🧠', 'Leadership Skills': '🧑‍🏫', 'Creativity': '💡', 'Problem Solving': '🧩', 'Emotional Intelligence': '❤️'}
    return render_template('non-technical-activities.html', soft_skill_data=soft_skill_data, ACTIVITIES=ACTIVITIES, ICONS=ICONS)

@app.route('/save_soft_skills', methods=['POST'])
@login_required
def save_soft_skills():
    return redirect(url_for('non_tech'))

@app.route('/feedback.html')
def feedback():
    try:
        feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    except:
        feedbacks = []
    return render_template('feedback.html', feedbacks=feedbacks)

@app.route('/submit_feedback', methods=['GET', 'POST'])
def submit_feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        rating = request.form.get('rating')
        message = request.form.get('message')
        new_feedback = Feedback(student_name=name, rating=int(rating), message=message)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(url_for('feedback'))
    return render_template('submit_feedback.html')

@app.route('/review-form.html')
def review_form():
    return redirect(url_for('submit_feedback'))

# --- UPDATED CHATBOT PROXY (Matches Your UI Models) ---
@app.route('/api/chat', methods=['POST'])
def chat_proxy():
    data = request.json
    user_message = data.get('message', '')
    API_KEY = "AIzaSyCgn4GzzsxN-2DHhDBY9IRWpiDFuWdE_vU" 
    
    # THESE MATCH THE NAMES IN YOUR GOOGLE MENU
    models_to_try = [
        "gemini-2.0-flash-exp",    # Matches "Gemini 2.0 Flash"
        "gemini-1.5-flash-latest", # Matches "Gemini Flash Latest"
        "gemini-1.5-flash",        # Fallback
        "gemini-1.5-pro"           # Fallback
    ]
    
    last_error = ""

    for model in models_to_try:
        URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
        payload = { "contents": [{"parts": [{"text": user_message}]}] }
        
        try:
            response = requests.post(URL, json=payload, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                print(f"SUCCESS using model: {model}")
                return jsonify(response.json())
            else:
                print(f"Failed model {model}: {response.text}")
                last_error = response.text
                
        except Exception as e:
            print(f"Connection error with {model}: {str(e)}")
            last_error = str(e)

    return jsonify({"error": f"All models failed. Last error: {last_error}"}), 500

# --- MAIN EXECUTION BLOCK ---
with app.app_context():
    db.create_all()
    seed_database()

if __name__ == '__main__':
    app.run(debug=True) 
    