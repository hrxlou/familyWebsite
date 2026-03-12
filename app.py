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
app.register_blueprint(auth_bp)
app.register_blueprint(board_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(album_bp)
app.register_blueprint(chatbot_bp)

# Register Global Error Handlers
from errors import register_error_handlers
register_error_handlers(app)

# Seed Initial Data if empty
def seed_data():
    if User.query.first() is None:
        admin_password_hash = bcrypt.generate_password_hash(app.config['ADMIN_PASSWORD']).decode('utf-8')
        admin_user = User(
            username='admin',
            password_hash=admin_password_hash,
            nickname='관리자',
            introduction='우리 가족 앨범 사이트의 관리자입니다.',
            avatar_url=None
        )
        db.session.add(admin_user)
        db.session.commit()
        
        # Adding Mock Users for Posts
        mock_users = [
            ('dad', '아빠', '아빠입니다.'),
            ('mom', '엄마', '엄마입니다.'),
            ('son', '아들', '아들입니다.'),
            ('daughter', '딸', '딸입니다.')
        ]
        for u_id, u_nick, u_intro in mock_users:
            if not User.query.get(u_id):
                new_u = User(
                    username=u_id,
                    password_hash=bcrypt.generate_password_hash('password123').decode('utf-8'),
                    nickname=u_nick,
                    introduction=u_intro,
                    avatar_url=None
                )
                db.session.add(new_u)
        db.session.commit()
        
        # Adding Mock Posts
        mock_posts = [
            (6, "dad", "아빠", "다음 주 가족 외식 장소 투표!", "다음 주 토요일에 다 같이 저녁 먹자. 1. 한정식 2. 중식 3. 이탈리안 중에 댓글로 투표해줘!", None),
            (5, "mom", "엄마", "여름휴가 사진 앨범에 올렸어요", "이번에 다녀온 강릉 여행 사진들 앨범에 업데이트 했으니 다들 구경하세요~", "/uploads/post_5_summer_vacation.jpg"),
            (4, "son", "아들", "주말에 PC방 갈 사람?", "시험도 끝났는데 주말에 같이 게임할 사람 구합니다. 댓글 ㄱㄱ", None),
            (3, "daughter", "딸", "제 생일 선물로 받고 싶은 것(필독)", "곧 제 생일인 거 아시죠? 갖고 싶은 거 목록 적어두고 갑니다. 1. 최신형 아이패드 2. 용돈 3. 강아지", None),
            (2, "mom", "엄마", "오늘 저녁 장보기 목록", "혹시 더 필요한 거 있으면 저녁 6시까지 댓글로 알려주세요. (우유, 계란, 파, 양파 살 예정)", None),
            (1, "dad", "아빠", "주말에 공원 나들이 어때?", "날씨도 좋은데, 이번 주말에 다 같이 서울숲 공원이라도 갈까요? 도시락 싸서 가면 좋을 것 같아요.", None)
        ]
        
        for p_id, p_author, p_nick, p_title, p_content, p_img in reversed(mock_posts):
            post = Post(author_username=p_author, author_nickname=p_nick, title=p_title, content=p_content, image_url=p_img)
            db.session.add(post)
        db.session.commit()
        
        # Add a Comment to Post id 1
        post_1 = Post.query.filter_by(title="주말에 공원 나들이 어때?").first()
        if post_1:
            comment = Comment(post_id=post_1.id, author_username="mom", author_nickname="엄마", content="좋아요! 제가 도시락 준비할게요!")
            db.session.add(comment)
            db.session.commit()
            
        # Add Mock Events
        e1 = Event(date="2025-08-15", title="가족 여름휴가 🏖️")
        e2 = Event(date="2025-08-16", title="가족 여름휴가 🏖️")
        db.session.add_all([e1, e2])
        
        # Add Mock Anniversaries
        a1 = Anniversary(month=6, day=13, title="내 생일 🎂")
        a2 = Anniversary(month=8, day=28, title="할머니 생신")
        db.session.add_all([a1, a2])
        
        db.session.commit()

# Create DB and seed data
with app.app_context():
    db.create_all()
    seed_data()

# File routes
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)