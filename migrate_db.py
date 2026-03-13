from app import app
from extensions import db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        # Check if column exists
        try:
            db.session.execute(text("SELECT category FROM events LIMIT 1"))
            print("Columns already exist.")
        except Exception:
            print("Adding category and repeat_type columns to events table...")
            try:
                db.session.execute(text("ALTER TABLE events ADD COLUMN category VARCHAR(50) DEFAULT 'others'"))
                db.session.execute(text("ALTER TABLE events ADD COLUMN repeat_type VARCHAR(50) DEFAULT 'none'"))
                db.session.commit()
                print("Database schema updated successfully!")
            except Exception as e:
                db.session.rollback()
                print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
