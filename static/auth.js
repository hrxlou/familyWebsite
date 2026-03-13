let currentUser = null;

async function checkLoginStatus() {
    try {
        const data = await api.get('/check_session');
        currentUser = data;
    } catch (error) {
        currentUser = null;
    } finally {
        const navUserSection = document.getElementById('nav-user-section');
        if (navUserSection) {
            updateHeader(!!currentUser, currentUser ? currentUser.nickname : '');
        } else {
            // Header might not be rendered yet, wait for it
            document.addEventListener('header-rendered', () => {
                updateHeader(!!currentUser, currentUser ? currentUser.nickname : '');
            }, { once: true });
        }
        document.dispatchEvent(new CustomEvent('auth-checked'));
    }
}

function updateHeader(isLoggedIn, nickname = '') {
    const navUserSection = document.getElementById('nav-user-section');
    if (!navUserSection) return;

    if (isLoggedIn) {
        navUserSection.innerHTML = `
            <div class="notif-btn-wrapper">
                <button class="toss-button" id="notif-btn" style="padding: 8px; width: 40px; height: 40px; font-size: 1.2rem; background: var(--color-border-light); border-radius: 12px; display: flex; align-items: center; justify-content: center; border: none; cursor: pointer; color: var(--color-text-primary);">🔔</button>
                <span id="notif-badge" class="notif-badge" style="display:none;">0</span>
                <div id="notif-dropdown" class="notif-dropdown"></div>
            </div>
            <div class="header-user-info">
                <span class="user-greeting">반가워요, <strong>${escapeHtml(nickname)}</strong>님</span>
                <a href="/profile.html" class="subtle-link">프로필</a>
                <button id="logout-btn" class="toss-button logout-btn">로그아웃</button>
            </div>
        `;
        document.getElementById('logout-btn').addEventListener('click', handleLogout);
        initNotifications();
    } else {
        navUserSection.innerHTML = `
            <a href="/login.html" class="toss-button primary login-btn-header" style="height: 38px; padding: 0 20px; font-size: 0.9rem;">로그인</a>
        `;
    }
}

async function initNotifications() {
    const notifBtn = document.getElementById('notif-btn');
    const notifDropdown = document.getElementById('notif-dropdown');
    const notifBadge = document.getElementById('notif-badge');

    if (!notifBtn) return;

    // 알림 수 가져오기
    try {
        const data = await api.get('/notifications');
        if (data.unread_count > 0) {
            notifBadge.textContent = data.unread_count > 9 ? '9+' : data.unread_count;
            notifBadge.style.display = 'flex';
        }

        // 드롭다운 내용 구성
        if (data.notifications.length === 0) {
            notifDropdown.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--color-text-tertiary);">알림이 없습니다.</div>';
        } else {
            let html = '<div style="padding: 12px 16px; font-weight: 700; border-bottom: 1px solid var(--color-border-light); display: flex; justify-content: space-between; align-items: center;">알림 <button id="read-all-btn" style="background: none; border: none; color: var(--color-primary); cursor: pointer; font-size: 0.8rem;">모두 읽음</button></div>';
            data.notifications.forEach(n => {
                html += `<div class="notif-item ${n.is_read ? '' : 'unread'}" data-id="${n.id}" data-link="${n.link || ''}">
                    <div>${escapeHtml(n.message)}</div>
                    <div class="notif-time">${timeAgo(n.created_at)}</div>
                </div>`;
            });
            notifDropdown.innerHTML = html;

            // 모두 읽음 버튼
            document.getElementById('read-all-btn')?.addEventListener('click', async (e) => {
                e.stopPropagation();
                try {
                    await api.put('/notifications/read-all', {});
                    notifBadge.style.display = 'none';
                    notifDropdown.querySelectorAll('.unread').forEach(el => el.classList.remove('unread'));
                } catch (err) { console.error(err); }
            });

            // 알림 클릭
            notifDropdown.querySelectorAll('.notif-item').forEach(item => {
                item.addEventListener('click', async () => {
                    const id = item.dataset.id;
                    const link = item.dataset.link;
                    try { await api.put(`/notifications/${id}/read`, {}); } catch (e) {}
                    if (link) window.location.href = link;
                });
            });
        }
    } catch (error) {
        console.error('알림 로드 실패:', error);
    }

    // 토글 드롭다운
    notifBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isHidden = notifDropdown.style.display === 'none';
        notifDropdown.style.display = isHidden ? 'block' : 'none';
    });

    // 바깥 클릭 시 닫기
    document.addEventListener('click', () => {
        notifDropdown.style.display = 'none';
    });
    notifDropdown.addEventListener('click', (e) => e.stopPropagation());
}

async function handleLogout() {
    try {
        await api.post('/logout', {});
        // Note: Redirecting immediately might clear the toast, 
        // so we can either wait or just let the landing page handle it if it were different.
        // For simplicity, we'll use alert or a slightly delayed redirect.
        showToast('로그아웃 되었습니다.', 'success');
        setTimeout(() => {
            currentUser = null;
            window.location.href = '/';
        }, 1000);
    } catch (error) {
        showToast('로그아웃 실패: ' + error.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', checkLoginStatus);