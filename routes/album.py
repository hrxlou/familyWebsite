import os
import time
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models import Photo

logger = logging.getLogger(__name__)
album_bp = Blueprint('album_bp', __name__)
PHOTOS_PER_PAGE = 20

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@album_bp.route('/photos', methods=['GET'])
def get_photos():
    page = request.args.get('page', 1, type=int)
    from models import Post, Photo
    
    # 1. 앨범 전용 사진 (Photo)
    photos_query = Photo.query.all()
    photo_list = []
    for p in photos_query:
        photo_list.append({
            'id': f"photo_{p.id}",
            'url': p.url,
            'author_nickname': p.uploader_nickname,
            'uploader_username': p.uploader_username,
            'created_at': p.created_at,
            'type': 'photo'
        })
    
    # 2. 게시판 사진 (Post)
    posts_query = Post.query.filter(Post.image_url != None, Post.image_url != '').all()
    post_photo_list = []
    for p in posts_query:
        url = p.image_url
        if url and not url.startswith('/') and not url.startswith('http'):
            url = f"/uploads/{url}"
            
        post_photo_list.append({
            'id': f"post_{p.id}",
            'url': url,
            'author_nickname': p.author_nickname,
            'uploader_username': p.author_username,
            'created_at': p.created_at,
            'type': 'post',
            'link': f"/post.html?id={p.id}"
        })
    
    # 통합 및 정렬 (최신순)
    all_photos = sorted(photo_list + post_photo_list, key=lambda x: x['created_at'] if x['created_at'] else datetime.min, reverse=True)
    
    # 수동 페이징 처리
    start = (page - 1) * PHOTOS_PER_PAGE
    end = start + PHOTOS_PER_PAGE
    paginated_items = all_photos[start:end]
    total_pages = (len(all_photos) + PHOTOS_PER_PAGE - 1) // PHOTOS_PER_PAGE

    return jsonify({
        'photos': [{
            **p,
            'created_at': p['created_at'].isoformat() if p['created_at'] else None
        } for p in paginated_items],
        'page': page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    })

@album_bp.route('/photos', methods=['POST'])
def upload_photo():
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "선택된 파일이 없습니다."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "허용되지 않는 파일 형식입니다. (png, jpg, jpeg, gif, webp만 가능)"}), 400

    try:
        UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        original_filename, ext = os.path.splitext(file.filename)
        timestamp = int(time.time())
        filename = secure_filename(f"photo_{timestamp}_{original_filename}{ext}")

        file.save(os.path.join(UPLOAD_FOLDER, filename))

        new_photo = Photo(
            filename=filename,
            url=f"/uploads/{filename}",
            uploader_username=session['username'],
            uploader_nickname=session['nickname']
        )
        db.session.add(new_photo)
        db.session.commit()

        return jsonify({
            'id': f"photo_{new_photo.id}",
            'url': new_photo.url,
            'author_nickname': new_photo.uploader_nickname,
            'created_at': new_photo.created_at.isoformat(),
            'type': 'photo'
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"사진 업로드 오류: {e}")
        return jsonify({"error": "사진 업로드 중 오류가 발생했습니다."}), 500


@album_bp.route('/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    photo = Photo.query.get(photo_id)
    if not photo:
        return jsonify({"error": "사진을 찾을 수 없습니다."}), 404

    current_user = session['username']
    if current_user != 'admin' and current_user != photo.uploader_username:
        return jsonify({"error": "사진을 삭제할 권한이 없습니다."}), 403

    try:
        UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        filepath = os.path.join(UPLOAD_FOLDER, photo.filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        db.session.delete(photo)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logger.error(f"사진 삭제 오류: {e}")
        return jsonify({"error": "파일 삭제 중 오류가 발생했습니다."}), 500
