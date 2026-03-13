import os
import re
import logging
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from extensions import db, bcrypt
from models import User

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth_bp', __name__)

# 비밀번호 정책 검증
def validate_password(password):
    if len(password) < 6:
        return "비밀번호는 최소 6자 이상이어야 합니다."
    if not re.search(r'[a-zA-Z]', password):
        return "비밀번호에 영문자가 포함되어야 합니다."
    if not re.search(r'[0-9]', password):
        return "비밀번호에 숫자가 포함되어야 합니다."
    return None


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username, password, nickname = data.get('username'), data.get('password'), data.get('nickname')
    if not all([username, password, nickname]):
        return jsonify({"error": "모든 필드를 입력해주세요."}), 400
    if User.query.get(username):
        return jsonify({"error": "이미 존재하는 아이디입니다."}), 409

    pw_error = validate_password(password)
    if pw_error:
        return jsonify({"error": pw_error}), 400

    try:
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
    except Exception as e:
        db.session.rollback()
        logger.error(f"회원가입 오류: {e}")
        return jsonify({"error": "회원가입 처리 중 오류가 발생했습니다."}), 500


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
    return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404


@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    username = session['username']
    user = User.query.get(username)
    if not user:
        return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), 404

    try:
        user.nickname = request.form.get('nickname', user.nickname)
        user.introduction = request.form.get('introduction', user.introduction)
        session['nickname'] = user.nickname

        new_password = request.form.get('password')
        if new_password:
            pw_error = validate_password(new_password)
            if pw_error:
                return jsonify({"error": pw_error}), 400
            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                from utils.image_utils import process_and_save_image, delete_image_file
                if user.avatar_url:
                    try:
                        delete_image_file(user.avatar_url)
                    except:
                        pass
                user.avatar_url = process_and_save_image(file, prefix="avatar")

        db.session.commit()
        return jsonify({"success": "프로필이 성공적으로 업데이트되었습니다."})
    except Exception as e:
        db.session.rollback()
        logger.error(f"프로필 업데이트 오류: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/find_id', methods=['POST'])
def find_id():
    data = request.get_json()
    nickname = data.get('nickname')
    if not nickname:
        return jsonify({"error": "닉네임을 입력해주세요."}), 400
    users = User.query.filter_by(nickname=nickname).all()
    if not users:
        return jsonify({"error": "해당 닉네임으로 가입된 아이디가 없습니다."}), 404
    return jsonify({"usernames": [u.username for u in users]})


@auth_bp.route('/verify_user', methods=['POST'])
def verify_user():
    data = request.get_json()
    username, nickname = data.get('username'), data.get('nickname')
    if not all([username, nickname]):
        return jsonify({"error": "아이디와 닉네임을 모두 입력해주세요."}), 400
    user = User.query.get(username)
    if not user or user.nickname != nickname:
        return jsonify({"error": "입력하신 아이디 또는 닉네임이 올바르지 않습니다."}), 404
    return jsonify({"success": "인증에 성공했습니다."})


@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username, nickname, new_password = data.get('username'), data.get('nickname'), data.get('new_password')
    if not all([username, nickname, new_password]):
        return jsonify({"error": "모든 필드를 입력해주세요."}), 400

    pw_error = validate_password(new_password)
    if pw_error:
        return jsonify({"error": pw_error}), 400

    user = User.query.get(username)
    if not user or user.nickname != nickname:
        return jsonify({"error": "입력하신 아이디 또는 닉네임이 올바르지 않습니다."}), 404

    try:
        new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password_hash = new_password_hash
        db.session.commit()
        return jsonify({"success": "비밀번호가 성공적으로 변경되었습니다. 다시 로그인해주세요."})
    except Exception as e:
        db.session.rollback()
        logger.error(f"비밀번호 변경 오류: {e}")
        return jsonify({"error": "비밀번호 변경 중 오류가 발생했습니다."}), 500
