let currentUser = null;

async function checkLoginStatus() {
    try {
<<<<<<< HEAD
        const data = await api.get('/check_session');
        currentUser = data;
    } catch (error) {
=======
        const response = await fetch('/api/check_session', { credentials: 'include' });
        currentUser = response.ok ? await response.json() : null;
    } catch (error) {
        console.error('세션 확인 중 오류:', error);
>>>>>>> 9554cf59aa61a0160fb8d748f8d294f10aa7f261
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
<<<<<<< HEAD
=======
        // [수정] 새로운 CSS 클래스를 사용하는 간결한 구조로 변경
>>>>>>> 9554cf59aa61a0160fb8d748f8d294f10aa7f261
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
<<<<<<< HEAD
    try {
        await api.post('/logout', {});
        alert('로그아웃 되었습니다.');
        currentUser = null;
        window.location.href = '/';
    } catch (error) {
        alert('로그아웃 실패: ' + error.message);
    }
=======
    await fetch('/api/logout', { method: 'POST', credentials: 'include' });
    alert('로그아웃 되었습니다.');
    currentUser = null;
    window.location.href = '/';
>>>>>>> 9554cf59aa61a0160fb8d748f8d294f10aa7f261
}

document.addEventListener('DOMContentLoaded', checkLoginStatus);