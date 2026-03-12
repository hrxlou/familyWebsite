// shared.js - Global Premium Effects
document.addEventListener('DOMContentLoaded', () => {
    // 1. Version Info
    const versionInfo = document.createElement('div');
    versionInfo.className = 'version-info';
    versionInfo.style.cssText = 'position: fixed; bottom: 20px; right: 20px; font-size: 11px; color: var(--color-text-tertiary); opacity: 0.5; pointer-events: none; z-index: 100;';
    versionInfo.textContent = 'FamilyWebsite Premium v2.1'; 
    document.body.appendChild(versionInfo);

    // 2. Header Scroll Effect (Glassmorphism transition)
    const header = document.querySelector('.toss-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                header.style.boxShadow = 'var(--shadow-md)';
                header.style.backgroundColor = 'rgba(255, 255, 255, 0.85)';
            } else {
                header.style.boxShadow = 'none';
                header.style.backgroundColor = 'var(--color-bg-header)';
            }
        });
    }

    // 3. Active Nav Link Highlighting
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.feature-card, .logo a');

    // 4. Dark Mode Logic
    const initTheme = () => {
        const savedTheme = localStorage.getItem('theme');
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        const theme = savedTheme || systemTheme;
        document.documentElement.setAttribute('data-theme', theme);
    };
    initTheme();

    const initThemeToggle = () => {
        const navRight = document.getElementById('nav-user-section');
        if (navRight && !document.querySelector('.theme-toggle-btn')) {
            const themeBtn = document.createElement('button');
            themeBtn.className = 'toss-button theme-toggle-btn';
            themeBtn.style.cssText = 'padding: 8px; width: 40px; height: 40px; font-size: 1.2rem; background: var(--color-border-light); border-radius: 12px; margin-right: 8px; display: flex; align-items: center; justify-content: center; border: none; cursor: pointer;';
            
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
            });
            
            navRight.prepend(themeBtn);
        }
    };

    document.addEventListener('auth-checked', initThemeToggle);
    initThemeToggle();

    // 5. Global Lightbox Logic
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox-overlay';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <button class="lightbox-close">&times;</button>
            <img src="" class="lightbox-image">
        </div>
    `;
    document.body.appendChild(lightbox);

    const lightboxImg = lightbox.querySelector('.lightbox-image');
    const closeBtn = lightbox.querySelector('.lightbox-close');

    window.openLightbox = (src) => {
        lightboxImg.src = src;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    const closeLightbox = () => {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
    };

    closeBtn.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) closeLightbox();
    });
});