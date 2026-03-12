from flask import Blueprint, request, jsonify
from services.chatbot_service import analyze_intent
from models import Event, Post

chatbot_bp = Blueprint('chatbot_bp', __name__)


@chatbot_bp.route('/chatbot', methods=['POST'])
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
            events = Event.query.filter(Event.title.like(f"%{search_term}%")).all()
            results = [e.to_dict() for e in events]
            if not results:
                return jsonify({'type': 'text', 'text': f"'{search_term}' 관련 일정을 찾지 못했어요."})
            return jsonify({'type': 'calendar_results', 'text': f"'{search_term}'에 대한 일정 검색 결과입니다.", 'results': results})
        else:
            # 통일된 검색 파라미터 사용 (q)
            posts = Post.query.filter(
                (Post.title.like(f"%{search_term}%")) |
                (Post.content.like(f"%{search_term}%"))
            ).all()
            results = [p.to_dict() for p in posts]
            if not results:
                return jsonify({'type': 'text', 'text': f"'{search_term}' 관련 게시글을 찾지 못했어요."})
            return jsonify({'type': 'search_results', 'text': f"'{search_term}'에 대한 검색 결과입니다.", 'results': results})

    elif intent['intent'] == 'greet':
        return jsonify({'type': 'text', 'text': '안녕하세요! 무엇을 도와드릴까요? (기능이 궁금하시면 !help 를 입력해보세요)'})
    else:
        return jsonify({'type': 'text', 'text': '죄송합니다, 잘 이해하지 못했어요. 도움이 필요하시면 !help 를 입력해주세요.'})
