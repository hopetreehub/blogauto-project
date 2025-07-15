# 🚀 BlogAuto - AI 기반 블로그 자동화 시스템

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AI 기반 키워드 분석부터 콘텐츠 생성까지 한 번에 처리하는 완전 자동화 솔루션

## 🚀 빠른 시작

### 시스템 시작
```bash
cd /mnt/e/project/test-blogauto-project
./start-blogauto.sh
```

### 시스템 중지
```bash
./stop-blogauto.sh
```

### 상태 확인
```bash
./status-blogauto.sh
```

## 📍 접속 정보

- **🌐 메인 서비스**: http://localhost:4007
- **🔧 백엔드 API**: http://localhost:8000

## 🌟 주요 기능

### 📝 콘텐츠 생성
- **키워드 분석**: SEO 최적화된 키워드 분석 및 기회 점수 계산
- **제목 생성**: AI 기반 매력적인 블로그 제목 자동 생성
- **콘텐츠 작성**: 고품질 블로그 콘텐츠 자동 생성
- **이미지 처리**: Unsplash API 연동 이미지 자동 삽입
- **WordPress 발행**: 자동 포스팅 및 카테고리/태그 설정

### 🔐 보안 기능
- **Rate Limiting**: IP 기반 요청 제한 (분당 60회)
- **API 키 암호화**: AES-256 암호화로 안전한 키 관리
- **CORS 설정**: 크로스 오리진 요청 제어
- **입력 검증**: 모든 API 엔드포인트 입력값 검증
- **IP 차단**: 의심스러운 패턴 감지 시 자동 차단

### 🚀 성능 최적화
- **하이브리드 캐싱**: L1(메모리) + L2(Redis) 캐싱
- **연결 풀링**: 데이터베이스 및 HTTP 연결 풀
- **응답 압축**: gzip 압축으로 대역폭 절감
- **비동기 처리**: FastAPI 비동기 지원
- **배치 처리**: 대량 요청 최적화

### 📊 모니터링
- **Prometheus**: 메트릭 수집 및 저장
- **Grafana**: 실시간 대시보드 및 시각화
- **Sentry**: 에러 추적 및 성능 모니터링
- **Jaeger**: 분산 추적 시스템
- **Loki**: 로그 수집 및 분석

## 🔧 설정 방법

### 1. API 키 설정
1. http://localhost:4007/settings 접속
2. OpenAI API 키 입력 (필수)
3. 기타 API 키 설정 (선택)

### 2. 작성 지침 설정
1. http://localhost:4007/guidelines 접속
2. 키워드, 제목, 콘텐츠, SEO 지침 편집
3. 저장 후 자동 적용

## 📱 사용 방법

### 키워드 분석
1. **키워드 분석** 메뉴 클릭
2. 분석할 키워드 입력 → 국가 선택 → **키워드 분석** 클릭
3. 결과 확인 및 CSV 다운로드

### 제목 생성
1. **제목 생성** 메뉴 클릭
2. 키워드 입력 → 설정 조정 → **제목 생성** 클릭
3. 결과 클릭하여 복사

### 콘텐츠 생성
1. **콘텐츠 생성** 메뉴 클릭
2. 제목 입력 → **작성 지침 보기** 확인 → **콘텐츠 생성** 클릭
3. 생성된 콘텐츠 복사 또는 다운로드

## ⚡ 성능 및 상태

### 리소스 사용량
- **백엔드**: CPU ~1%, 메모리 ~100MB
- **프론트엔드**: CPU ~2%, 메모리 ~200MB

### 응답 시간
- **키워드 분석**: ~2초
- **제목 생성**: ~3초  
- **콘텐츠 생성**: ~10-30초 (OpenAI API 속도에 따라)

## 🛡️ 시스템 관리

### 로그 파일 위치
- **백엔드**: `/mnt/e/project/test-blogauto-project/backend/backend.log`
- **프론트엔드**: `/mnt/e/project/test-blogauto-project/nextjs-app/frontend.log`

### 문제 해결
```bash
# 서비스 재시작
./stop-blogauto.sh && ./start-blogauto.sh

# 프로세스 확인
ps aux | grep -E "python3.*real_api|node.*dev"

# 포트 확인
lsof -i :4007 -i :8000
```

---

**🎯 목표**: AI 기반 완전 자동화로 고품질 블로그 콘텐츠 제작  
**⚡ 성능**: 빠르고 안정적인 24/7 서비스  
**🔒 보안**: API 키 로컬 저장으로 안전한 데이터 관리

---

## 📚 기존 개발 계획 (참고용)

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

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **Queue**: Celery + Redis
- **API**: OpenAI GPT, Google Search, Unsplash

### Frontend
- **Framework**: React 18 + TypeScript
- **UI**: Material-UI
- **State**: Redux Toolkit
- **HTTP**: Axios

### Infrastructure
- **Container**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana + Sentry
- **Logging**: Loki + Promtail

## 📋 필수 요구사항

- Python 3.8 이상
- Node.js 16 이상
- Docker & Docker Compose
- Redis 6.0 이상
- PostgreSQL 13 이상

### 1. 저장소 클론
```bash
git clone https://github.com/your-org/test-blogauto-project.git
cd test-blogauto-project
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 필요한 값들을 설정하세요
```

필수 환경 변수:
```
# API Keys
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
UNSPLASH_ACCESS_KEY=your_unsplash_key

# Database
DATABASE_URL=postgresql://user:password@localhost/blogauto

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# Security
MASTER_PASSWORD=your_master_password
SECRET_KEY=your_secret_key

# WordPress
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your_username
WORDPRESS_PASSWORD=your_password

# Monitoring
SENTRY_DSN=your_sentry_dsn
```

### 3. Docker Compose로 실행
```bash
# 전체 스택 실행
docker-compose up -d

# 모니터링 스택 포함
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### 4. 개발 환경 설정
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn real_api_simple:app --reload

# Frontend
cd frontend
npm install
npm start
```

## 📖 상세 문서

- [API 문서](./docs/api-documentation.md) - API 엔드포인트 상세 설명
- [배포 가이드](./docs/deployment-guide.md) - 프로덕션 배포 방법
- [모니터링 가이드](./docs/monitoring-guide.md) - 모니터링 시스템 사용법
- [보안 가이드](./docs/security-guide.md) - 보안 설정 및 모범 사례
- [성능 가이드](./docs/performance-guide.md) - 성능 최적화 팁
- [CI/CD 가이드](./docs/ci-cd-guide.md) - 자동화 파이프라인 설정

## 🧪 테스트

```bash
# Backend 테스트
cd backend
pytest -v

# Frontend 테스트
cd frontend
npm test

# 통합 테스트
python test_integration.py

# 성능 테스트
python test_performance_optimization.py
```

## 📊 모니터링 접속 정보

- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686


## 🤝 기여 방법

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 👥 팀

- **개발팀**: BlogAuto Development Team
- **문의**: support@blogauto.com

## 🙏 감사의 말

- OpenAI - GPT API 제공
- Google - Custom Search API
- Unsplash - 이미지 API
- 모든 오픈소스 기여자들

---

**Version**: 1.0.0  
**Last Updated**: 2025년 7월 12일