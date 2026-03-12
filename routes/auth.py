import os
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from extensions import db, bcrypt
from models import User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username, password, nickname = data.get('username'), data.get('password'), data.get('nickname')
    if not all([username, password, nickname]): return jsonify({"error": "모든 필드를 입력해주세요."}), 400
    if User.query.get(username): return jsonify({"error": "이미 존재하는 아이디입니다."}), 409
    
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        username=username,
        password_hash=password_hash,
        nickname=nickname,
        introduction=f"{nickname}입니다. 잘 부탁드려요!",
        avatar_url=None
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": "회원가입이 완료되었습니다."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    user = User.query.get(username)
    if user and bcrypt.check_password_hash(user.password_hash, password):
        session['username'] = username
        session['nickname'] = user.nickname
        return jsonify({"nickname": user.nickname})
    return jsonify({"error": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": "로그아웃 되었습니다."})

@auth_bp.route('/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({"is_logged_in": True, "nickname": session['nickname'], "username": session['username']})
    return jsonify({"is_logged_in": False}), 401

@auth_bp.route('/users/<username>', methods=['GET'])
def get_user_profile(username):
    user = User.query.get(username)
    if user:
        return jsonify({"username": username, "nickname": user.nickname, "introduction": user.introduction or '', "avatar_url": user.avatar_url})
    return jsonify({"error": "사용자를 찾을 수 무 없습니다."}), 404

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    username = session['username']
    user = User.query.get(username)
    if not user: return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), 404
    
    user.nickname = request.form.get('nickname', user.nickname)
    user.introduction = request.form.get('introduction', user.introduction)
    session['nickname'] = user.nickname
    
    avatar_choice = request.form.get('avatar_choice')
    UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    if avatar_choice == 'default':
        user.avatar_url = None
    elif avatar_choice == 'upload' and 'avatar_file' in request.files:
        file = request.files['avatar_file']
        if file and file.filename != '':
            if user.avatar_url:
                old_filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(user.avatar_url))
                if os.path.exists(old_filepath): os.remove(old_filepath)
            filename = secure_filename(f"avatar_{username}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            user.avatar_url = f"/uploads/{filename}"
            
    db.session.commit()
    return jsonify({"success": "프로필이 성공적으로 업데이트되었습니다.", "updated_user": {"username": username, "nickname": user.nickname, "introduction": user.introduction, "avatar_url": user.avatar_url}})

@auth_bp.route('/find_id', methods=['POST'])
def find_id():
    data = request.get_json()
    nickname = data.get('nickname')
    if not nickname: return jsonify({"error": "닉네임을 입력해주세요."}), 400
    users = User.query.filter_by(nickname=nickname).all()
    if not users: return jsonify({"error": "해당 닉네임으로 가입된 아이디가 없습니다."}), 404
    return jsonify({"usernames": [u.username for u in users]})

@auth_bp.route('/verify_user', methods=['POST'])
def verify_user():
    data = request.get_json()
    username, nickname = data.get('username'), data.get('nickname')
    if not all([username, nickname]): return jsonify({"error": "아이디와 닉네임을 모두 입력해주세요."}), 400
    user = User.query.get(username)
    if not user or user.nickname != nickname: return jsonify({"error": "입력하신 아이디 또는 닉네임이 올바르지 않습니다."}), 404
    return jsonify({"success": "인증에 성공했습니다."})

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username, nickname, new_password = data.get('username'), data.get('nickname'), data.get('new_password')
    if not all([username, nickname, new_password]): return jsonify({"error": "모든 필드를 입력해주세요."}), 400
    user = User.query.get(username)
    if not user or user.nickname != nickname: return jsonify({"error": "입력하신 아이디 또는 닉네임이 올바르지 않습니다."}), 404
    new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.password_hash = new_password_hash
    db.session.commit()
    return jsonify({"success": "비밀번호가 성공적으로 변경되었습니다. 다시 로그인해주세요."})
