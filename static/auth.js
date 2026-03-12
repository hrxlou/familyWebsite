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
            <div class="header-user-info" style="display: flex; align-items: center; gap: 16px;">
                <span style="font-size: 0.9rem; color: var(--color-text-secondary);">반가워요, <strong>${nickname}</strong>님</span>
                <a href="/profile.html" class="subtle-link" style="font-weight: 600;">프로필</a>
                <button id="logout-btn" class="toss-button" style="padding: 6px 12px; font-size: 0.85rem; background-color: var(--color-border-medium);">로그아웃</button>
            </div>
        `;
        document.getElementById('logout-btn').addEventListener('click', handleLogout);
    } else {
        navUserSection.innerHTML = `
            <a href="/login.html" class="subtle-link" style="margin-right: 12px; font-weight: 600;">로그인</a>
            <a href="/signup.html" class="toss-button primary" style="padding: 8px 16px; font-size: 0.9rem;">시작하기</a>
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