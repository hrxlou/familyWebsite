document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.chatbot-toggler')) return;

    const chatbotHTML = `
        <button class="chatbot-toggler">💬</button>
        <div class="chatbot-window" style="display: none;">
            <div class="chat-header">
                <span>ChatBot V3.1</span>
                <button class="chat-close-btn">&times;</button>
            </div>
            <div class="chat-messages"></div>
            <form class="chat-input-form">
                <input type="text" placeholder="메시지를 입력하세요...">
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

    const CHAT_HISTORY_KEY = 'family_chatbot_history';
    const CHAT_CONTEXT_KEY = 'family_chatbot_context';

    let conversationContext = sessionStorage.getItem(CHAT_CONTEXT_KEY) || 'default';

    function loadChatHistory() {
        const history = JSON.parse(sessionStorage.getItem(CHAT_HISTORY_KEY)) || [];
        if (history.length === 0) {
            // [수정] 첫 인사 메시지에 !help 안내 추가
            const initialMessage = { type: 'bot', data: { type: 'text', text: '안녕하세요! 무엇을 도와드릴까요? (기능이 궁금하시면 !help를 입력해보세요.)' } };
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

    function clearChatHistory() {
        sessionStorage.removeItem(CHAT_HISTORY_KEY);
        sessionStorage.removeItem(CHAT_CONTEXT_KEY);
        conversationContext = 'default';
        loadChatHistory();
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
        clearChatHistory();
    });

    inputForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const userInput = inputField.value.trim();
        if (!userInput) return;

        addMessageToUI(userInput, 'user');
        saveMessageToHistory({ type: 'user', text: userInput });
        inputField.value = '';

        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: userInput,
                    context: conversationContext
                })
            });
            const data = await response.json();

            if (data.type === 'ask_keyword') {
                conversationContext = data.context;
            } else {
                conversationContext = 'default';
            }
            sessionStorage.setItem(CHAT_CONTEXT_KEY, conversationContext);

            addBotMessageToUI(data);
            saveMessageToHistory({ type: 'bot', data: data });

        } catch (error) {
            const errorData = { type: 'text', text: '죄송합니다, 오류가 발생했어요.' };
            addBotMessageToUI(errorData);
            saveMessageToHistory({ type: 'bot', data: errorData });
        }
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
        // [수정] \n (줄바꿈) 문자를 <br> 태그로 변환하여 HTML에 올바르게 표시
        let contentHTML = `<p>${data.text.replace(/\n/g, '<br>')}</p>`;
        if (data.type === 'link') {
            contentHTML += `<a href="${data.url}">여기를 클릭하여 이동하세요.</a>`;
        } else if (data.type === 'search_results') {
            contentHTML += '<ul>';
            data.results.forEach(post => {
                contentHTML += `<li><a href="/post.html?id=${post.id}">- ${post.title}</a></li>`;
            });
            contentHTML += '</ul>';
        } else if (data.type === 'calendar_results') {
            contentHTML += '<ul>';
            data.results.forEach(event => {
                contentHTML += `<li>- ${event.date}: ${event.title}</li>`;
            });
            contentHTML += '</ul><a href="/calendar.html">캘린더에서 직접 확인하기</a>';
        }
        messageElement.innerHTML = contentHTML;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    loadChatHistory();
});