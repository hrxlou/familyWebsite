import logging
import datetime
import requests
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Event, Anniversary

logger = logging.getLogger(__name__)
calendar_bp = Blueprint('calendar_bp', __name__)

# 공휴일 인메모리 캐시
_holiday_cache = {}


def get_holidays(year):
    """공휴일 데이터를 캐싱하여 반환"""
    if year in _holiday_cache:
        return _holiday_cache[year]
    try:
        response = requests.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/KR", timeout=5)
        if response.status_code == 200:
            _holiday_cache[year] = response.json()
            return _holiday_cache[year]
    except Exception as e:
        logger.error(f"공휴일 API 호출 오류: {e}")
    return []


@calendar_bp.route('/events', methods=['GET', 'POST'])
def handle_events():
    if request.method == 'GET':
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        if not year or not month:
            return jsonify({"error": "연도와 월 정보가 필요합니다."}), 400

        all_monthly_events = []

        # Events (DB에서 LIKE로 해당 월 검색)
        month_str = f"{year}-{str(month).zfill(2)}"
        db_events = Event.query.filter(Event.date.startswith(month_str)).all()
        all_monthly_events.extend([e.to_dict() for e in db_events])

        # Anniversaries (DB에서 특정 월의 기념일 검색)
        db_annivs = Anniversary.query.filter_by(month=month).all()
        for anniv in db_annivs:
            all_monthly_events.append({
                "id": f"a_{anniv.id}",
                "date": f"{year}-{str(anniv.month).zfill(2)}-{str(anniv.day).zfill(2)}",
                "title": anniv.title,
                "type": "anniversary"
            })

        # Holidays (캐시 활용)
        holidays_data = get_holidays(year)
        for holiday in holidays_data:
            holiday_date = datetime.datetime.strptime(holiday['date'], '%Y-%m-%d')
            if holiday_date.month == month:
                all_monthly_events.append({
                    "id": f"h_{holiday_date.day}",
                    "date": holiday['date'],
                    "title": holiday['localName'],
                    "type": "holiday"
                })

        return jsonify(all_monthly_events)

    if request.method == 'POST':
        if 'username' not in session:
            return jsonify({"error": "로그인이 필요합니다."}), 401
        data = request.get_json()
        try:
            new_event = Event(
                date=data['date'],
                title=data['title'],
                type="event"
            )
            db.session.add(new_event)
            db.session.commit()
            return jsonify(new_event.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            logger.error(f"일정 생성 오류: {e}")
            return jsonify({"error": "일정 생성 중 오류가 발생했습니다."}), 500


@calendar_bp.route('/anniversaries', methods=['POST'])
def add_anniversary():
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    data = request.get_json()
    try:
        new_anniv = Anniversary(
            month=data['month'],
            day=data['day'],
            title=data['title'],
            type="anniversary"
        )
        db.session.add(new_anniv)
        db.session.commit()
        return jsonify(new_anniv.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"기념일 생성 오류: {e}")
        return jsonify({"error": "기념일 생성 중 오류가 발생했습니다."}), 500


@calendar_bp.route('/anniversaries/<int:anniv_id>', methods=['PUT', 'DELETE'])
def handle_anniversary(anniv_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    anniv = Anniversary.query.get(anniv_id)
    if not anniv:
        return jsonify({"error": "기념일을 찾을 수 없습니다."}), 404

    try:
        if request.method == 'PUT':
            data = request.get_json()
            anniv.title = data.get('title', anniv.title)
            db.session.commit()
            return jsonify(anniv.to_dict())

        if request.method == 'DELETE':
            db.session.delete(anniv)
            db.session.commit()
            return '', 204
    except Exception as e:
        db.session.rollback()
        logger.error(f"기념일 처리 오류: {e}")
        return jsonify({"error": "기념일 처리 중 오류가 발생했습니다."}), 500


@calendar_bp.route('/events/<int:event_id>', methods=['PUT', 'DELETE'])
def handle_event(event_id):
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "일정을 찾을 수 없습니다."}), 404

    try:
        if request.method == 'PUT':
            data = request.get_json()
            event.title = data.get('title', event.title)
            db.session.commit()
            return jsonify(event.to_dict())

        if request.method == 'DELETE':
            db.session.delete(event)
            db.session.commit()
            return '', 204
    except Exception as e:
        db.session.rollback()
        logger.error(f"일정 처리 오류: {e}")
        return jsonify({"error": "일정 처리 중 오류가 발생했습니다."}), 500


@calendar_bp.route('/upcoming', methods=['GET'])
def get_upcoming():
    today = datetime.date.today()
    thirty_days_later = today + datetime.timedelta(days=30)

    upcoming_items = []

    # 1. Events in the next 30 days
    events = Event.query.filter(
        Event.date >= today.strftime('%Y-%m-%d'),
        Event.date <= thirty_days_later.strftime('%Y-%m-%d')
    ).all()
    upcoming_items.extend([e.to_dict() for e in events])

    # 2. Anniversaries in the next 30 days
    all_annivs = Anniversary.query.all()
    for anniv in all_annivs:
        try:
            anniv_this_year = datetime.date(today.year, anniv.month, anniv.day)
        except ValueError:
            if anniv.month == 2 and anniv.day == 29:
                anniv_this_year = datetime.date(today.year, 2, 28)
            else:
                continue

        if today <= anniv_this_year <= thirty_days_later:
            upcoming_items.append({
                "id": f"a_{anniv.id}",
                "date": anniv_this_year.strftime('%Y-%m-%d'),
                "title": anniv.title,
                "type": "anniversary"
            })
        else:
            try:
                anniv_next_year = datetime.date(today.year + 1, anniv.month, anniv.day)
            except ValueError:
                if anniv.month == 2 and anniv.day == 29:
                    anniv_next_year = datetime.date(today.year + 1, 2, 28)
                else:
                    continue

            if today <= anniv_next_year <= thirty_days_later:
                upcoming_items.append({
                    "id": f"a_{anniv.id}",
                    "date": anniv_next_year.strftime('%Y-%m-%d'),
                    "title": anniv.title,
                    "type": "anniversary"
                })

    # Sort by date
    upcoming_items.sort(key=lambda x: x['date'])

    return jsonify(upcoming_items[:5])
