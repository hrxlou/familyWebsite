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

    const CHAT_HISTORY_KEY = 'family_chatbot_history_v2';
    
    // --- 챗봇 규칙 엔진 데이터베이스 ---
    const chatbotRules = [
        { keywords: ['안녕', '하이', '반가워', 'ㅎㅇ'], responses: ['안녕하세요! 즐거운 하루 보내고 계신가요? 😊', '반가워요! 우리 가족 웹사이트 가이드입니다. 무엇을 도와드릴까요?', '안녕! 오늘도 가족들과 행복한 시간 되세요!'] },
        { keywords: ['기능', '뭐할수있어', '메뉴', '안내', '방법'], responses: ['저희 웹사이트는 **가족 게시판**, **사진 앨범**, **일정 캘린더** 링크를 제공해요.\n\n글을 쓰거나 사진을 올리려면 로그인이 필요합니다!'] },
        { keywords: ['게시판', '글쓰기', '댓글'], responses: ['가족 게시판에서는 일상을 공유할 수 있어요. 상단의 [글쓰기] 버튼을 눌러보세요!', '사진과 함께 글을 올리면 더 멋진 포스트가 된답니다.'] },
        { keywords: ['앨범', '사진', '이미지', '업로드'], responses: ['가족 앨범 페이지에서 소중한 순간들을 사진으로 남길 수 있어요. 라이트박스 기능을 통해 큰 화면으로도 감상 가능합니다 📸'] },
        { keywords: ['캘린더', '일정', '기념일', '생일'], responses: ['가족 캘린더에서 중요한 행사나 생일을 등록하세요. 그러면 메인 화면의 [다가오는 일정] 위젯에도 자동으로 나온답니다 📅', '생일은 한 번 등록하면 매년 자동으로 표시되니 참 편리하죠?'] },
        { keywords: ['다크모드', '어두운', '화면테마'], responses: ['오른쪽 상단의 해/달 아이콘을 클릭하면 다크 모드로 전환할 수 있어요! 밤에 보면 눈이 더 편안하답니다 🌙'] },
        { keywords: ['사랑해', '고마워', '똑똑'], responses: ['헤헤, 저도 우리 가족을 사랑해요! ❤️', '천만에요! 제가 더 도움이 되었으면 좋겠네요.', '감사합니다! 더 똑똑한 가이드가 되도록 노력할게요.'] },
        { keywords: ['배고파', '밥', '점심', '저녁'], responses: ['우리 가족 단톡방에 "밥 먹자!"라고 말해보는 건 어떨까요? 함께 먹으면 더 맛있을 거예요! 🍚'] },
        { keywords: ['개발자', '누가만들', '정보'], responses: ['이 웹사이트는 우리 가족의 소중한 소통을 위해 프리미엄 디자인으로 제작되었습니다. 버전은 2.4입니다! 🚀'] },
        { keywords: ['검색', '찾기'], responses: ['게시판이나 메인 화면에서 검색창을 이용해 보세요. 글 제목이나 내용에 포함된 단어로 빠르게 찾을 수 있습니다.'] },
        { keywords: ['로그인', '회원가입', '비밀번호'], responses: ['상단 [로그인] 메뉴를 이용해 주세요. 계정이 없다면 [회원가입]을 통해 만드실 수 있습니다.'] }
    ];

    async function processUserMessage(text) {
        const input = text.toLowerCase();
        let match = chatbotRules.find(rule => 
            rule.keywords.some(keyword => input.includes(keyword))
        );

        if (match) {
            const randomIdx = Math.floor(Math.random() * match.responses.length);
            return { type: 'text', text: match.responses[randomIdx] };
        }

        // 특수 명령 처리: 검색 연동
        if (input.includes('찾아') || input.includes('검색')) {
            const query = input.replace(/찾아|검색|줘|해|봐/g, '').trim();
            if (query.length >= 2) {
                try {
                    const data = await api.get(`/posts?search=${query}`);
                    if (data.posts && data.posts.length > 0) {
                        return { 
                            type: 'search_results', 
                            text: `'${query}' 검색 결과입니다.`, 
                            results: data.posts 
                        };
                    }
                } catch (e) {}
            }
        }

        return { type: 'text', text: '죄송해요, 조금 더 자세히 말씀해 주시겠어요? 혹은 "기능"이라고 입력해 보세요!' };
    }

    function loadChatHistory() {
        const history = JSON.parse(sessionStorage.getItem(CHAT_HISTORY_KEY)) || [];
        if (history.length === 0) {
            const initialMessage = { type: 'bot', data: { type: 'text', text: '안녕하세요! 우리 가족 웹사이트 가이드입니다. 🤖 무엇이든 물어보세요!' } };
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

        // API 대신 로컬 규칙 엔진 사용
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
        
        let contentHTML = `<p>${data.text.replace(/\n/g, '<br>')}</p>`;
        
        if (data.type === 'search_results') {
            contentHTML += '<ul style="margin-top: 8px; list-style: none; padding: 0;">';
            data.results.forEach(post => {
                contentHTML += `<li style="margin-bottom: 4px;"><a href="/post.html?id=${post.id}" style="color: var(--color-primary); font-size: 0.9rem;">- ${post.title}</a></li>`;
            });
            contentHTML += '</ul>';
        }
        
        messageElement.innerHTML = contentHTML;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    loadChatHistory();
});