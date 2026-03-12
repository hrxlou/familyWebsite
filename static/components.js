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

// Auto-init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    HeaderComponent.init();
    FooterComponent.init();
});
