# 👨‍👩‍👧‍👦 우리 가족 (FamilyWebsite)

가족 구성원들이 사진, 게시글, 그리고 일정을 공유할 수 있는 가족 전용 커뮤니티 플랫폼입니다.  
현대적이고 직관적인 UI를 제공하여 가족 간의 소통을 돕습니다.

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/hrxlou/familyWebsite/releases)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 주요 기능 (Key Features)

### 1. 📝 가족 게시판
*   **게시글 작성**: 텍스트와 이미지를 포함한 일상 기록 기능.
*   **댓글 시스템**: 게시글에 대한 실시간 가족 간 소통 지원.
*   **검색 기능**: 키워드를 통한 이전 게시글 탐색.

### 2. 📸 가족 앨범
*   **사진 뷰어**: 고화질 사진을 위한 슬라이드 및 라이트박스 뷰어.
*   **앨범 관리**: 날짜 및 카테고리별 사진 분류 기능.

### 3. 🗳️ 가족 투표
*   **의사결정 지원**: 휴가 계획이나 식사 메뉴 등 가족 내 투표 기능.
*   **실시간 결과**: 투표 현황을 실시간으로 확인하는 차트 제공.

### 4. 🔔 알림 시스템
*   **실시간 알림**: 새 게시글, 댓글, 일정 등록 시 알림 제공.
*   **알림 센터**: 개인별 알림 내역 확인 및 관리.

### 5. 📅 캘린더 & 일정
*   **공유 일정**: 가족 구성원 모두가 확인 가능한 통합 캘린더.
*   **기념일 관리**: 생일, 제사 등 중요한 가족 행사 알림 및 D-Day 표시.

### 6. 🌙 UI/UX & PWA
*   **다크 모드**: 다크 테마 지원으로 시각적 편안함 제공.
*   **반응형 디자인**: 모바일 및 PC 환경에 최적화된 레이아웃.
*   **PWA 지원**: 앱 설치 기능을 통해 접근성 강화.

---

## 🛠 기술 스택 (Tech Stack)

| 구분 | 기술 |
| :--- | :--- |
| **Backend** | Python 3, Flask, SQLAlchemy |
| **Database** | SQLite3 |
| **Frontend** | Vanilla JS (ES6+), CSS3, HTML5 |
| **Infrastructure** | PWA, RESTful API |

---

## ⚙️ 실행 방법 (Usage)

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
브라우저에서 `http://localhost:5000`으로 접속하여 확인하세요.

---

## 📂 프로젝트 구조 (Project Structure)

```text
.
├── app.py              # 애플리케이션 엔트리 포인트
├── models.py           # 데이터베이스 모델 (User, Post, Vote 등)
├── config.py           # 시스템 전역 설정
├── routes/             # 도메인별 라우트 핸들러
├── static/             # 정적 리소스 (JS, CSS, Images)
└── templates/          # HTML 템플릿 파일
```


