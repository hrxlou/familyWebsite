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

    // --- 챗봇 규칙 엔진 데이터베이스 (V5: 매머드급 확장) ---
    const chatbotRules = [
        // 1. 인사 및 사교 (Greetings)
        { keywords: ['안녕', '하이', '반가워', 'ㅎㅇ', '조은아침', '좋은아침', '굿모닝'], responses: ['안녕하세요! 즐거운 하루 보내고 계신가요? 😊', '반가워요! 우리 가족 웹사이트 가이드입니다. 무엇을 도와드릴까요?', '안녕! 오늘도 가족들과 행복한 시간 되세요!', '좋은 아침이에요! 상쾌한 시작 하시길 바랄게요.'] },
        { keywords: ['잘자', '굿나잇', '잘 자', '굿밤'], responses: ['안녕히 주무세요! 내일도 행복한 소식으로 만나요 🌙', '좋은 꿈 꾸세요! 가족들 모두 편안한 밤 되시길.', '굿나잇! 불 끄고 푹 쉬세요.'] },
        { keywords: ['이름이', '누구니', '정체', '넌누구'], responses: ['저는 우리 가족 웹사이트의 마스코트이자 가이드인 "패밀리 봇"입니다! 🤖', '가족들의 행복한 소통을 돕는 인공지능 도우미예요.'] },

        // 2. 가이드 및 기능 설명 (Feature Guides)
        { keywords: ['기능', '뭐할수있어', '메뉴', '안내', '방법', '도움'], responses: ['저희 웹사이트는 **가족 게시판**, **사진 앨범**, **일정 캘린더** 세 가지 메인 기능을 제공해요.\n\n각 페이지로 이동해서 가족들의 소식을 확인해 보세요!'] },
        { keywords: ['게시판', '글쓰기', '게시물', '글쓰는법'], responses: ['가족 게시판 메뉴에서 [글쓰기] 버튼을 누르면 일상을 남길 수 있어요.\n제목과 내용을 입력하고 사진도 첨부해 보세요!'] },
        { keywords: ['댓글', '반응'], responses: ['게시글 하단에 댓글을 달아 가족들과 소통할 수 있어요. 따뜻한 댓글 한마디가 큰 힘이 됩니다 ❤️'] },
        { keywords: ['앨범', '사진', '이미지', '업로드', '갤러리'], responses: ['가족 앨범에서는 사진을 올리고 한눈에 모아볼 수 있어요. 업로드된 사진을 클릭하면 크게 감상할 수 있는 라이트박스 기능도 있답니다!'] },
        { keywords: ['캘린더', '일정', '기념일', '생일', '약속'], responses: ['가족 캘린더에서 중요한 약속이나 생일을 관리하세요.\n**매년 반복** 옵션을 쓰면 생일 같은 일정도 잊지 않게 도와드려요!'] },
        { keywords: ['점프', '날짜이동', '년도선택', '미래'], responses: ['캘린더 페이지 상단의 "년/월"을 클릭해 보세요! 원하는 날짜로 즉시 점프할 수 있는 선택창이 나온답니다 📅'] },
        { keywords: ['삭제', '지우기'], responses: ['일정이나 게시글은 상세 보기 창에서 삭제 버튼(X)을 눌러 지울 수 있습니다. (자신이 쓴 글만 가능해요!)'] },

        // 3. 가족 생활 및 에티켓 (Family Life)
        { keywords: ['식사', '메뉴', '점심', '저녁', '뭐먹지', '밥추천'], responses: ['오늘은 따뜻한 김치찌개 어때요?', '치킨이나 피자로 가족 파티를 즐겨보시는 것도 좋겠네요 🍕', '건강하게 비빔밥이나 쌈밥은 어떠신가요?', '날씨도 좋은데 외식 어때요? 아빠께 여쭤봐요!'] },
        { keywords: ['안부', '사랑', '엄마', '아빠', '아들', '딸'], responses: ['가족에게 "사랑해요"라고 먼저 메시지를 보내보세요. 큰 행복이 될 거예요!', '오늘 하루 어땠냐고 서로 물어보는 건 어떨까요? ❤️'] },
        { keywords: ['화해', '싸움', '미안'], responses: ['먼저 "미안해"라고 말하는 용기가 가족을 더 뜨겁게 합니다. 오늘 용기 내보세요!'] },

        // 4. 감성 및 유머 (Emotional & Humor)
        { keywords: ['사랑해', '조아해', '좋아해', '러브'], responses: ['저도 우리 가족을 무지무지 사랑해요! ❤️ 우리 가족 화이팅!', '사랑은 표현할 때 더 커진답니다. 가족들에게도 바로 말해주세요!'] },
        { keywords: ['고마워', '똑똑해', '친절해', '칭찬'], responses: ['천만에요! 제가 도움이 되어 정말 기뻐요 😊', '과찬이세요! 더 똑똑해지려고 매일 공부 중이랍니다.', '칭찬받으니 기분이 날아갈 것 같아요! 감사합니다.'] },
        { keywords: ['심심해', '놀아줘', '심심'], responses: ['앨범에서 옛날 사진들을 구경해 보는 건 어떨까요? 추억이 새록새록 돋을 거예요.', '게시판에 재미있는 유머 하나 올려보세요! 가족들이 즐거워할걸요?'] },
        { keywords: ['웃겨', '유머', '농담'], responses: ['세상에서 가장 가난한 왕은? 최저임금... 깔깔깔! 🤣', '전화기로 세운 건물은? 콜로세움!', '딸기가 시력을 잃으면? 딸기시럽(실업)... 미안해요.'] },

        // 5. 기술 지원 및 설정 (Tech Support)
        { keywords: ['다크모드', '테마', '밝기', '어두운', '화면색'], responses: ['오른쪽 상단의 달/해 모양 아이콘을 누르면 다크 모드로 바꿀 수 있어요. 밤에는 다크 모드가 눈에 훨씬 좋답니다 🌙'] },
        { keywords: ['PWA', '설치', '홈화면', '앱'], responses: ['브라우저 설정 메뉴에서 "홈 화면에 추가"를 누르면 앱처럼 설치해서 편하게 접속할 수 있습니다! 📱'] },
        { keywords: ['속도', '느려', '느림', '렉'], responses: ['광력 새로고침(Ctrl + Shift + R)을 해보시거나, 인터넷 연결을 확인해 주세요. 브라우저 캐시 문제일 수 있습니다!'] },
        { keywords: ['오류', '버그', '안돼', '이상해'], responses: ['어떤 부분이 이상한가요? 새로고침을 먼저 해보시고, 계속 안 되면 개발자(아들/딸)에게 문의해 주세요! 🛠️'] },

        // 6. 일상 정보 및 계절 (Daily & Seasons)
        { keywords: ['날씨', '비', '눈', '더워', '추워', '미세먼지', '마스크'], responses: ['날씨가 변덕스러울 땐 외출 전 꼭 일기예보를 확인하세요! 가족들과 우산 챙기라고 안부 인사도 잊지 마시고요 ☔', '더운 날엔 시원한 수박 하나 잘라먹으며 가족들과 도란도란 이야기 나눠봐요!', '추운 날씨엔 따뜻한 차 한 잔 어떠세요? 감기 조심하세요!', '미세먼지가 심한 날엔 마스크 꼭 챙기세요! 가족 건강이 최우선입니다.'] },
        { keywords: ['운동', '건강', '헬스', '산책', '비타민'], responses: ['오늘 가족들과 가벼운 산책 어떠세요? 건강이 최고의 재산입니다! 🏃', '영양제 챙겨 드셨나요? 아빠, 엄마 건강도 꼭 챙겨주세요.', '꾸준한 운동은 기분 전환에도 최고예요!'] },
        { keywords: ['여행', '휴가', '나들이', '캠핑'], responses: ['이번 주말에 가족 나들이 계획해 보시는 건 어떨까요? 사진 많이 찍어서 앨범에 올려주세요!', '여행은 어디로 가든 가족과 함께라면 즐거울 거예요 🚗'] },

        // 7. 격려 및 응원 (Encouragement)
        { keywords: ['힘들어', '우울', '슬퍼', '지쳐', '피곤'], responses: ['많이 힘드셨군요... 제가 따뜻하게 안아드릴게요. 🫂 가족들과 맛있는 거 먹고 푹 쉬세요!', '오늘 하루 정말 수고 많으셨어요. 당신은 최고입니다!', '잠시 숨을 고르고 하늘을 한번 보세요. 내일은 더 좋은 일이 생길 거예요.'] },
        { keywords: ['시험', '공부', '합격', '응원', '화이팅'], responses: ['준비하신 만큼 좋은 결과 있을 거예요! 화이팅!', '노력은 배신하지 않아요. 가족 모두가 당신을 응원하고 있습니다 🍀'] },

        // 8. 명언 및 문학 (Quotes)
        { keywords: ['명언', '좋은글', '한마디', '조언'], responses: ['"행복은 가족으로부터 시작된다." - 무명 저자', '"어제의 나보다 오늘의 내가 더 성장했기를." 😊', '"가장 위대한 승리는 나 자신을 이기는 것이다."', '오늘의 한마디: "웃으면 복이 와요!"'] },

        // 9. 가족 에피소드 및 질문 (Family Chat)
        { keywords: ['이벤트', '기획', '파티'], responses: ['깜짝 케이크 이벤트를 준비해 보세요! 가족들이 정말 좋아할 거예요 🎂', '소박한 홈파티는 언제나 즐겁죠!'] },
        { keywords: ['용돈', '선물', '효도'], responses: ['작은 꽃 한 송이도 훌륭한 효도 선물이 됩니다 🌸', '부모님께 안부 전화 한 통 드리는 건 어떠세요?'] },

        // 10. 기술/컴퓨터 질문 (Tech & Tips)
        { keywords: ['비밀번호변경', '회원정보', '수정'], responses: ['우측 상단 프로필 메뉴에서 정보를 수정할 수 있습니다! 보안을 위해 비밀번호는 주기적으로 바꿔주세요.'] },
        { keywords: ['사진안나와', '엑박', '이미지오류'], responses: ['이미지 파일 형식이 올바른지 확인해 주세요 (jpg, png 권장). 새로고침도 잊지 마세요!'] },

        // 11. 심화 질문 (Advanced Inquiries)
        { keywords: ['인공지능', '챗GPT', '원리', '봇'], responses: ['저는 사용자가 입력한 단어를 분석해서 가장 적절한 답변을 골라내는 지능형 엔진으로 작동합니다! 🧠'] },
        { keywords: ['사이트맵', '구조'], responses: ['홈 -> 게시판 -> 앨범 -> 캘린더 순으로 이어지는 직관적인 구조입니다!'] },

        // 12. 계절별 대화 (Seasonal)
        { keywords: ['봄', '벚꽃', '꽃구경'], responses: ['봄바람이 살랑살랑 하네요. 가족들과 꽃구경 다녀오세요! 🌸'] },
        { keywords: ['여름', '바다', '계곡', '수영'], responses: ['무더운 여름, 시원한 바다가 생각나네요! 🌊'] },
        { keywords: ['가을', '단풍', '독서'], responses: ['가을은 독서의 계절! 좋은 책 있으면 게시판에 추천해 주세요 🍂'] },
        { keywords: ['겨울', '스키', '썰매', '붕어빵'], responses: ['붕어빵이 맛있는 계절이에요! 가족들 몫까지 사 가시는 센스! ❄️'] },

        // 13. 기타 (Miscellaneous)
        { keywords: ['뭐해', '놀자'], responses: ['저는 당신의 질문을 기다리고 있었어요! 헤헤 😊'] },
        { keywords: ['졸려', '잠와'], responses: ['잠깐만 눈을 붙여보세요. 15분 정도의 낮잠은 보약이랍니다.'] },
        { keywords: ['날짜', '오늘'] , responses: [`오늘은 ${new Date().toLocaleDateString('ko-KR')} 입니다! 행복한 하루 되세요.`] }
    ];

    // --- 매칭 로직 (점수제/우선순위 개선 버전) ---
    async function processUserMessage(text) {
        const input = text.toLowerCase().replace(/\s/g, '');
        let bestMatch = null;
        let highestScore = 0;

        chatbotRules.forEach(rule => {
            let currentScore = 0;
            rule.keywords.forEach(kw => {
                if (input.includes(kw)) {
                    currentScore += kw.length; // 키워드가 길수록 높은 점수
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