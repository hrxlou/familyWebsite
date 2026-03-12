import logging
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Vote, VoteOption, VoteResponse

logger = logging.getLogger(__name__)
votes_bp = Blueprint('votes_bp', __name__)


@votes_bp.route('/votes', methods=['GET', 'POST'])
def handle_votes():
    if request.method == 'GET':
        votes = Vote.query.order_by(Vote.created_at.desc()).all()
        current_username = session.get('username')
        return jsonify([v.to_dict(current_username) for v in votes])

    if request.method == 'POST':
        if 'username' not in session:
            return jsonify({"error": "로그인이 필요합니다."}), 401

        data = request.get_json()
        title = data.get('title')
        options = data.get('options', [])

        if not title:
            return jsonify({"error": "투표 제목을 입력해주세요."}), 400
        if len(options) < 2:
            return jsonify({"error": "최소 2개의 선택지가 필요합니다."}), 400

        try:
            new_vote = Vote(
                author_username=session['username'],
                author_nickname=session['nickname'],
                title=title
            )
            db.session.add(new_vote)
            db.session.flush()  # ID 생성

            for opt_text in options:
                if opt_text.strip():
                    option = VoteOption(vote_id=new_vote.id, text=opt_text.strip())
                    db.session.add(option)

            db.session.commit()
            return jsonify(new_vote.to_dict(session['username'])), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"투표 생성 오류: {e}")
            return jsonify({"error": "투표 생성 중 오류가 발생했습니다."}), 500


@votes_bp.route('/votes/<int:vote_id>', methods=['GET', 'DELETE'])
def handle_vote(vote_id):
    vote = Vote.query.get(vote_id)
    if not vote:
        return jsonify({"error": "투표를 찾을 수 없습니다."}), 404

    if request.method == 'GET':
        current_username = session.get('username')
        return jsonify(vote.to_dict(current_username))

    if request.method == 'DELETE':
        if 'username' not in session:
            return jsonify({"error": "로그인이 필요합니다."}), 401
        current_user = session['username']
        if current_user != 'admin' and current_user != vote.author_username:
            return jsonify({"error": "투표를 삭제할 권한이 없습니다."}), 403
        try:
            db.session.delete(vote)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            logger.error(f"투표 삭제 오류: {e}")
            return jsonify({"error": "투표 삭제 중 오류가 발생했습니다."}), 500


@votes_bp.route('/votes/<int:vote_id>/respond', methods=['POST'])
def respond_to_vote(vote_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    vote = Vote.query.get(vote_id)
    if not vote:
        return jsonify({"error": "투표를 찾을 수 없습니다."}), 404
    if not vote.is_active:
        return jsonify({"error": "이미 종료된 투표입니다."}), 400

    data = request.get_json()
    option_id = data.get('option_id')
    if not option_id:
        return jsonify({"error": "선택지를 선택해주세요."}), 400

    option = VoteOption.query.get(option_id)
    if not option or option.vote_id != vote_id:
        return jsonify({"error": "유효하지 않은 선택지입니다."}), 400

    username = session['username']

    # 기존 투표가 있으면 변경 (하나만 선택 가능)
    try:
        existing = VoteResponse.query.join(VoteOption).filter(
            VoteOption.vote_id == vote_id,
            VoteResponse.username == username
        ).first()

        if existing:
            existing.option_id = option_id
        else:
            new_response = VoteResponse(option_id=option_id, username=username)
            db.session.add(new_response)

        db.session.commit()
        return jsonify(vote.to_dict(username))
    except Exception as e:
        db.session.rollback()
        logger.error(f"투표 참여 오류: {e}")
        return jsonify({"error": "투표 참여 중 오류가 발생했습니다."}), 500


@votes_bp.route('/votes/<int:vote_id>/close', methods=['PUT'])
def close_vote(vote_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    vote = Vote.query.get(vote_id)
    if not vote:
        return jsonify({"error": "투표를 찾을 수 없습니다."}), 404

    current_user = session['username']
    if current_user != 'admin' and current_user != vote.author_username:
        return jsonify({"error": "투표를 종료할 권한이 없습니다."}), 403

    try:
        vote.is_active = False
        db.session.commit()
        return jsonify(vote.to_dict(current_user))
    except Exception as e:
        db.session.rollback()
        logger.error(f"투표 종료 오류: {e}")
        return jsonify({"error": "투표 종료 중 오류가 발생했습니다."}), 500
