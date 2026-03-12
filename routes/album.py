import os
import time
import logging
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


@album_bp.route('/photos', methods=['GET', 'POST'])
def handle_photos():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        pagination = Photo.query.order_by(Photo.id.desc()).paginate(
            page=page, per_page=PHOTOS_PER_PAGE, error_out=False
        )
        return jsonify({
            'photos': [photo.to_dict() for photo in pagination.items],
            'page': page,
            'total_pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        })

    if request.method == 'POST':
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
            UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER', 'uploads')
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

            return jsonify(new_photo.to_dict()), 201
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
