import re

def analyze_intent(message):
    # 1. 페이지 이동 의도 분석
    nav_patterns = {
        '/album.html': ['앨범', '사진'], '/board.html': ['게시판', '게시글 목록'],
        '/calendar.html': ['캘린더', '일정표'], '/profile.html': ['프로필', '내 정보']
    }
    for url, keywords in nav_patterns.items():
        for keyword in keywords:
            if f"{keyword} 페이지" in message or f"{keyword}으로" in message or f"{keyword} 보여줘" in message:
                return {'intent': 'navigate', 'entity': url, 'text': f'{keyword.capitalize()} 페이지로 이동할게요.'}
    
    # 2. 검색 의도 분석
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
            
    # 3. 인사 및 도움말
    if any(greet in message for greet in ['안녕', '하이', '헬로']): return {'intent': 'greet'}
    
    return {'intent': 'unknown'}
