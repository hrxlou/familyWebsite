import logging
from flask import Blueprint, request, jsonify, session, current_app
from sqlalchemy.orm import joinedload
from extensions import db
from models import Post, Comment, Notification
from utils.image_utils import process_and_save_image, delete_image_file

logger = logging.getLogger(__name__)
board_bp = Blueprint('board_bp', __name__)


@board_bp.route('/posts', methods=['GET', 'POST'])
def handle_posts():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '', type=str)
        search_type = request.args.get('type', 'all', type=str)

        query = Post.query.options(joinedload(Post.comments), joinedload(Post.likes))
        if search_query:
            if search_type == 'title':
                query = query.filter(Post.title.contains(search_query))
            elif search_type == 'content':
                query = query.filter(Post.content.contains(search_query))
            elif search_type == 'author':
                query = query.filter(Post.author_nickname.contains(search_query))
            else:  # 'all'
                query = query.filter(
                    (Post.title.contains(search_query)) |
                    (Post.content.contains(search_query)) |
                    (Post.author_nickname.contains(search_query))
                )

        pagination = query.order_by(Post.id.desc()).paginate(
            page=page, 
            per_page=current_app.config.get('POSTS_PER_PAGE', 5), 
            error_out=False
        )
        current_username = session.get('username')
        posts = [post.to_dict(current_username) for post in pagination.items]
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
            try:
                image_url = process_and_save_image(file, prefix="post")
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        try:
            new_post = Post(
                author_username=session['username'],
                author_nickname=session['nickname'],
                title=title,
                content=content,
                image_url=image_url
            )
            db.session.add(new_post)
            db.session.commit()
            return jsonify(new_post.to_dict(session['username'])), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"게시글 생성 오류: {e}")
            return jsonify({"error": "게시글 생성 중 오류가 발생했습니다."}), 500


@board_bp.route('/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_post(post_id):
    if request.method == 'GET':
        post = Post.query.options(joinedload(Post.comments), joinedload(Post.likes)).get(post_id)
        if post:
            current_username = session.get('username')
            return jsonify(post.to_dict(current_username))
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    current_user = session['username']
    if current_user != 'admin' and current_user != post.author_username:
        return jsonify({"error": "권한이 없습니다."}), 403

    if request.method == 'PUT':
        data = request.get_json()
        try:
            post.title = data.get('title', post.title)
            post.content = data.get('content', post.content)
            db.session.commit()
            return jsonify(post.to_dict(current_user))
        except Exception as e:
            db.session.rollback()
            logger.error(f"게시글 수정 오류: {e}")
            return jsonify({"error": "게시글 수정 중 오류가 발생했습니다."}), 500

    if request.method == 'DELETE':
        try:
            # 이미지 파일도 삭제
            if post.image_url:
                delete_image_file(post.image_url)

            db.session.delete(post)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            logger.error(f"게시글 삭제 오류: {e}")
            return jsonify({"error": "게시글 삭제 중 오류가 발생했습니다."}), 500


@board_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    data = request.get_json()
    if not data.get('content'):
        return jsonify({"error": "댓글 내용을 입력해주세요."}), 400

    try:
        new_comment = Comment(
            post_id=post_id,
            author_username=session['username'],
            author_nickname=session['nickname'],
            content=data['content']
        )
        db.session.add(new_comment)

        # 알림 생성 (자신의 글에 자신이 댓글 달면 알림 안 보냄)
        if post.author_username != session['username']:
            notification = Notification(
                username=post.author_username,
                message=f"{session['nickname']}님이 '{post.title}' 글에 댓글을 남겼습니다.",
                link=f"/post.html?id={post_id}"
            )
            db.session.add(notification)

        db.session.commit()
        return jsonify(new_comment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"댓글 생성 오류: {e}")
        return jsonify({"error": "댓글 작성 중 오류가 발생했습니다."}), 500


@board_bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    comment = Comment.query.get(comment_id)
    if not comment or comment.post_id != post_id:
        return jsonify({"error": "댓글을 찾을 수 없습니다."}), 404

    current_user = session['username']
    if current_user != 'admin' and current_user != comment.author_username:
        return jsonify({"error": "댓글을 삭제할 권한이 없습니다."}), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logger.error(f"댓글 삭제 오류: {e}")
        return jsonify({"error": "댓글 삭제 중 오류가 발생했습니다."}), 500


@board_bp.route('/posts/<int:post_id>/like', methods=['POST', 'DELETE'])
def handle_like(post_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    from models import Like
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    username = session['username']
    existing_like = Like.query.filter_by(post_id=post_id, username=username).first()

    try:
        if request.method == 'POST':
            if existing_like:
                return jsonify({"error": "이미 좋아요를 눌렀습니다."}), 409
            new_like = Like(post_id=post_id, username=username)
            db.session.add(new_like)

            # 좋아요 알림 (자기 글에 좋아요는 알림 X)
            if post.author_username != username:
                notification = Notification(
                    username=post.author_username,
                    message=f"{session['nickname']}님이 '{post.title}' 글에 좋아요를 눌렀습니다.",
                    link=f"/post.html?id={post_id}"
                )
                db.session.add(notification)

            db.session.commit()
            return jsonify({"liked": True, "like_count": len(post.likes)})

        if request.method == 'DELETE':
            if not existing_like:
                return jsonify({"error": "좋아요 기록이 없습니다."}), 404
            db.session.delete(existing_like)
            db.session.commit()
            return jsonify({"liked": False, "like_count": len(post.likes)})
    except Exception as e:
        db.session.rollback()
        logger.error(f"좋아요 처리 오류: {e}")
        return jsonify({"error": "좋아요 처리 중 오류가 발생했습니다."}), 500
