import os
from app import app, db
from seed_db import seed_database

def hard_reset():
    print("🔄 Starting Hard Reset of Database...")
    
    # 1. Try to find and remove the database file
    db_path = os.path.join('instance', 'skillsync.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✅ Old database file deleted.")
        except PermissionError:
            print("❌ Error: Could not delete database. Please STOP the flask server (Control+C) and try again.")
            return

    # 2. Create new tables
    with app.app_context():
        db.create_all()
        print("✅ New database tables created (including username & tracking columns).")
        
        # 3. Seed data
        seed_database()
        print("✅ Database seeded with all Roadmaps and Skills.")
        print("🚀 DONE! You can now run 'python3 app.py'")

if __name__ == '__main__':
    hard_reset()