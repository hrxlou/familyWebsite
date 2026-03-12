import os
from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models import Post, Comment
from PIL import Image

board_bp = Blueprint('board_bp', __name__)
POSTS_PER_PAGE = 5

@board_bp.route('/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '', type=str)
        
        query = Post.query
        if search_query:
            query = query.filter(
                (Post.title.contains(search_query)) | 
                (Post.content.contains(search_query))
            )
            
        pagination = query.order_by(Post.id.desc()).paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
        posts = [post.to_dict() for post in pagination.items]
        return jsonify({
            'posts': posts,
            'page': page,
            'total_pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        })
    
    if request.method == 'POST':
        if 'username' not in session: 
            return jsonify({"error": "로그인이 필요합니다."}), 401
        
        if 'title' not in request.form or 'content' not in request.form:
            return jsonify({"error": "제목과 내용을 모두 입력해주세요."}), 400
            
        title = request.form['title']
        content = request.form['content']
        image_url = None
        UPLOAD_FOLDER = current_app.config.get('UPLOAD_FOLDER', 'uploads')

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                try:
                    original_filename, _ = os.path.splitext(file.filename)
                    import time
                    timestamp = int(time.time())
                    filename = secure_filename(f"post_{timestamp}_{original_filename}.jpg")
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    
                    if not os.path.exists(UPLOAD_FOLDER):
                        os.makedirs(UPLOAD_FOLDER)
                        
                    image = Image.open(file.stream)
                    if image.mode in ("RGBA", "P"):
                        image = image.convert("RGB")
                    image.thumbnail((1920, 1920))
                    image.save(filepath, 'JPEG', quality=85)
                    image_url = f"/uploads/{filename}"
                except Exception as e:
                    print(f"이미지 처리 오류: {e}")
                    return jsonify({"error": "이미지 처리 중 오류가 발생했습니다."}), 500

        new_post = Post(
            author_username=session['username'],
            author_nickname=session['nickname'],
            title=title,
            content=content,
            image_url=image_url
        )
        db.session.add(new_post)
        db.session.commit()
        return jsonify(new_post.to_dict()), 201

@board_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id)
    if post:
        return jsonify(post.to_dict())
    return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

@board_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def handle_comments(post_id):
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    post = Post.query.get(post_id)
    if not post: return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404
    
    data = request.get_json()
    new_comment = Comment(
        post_id=post_id,
        author_username=session['username'],
        author_nickname=session['nickname'],
        content=data['content']
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(new_comment.to_dict()), 201
