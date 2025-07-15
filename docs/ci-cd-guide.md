# BlogAuto CI/CD 파이프라인 가이드

## 📋 개요

BlogAuto 프로젝트는 GitHub Actions을 기반으로 한 완전 자동화된 CI/CD 파이프라인을 제공합니다. 이 가이드는 파이프라인의 구조, 사용법, 그리고 모범 사례를 설명합니다.

## 🏗️ 파이프라인 구조

### 1. 워크플로우 파일

#### `ci-cd.yml` - 메인 CI/CD 파이프라인
- **트리거**: `main`, `develop` 브랜치 push 및 PR
- **단계**: 코드 품질 검사 → 테스트 → 빌드 → 배포
- **환경**: staging (develop), production (main)

#### `development.yml` - 개발자 워크플로우
- **트리거**: feature/*, bugfix/*, hotfix/* 브랜치
- **목적**: 빠른 피드백과 기본 품질 검사
- **단계**: 구문 검사 → 단위 테스트 → 코드 품질 → 빌드 테스트

#### `release.yml` - 릴리즈 관리
- **트리거**: 릴리즈 생성 또는 수동 실행
- **목적**: 프로덕션 배포 및 릴리즈 관리
- **단계**: 검증 → 빌드 → 보안 스캔 → 배포 → 테스트

### 2. 환경 설정

#### Staging 환경
```yaml
url: https://staging.blogauto.com
strategy: rolling
replicas: 2
protection_rules:
  required_reviewers: 1
```

#### Production 환경
```yaml
url: https://blogauto.com
strategy: blue-green
replicas: 3
protection_rules:
  required_reviewers: 2
  wait_timer: 300
```

## 🚀 CI/CD 단계

### 1. 코드 품질 검사 (Code Quality)

**Python 검사**
- **Black**: 코드 포맷팅
- **isort**: import 정렬
- **Flake8**: 린팅
- **Bandit**: 보안 스캔
- **Safety**: 의존성 보안 검사

**TypeScript/JavaScript 검사**
- **ESLint**: 코드 린팅
- **TypeScript 컴파일**: 타입 검사

### 2. 테스트 (Testing)

**백엔드 테스트**
- **Pytest**: 단위 테스트 및 통합 테스트
- **Coverage**: 코드 커버리지 측정
- **Crypto System**: 암호화 시스템 테스트

**프론트엔드 테스트**
- **Jest**: 단위 테스트
- **React Testing Library**: 컴포넌트 테스트

**통합 테스트**
- **API Health Check**: API 서버 상태 확인
- **Rate Limiting**: 속도 제한 기능 테스트
- **Security Features**: 보안 기능 테스트

### 3. 보안 스캔 (Security Scanning)

**정적 분석**
- **Bandit**: Python 보안 취약점
- **Safety**: 패키지 보안 취약점
- **Trivy**: 컨테이너 이미지 스캔
- **CodeQL**: 코드 분석 (GitHub 보안 탭)

### 4. 빌드 (Build)

**Docker 이미지 빌드**
- **Multi-stage Build**: 최적화된 이미지 생성
- **Container Registry**: GitHub Container Registry (ghcr.io)
- **Image Tagging**: 버전, 브랜치, SHA 기반 태깅

### 5. 배포 (Deployment)

**Staging 배포**
- **Rolling Update**: 점진적 업데이트
- **Health Check**: 자동 상태 확인
- **Smoke Test**: 기본 기능 테스트

**Production 배포**
- **Blue-Green**: 무중단 배포
- **Manual Approval**: 수동 승인 필요
- **Comprehensive Testing**: 전체 기능 테스트

## 📦 배포 스크립트

### deploy.sh 사용법

```bash
# Staging 배포
./scripts/deployment/deploy.sh staging v1.0.0

# Production 배포
./scripts/deployment/deploy.sh production v1.0.0
```

### 주요 기능
- ✅ 환경 검증
- ✅ 버전 형식 확인
- ✅ Docker 이미지 검증
- ✅ Kubernetes 연결 확인
- ✅ 백업 생성 (Production)
- ✅ Blue-Green 배포 지원
- ✅ 헬스체크 및 롤백

## 🔐 보안 및 권한

### 환경 보호 규칙

**Staging**
- 1명의 리뷰어 필요
- `develop`, `release/*` 브랜치만 배포 가능

**Production**
- 2명의 리뷰어 필요
- 5분 대기 시간
- `main` 브랜치만 배포 가능
- 자체 승인 금지

### 필수 시크릿

```yaml
# Database
DATABASE_PASSWORD
REDIS_PASSWORD

# Security
MASTER_PASSWORD      # API 키 암호화
JWT_SECRET          # 인증 토큰
SSL_CERTIFICATE     # HTTPS 인증서
SSL_PRIVATE_KEY     # HTTPS 개인키

# External APIs
OPENAI_API_KEY_DEFAULT
SENTRY_DSN

# Communication
SMTP_PASSWORD
```

## 🔧 개발 워크플로우

### 1. Feature 개발
```bash
# 브랜치 생성
git checkout -b feature/new-feature

# 개발 및 커밋
git commit -m "feat: add new feature"

# 푸시 (development.yml 트리거)
git push origin feature/new-feature
```

### 2. Pull Request
```bash
# PR 생성 (develop 대상)
# → development.yml 재실행
# → 코드 리뷰 및 승인

# develop에 머지
# → ci-cd.yml 트리거 (staging 배포)
```

### 3. Release
```bash
# main으로 머지
git checkout main
git merge develop

# 릴리즈 태그 생성
git tag v1.0.0
git push origin v1.0.0

# → release.yml 트리거 (production 배포)
```

## 📊 모니터링 및 알림

### GitHub Actions 모니터링
- **Workflow Status**: 실시간 상태 확인
- **Job Logs**: 상세 로그 확인
- **Artifact Downloads**: 빌드 산출물 다운로드

### 보안 모니터링
- **Security Tab**: 보안 스캔 결과
- **Dependabot**: 의존성 업데이트 알림
- **Code Scanning**: 코드 분석 결과

### 배포 모니터링
- **Environment Status**: 환경별 배포 상태
- **Deployment History**: 배포 이력
- **Performance Metrics**: 성능 지표

## 🛠️ 트러블슈팅

### 일반적인 문제

**1. 테스트 실패**
```yaml
# 해결책: 로컬에서 테스트 실행
cd backend && python -m pytest tests/
cd nextjs-app && npm test
```

**2. 빌드 실패**
```yaml
# 해결책: 의존성 확인
pip install -r requirements.txt
npm install
```

**3. 배포 실패**
```yaml
# 해결책: 리소스 및 권한 확인
kubectl get pods -n staging
kubectl logs deployment/blogauto-staging
```

### 롤백 절차

**자동 롤백**
```bash
# Helm을 통한 이전 버전 롤백
helm rollback blogauto-production -n production
```

**수동 롤백**
```bash
# 배포 스크립트의 롤백 기능 사용
./scripts/deployment/deploy.sh production v1.0.0 --rollback
```

## 📈 성능 최적화

### 빌드 최적화
- **캐시 활용**: GitHub Actions 캐시
- **병렬 실행**: 독립적인 Job 병렬화
- **리소스 제한**: 적절한 리소스 할당

### 배포 최적화
- **이미지 최적화**: Multi-stage 빌드
- **네트워크 최적화**: 로컬 레지스트리 활용
- **스케일링**: 자동 스케일링 설정

## 🎯 모범 사례

### 커밋 메시지
```
feat: 새 기능 추가
fix: 버그 수정
docs: 문서 업데이트
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 프로세스 변경
```

### 브랜치 전략
- `main`: 프로덕션 릴리즈
- `develop`: 개발 통합
- `feature/*`: 기능 개발
- `bugfix/*`: 버그 수정
- `hotfix/*`: 긴급 수정

### 코드 품질
- **Pre-commit Hook**: 로컬 검사
- **Code Review**: 필수 리뷰
- **Test Coverage**: 80% 이상 유지
- **Security Scan**: 정기적인 보안 검사

## 🔗 관련 문서

- [API Documentation](./api-documentation.md)
- [Setup Guide](./setup-guide.md)
- [Security Guide](./security-guide.md)
- [Monitoring Guide](./monitoring-guide.md)

---

**마지막 업데이트**: 2025년 7월 12일  
**버전**: v1.0.0  
**담당자**: BlogAuto 개발팀