// shared.js
document.addEventListener('DOMContentLoaded', () => {
    // 버전 정보를 담고 있는 div 요소를 생성합니다.
    const versionInfo = document.createElement('div');
    versionInfo.className = 'version-info';
    
    // 이 부분의 텍스트만 수정하면 모든 페이지의 버전이 한 번에 변경됩니다.
    versionInfo.textContent = '2025-08-09 beta v1.5.2'; 
    
    // 생성된 요소를 body의 가장 마지막에 추가합니다.
    document.body.appendChild(versionInfo);
});