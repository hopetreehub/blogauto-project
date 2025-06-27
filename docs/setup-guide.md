# Blog Auto Process - 설치 가이드

## 시스템 요구사항

- Node.js 18 이상
- Python 3.11 이상
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

## 설치 방법

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd blogauto-project
```

### 2. 환경변수 설정
```bash
cp backend/.env.example backend/.env
```

`.env` 파일을 열어 필요한 API 키들을 설정하세요:
- OPENAI_API_KEY
- GEMINI_API_KEY
- SEMRUSH_API_KEY
- AHREFS_API_KEY

### 3. Docker로 실행 (권장)
```bash
cd docker
docker-compose up -d
```

### 4. 수동 설치 및 실행

#### 백엔드 실행
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### 프론트엔드 (React + Electron) 실행
```bash
cd frontend
npm install
npm start
```

#### Next.js 웹 앱 실행
```bash
cd nextjs-app
npm install
npm run dev
```

## 데이터베이스 초기화

### PostgreSQL 설정
```bash
# PostgreSQL 연결 후
psql -U postgres -c "CREATE DATABASE blogauto;"
psql -U postgres -d blogauto -f database/schema.sql
```

## 접속 주소

- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- React Electron 앱: 데스크톱 애플리케이션으로 실행
- Next.js 웹 앱: http://localhost:3000

## 주요 기능

### 1. 키워드 분석
- Google Keyword Planner API 연동
- SEMrush, Ahrefs API 지원
- 검색량, 경쟁도, CPC 분석
- 기회점수 자동 계산

### 2. AI 제목 생성
- OpenAI GPT 모델 지원
- Google Gemini 모델 지원
- 다양한 톤과 길이 옵션
- 중복률 검사

### 3. 콘텐츠 생성
- AI 기반 블로그 글 생성
- SEO 최적화
- 이미지 자동 생성
- Copyscape 중복 검사

### 4. 자동 포스팅
- WordPress API 연동
- Blogspot API 연동
- 예약 포스팅 기능
- 실패 시 재시도 로직

## 트러블슈팅

### 1. API 연결 오류
- API 키가 올바르게 설정되었는지 확인
- 네트워크 연결 상태 확인
- API 사용량 제한 확인

### 2. 데이터베이스 연결 오류
- PostgreSQL 서비스 실행 상태 확인
- 연결 정보가 올바른지 확인
- 방화벽 설정 확인

### 3. 프론트엔드 빌드 오류
- Node.js 버전 확인 (18 이상 필요)
- 의존성 재설치: `rm -rf node_modules && npm install`
- TypeScript 에러 확인

## 개발 가이드

### 백엔드 API 추가
1. `backend/main.py`에 새 엔드포인트 추가
2. Pydantic 모델 정의
3. 비즈니스 로직 구현
4. 테스트 작성

### 프론트엔드 컴포넌트 추가
1. `frontend/src/components/` 또는 `frontend/src/pages/`에 새 컴포넌트 추가
2. TypeScript 인터페이스 정의
3. CSS 스타일링
4. API 연동

### 데이터베이스 스키마 변경
1. `database/schema.sql` 수정
2. 마이그레이션 스크립트 작성
3. 백엔드 모델 업데이트

## 배포

### Docker 배포
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 수동 배포
1. 환경변수 프로덕션용으로 설정
2. 정적 파일 빌드
3. 리버스 프록시 설정 (nginx)
4. SSL 인증서 설정

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.