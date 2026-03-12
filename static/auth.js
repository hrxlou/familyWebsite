let currentUser = null;

async function checkLoginStatus() {
    try {
        const data = await api.get('/check_session');
        currentUser = data;
    } catch (error) {
        currentUser = null;
    } finally {
        updateHeader(!!currentUser, currentUser ? currentUser.nickname : '');
        document.dispatchEvent(new CustomEvent('auth-checked'));
    }
}

function updateHeader(isLoggedIn, nickname = '') {
    const navUserSection = document.getElementById('nav-user-section');
    if (!navUserSection) return;

    if (isLoggedIn) {
        navUserSection.innerHTML = `
            <div class="header-user-info">
                <a href="/profile.html" class="post-author-link">프로필</a>
                <span class="nav-welcome-msg">환영합니다, ${nickname}님</span>
                <button id="logout-btn" class="toss-button">로그아웃</button>
            </div>
        `;
        document.getElementById('logout-btn').addEventListener('click', handleLogout);
    } else {
        navUserSection.innerHTML = `
            <a href="/login.html" class="toss-button" style="background-color: #f2f4f6; color: #4e5968;">로그인</a>
            <a href="/signup.html" class="toss-button primary">회원가입</a>
        `;
    }
}

async function handleLogout() {
    try {
        await api.post('/logout', {});
        alert('로그아웃 되었습니다.');
        currentUser = null;
        window.location.href = '/';
    } catch (error) {
        alert('로그아웃 실패: ' + error.message);
    }
}

document.addEventListener('DOMContentLoaded', checkLoginStatus);