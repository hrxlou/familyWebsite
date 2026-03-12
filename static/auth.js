let currentUser = null;

async function checkLoginStatus() {
    try {
        const data = await api.get('/check_session');
        currentUser = data;
    } catch (error) {
        console.error('세션 확인 중 오류:', error);
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
                <span class="user-greeting">반가워요, <strong>${nickname}</strong>님</span>
                <a href="/profile.html" class="subtle-link">프로필</a>
                <button id="logout-btn" class="toss-button logout-btn">로그아웃</button>
            </div>
        `;
        document.getElementById('logout-btn').addEventListener('click', handleLogout);
    } else {
        navUserSection.innerHTML = `
            <a href="/login.html" class="subtle-link mr-12">로그인</a>
            <a href="/signup.html" class="toss-button primary start-btn">시작하기</a>
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