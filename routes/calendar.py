import logging
import datetime
import requests
from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Event, Anniversary
from korean_lunar_calendar import KoreanLunarCalendar

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

        # 1. Normal Events for this month (Solar)
        month_str = f"{year}-{str(month).zfill(2)}"
        db_events = Event.query.filter(Event.date.startswith(month_str), Event.repeat_type == 'none', Event.is_lunar == False).all()
        all_monthly_events.extend([e.to_dict() for e in db_events])

        # 2. Yearly repeating Solar events
        yearly_events = Event.query.filter_by(repeat_type='yearly', is_lunar=False).all()
        for e in yearly_events:
            try:
                event_date = datetime.datetime.strptime(e.date, '%Y-%m-%d')
                if event_date.month == month:
                    event_dict = e.to_dict()
                    event_dict['date'] = f"{year}-{str(month).zfill(2)}-{str(event_date.day).zfill(2)}"
                    all_monthly_events.append(event_dict)
            except: pass

        # 3. Lunar Events (Check if they fall into this Solar month)
        lunar_events = Event.query.filter_by(is_lunar=True).all()
        calendar = KoreanLunarCalendar()
        for e in lunar_events:
            try:
                orig_date = datetime.datetime.strptime(e.date, '%Y-%m-%d')
                check_years = [year] if e.repeat_type == 'yearly' else [orig_date.year]
                for check_year in check_years:
                    calendar.setLunarDate(check_year, orig_date.month, orig_date.day, False)
                    solar_iso = calendar.SolarIsoFormat()
                    solar_date = datetime.datetime.strptime(solar_iso, '%Y-%m-%d')
                    if solar_date.year == year and solar_date.month == month:
                        event_dict = e.to_dict()
                        event_dict['date'] = solar_iso
                        event_dict['lunar_info'] = f" (음 {orig_date.month}/{orig_date.day})"
                        all_monthly_events.append(event_dict)
            except: pass

        # Anniversaries (Legacy support)
        db_annivs = Anniversary.query.filter_by(month=month).all()
        for anniv in db_annivs:
            all_monthly_events.append({
                "id": f"a_{anniv.id}",
                "date": f"{year}-{str(anniv.month).zfill(2)}-{str(anniv.day).zfill(2)}",
                "title": anniv.title,
                "type": "anniversary",
                "category": "anniversary",
                "repeat_type": "yearly"
            })

        # Holidays
        holidays_data = get_holidays(year)
        for holiday in holidays_data:
            holiday_date = datetime.datetime.strptime(holiday['date'], '%Y-%m-%d')
            if holiday_date.month == month:
                all_monthly_events.append({
                    "id": f"h_{holiday_date.day}",
                    "date": holiday['date'],
                    "title": holiday['localName'],
                    "type": "holiday",
                    "category": "holiday",
                    "repeat_type": "none"
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
                type="event",
                category=data.get('category', 'others'),
                repeat_type=data.get('repeat_type', 'none'),
                is_lunar=data.get('is_lunar', False)
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

    # 1. Normal Events in the next 30 days
    events = Event.query.filter(
        Event.date >= today.strftime('%Y-%m-%d'),
        Event.date <= thirty_days_later.strftime('%Y-%m-%d'),
        Event.repeat_type == 'none'
    ).all()
    upcoming_items.extend([e.to_dict() for e in events])

    # 2. Yearly Repeating Solar Events in the next 30 days
    yearly_events = Event.query.filter_by(repeat_type='yearly', is_lunar=False).all()
    for e in yearly_events:
        try:
            event_orig_date = datetime.datetime.strptime(e.date, '%Y-%m-%d').date()
            # Try this year and next year
            for check_year in [today.year, today.year + 1]:
                try:
                    event_date = datetime.date(check_year, event_orig_date.month, event_orig_date.day)
                    if today <= event_date <= thirty_days_later:
                        item = e.to_dict()
                        item['date'] = event_date.strftime('%Y-%m-%d')
                        upcoming_items.append(item)
                except ValueError:
                    if event_orig_date.month == 2 and event_orig_date.day == 29:
                        event_date = datetime.date(check_year, 2, 28)
                        if today <= event_date <= thirty_days_later:
                            item = e.to_dict()
                            item['date'] = event_date.strftime('%Y-%m-%d')
                            upcoming_items.append(item)
        except: pass

    # 2.5 Yearly Repeating Lunar Events in the next 30 days
    yearly_lunar = Event.query.filter_by(repeat_type='yearly', is_lunar=True).all()
    calendar = KoreanLunarCalendar()
    for e in yearly_lunar:
        try:
            orig_date = datetime.datetime.strptime(e.date, '%Y-%m-%d').date()
            for check_year in [today.year, today.year + 1]:
                calendar.setLunarDate(check_year, orig_date.month, orig_date.day, False)
                solar_iso = calendar.SolarIsoFormat()
                solar_date = datetime.datetime.strptime(solar_iso, '%Y-%m-%d').date()
                if today <= solar_date <= thirty_days_later:
                    item = e.to_dict()
                    item['date'] = solar_iso
                    item['lunar_info'] = f" (음 {orig_date.month}/{orig_date.day})"
                    upcoming_items.append(item)
        except: pass

    # 3. Legacy Anniversaries in the next 30 days
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
                "type": "anniversary",
                "category": "anniversary"
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
                    "type": "anniversary",
                    "category": "anniversary"
                })

    # Sort by date
    upcoming_items.sort(key=lambda x: x['date'])

    return jsonify(upcoming_items[:5])
