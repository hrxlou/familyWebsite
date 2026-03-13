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
    versionInfo.textContent = 'FamilyWebsite Premium v2.3'; 
    document.body.appendChild(versionInfo);

    // 2. Header Scroll Effect (Use MutationObserver to wait for header injection if needed)
    const initScrollEffect = () => {
        const header = document.querySelector('.toss-header');
        if (header) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 20) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }
            });
        }
    };


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
            });
            
            navRight.prepend(themeBtn);
        }
    };

    // Initialize components after injection
    document.addEventListener('header-rendered', () => {
        initScrollEffect();
        initThemeToggle();
    });

    // Fallback if already rendered
    setTimeout(() => {
        initScrollEffect();
        initThemeToggle();
    }, 500);

    document.addEventListener('auth-checked', initThemeToggle);



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

// --- Toast Notifications ---
(function() {
    const toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    document.body.appendChild(toastContainer);

    window.showToast = function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = '🔔';
        if (type === 'success') icon = '✅';
        if (type === 'error') icon = '🚨';
        
        const content = document.createElement('div');
        content.style.display = 'flex';
        content.style.alignItems = 'center';
        content.style.gap = '12px';
        content.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
        
        toast.appendChild(content);
        toastContainer.appendChild(toast);
        
        // Auto remove after animation (3s matches CSS)
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    };
})();