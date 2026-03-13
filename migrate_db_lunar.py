from app import app
from extensions import db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        try:
            db.session.execute(text("ALTER TABLE events ADD COLUMN is_lunar BOOLEAN DEFAULT FALSE"))
            db.session.commit()
            print("is_lunar column added successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Column might already exist or error: {e}")

if __name__ == "__main__":
    update_schema()
