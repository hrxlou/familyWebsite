/* components.js - Centralized Reusable Components */

const HeaderComponent = {
    render() {
        const currentPath = window.location.pathname;
        const links = [
            { name: '홈', path: '/' },
            { name: '게시판', path: '/board.html' },
            { name: '앨범', path: '/album.html' },
            { name: '캘린더', path: '/calendar.html' },
            { name: '투표', path: '/vote.html' }
        ];

        const navLinks = links.map(link => {
            const isActive = currentPath === link.path || (currentPath === '' && link.path === '/') || (currentPath === '/index.html' && link.path === '/');
            return `<a href="${link.path}" class="nav-link ${isActive ? 'active' : ''}">${link.name}</a>`;
        }).join('');

        return `
            <header class="toss-header">
                <div class="header-inner">
                    <div class="header-left">
                        <h1 class="logo"><a href="/">👨‍👩‍👧‍👦 우리 가족</a></h1>
                        <nav class="main-nav">
                            ${navLinks}
                        </nav>
                    </div>
                    <nav id="nav-user-section" class="nav-right"></nav>
                </div>
            </header>
        `;
    },
    init() {
        const placeholder = document.getElementById('header-placeholder');
        if (placeholder) {
            placeholder.outerHTML = this.render();
            document.dispatchEvent(new CustomEvent('header-rendered'));
        }
    }

};

const FooterComponent = {
    render() {
        return `
            <footer class="toss-footer">
                <div class="footer-inner">
                    <p>© 2026 FamilyWebsite Premium</p>
                </div>
            </footer>
        `;
    },
    init() {
        // Footer injection if needed
        const footerPlaceholder = document.getElementById('footer-placeholder');
        if (footerPlaceholder) {
            footerPlaceholder.outerHTML = this.render();
            document.dispatchEvent(new CustomEvent('footer-rendered'));
        }
    }

};
const Toast = {
    show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toss-toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }, 100);
    }
};

const Loading = {
    show() {
        if (document.getElementById('global-loader')) return;
        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.className = 'toss-loader-overlay';
        loader.innerHTML = '<div class="toss-loader"></div>';
        document.body.appendChild(loader);
    },
    hide() {
        const loader = document.getElementById('global-loader');
        if (loader) loader.remove();
    }
};

window.Toast = Toast;
window.Loading = Loading;

// Auto-init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    HeaderComponent.init();
    FooterComponent.init();
});
