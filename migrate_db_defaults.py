from app import app
from extensions import db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        # Set defaults for any NULL values if columns were just added
        try:
            db.session.execute(text("UPDATE events SET category = 'event' WHERE category IS NULL"))
            db.session.execute(text("UPDATE events SET repeat_type = 'none' WHERE repeat_type IS NULL"))
            db.session.commit()
            print("Defaults updated successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error setting defaults: {e}")

if __name__ == "__main__":
    update_schema()
