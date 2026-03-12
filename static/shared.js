// shared.js - Global Premium Effects
document.addEventListener('DOMContentLoaded', () => {
    // 1. Version Info
    const versionInfo = document.createElement('div');
    versionInfo.className = 'version-info';
    versionInfo.style.cssText = 'position: fixed; bottom: 20px; right: 20px; font-size: 11px; color: var(--color-text-tertiary); opacity: 0.5; pointer-events: none; z-index: 100;';
    versionInfo.textContent = 'FamilyWebsite Premium v2.0'; 
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
    // Note: feature-cards are on the main page, logo is everywhere.
    // For breadcrumb-like or simple active states if we had a top nav.
});