import logging
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Notification

logger = logging.getLogger(__name__)
notifications_bp = Blueprint('notifications_bp', __name__)


@notifications_bp.route('/notifications', methods=['GET'])
def get_notifications():
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    username = session['username']
    notifications = Notification.query.filter_by(username=username) \
        .order_by(Notification.created_at.desc()).limit(20).all()

    unread_count = Notification.query.filter_by(username=username, is_read=False).count()

    return jsonify({
        "notifications": [n.to_dict() for n in notifications],
        "unread_count": unread_count
    })


@notifications_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
def mark_as_read(notif_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    notification = Notification.query.get(notif_id)
    if not notification or notification.username != session['username']:
        return jsonify({"error": "알림을 찾을 수 없습니다."}), 404

    try:
        notification.is_read = True
        db.session.commit()
        return jsonify(notification.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"알림 읽음 처리 오류: {e}")
        return jsonify({"error": "알림 처리 중 오류가 발생했습니다."}), 500


@notifications_bp.route('/notifications/read-all', methods=['PUT'])
def mark_all_read():
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401

    try:
        Notification.query.filter_by(
            username=session['username'], is_read=False
        ).update({'is_read': True})
        db.session.commit()
        return jsonify({"success": "모든 알림을 읽음 처리했습니다."})
    except Exception as e:
        db.session.rollback()
        logger.error(f"알림 전체 읽음 처리 오류: {e}")
        return jsonify({"error": "알림 처리 중 오류가 발생했습니다."}), 500
