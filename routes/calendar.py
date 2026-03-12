from flask import Blueprint, request, jsonify, session
from extensions import db
from models import Event, Anniversary
import datetime
import requests

calendar_bp = Blueprint('calendar_bp', __name__)

@calendar_bp.route('/api/events', methods=['GET', 'POST'])
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
            
        # Holidays
        try:
            response = requests.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/KR")
            if response.status_code == 200:
                holidays_data = response.json()
                for holiday in holidays_data:
                    holiday_date = datetime.datetime.strptime(holiday['date'], '%Y-%m-%d')
                    if holiday_date.month == month:
                        all_monthly_events.append({
                            "id": f"h_{holiday_date.day}", 
                            "date": holiday['date'], 
                            "title": holiday['localName'], 
                            "type": "holiday"
                        })
        except Exception as e:
            print(f"공휴일 API 호출 오류: {e}")
            
        return jsonify(all_monthly_events)
        
    if request.method == 'POST':
        if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
        data = request.get_json()
        new_event = Event(
            date=data['date'],
            title=data['title'],
            type="event"
        )
        db.session.add(new_event)
        db.session.commit()
        return jsonify(new_event.to_dict()), 201

@calendar_bp.route('/api/anniversaries', methods=['POST'])
def add_anniversary():
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    data = request.get_json()
    new_anniv = Anniversary(
        month=data['month'],
        day=data['day'],
        title=data['title'],
        type="anniversary"
    )
    db.session.add(new_anniv)
    db.session.commit()
    return jsonify(new_anniv.to_dict()), 201

@calendar_bp.route('/api/anniversaries/<int:anniv_id>', methods=['PUT', 'DELETE'])
def handle_anniversary(anniv_id):
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    anniv = Anniversary.query.get(anniv_id)
    if not anniv: return jsonify({"error": "기념일을 찾을 수 없습니다."}), 404
    
    if request.method == 'PUT':
        data = request.get_json()
        anniv.title = data.get('title', anniv.title)
        db.session.commit()
        return jsonify(anniv.to_dict())
        
    if request.method == 'DELETE':
        db.session.delete(anniv)
        db.session.commit()
        return '', 204

@calendar_bp.route('/api/events/<int:event_id>', methods=['PUT', 'DELETE'])
def handle_event(event_id):
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    event = Event.query.get(event_id)
    if not event: return jsonify({"error": "일정을 찾을 수 없습니다."}), 404
    
    if request.method == 'PUT':
        data = request.get_json()
        event.title = data.get('title', event.title)
        db.session.commit()
        return jsonify(event.to_dict())
        
    if request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return '', 204
