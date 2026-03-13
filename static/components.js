/* components.js - Centralized Reusable Components */

const HeaderComponent = {
    render() {
        return `
            <header class="toss-header">
                <div class="header-inner">
                    <h1 class="logo"><a href="/">👨‍👩‍👧‍👦 우리 가족</a></h1>
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
                    <div class="footer-links">
                        <a href="/">홈</a>
                        <a href="/board.html">게시판</a>
                        <a href="/album.html">앨범</a>
                        <a href="/calendar.html">캘린더</a>
                        <a href="/vote.html">투표</a>
                    </div>
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
