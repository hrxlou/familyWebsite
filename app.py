import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from extensions import db, bcrypt
from models import User, Post, Comment, Photo, Event, Anniversary
from config import Config

# Import blueprints
from routes.auth import auth_bp
from routes.board import board_bp
from routes.calendar import calendar_bp
from routes.album import album_bp
from routes.chatbot import chatbot_bp

# Set up the app
app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(Config)
CORS(app, supports_credentials=True)

# Constants
UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(board_bp, url_prefix='/api')
app.register_blueprint(calendar_bp, url_prefix='/api')
app.register_blueprint(album_bp, url_prefix='/api')
app.register_blueprint(chatbot_bp, url_prefix='/api')

# Register Global Error Handlers
from errors import register_error_handlers
register_error_handlers(app)

# Seed Initial Data if empty
def seed_data():
    if User.query.filter_by(username='admin').first() is None:
        admin_password_hash = bcrypt.generate_password_hash(app.config['ADMIN_PASSWORD']).decode('utf-8')
        admin_user = User(
            username='admin',
            password_hash=admin_password_hash,
            nickname='관리자'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created.")

# --- Static File Serving ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    # Check if the file exists in static folder
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Default to index.html for SPA-like behavior if needed, 
    # but carefully handle API routes which should return 404 if not found
    if path.startswith('api/'):
        return {"error": "API route not found"}, 404
    return send_from_directory(app.static_folder, 'index.html')

# --- Main Entry Point ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
