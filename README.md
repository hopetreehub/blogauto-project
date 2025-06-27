# Blog Auto Process Project

AI 기반 블로그 자동화 프로세스 프로젝트입니다. 키워드 분석부터 콘텐츠 생성, 자동 포스팅까지 전체 블로깅 워크플로우를 자동화합니다.

## 🚀 주요 기능

### 1. 🔍 키워드 분석
- Google Keyword Planner, SEMrush, Ahrefs API 연동
- 검색량, 경쟁도, CPC 분석
- AI 기반 기회점수 계산
- CSV 내보내기 지원

### 2. ✍️ AI 제목 생성
- OpenAI GPT, Google Gemini 등 다중 AI 모델 지원
- 길이, 언어, 톤 커스터마이징
- 중복률 검사 (<10% 보장)
- 사용자별 제목 이력 관리

### 3. 📝 콘텐츠 생성
- AI 기반 고품질 블로그 글 생성
- SEO 최적화 자동 적용
- 이미지 자동 생성 및 삽입
- Copyscape 중복 검사

### 4. 🚀 자동 포스팅
- WordPress, Blogspot 플랫폼 연동
- 예약 포스팅 및 배치 처리
- 실패 시 자동 재시도
- 포스팅 상태 모니터링

### 5. 📊 SEO 분석 대시보드
- CTR, PV, 검색 순위 추적
- 키워드별 성과 분석
- 실시간 모니터링
- 성과 리포트 생성

## 🏗️ 프로젝트 구조

```
blogauto-project/
├── frontend/           # React + Electron 데스크탑 앱
├── backend/           # FastAPI 백엔드 서버
├── nextjs-app/        # Next.js 웹 애플리케이션
├── database/          # 데이터베이스 스키마
├── docker/            # Docker 설정 파일들
└── docs/              # 프로젝트 문서
```

## 🛠️ 기술 스택

### Frontend
- **React 19** - 모던 UI 라이브러리
- **Electron** - 크로스플랫폼 데스크탑 앱
- **Next.js 15** - 풀스택 React 프레임워크
- **Tailwind CSS** - 유틸리티 기반 CSS 프레임워크
- **TypeScript** - 타입 안전성

### Backend
- **FastAPI** - 고성능 비동기 API 프레임워크
- **Python 3.11** - 최신 Python 기능 활용
- **PostgreSQL** - 관계형 데이터베이스
- **Redis** - 인메모리 캐시 및 세션 스토어
- **SQLAlchemy** - ORM (향후 추가 예정)

### AI & External APIs
- **OpenAI GPT** - 텍스트 생성
- **Google Gemini** - 멀티모달 AI
- **HuggingFace** - 오픈소스 AI 모델
- **Google Keyword Planner** - 키워드 분석
- **SEMrush/Ahrefs** - SEO 데이터

### Infrastructure
- **Docker & Docker Compose** - 컨테이너화
- **AWS S3** - 파일 스토리지
- **GitHub Actions** - CI/CD (향후 추가)
- **Kubernetes** - 오케스트레이션 (향후 추가)

## 🚀 빠른 시작

### 전제 조건
- Node.js 18 이상
- Python 3.11 이상
- Docker & Docker Compose

### 1. Docker로 실행 (권장)
```bash
git clone <repository-url>
cd blogauto-project
cp backend/.env.example backend/.env
# .env 파일에서 API 키 설정
cd docker
docker-compose up -d
```

### 2. 수동 설치
```bash
# 백엔드 실행
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# 프론트엔드 실행 (새 터미널)
cd frontend
npm install
npm start

# Next.js 웹앱 실행 (새 터미널)
cd nextjs-app
npm install
npm run dev
```

### 3. 접속 주소
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Next.js 웹앱: http://localhost:3000
- Electron 데스크탑 앱: 자동 실행

## 📖 문서

- [설치 가이드](docs/setup-guide.md) - 상세한 설치 및 설정 가이드
- [API 문서](docs/api-documentation.md) - REST API 사용법
- [개발 가이드](docs/development-guide.md) - 개발자를 위한 가이드

## 🔧 설정

### 환경 변수
```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
SEMRUSH_API_KEY=your_semrush_api_key
AHREFS_API_KEY=your_ahrefs_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/blogauto
REDIS_URL=redis://localhost:6379

# AWS (선택사항)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your-s3-bucket
```

## 🎯 로드맵

### Phase 1 (완료) ✅
- [x] 프로젝트 초기 설정
- [x] React + Electron 데스크탑 앱
- [x] FastAPI 백엔드 구조
- [x] Next.js 웹 애플리케이션
- [x] 데이터베이스 스키마 설계
- [x] Docker 환경 구성

### Phase 2 (진행 중) 🚧
- [ ] 사용자 인증 시스템
- [ ] 실제 AI API 연동
- [ ] 키워드 분석 고도화
- [ ] 콘텐츠 생성 엔진
- [ ] 플랫폼 연동 API

### Phase 3 (계획) 📋
- [ ] SEO 분석 대시보드
- [ ] 배치 처리 시스템
- [ ] 팀 협업 기능
- [ ] 성과 분석 및 리포팅
- [ ] 모바일 앱

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의

프로젝트 관련 문의사항이나 버그 리포트는 GitHub Issues를 통해 남겨주세요.

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!