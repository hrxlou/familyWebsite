// shared.js - Global Premium Effects
// 0. Theme Initialization (Inline execution protection)
(function() {
    const savedTheme = localStorage.getItem('theme');
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const theme = savedTheme || systemTheme;
    document.documentElement.setAttribute('data-theme', theme);
})();

document.addEventListener('DOMContentLoaded', () => {
    // 1. Version Info
    const versionInfo = document.createElement('div');
    versionInfo.className = 'version-info';
    versionInfo.style.cssText = 'position: fixed; bottom: 20px; right: 20px; font-size: 11px; color: var(--color-text-tertiary); opacity: 0.5; pointer-events: none; z-index: 100;';
    versionInfo.textContent = 'FamilyWebsite Premium v2.2'; 
    document.body.appendChild(versionInfo);

    // 2. Header Scroll Effect
    const header = document.querySelector('.toss-header');
    if (header) {
        window.addEventListener('scroll', () => {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            if (window.scrollY > 20) {
                header.style.boxShadow = 'var(--shadow-md)';
                header.style.backgroundColor = isDark ? 'rgba(30, 31, 33, 0.85)' : 'rgba(255, 255, 255, 0.85)';
            } else {
                header.style.boxShadow = 'none';
                header.style.backgroundColor = 'var(--color-bg-header)';
            }
        });
    }

    // 3. Dark Mode Toggle
    const initThemeToggle = () => {
        const navRight = document.getElementById('nav-user-section');
        if (navRight && !document.querySelector('.theme-toggle-btn')) {
            const themeBtn = document.createElement('button');
            themeBtn.className = 'toss-button theme-toggle-btn';
            themeBtn.style.cssText = 'padding: 8px; width: 40px; height: 40px; font-size: 1.2rem; background: var(--color-border-light); border-radius: 12px; margin-right: 8px; display: flex; align-items: center; justify-content: center; border: none; cursor: pointer; color: var(--color-text-primary);';
            
            const updateBtnIcon = (theme) => {
                themeBtn.innerHTML = theme === 'dark' ? '☀️' : '🌙';
            };

            updateBtnIcon(document.documentElement.getAttribute('data-theme'));
            
            themeBtn.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                updateBtnIcon(newTheme);
                
                // 스크롤 중일 때 헤더 색상 즉시 업데이트
                if (window.scrollY > 20 && header) {
                    header.style.backgroundColor = newTheme === 'dark' ? 'rgba(30, 31, 33, 0.85)' : 'rgba(255, 255, 255, 0.85)';
                }
            });
            
            navRight.prepend(themeBtn);
        }
    };

    document.addEventListener('auth-checked', initThemeToggle);
    initThemeToggle();

    // 4. Global Lightbox Logic
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox-overlay';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <button class="lightbox-close">&times;</button>
            <img src="" class="lightbox-image">
        </div>
    `;
    document.body.appendChild(lightbox);

    window.openLightbox = (src) => {
        const lightboxImg = lightbox.querySelector('.lightbox-image');
        lightboxImg.src = src;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    const closeLightbox = () => {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    };

    lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });
});