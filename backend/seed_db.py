from app import app, db, Skill
import pandas as pd 

ROADMAP_DATA = {
    'Web Developer': {'category': 'Technical', 'skills': [{'name': 'HTML & CSS', 'industryNeed': 4}, {'name': 'JavaScript', 'industryNeed': 5}, {'name': 'Git & GitHub', 'industryNeed': 4}, {'name': 'Frontend Framework (React/Vue)', 'industryNeed': 5}, {'name': 'Backend Language (Python/Node)', 'industryNeed': 4}, {'name': 'Database (SQL/NoSQL)', 'industryNeed': 3}, {'name': 'APIs (RESTful)', 'industryNeed': 4}, {'name': 'Deployment (Cloud/Hosting)', 'industryNeed': 3}]},
    'Data Scientist': {'category': 'Technical', 'skills': [{'name': 'Probability & Statistics', 'industryNeed': 4}, {'name': 'Python (Pandas, NumPy)', 'industryNeed': 5}, {'name': 'SQL', 'industryNeed': 4}, {'name': 'Data Cleaning & Preprocessing', 'industryNeed': 4}, {'name': 'Machine Learning', 'industryNeed': 5}, {'name': 'Data Visualization', 'industryNeed': 3}, {'name': 'Big Data (Spark/Hadoop)', 'industryNeed': 2}, {'name': 'Deployment (APIs/Cloud)', 'industryNeed': 3}]},
    'Cybersecurity Analyst': {'category': 'Technical', 'skills': [{'name': 'Computer Fundamentals', 'industryNeed': 3}, {'name': 'Linux & Networking', 'industryNeed': 4}, {'name': 'Python for Automation', 'industryNeed': 3}, {'name': 'Security Tools (Nmap, Wireshark)', 'industryNeed': 4}, {'name': 'Web Security (OWASP)', 'industryNeed': 5}, {'name': 'Penetration Testing Basics', 'industryNeed': 4}, {'name': 'SOC/Blue Team Basics', 'industryNeed': 3}]},
    'App Developer': {'category': 'Technical', 'skills': [{'name': 'Java or Kotlin', 'industryNeed': 4}, {'name': 'Android Studio', 'industryNeed': 4}, {'name': 'UI/UX basics', 'industryNeed': 3}, {'name': 'Android components', 'industryNeed': 4}, {'name': 'Databases (Room, SQLite)', 'industryNeed': 3}, {'name': 'API integration', 'industryNeed': 4}, {'name': 'Firebase', 'industryNeed': 3}]},
    'Cloud Engineer': {'category': 'Technical', 'skills': [{'name': 'Linux basics', 'industryNeed': 3}, {'name': 'Networking (VPC, Subnets)', 'industryNeed': 4}, {'name': 'Cloud provider (AWS/Azure/GCP)', 'industryNeed': 5}, {'name': 'IAM', 'industryNeed': 4}, {'name': 'Compute (EC2, VM)', 'industryNeed': 5}, {'name': 'Storage (S3/Blob)', 'industryNeed': 3}, {'name': 'Databases (RDS, DynamoDB)', 'industryNeed': 3}, {'name': 'Monitoring & Security', 'industryNeed': 4}]},
    'AI/ML Engineer': {'category': 'Technical', 'skills': [{'name': 'Python (Adv. Libraries)', 'industryNeed': 4}, {'name': 'Stats & Probability', 'industryNeed': 4}, {'name': 'ML Algorithms', 'industryNeed': 5}, {'name': 'Deep Learning (TensorFlow/PyTorch)', 'industryNeed': 5}, {'name': 'Data Engineering basics', 'industryNeed': 3}, {'name': 'NLP / CV', 'industryNeed': 4}, {'name': 'Deployment (Docker, APIs)', 'industryNeed': 4}]},
    'UI/UX Designer': {'category': 'Technical', 'skills': [{'name': 'Design principles', 'industryNeed': 4}, {'name': 'Figma', 'industryNeed': 5}, {'name': 'Typography & Color Theory', 'industryNeed': 3}, {'name': 'Wireframes', 'industryNeed': 3}, {'name': 'Prototypes', 'industryNeed': 4}, {'name': 'User research', 'industryNeed': 4}, {'name': 'Portfolio building', 'industryNeed': 3}]},
    
    'Ethical Hacker': {'category': 'Technical', 'skills': [{'name': 'Linux fundamentals', 'industryNeed': 4}, {'name': 'Networking basics', 'industryNeed': 4}, {'name': 'Security concepts (CIA triad, attacks)', 'industryNeed': 5}, {'name': 'Kali Linux tools', 'industryNeed': 5}, {'name': 'Vulnerability scanning', 'industryNeed': 4}, {'name': 'Metasploit basics', 'industryNeed': 3}, {'name': 'Reporting & documentation', 'industryNeed': 3}]},
    'Data Analyst': {'category': 'Technical', 'skills': [{'name': 'Excel fundamentals', 'industryNeed': 4}, {'name': 'SQL basics (joins, subqueries)', 'industryNeed': 5}, {'name': 'Visualization tools (Power BI/Tableau)', 'industryNeed': 4}, {'name': 'Reports & dashboards', 'industryNeed': 3}, {'name': 'Basic analytics case studies', 'industryNeed': 3}]},
    'Full Stack Developer': {'category': 'Technical', 'skills': [{'name': 'HTML & CSS', 'industryNeed': 4}, {'name': 'JavaScript', 'industryNeed': 5}, {'name': 'Frontend Framework (React/Vue)', 'industryNeed': 5}, {'name': 'Backend Language (Node.js / Python)', 'industryNeed': 4}, {'name': 'Database (SQL/NoSQL)', 'industryNeed': 4}, {'name': 'APIs + Authentication', 'industryNeed': 4}, {'name': 'Deployment (Render, Vercel, AWS)', 'industryNeed': 4}]},

    'Soft Skills': {
        'category': 'Soft',
        'skills': [
            {'name': 'Communication Skills', 'industryNeed': 4}, {'name': 'Time Management', 'industryNeed': 3},
            {'name': 'Public Speaking', 'industryNeed': 3}, {'name': 'Teamwork Skills', 'industryNeed': 4},
            {'name': 'Critical Thinking', 'industryNeed': 5}, {'name': 'Leadership Skills', 'industryNeed': 4},
            {'name': 'Emotional Intelligence', 'industryNeed': 4}, {'name': 'Creativity', 'industryNeed': 3},
            {'name': 'Problem Solving', 'industryNeed': 5}
        ],
    }
}

def seed_database():
    print("Starting database seeding...")
    with app.app_context():
        skills_to_check = []
        for goal_name, data in ROADMAP_DATA.items():
            category = data['category']
            for skill_data in data['skills']:
                skills_to_check.append({'name': skill_data['name'], 'category': category, 'industry_need_level': skill_data['industryNeed']})

        df_skills = pd.DataFrame(skills_to_check).drop_duplicates(subset=['name'])
        
        skills_to_add = []
        for index, row in df_skills.iterrows():
            existing_skill = Skill.query.filter_by(name=row['name']).first()
            if not existing_skill:
                skills_to_add.append(Skill(name=row['name'], category=row['category'], industry_need_level=row['industry_need_level']))
        
        if skills_to_add:
            db.session.add_all(skills_to_add)
            db.session.commit()
            print(f"Successfully added {len(skills_to_add)} new skills to the database.")
        else:
            print("Database already contains all skills. No changes made.")

if __name__ == '__main__':
    seed_database()