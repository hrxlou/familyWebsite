# 👨‍👩‍👧‍👦 우리 가족 (FamilyWebsite Premium)

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/hrxlou/familyWebsite/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

가족들만의 소중한 사진, 게시물, 그리고 일정을 공유하는 **프리미엄 패밀리 플랫폼**입니다.  
토스(Toss)의 정갈한 디자인 시스템을 모티프 삼아, 현대적이고 직관적인 사용자 경험을 선사합니다.

---

## ✨ 주요 기능 (Key Features)

### 1. 📝 스마트 가족 게시판
*   **일상의 기록**: 텍스트와 고화질 이미지를 활용한 풍성한 포스팅.
*   **활발한 소통**: 실시간 댓글 시스템으로 나누는 가족 간의 대화.
*   **강력한 검색**: 키워드 기반 필터링으로 소중한 추억을 빠르게 탐색.

### 2. 📸 고품격 가족 앨범
*   **몰입형 뷰어**: 글래스모피즘이 적용된 라이트박스로 감상하는 고화질 사진.
*   **지능형 관리**: 날짜 및 카테고리별 자동 분류 시스템.

### 3. 🗳️ 가족 투표 및 의사결정 (New!)
*   **투표 시스템**: 저녁 메뉴 정하기부터 휴가 계획까지, 가족 간의 민주적인 의사결정 지원.
*   **실시간 투표**: 역동적인 차트와 결과 확인 기능.

### 4. 🔔 지능형 알림 시스템 (New!)
*   **실시간 알림**: 새로운 게시글, 댓글, 등록된 일정에 대한 즉각적인 피드백.
*   **맞춤형 알림**: 개인별 중요도를 고려한 스마트 알림 센터 구축.

### 5. 📅 스마트 캘린더 & 일정
*   **기념일 관리**: 생일, 제사, 가족 행사를 잊지 않게 챙겨주는 D-Day 기능.
*   **일정 동기화**: 모든 가족 구성원이 실시간으로 공유하는 통합 일정표.

### 6. 🌙 프리미엄 UI/UX & PWA
*   **다크 모드**: 시각적 편안함과 세련미를 동시에 제공하는 완벽한 다크 테마.
*   **글래스모피즘**: 고급스러운 투명도와 블러 효과가 적용된 현대적 UI.
*   **PWA 지원**: 앱 설치 없이도 앱처럼 빠르고 편리한 익스피리언스 제공.

---

## 🛠 기술 스택 (Tech Stack)

| 구분 | 기술 |
| :--- | :--- |
| **Backend** | Python 3, Flask, SQLAlchemy |
| **Database** | SQLite3 (Easy Setup, Zero Config) |
| **Frontend** | Vanilla JS (ES6+), CSS3 (Modern Glassmorphism), HTML5 |
| **Infrastructure** | PWA (Service Workers), RESTful API Design |

---

## 🚀 빠른 시작 (Quick Start)

### 1. 환경 설정
```bash
# 레포지토리 클론
git clone https://github.com/hrxlou/familyWebsite.git
cd familyWebsite

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python app.py
```
브라우저에서 `http://localhost:5000`으로 접속하여 프리미엄 패밀리 서비스를 만나보세요!

---

## 📂 프로젝트 구조 (Project Structure)

```text
.
├── app.py              # 시스템 메인 엔트리 및 API 서버
├── models.py           # 데이터베이스 통합 모델 (User, Post, Vote, etc.)
├── config.py           # 서비스 전역 설정 로직
├── routes/             # 도메인별 모듈화된 라우트 핸들러
├── static/             # 리소스 (Design Tokens, Components, Assets)
└── templates/          # (Optional) 서버 사이드 렌더링 템플릿
```

---
*가족의 모든 소중한 순간이 더 특별해지는 곳, **FamilyWebsite Premium**입니다.*
