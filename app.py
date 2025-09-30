import os
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import datetime
import re
import requests
from PIL import Image

# --- Flask 앱 설정 ---
app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = 'this-is-a-super-secret-key-for-our-family'
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

# --- 폴더 및 상수 설정 ---
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
POSTS_PER_PAGE = 5

# --- 데이터 저장소 (기존과 동일) ---
users = {}
with app.app_context():
    admin_password_hash = bcrypt.generate_password_hash('Tempest1570!').decode('utf-8')
    users['admin'] = {
        "password_hash": admin_password_hash,
        "nickname": "관리자",
        "introduction": "우리 가족 앨범 사이트의 관리자입니다.",
        "avatar_url": None
    }
comment_id_counter = 100
posts = [
    {"id": 6, "author_username": "dad", "author_nickname": "아빠", "title": "다음 주 가족 외식 장소 투표!", "content": "다음 주 토요일에 다 같이 저녁 먹자. 1. 한정식 2. 중식 3. 이탈리안 중에 댓글로 투표해줘!", "image_url": None, "comments": []},
    {"id": 5, "author_username": "mom", "author_nickname": "엄마", "title": "여름휴가 사진 앨범에 올렸어요", "content": "이번에 다녀온 강릉 여행 사진들 앨범에 업데이트 했으니 다들 구경하세요~", "image_url": "/uploads/post_5_summer_vacation.jpg", "comments": []},
    {"id": 4, "author_username": "son", "author_nickname": "아들", "title": "주말에 PC방 갈 사람?", "content": "시험도 끝났는데 주말에 같이 게임할 사람 구합니다. 댓글 ㄱㄱ", "image_url": None, "comments": []},
    {"id": 3, "author_username": "daughter", "author_nickname": "딸", "title": "제 생일 선물로 받고 싶은 것(필독)", "content": "곧 제 생일인 거 아시죠? 갖고 싶은 거 목록 적어두고 갑니다. 1. 최신형 아이패드 2. 용돈 3. 강아지", "image_url": None, "comments": []},
    {"id": 2, "author_username": "mom", "author_nickname": "엄마", "title": "오늘 저녁 장보기 목록", "content": "혹시 더 필요한 거 있으면 저녁 6시까지 댓글로 알려주세요. (우유, 계란, 파, 양파 살 예정)", "image_url": None, "comments": []},
    {"id": 1, "author_username": "dad", "author_nickname": "아빠", "title": "주말에 공원 나들이 어때?", "content": "날씨도 좋은데, 이번 주말에 다 같이 서울숲 공원이라도 갈까요? 도시락 싸서 가면 좋을 것 같아요.", "image_url": None, "comments": [
        {"id": 2, "author_username": "mom", "author_nickname": "엄마", "content": "좋아요! 제가 도시락 준비할게요!"}
    ]}
]
post_id_counter = 7
photos = []
photo_id_counter = 1
events = [
    {"id": 1, "date": "2025-08-15", "title": "가족 여름휴가 🏖️", "type": "event"},
    {"id": 2, "date": "2025-08-16", "title": "가족 여름휴가 🏖️", "type": "event"}
]
anniversaries = [
    {"id": 1, "month": 6, "day": 13, "title": "내 생일 🎂", "type": "anniversary"},
    {"id": 2, "month": 8, "day": 28, "title": "할머니 생신", "type": "anniversary"}
]
event_id_counter = 3
anniversary_id_counter = 3

# --- API 및 경로 (기존과 동일한 부분 생략) ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def analyze_intent(message):
    nav_patterns = {
        '/album.html': ['앨범', '사진'], '/board.html': ['게시판', '게시글 목록'],
        '/calendar.html': ['캘린더', '일정표'], '/profile.html': ['프로필', '내 정보']
    }
    for url, keywords in nav_patterns.items():
        for keyword in keywords:
            if f"{keyword} 페이지" in message or f"{keyword}으로" in message or f"{keyword} 보여줘" in message:
                return {'intent': 'navigate', 'entity': url, 'text': f'{keyword.capitalize()} 페이지로 이동할게요.'}
    search_patterns = {'post': ['게시글', '게시물', '글'], 'event': ['일정']}
    search_triggers = ['찾아줘', '검색', '알려줘', '뭐 있어']
    for context, keywords in search_patterns.items():
        for keyword in keywords:
            for trigger in search_triggers:
                match = re.search(f"(.+)?{keyword}\\s*{trigger}", message)
                if match:
                    search_term = match.group(1).strip() if match.group(1) else None
                    return {'intent': 'search', 'context': context, 'term': search_term}
    for trigger in search_triggers:
        if trigger in message:
            search_term = message.split(trigger)[0].strip()
            return {'intent': 'search', 'context': 'post', 'term': search_term}
    if any(greet in message for greet in ['안녕', '하이', '헬로']): return {'intent': 'greet'}
    return {'intent': 'unknown'}

@app.route('/api/chatbot', methods=['POST'])
def handle_chatbot():
    data = request.get_json()
    message = data.get('message', '').lower().strip()
    context = data.get('context', 'default')
    if message == '!help':
        intent = {'intent': 'help'}
    elif context.startswith('awaiting_keyword_'):
        search_type = context.split('_')[-1]
        intent = {'intent': 'search', 'context': search_type, 'term': message}
    else:
        intent = analyze_intent(message)
    if intent['intent'] == 'help':
        help_text = "안녕하세요! 저는 가족 앨범 챗봇입니다.\n\n- **페이지 이동**: \"앨범 페이지 보여줘\"\n- **게시글 검색**: \"외식 찾아줘\" 또는 \"게시글 검색\"\n- **일정 검색**: \"건강검진 일정 알려줘\""
        return jsonify({'type': 'text', 'text': help_text})
    elif intent['intent'] == 'navigate':
        return jsonify({'type': 'link', 'text': intent['text'], 'url': intent['entity']})
    elif intent['intent'] == 'search':
        search_term, search_context = intent.get('term'), intent.get('context')
        if not search_term:
            return jsonify({'type': 'ask_keyword', 'context': f'awaiting_keyword_{search_context}', 'text': f'어떤 {search_context}을(를) 찾아드릴까요?'})
        if search_context == 'event':
            results = [event for event in events if search_term in event['title'].lower()]
            if not results: return jsonify({'type': 'text', 'text': f"'{search_term}' 관련 일정을 찾지 못했어요."})
            return jsonify({'type': 'calendar_results', 'text': f"'{search_term}'에 대한 일정 검색 결과입니다.", 'results': results})
        else:
            results = [post for post in posts if search_term in post['title'].lower() or search_term in post['content'].lower()]
            if not results: return jsonify({'type': 'text', 'text': f"'{search_term}' 관련 게시글을 찾지 못했어요."})
            return jsonify({'type': 'search_results', 'text': f"'{search_term}'에 대한 검색 결과입니다.", 'results': results})
    elif intent['intent'] == 'greet':
        return jsonify({'type': 'text', 'text': '안녕하세요! 무엇을 도와드릴까요? (기능이 궁금하시면 !help 를 입력해보세요)'})
    else:
        return jsonify({'type': 'text', 'text': '죄송합니다, 잘 이해하지 못했어요. 도움이 필요하시면 !help 를 입력해주세요.'})

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username, password, nickname = data.get('username'), data.get('password'), data.get('nickname')
    if not all([username, password, nickname]): return jsonify({"error": "모든 필드를 입력해주세요."}), 400
    if username in users: return jsonify({"error": "이미 존재하는 아이디입니다."}), 409
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    users[username] = {"password_hash": password_hash, "nickname": nickname, "introduction": f"{nickname}입니다. 잘 부탁드려요!", "avatar_url": None}
    return jsonify({"success": "회원가입이 완료되었습니다."}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username, password = data.get('username'), data.get('password')
    user = users.get(username)
    if user and bcrypt.check_password_hash(user['password_hash'], password):
        session['username'], session['nickname'] = username, user['nickname']
        return jsonify({"nickname": user['nickname']})
    return jsonify({"error": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": "로그아웃 되었습니다."})

@app.route('/api/check_session', methods=['GET'])
def check_session():
    if 'username' in session:
        return jsonify({"is_logged_in": True, "nickname": session['nickname'], "username": session['username']})
    return jsonify({"is_logged_in": False}), 401

@app.route('/api/users/<username>', methods=['GET'])
def get_user_profile(username):
    user = users.get(username)
    if user:
        return jsonify({"username": username, "nickname": user['nickname'], "introduction": user.get('introduction', ''), "avatar_url": user.get('avatar_url')})
    return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    username = session['username']
    user = users.get(username)
    if not user: return jsonify({"error": "사용자 정보를 찾을 수 없습니다."}), 404
    user['nickname'] = request.form.get('nickname', user['nickname'])
    user['introduction'] = request.form.get('introduction', user['introduction'])
    session['nickname'] = user['nickname']
    avatar_choice = request.form.get('avatar_choice')
    if avatar_choice == 'default':
        user['avatar_url'] = None
    elif avatar_choice == 'upload' and 'avatar_file' in request.files:
        file = request.files['avatar_file']
        if file and file.filename != '':
            if user.get('avatar_url'):
                old_filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(user['avatar_url']))
                if os.path.exists(old_filepath): os.remove(old_filepath)
            filename = secure_filename(f"avatar_{username}_{file.filename}")
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            user['avatar_url'] = f"/uploads/{filename}"
    return jsonify({"success": "프로필이 성공적으로 업데이트되었습니다.", "updated_user": {"username": username, "nickname": user['nickname'], "introduction": user['introduction'], "avatar_url": user['avatar_url']}})

@app.route('/api/find_id', methods=['POST'])
def find_id():
    data = request.get_json()
    nickname = data.get('nickname')
    if not nickname: return jsonify({"error": "닉네임을 입력해주세요."}), 400
    found_usernames = [username for username, user_data in users.items() if user_data['nickname'] == nickname]
    if not found_usernames: return jsonify({"error": "해당 닉네임으로 가입된 아이디가 없습니다."}), 404
    return jsonify({"usernames": found_usernames})

@app.route('/api/verify_user', methods=['POST'])
def verify_user():
    data = request.get_json()
    username, nickname = data.get('username'), data.get('nickname')
    if not all([username, nickname]): return jsonify({"error": "아이디와 닉네임을 모두 입력해주세요."}), 400
    user = users.get(username)
    if not user or user['nickname'] != nickname: return jsonify({"error": "입력하신 아이디 또는 닉네임이 올바르지 않습니다."}), 404
    return jsonify({"success": "인증에 성공했습니다."})

@app.route('/api/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    username, nickname, new_password = data.get('username'), data.get('nickname'), data.get('new_password')
    if not all([username, nickname, new_password]): return jsonify({"error": "모든 필드를 입력해주세요."}), 400
    user = users.get(username)
    if not user or user['nickname'] != nickname: return jsonify({"error": "입력하신 아이디 또는 닉네임이 올바르지 않습니다."}), 404
    new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    users[username]['password_hash'] = new_password_hash
    return jsonify({"success": "비밀번호가 성공적으로 변경되었습니다. 다시 로그인해주세요."})

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def handle_comments(post_id):
    global comment_id_counter
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post: return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404
    data = request.get_json()
    new_comment = {"id": comment_id_counter, "author_username": session['username'], "author_nickname": session['nickname'], "content": data['content']}
    post['comments'].append(new_comment)
    comment_id_counter += 1
    return jsonify(new_comment), 201

@app.route('/api/events', methods=['GET', 'POST'])
def handle_events():
    global event_id_counter
    if request.method == 'GET':
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        if not year or not month: return jsonify({"error": "연도와 월 정보가 필요합니다."}), 400
        all_monthly_events = []
        all_monthly_events.extend([e for e in events if datetime.datetime.strptime(e['date'], '%Y-%m-%d').year == year and datetime.datetime.strptime(e['date'], '%Y-%m-%d').month == month])
        for anniv in anniversaries:
            if anniv['month'] == month:
                all_monthly_events.append({"id": f"a_{anniv['id']}", "date": f"{year}-{str(anniv['month']).zfill(2)}-{str(anniv['day']).zfill(2)}", "title": anniv['title'], "type": "anniversary"})
        try:
            response = requests.get(f"https://date.nager.at/api/v3/PublicHolidays/{year}/KR")
            if response.status_code == 200:
                for holiday in response.json():
                    holiday_date = datetime.datetime.strptime(holiday['date'], '%Y-%m-%d')
                    if holiday_date.month == month:
                        all_monthly_events.append({"id": f"h_{holiday_date.day}", "date": holiday['date'], "title": holiday['localName'], "type": "holiday"})
        except Exception as e:
            print(f"공휴일 API 호출 오류: {e}")
        return jsonify(all_monthly_events)
    if request.method == 'POST':
        if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
        data = request.get_json()
        new_event = {"id": event_id_counter, "date": data['date'], "title": data['title'], "type": "event"}
        events.append(new_event)
        event_id_counter += 1
        return jsonify(new_event), 201

@app.route('/api/anniversaries', methods=['POST'])
def add_anniversary():
    global anniversary_id_counter
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    data = request.get_json()
    new_anniv = {"id": anniversary_id_counter, "month": data['month'], "day": data['day'], "title": data['title'], "type": "anniversary"}
    anniversaries.append(new_anniv)
    anniversary_id_counter += 1
    return jsonify(new_anniv), 201

@app.route('/api/anniversaries/<int:anniv_id>', methods=['PUT', 'DELETE'])
def handle_anniversary(anniv_id):
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    anniv = next((a for a in anniversaries if a['id'] == anniv_id), None)
    if not anniv: return jsonify({"error": "기념일을 찾을 수 없습니다."}), 404
    if request.method == 'PUT':
        data = request.get_json()
        anniv['title'] = data.get('title', anniv['title'])
        return jsonify(anniv)
    if request.method == 'DELETE':
        anniversaries.remove(anniv)
        return '', 204

@app.route('/api/events/<int:event_id>', methods=['PUT', 'DELETE'])
def handle_event(event_id):
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    event = next((e for e in events if e['id'] == event_id), None)
    if not event: return jsonify({"error": "일정을 찾을 수 없습니다."}), 404
    if request.method == 'PUT':
        data = request.get_json()
        event['title'] = data.get('title', event['title'])
        return jsonify(event)
    if request.method == 'DELETE':
        events.remove(event)
        return '', 204

@app.route('/api/posts', methods=['GET', 'POST'])
def handle_posts():
    global post_id_counter
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        sorted_posts = sorted(posts, key=lambda p: p['id'], reverse=True)
        total_posts, total_pages = len(sorted_posts), (len(sorted_posts) + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
        start_index = (page - 1) * POSTS_PER_PAGE
        end_index = start_index + POSTS_PER_PAGE
        paginated_posts = sorted_posts[start_index:end_index]
        return jsonify({'posts': paginated_posts, 'page': page, 'total_pages': total_pages, 'has_prev': page > 1, 'has_next': page < total_pages})
    
    if request.method == 'POST':
        if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
        if 'title' not in request.form or 'content' not in request.form: return jsonify({"error": "제목과 내용을 모두 입력해주세요."}), 400
        title, content, image_url = request.form['title'], request.form['content'], None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                try:
                    original_filename, _ = os.path.splitext(file.filename)
                    filename = secure_filename(f"post_{post_id_counter}_{original_filename}.jpg")
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    image = Image.open(file.stream)
                    if image.mode in ("RGBA", "P"): image = image.convert("RGB")
                    image.thumbnail((1920, 1920))
                    image.save(filepath, 'JPEG', quality=85)
                    image_url = f"/uploads/{filename}"
                except Exception as e:
                    print(f"이미지 처리 오류: {e}")
                    return jsonify({"error": "이미지 처리 중 오류가 발생했습니다."}), 500
        new_post = {"id": post_id_counter, "author_username": session['username'], "author_nickname": session['nickname'], "title": title, "content": content, "image_url": image_url, "comments": []}
        posts.insert(0, new_post)
        post_id_counter += 1
        return jsonify(new_post), 201

# ★★★★★ [수정/추가] 게시글 수정 및 삭제 경로 ★★★★★
@app.route('/api/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_post(post_id):
    post = next((p for p in posts if p['id'] == post_id), None)
    if not post:
        return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

    # --- GET: 게시글 상세 정보 보기 ---
    if request.method == 'GET':
        return jsonify(post)

    # --- 로그인 및 권한 확인 (PUT, DELETE 공통) ---
    if 'username' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    
    current_user = session['username']
    if current_user != post['author_username'] and current_user != 'admin':
        return jsonify({"error": "이 게시글을 수정하거나 삭제할 권한이 없습니다."}), 403

    # --- PUT: 게시글 수정 ---
    if request.method == 'PUT':
        post['title'] = request.form.get('title', post['title'])
        post['content'] = request.form.get('content', post['content'])
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                # 기존 이미지 파일 삭제
                if post.get('image_url'):
                    old_filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(post['image_url']))
                    if os.path.exists(old_filepath):
                        os.remove(old_filepath)
                
                # 새 이미지 압축 저장
                try:
                    original_filename, _ = os.path.splitext(file.filename)
                    filename = secure_filename(f"post_{post_id}_{original_filename}.jpg")
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    image = Image.open(file.stream)
                    if image.mode in ("RGBA", "P"): image = image.convert("RGB")
                    image.thumbnail((1920, 1920))
                    image.save(filepath, 'JPEG', quality=85)
                    post['image_url'] = f"/uploads/{filename}"
                except Exception as e:
                    print(f"이미지 처리 오류: {e}")
                    return jsonify({"error": "이미지 처리 중 오류가 발생했습니다."}), 500
        
        return jsonify(post)

    # --- DELETE: 게시글 삭제 ---
    if request.method == 'DELETE':
        # 첨부 이미지 파일 삭제
        if post.get('image_url'):
            filepath = os.path.join(UPLOAD_FOLDER, os.path.basename(post['image_url']))
            if os.path.exists(filepath):
                os.remove(filepath)
        
        posts.remove(post)
        return jsonify({"success": "게시글이 삭제되었습니다."}), 200

# ★★★★★ [수정/추가 끝] ★★★★★

@app.route('/api/photos', methods=['GET', 'POST'])
def handle_photos():
    global photo_id_counter
    if request.method == 'GET':
        return jsonify(photos)
    if request.method == 'POST':
        if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
        if 'file' not in request.files: return jsonify({"error": "파일이 없습니다."}), 400
        file = request.files['file']
        if file.filename == '': return jsonify({"error": "선택된 파일이 없습니다."}), 400
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            new_photo = {"id": photo_id_counter, "filename": filename, "url": f"/uploads/{filename}", "uploader_username": session['username'], "uploader_nickname": session['nickname']}
            photos.append(new_photo)
            photo_id_counter += 1
            return jsonify(new_photo), 201

@app.route('/api/photos/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    if 'username' not in session: return jsonify({"error": "로그인이 필요합니다."}), 401
    photo_to_delete = next((p for p in photos if p['id'] == photo_id), None)
    if not photo_to_delete: return jsonify({"error": "사진을 찾을 수 없습니다."}), 404
    current_user = session['username']
    if current_user != 'admin' and current_user != photo_to_delete.get('uploader_username'):
        return jsonify({"error": "사진을 삭제할 권한이 없습니다."}), 403
    try:
        filepath = os.path.join(UPLOAD_FOLDER, photo_to_delete['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
        photos.remove(photo_to_delete)
        return '', 204
    except Exception as e:
        return jsonify({"error": "파일 삭제 중 오류가 발생했습니다."}), 500

# --- 일반 파일 제공 라우트 ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# --- 서버 실행 ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
