document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.chatbot-toggler')) return;

    const chatbotHTML = `
        <button class="chatbot-toggler">💬</button>
        <div class="chatbot-window" style="display: none;">
            <div class="chat-header">
                <span>가족 가이드 챗봇 🤖</span>
                <button class="chat-close-btn">&times;</button>
            </div>
            <div class="chat-messages"></div>
            <form class="chat-input-form">
                <input type="text" placeholder="메시지를 입력해 보세요 (팁: '기능', '인사', '생일')">
                <button type="submit">➤</button>
            </form>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);

    const toggler = document.querySelector('.chatbot-toggler');
    const chatWindow = document.querySelector('.chatbot-window');
    const closeBtn = document.querySelector('.chat-close-btn');
    const messagesContainer = document.querySelector('.chat-messages');
    const inputForm = document.querySelector('.chat-input-form');
    const inputField = inputForm.querySelector('input');
    const CHAT_HISTORY_KEY = 'family_chatbot_history_v6';

    // --- 챗봇 규칙 엔진 데이터베이스 (V6: 초대형 확장 버전) ---
    const chatbotRules = [
        // 1. 인사 및 사교 (Greetings)
        { keywords: ['안녕', '하이', '반가워', 'ㅎㅇ', '조은아침', '좋은아침', '굿모닝'], responses: ['안녕하세요! 즐거운 하루 보내고 계신가요? 😊', '반가워요! 우리 가족 웹사이트 가이드입니다. 무엇을 도와드릴까요?', '안녕! 오늘도 가족들과 행복한 시간 되세요!', '좋은 아침이에요! 상쾌한 시작 하시길 바랄게요.'] },
        { keywords: ['잘자', '굿나잇', '잘 자', '굿밤'], responses: ['안녕히 주무세요! 내일도 행복한 소식으로 만나요 🌙', '좋은 꿈 꾸세요! 가족들 모두 편안한 밤 되시길.', '굿나잇! 불 끄고 푹 쉬세요.'] },
        { keywords: ['이름이', '누구니', '정체', '넌누구'], responses: ['저는 우리 가족 웹사이트의 마스코트이자 가이드인 "패밀리 봇"입니다! 🤖', '가족들의 행복한 소통을 돕는 인공지능 도우미예요.'] },

        // 2. 가이드 및 기능 설명 (Feature Guides)
        { keywords: ['기능', '뭐할수있어', '메뉴', '안내', '방법', '도움', '가이드', '사용법', '!help'], responses: [`우리 가족 웹사이트는 다음과 같은 기능을 제공해요! 🚀
\n1. 가족 게시판 📝
- 소소한 일상 기록 및 사진 첨부
- 게시글에 댓글 남기기
- 제목이나 내용으로 게시글 검색
\n2. 가족 앨범 📸
- 가족과의 추억 사진 모아보기
- 라이트박스(크게 보기) 감상
\n3. 가족 캘린더 📅
- 중요한 행사/생일 관리
- 연도/월 클릭하여 날짜 점프 가능
- 일회성/매년 반복 일정 구분 등록
\n4. 기타 서비스 🌙
- 다크 모드 (밤눈 편안!)
- 지능형 챗봇 가이드 (지금 대화 중!)`] },
        { keywords: ['게시판', '글쓰기', '게시물', '글쓰는법'], responses: ['가족 게시판 메뉴에서 [글쓰기] 버튼을 누르면 일상을 남길 수 있어요.\n제목과 내용을 입력하고 사진도 첨부해 보세요!'] },
        { keywords: ['댓글', '반응'], responses: ['게시글 하단에 댓글을 달아 가족들과 소통할 수 있어요. 따뜻한 댓글 한마디가 큰 힘이 됩니다 ❤️'] },
        { keywords: ['앨범', '사진', '이미지', '업로드', '갤러리'], responses: ['가족 앨범에서는 사진을 올리고 한눈에 모아볼 수 있어요. 업로드된 사진을 클릭하면 크게 감상할 수 있는 라이트박스 기능도 있답니다!'] },
        { keywords: ['캘린더', '일정', '기념일', '생일', '약속'], responses: ['가족 캘린더에서 중요한 약속이나 생일을 관리하세요.\n매년 반복 옵션을 쓰면 생일 같은 일정도 잊지 않게 도와드려요!'] },
        { keywords: ['점프', '날짜이동', '년도선택', '미래'], responses: ['캘린더 페이지 상단의 "년/월"을 클릭해 보세요! 원하는 날짜로 즉시 점프할 수 있는 선택창이 나온답니다 📅'] },

        // 3. 요리 및 식사 (Cooking & Meal)
        { keywords: ['식사', '메뉴', '점심', '저녁', '뭐먹지', '밥추천'], responses: ['오늘은 따뜻한 김치찌개 어때요?', '치킨이나 피자로 가족 파티를 즐겨보시는 것도 좋겠네요 🍕', '건강하게 비빔밥이나 쌈밥은 어떠신가요?', '날씨도 좋은데 외식 어때요? 아빠께 여쭤봐요!', '간단하게 라면이나 샌드위치는 어떠세요?'] },
        { keywords: ['레시피', '요리법', '만드는법'], responses: ['유튜브나 네이버 블로그에서 "백종원 레시피"를 검색해 보세요! 실패 없는 맛을 보장합니다.', '정성이 가득 들어간 요리는 무엇이든 맛있을 거예요!'] },
        { keywords: ['배달', '야식', '치킨', '피자', '족발'], responses: ['배달 앱을 열어볼 때가 됐군요! 오늘은 치킨 어떠세요? 🍗', '피자 한 판 시켜서 가족들과 도란도란 나눠 드세요.'] },

        // 4. 감성 및 유머 (Emotional & Humor)
        { keywords: ['사랑해', '조아해', '좋아해', '러브'], responses: ['저도 우리 가족을 무지무지 사랑해요! ❤️ 우리 가족 화이팅!', '사랑은 표현할 때 더 커진답니다. 가족들에게도 바로 말해주세요!'] },
        { keywords: ['고마워', '똑똑해', '친절해', '칭찬'], responses: ['천만에요! 제가 도움이 되어 정말 기뻐요 😊', '과찬이세요! 더 똑똑해지려고 매일 공부 중이랍니다.', '칭찬받으니 기분이 날아갈 것 같아요! 감사합니다.'] },
        { keywords: ['웃겨', '유머', '농담'], responses: ['세상에서 가장 가난한 왕은? 최저임금... 깔깔깔! 🤣', '전화기로 세운 건물은? 콜로세움!', '딸기가 시력을 잃으면? 딸기시럽... 미안해요.', '반성문을 영어로 하면? 글로벌(글로 벌)... 희희!'] },

        // 5. 건강 및 삶 (Health)
        { keywords: ['운동', '스트레칭', '헬스', '조깅'], responses: ['가벼운 스트레칭으로 몸을 풀어보세요. 건강이 최고입니다!', '하루 30분 걷기는 기분 전환에도 정말 좋아요.'] },
        { keywords: ['건강', '비타민', '약', '영양제'], responses: ['영양제 챙겨 드셨나요? 부모님께도 하나 챙겨드리면 좋아하실 거예요.', '규칙적인 식습관과 충분한 수면이 가장 좋은 보약입니다.'] },
        { keywords: ['명상', '휴식', '졸려', '피곤'], responses: ['눈을 감고 깊게 숨을 들이마셔 보세요. 5분만 명상해도 머리가 맑아져요.', '너무 무리하지 마세요. 잠시 쉬어가는 것도 전략입니다. ☕'] },

        // 6. 여행 (Travel)
        { keywords: ['여행', '휴가', '비행기', '제주도', '해외여행'], responses: ['사진 앨범을 보며 지난 여행의 추억을 되새겨 보세요! 차기 여행 계획을 세우는 것만으로도 행복해지죠.', '가족여행은 어디로 가든 최고의 추억이 될 거예요.'] },
        { keywords: ['드라이브', '산책', '공원'], responses: ['가까운 공원으로 드라이브 어떠세요? 신선한 공기가 필요해요.', '주말에 도시락 싸서 피크닉 가는 것도 좋겠네요!'] },

        // 7. 명언 및 위로 (Counseling)
        { keywords: ['명언', '조언', '한마디'], responses: ['"행복은 가족으로부터 시작된다." - 무명 저자', '"어제의 나보다 오늘의 내가 더 성장했기를." 😊', '"가장 위대한 승리는 나 자신을 이기는 것이다."'] },
        { keywords: ['슬퍼', '우울해', '힘들어', '지쳐'], responses: ['많이 힘들었죠? 제가 곁에 있을게요. 🫂 가족들과 따뜻한 차 한 잔 나누며 이야기를 나눠보세요.', '오늘 하루 정말 수고 많으셨어요. 당신은 충분히 잘하고 있습니다!'] },

        // 100+ 확장 (Etc)
        { keywords: ['돈', '부자', '재테크', '주식'], responses: ['성실하게 저축하는 습관은 부자로 가는 첫걸음입니다 💰', '가족과 함께 상의하여 올바른 투자 계획을 세워보세요.'] },
        { keywords: ['강아지', '고양이', '반려견'], responses: ['댕댕이와 산책 나갈 시간인가요? 앨범에 우리 집 막둥이 사진도 올려주세요! 🐶'] },
        { keywords: ['영화', '드라마', '넷플릭스'], responses: ['이번 주말엔 가족들과 영화 한 편 어떠세요? 🍿'] },
        { keywords: ['공부', '영어', '시험'], responses: ['준비하신 만큼 좋은 결과 있을 거예요! 화이팅! 📚'] },
        { keywords: ['날씨', '비', '눈', '추워', '더워'], responses: ['외출 전 일기예보를 꼭 확인하세요! 가족들에게 우산 챙기라고 안부 인사 어떨까요?'] },
        { keywords: ['취미', '그림', '음악'], responses: ['좋은 취미는 삶을 풍요롭게 하죠. 가족들과 취미를 공유해 보세요!'] },
        { keywords: ['스포츠', '축구', '야구'], responses: ['가끔은 가족들과 스포츠 경기를 직관하거나 시청하며 응원해 보세요! ⚽'] },
        { keywords: ['날짜', '오늘'], responses: [`오늘은 ${new Date().toLocaleDateString('ko-KR')} 입니다! 행복한 하루 되세요.`] }
    ];

    // --- 엔진: 메시지 처리 로직 (검색 및 날짜 감지 강화) ---
    async function processUserMessage(text) {
        const input = text.toLowerCase().trim();
        const cleanInput = input.replace(/\s/g, '');

        // 1. 날짜 관련 검색 감지 (예: "3월 10일 일정", "2024-05-12 약속")
        const dateMatch = input.match(/(\d{4})?[년\-\.]?\s?(\d{1,2})[월\-\.]\s?(\d{1,2})[일]?/);
        if (dateMatch) {
            const year = dateMatch[1] || new Date().getFullYear();
            const month = parseInt(dateMatch[2]);
            const day = dateMatch[3].padStart(2, '0');
            const dateStr = `${year}-${dateMatch[2].padStart(2, '0')}-${day}`;
            
            try {
                const events = await api.get(`/events?year=${year}&month=${month}`);
                const dayEvents = events.filter(e => e.date === dateStr);
                
                if (dayEvents.length > 0) {
                    let respText = `${month}월 ${day}일에는 다음과 같은 일정이 있어요:\n`;
                    dayEvents.forEach(e => {
                        const icon = e.type === 'anniversary' ? '🎂' : (e.type === 'holiday' ? '🇰🇷' : '📌');
                        respText += `- ${icon} ${e.title}\n`;
                    });
                    return { type: 'text', text: respText };
                } else {
                    return { type: 'text', text: `${month}월 ${day}일에는 등록된 일정이 없습니다.` };
                }
            } catch (e) {
                console.error('Date search failed:', e);
            }
        }

        // 2. 게시물 제목 검색 감지
        if (input.includes('찾아') || input.includes('검색') || input.includes('조회')) {
            const query = input.replace(/찾아|검색|조회|줘|해|봐|일정|기념일/g, '').trim();
            if (query.length >= 1) {
                try {
                    const data = await api.get(`/posts?search=${query}`);
                    if (data.posts && data.posts.length > 0) {
                        return { 
                            type: 'search_results', 
                            text: `'${query}' 키워드로 ${data.posts.length}개의 게시물을 찾았습니다.`, 
                            results: data.posts 
                        };
                    }
                } catch (e) {}
            }
        }

        // 3. 규칙 기반 대화 매칭
        let bestMatch = null;
        let highestScore = 0;

        chatbotRules.forEach(rule => {
            let currentScore = 0;
            rule.keywords.forEach(kw => {
                if (cleanInput.includes(kw)) {
                    currentScore += kw.length; 
                }
            });
            if (currentScore > highestScore) {
                highestScore = currentScore;
                bestMatch = rule;
            }
        });

        if (bestMatch && highestScore > 0) {
            const randomIdx = Math.floor(Math.random() * bestMatch.responses.length);
            return { type: 'text', text: bestMatch.responses[randomIdx] };
        }

        return { type: 'text', text: '죄송해요, 조금 더 자세히 말씀해 주시겠어요? 혹은 "기능"이라고 입력해 보세요!' };
    }

    function loadChatHistory() {
        const history = JSON.parse(sessionStorage.getItem(CHAT_HISTORY_KEY)) || [];
        if (history.length === 0) {
            const initialMessage = { type: 'bot', data: { type: 'text', text: '안녕하세요! 우리 가족 웹사이트 가이드입니다. 🤖 무엇이든 물어보세요!\n\n💡 도움이 필요하시면:\n- "3월 14일 일정 뭐야?"\n- "제주도 게시글 찾아줘"\n- "식사 메뉴 추천해줘"' } };
            history.push(initialMessage);
            sessionStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(history));
        }
        messagesContainer.innerHTML = '';
        history.forEach(msg => {
            if (msg.type === 'user') addMessageToUI(msg.text, 'user');
            else addBotMessageToUI(msg.data);
        });
    }

    function saveMessageToHistory(messageData) {
        const history = JSON.parse(sessionStorage.getItem(CHAT_HISTORY_KEY)) || [];
        history.push(messageData);
        sessionStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(history));
    }

    toggler.addEventListener('click', () => {
        const isHidden = chatWindow.style.display === 'none';
        chatWindow.style.display = isHidden ? 'flex' : 'none';
        if (isHidden) {
            inputField.focus();
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.style.display = 'none';
    });

    inputForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userInput = inputField.value.trim();
        if (!userInput) return;

        addMessageToUI(userInput, 'user');
        saveMessageToHistory({ type: 'user', text: userInput });
        inputField.value = '';

        const botResponse = await processUserMessage(userInput);
        setTimeout(() => {
            addBotMessageToUI(botResponse);
            saveMessageToHistory({ type: 'bot', data: botResponse });
        }, 300);
    });

    function addMessageToUI(text, type) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = text;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addBotMessageToUI(data) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot';
        
        let cleanText = data.text
            .replace(/\*\*(.*?)\*\*/g, '$1')
            .replace(/\n/g, '<br>');
        
        let contentHTML = `<p>${cleanText}</p>`;
        if (data.type === 'search_results') {
            contentHTML += '<ul style="margin-top: 8px; list-style: none; padding: 0;">';
            data.results.forEach(post => {
                contentHTML += `<li style="margin-bottom: 6px;"><a href="/post.html?id=${post.id}" style="color: var(--color-primary); font-size: 0.9rem; text-decoration: none;">📄 ${post.title}</a></li>`;
            });
            contentHTML += '</ul>';
        }
        messageElement.innerHTML = contentHTML;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    loadChatHistory();
});