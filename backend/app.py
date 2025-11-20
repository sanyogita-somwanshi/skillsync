from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, UserMixin, login_required
from sqlalchemy import func

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
    # New field to group skills by roadmap (e.g., "Web Developer")
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

# --- DATA SEEDING (This fills your database automatically!) ---
def seed_database():
    # If database has ANY skills, assume it's seeded.
    # To force re-seeding with new skills, you might need to delete the old DB file or drop tables.
    # But for now, let's just check if it's empty.
    if Skill.query.first():
        # Optional: Check if specific new skills exist, if not add them.
        # For simplicity, we'll just return if ANY data exists.
        # To fully update, you'd typically drop the table or use a migration tool.
        # For this quick fix, we will just return. 
        # If you want to FORCE update, delete the 'instance/skillsync.db' file locally/on render.
        return 

    print("Seeding database with detailed roadmap skills...")
    
    # --- TECHNICAL ROADMAP SKILLS ---
    roadmap_data = {
        "Web Developer": ["HTML basics", "CSS basics", "JavaScript fundamentals", "Git & GitHub", "APIs & JSON", "Frontend framework (React)", "Deployment (Netlify/Vercel)"],
        "Cybersecurity Analyst": ["Networking basics", "Linux fundamentals", "Security concepts (CIA triad, attacks)", "Tools: Nmap, Wireshark", "SIEM basics (Splunk/ELK)", "Incident response", "Basic scripting (Python/Bash)"],
        "Ethical Hacker": ["Linux + Networking", "Security basics", "Kali Linux tools", "Web application hacking (OWASP Top 10)", "Vulnerability scanning", "Metasploit basics", "Reporting & documentation"],
        "AI/ML Engineer": ["Python fundamentals", "NumPy, Pandas, Matplotlib", "Data preprocessing", "Machine learning algorithms", "Model training & evaluation", "Deep learning (Neural networks)", "Deployment basics (Flask/FastAPI)"],
        "Data Scientist": ["Python + Statistics", "Data cleaning (Pandas)", "EDA (visualization)", "ML models", "Feature engineering", "Model evaluation", "Dashboard/Reporting basics"],
        "Data Analyst": ["Excel fundamentals", "SQL basics", "Python basics (optional)", "Data cleaning", "Visualization tools (Power BI/Tableau)", "Reports & dashboards", "Basic analytics case studies"],
        "Cloud Engineer": ["Linux basics", "Networking fundamentals", "Cloud provider basics (AWS/Azure/GCP)", "Storage + Compute services", "IAM & security", "Deployment (EC2, S3, Load Balancers)", "Basic DevOps (CI/CD)"],
        "UI/UX Designer": ["UX basics + design principles", "User research", "Wireframing (low-fidelity)", "UI design (Figma)", "Prototyping", "Usability testing", "Design system basics"],
        "Full Stack Developer": ["HTML + CSS", "JavaScript", "Frontend framework (React)", "Backend basics (Node.js / Python)", "Databases (SQL/NoSQL)", "APIs + Authentication", "Deployment (Render, Vercel, AWS)"]
    }

    for role, skills in roadmap_data.items():
        for skill_name in skills:
            if not Skill.query.filter_by(name=skill_name).first():
                db.session.add(Skill(name=skill_name, category='Technical', industry_need_level=5, roadmap_group=role))

    # --- SOFT SKILLS ---
    soft_skills = [
        'Communication Skills', 'Time Management', 'Public Speaking',
        'Teamwork Skills', 'Critical Thinking', 'Leadership Skills',
        'Creativity', 'Problem Solving', 'Emotional Intelligence'
    ]
    for name in soft_skills:
        if not Skill.query.filter_by(name=name).first():
            db.session.add(Skill(name=name, category='Soft', industry_need_level=5, roadmap_group='General'))

    db.session.commit()
    print("Database seeded successfully!")

# --- DATA ---
# This list matches the keys in our seed function to populate the dropdown
ROADMAP_GROUPS = [
    "Web Developer", "Cybersecurity Analyst", "Ethical Hacker", 
    "AI/ML Engineer", "Data Scientist", "Data Analyst", 
    "Cloud Engineer", "UI/UX Designer", "Full Stack Developer" 
]

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
    # Fetch all technical skills
    all_skills = Skill.query.filter_by(category='Technical').all()
    skill_data = []
    for s in all_skills:
        u_skill = StudentSkill.query.filter_by(user_id=current_user.id, skill_id=s.id).first()
        skill_data.append({
            'id': s.id, 'name': s.name, 'industryNeed': s.industry_need_level,
            'currentLevel': u_skill.current_level if u_skill else 1,
            'completedCount': u_skill.completed_activities_count if u_skill else 0,
            'roadmapGroup': s.roadmap_group # Pass this to frontend to filter by dropdown
        })
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
    # Show all feedbacks on the dedicated feedback page
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

# --- MAIN EXECUTION BLOCK ---
# We run this outside __main__ so Gunicorn sees it
with app.app_context():
    db.create_all()     # 1. Create tables
    seed_database()     # 2. Fill tables with ALL default skills

if __name__ == '__main__':
    app.run(debug=True)