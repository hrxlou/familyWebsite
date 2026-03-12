# 👨‍👩‍👧‍👦 우리 가족 - 가계 웹사이트 (Family Website)

가족들만의 소중한 사진, 게시글, 일정을 공유하고 관리할 수 있는 Flask 기반의 패밀리 커뮤니케이션 웹사이트입니다.

## ✨ 주요 기능

-   **가족 게시판**: 일상 공유, 투표 및 댓글 기능
-   **가족 앨범**: 사진 업로드 및 공유
-   **가족 캘린더**: 일정 관리 및 기념일 알림
-   **챗봇 서비스**: 정규식 기반의 간단한 가족 안내 챗봇
-   **보안 강화**: `bcrypt`를 이용한 비밀번호 암호화 및 환경 변수(`dotenv`) 관리

## 🛠 기술 스택

-   **Backend**: Flask, SQLAlchemy (SQLite), Flask-Bcrypt
-   **Frontend**: Vanilla HTML/JS, Toss UI 스타일 CSS
-   **Other**: python-dotenv, Pillow

## 🚀 시작하기

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd family-website
```

### 2. 가상 환경 설정 및 패키지 설치
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값을 설정하세요.
```bash
cp .env.example .env
```
- `SECRET_KEY`: Flask 세션 보안 키
- `ADMIN_PASSWORD`: 초기 관리자 비밀번호
- `DATABASE_URI`: 데이터베이스 주소 (기본값: sqlite:///app.db)

### 4. 서버 실행
```bash
python app.py
```
서버 실행 시 초기 데이터(관리자 계정 및 샘플 데이터)가 자동으로 생성됩니다.

## 📝 라이선스
MIT License
