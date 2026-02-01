import os
from app import app, db

def reset_database():
    print("Resetting database...")
    try:
        if os.path.exists("instance/student_planner.db"):
            os.remove("instance/student_planner.db")
            print("Removed old database file.")
        elif os.path.exists("student_planner.db"):
             os.remove("student_planner.db")
             print("Removed old database file (root).")
    except Exception as e:
        print(f"Error removing file (might be in use): {e}")
        # We proceed anyway, db.drop_all() might work if connection allows
        
    with app.app_context():
        try:
            db.drop_all()
            print("Dropped all tables.")
        except Exception as e:
            print(f"Warning dropping tables: {e}")
            
        db.create_all()
        print("Created all tables with new schema.")
        
    print("Database reset complete. Please restart the Flask server.")

if __name__ == "__main__":
    reset_database()
