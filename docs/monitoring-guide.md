# BlogAuto 모니터링 시스템 가이드

## 📋 개요

BlogAuto는 Prometheus, Grafana, Sentry를 기반으로 한 종합적인 모니터링 시스템을 제공합니다. 이 가이드는 모니터링 시스템의 구성 요소, 설정 방법, 그리고 활용 방법을 설명합니다.

## 🏗️ 모니터링 아키텍처

### 1. 핵심 구성 요소

#### Prometheus
- **역할**: 메트릭 수집 및 저장
- **포트**: 9090
- **수집 주기**: 15초
- **데이터 보관**: 30일

#### Grafana
- **역할**: 데이터 시각화 및 대시보드
- **포트**: 3001
- **기본 계정**: admin/admin

#### Sentry
- **역할**: 에러 추적 및 성능 모니터링
- **통합**: FastAPI, SQLAlchemy
- **샘플링**: 트레이스 10%, 프로파일 10%

#### Loki & Promtail
- **역할**: 로그 수집 및 분석
- **포트**: 3100 (Loki)
- **로그 소스**: 컨테이너, 애플리케이션

#### Jaeger
- **역할**: 분산 추적
- **포트**: 16686 (UI)
- **프로토콜**: OTLP

## 📊 메트릭 수집

### 1. 시스템 메트릭

```yaml
# CPU 사용률
blogauto_cpu_usage_percent

# 메모리 사용량
blogauto_memory_usage_bytes

# 디스크 사용률
blogauto_disk_usage_percent

# 활성 연결 수
blogauto_active_connections{type="tcp"}
```

### 2. API 메트릭

```yaml
# API 요청 수
blogauto_api_requests_total{method="POST", endpoint="/api/keywords/analyze", status="200"}

# API 응답 시간
blogauto_api_request_duration_seconds{method="GET", endpoint="/api/health"}

# 진행 중인 요청
blogauto_api_requests_in_progress{method="POST", endpoint="/api/content/generate"}

# 에러 수
blogauto_errors_total{type="HTTPException", endpoint="/api/secure/store-key"}
```

### 3. 비즈니스 메트릭

```yaml
# 분석된 키워드 수
blogauto_keywords_analyzed_total

# 생성된 제목 수
blogauto_titles_generated_total

# 생성된 콘텐츠 수
blogauto_content_generated_total

# WordPress 게시물 발행
blogauto_wordpress_posts_published_total{status="success"}

# 저장된 API 키
blogauto_api_keys_stored_total{service="openai"}
```

### 4. 보안 메트릭

```yaml
# Rate Limit 거부
blogauto_rate_limit_rejected_total{endpoint="/api/keywords/analyze"}

# 차단된 IP 수
blogauto_blocked_ips_total

# 보안 이벤트
blogauto_security_events_total{type="suspicious_pattern"}
```

## 🚨 알림 설정

### 1. 애플리케이션 알림

#### 높은 API 응답 시간
```yaml
alert: HighApiResponseTime
expr: histogram_quantile(0.95, rate(blogauto_api_request_duration_seconds_bucket[5m])) > 2
for: 5m
severity: warning
```

#### 높은 에러율
```yaml
alert: HighApiErrorRate
expr: rate(blogauto_api_requests_total{status=~"5.."}[5m]) > 0.05
for: 5m
severity: critical
```

#### Rate Limiting 과다
```yaml
alert: HighRateLimitRejections
expr: rate(blogauto_rate_limit_rejected_total[5m]) > 10
for: 5m
severity: warning
```

### 2. 인프라 알림

#### CPU 사용률 높음
```yaml
alert: HighCpuUsage
expr: blogauto_cpu_usage_percent > 80
for: 5m
severity: warning
```

#### 메모리 부족
```yaml
alert: LowMemoryAvailable
expr: blogauto_memory_usage_bytes / (1024*1024*1024) > 3.5
for: 5m
severity: critical
```

#### 서비스 다운
```yaml
alert: BackendServiceDown
expr: up{job="blogauto-backend"} == 0
for: 1m
severity: critical
```

## 📈 Grafana 대시보드

### 1. Overview Dashboard
- **시스템 상태**: CPU, 메모리, 디스크
- **API 성능**: 요청량, 응답 시간, 에러율
- **비즈니스 메트릭**: 키워드, 제목, 콘텐츠 생성량

### 2. API Performance Dashboard
- **엔드포인트별 성능**: 응답 시간 분포
- **상태 코드 분포**: 2xx, 4xx, 5xx
- **처리량**: 초당 요청 수

### 3. Security Dashboard
- **Rate Limiting**: 거부된 요청, 차단된 IP
- **보안 이벤트**: 의심스러운 패턴
- **인증 실패**: 로그인 시도

### 4. Business Metrics Dashboard
- **콘텐츠 생성**: 일별/시간별 추이
- **WordPress 발행**: 성공/실패율
- **API 키 사용**: 서비스별 사용량

## 🔧 설정 방법

### 1. 환경 변수 설정

```bash
# .env 파일
ENVIRONMENT=production
SENTRY_DSN=https://xxx@sentry.io/xxx
GRAFANA_USER=admin
GRAFANA_PASSWORD=secure_password
DB_USER=blogauto
DB_PASSWORD=secure_password
REDIS_PASSWORD=secure_password
```

### 2. 모니터링 스택 시작

```bash
# 모니터링 스택 시작
docker-compose -f docker-compose.monitoring.yml up -d

# 상태 확인
docker-compose -f docker-compose.monitoring.yml ps

# 로그 확인
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
```

### 3. 초기 설정

#### Prometheus 타겟 확인
1. http://localhost:9090/targets 접속
2. 모든 타겟이 "UP" 상태인지 확인

#### Grafana 설정
1. http://localhost:3001 접속
2. 기본 계정으로 로그인
3. 데이터 소스 확인 (Prometheus, Loki, Jaeger)
4. 대시보드 임포트

#### Sentry 프로젝트 설정
1. Sentry 계정 생성
2. 새 프로젝트 생성 (Python/FastAPI)
3. DSN 복사하여 환경 변수 설정

## 🔍 모니터링 활용

### 1. 성능 분석

```promql
# 95 percentile 응답 시간
histogram_quantile(0.95, 
  sum(rate(blogauto_api_request_duration_seconds_bucket[5m])) 
  by (endpoint, le)
)

# 초당 요청 수
sum(rate(blogauto_api_requests_total[1m])) by (endpoint)

# 에러율
sum(rate(blogauto_api_requests_total{status=~"5.."}[5m])) 
/ 
sum(rate(blogauto_api_requests_total[5m]))
```

### 2. 비즈니스 인사이트

```promql
# 일별 콘텐츠 생성량
increase(blogauto_content_generated_total[1d])

# WordPress 발행 성공률
sum(rate(blogauto_wordpress_posts_published_total{status="success"}[1h]))
/
sum(rate(blogauto_wordpress_posts_published_total[1h]))

# 가장 많이 사용되는 API 엔드포인트
topk(5, sum(rate(blogauto_api_requests_total[1h])) by (endpoint))
```

### 3. 보안 모니터링

```promql
# Rate limit 거부 추이
sum(rate(blogauto_rate_limit_rejected_total[5m])) by (endpoint)

# 차단된 IP 수 변화
blogauto_blocked_ips_total

# 보안 이벤트 발생률
sum(rate(blogauto_security_events_total[1h])) by (type)
```

## 🛠️ 트러블슈팅

### 1. 메트릭이 수집되지 않음

```bash
# Prometheus 타겟 상태 확인
curl http://localhost:9090/api/v1/targets

# 애플리케이션 메트릭 엔드포인트 확인
curl http://localhost:8000/metrics

# 네트워크 연결 확인
docker network ls
docker network inspect blogauto-network
```

### 2. Grafana 대시보드 오류

```bash
# 데이터 소스 연결 테스트
curl -u admin:admin http://localhost:3001/api/datasources

# Prometheus 쿼리 테스트
curl 'http://localhost:9090/api/v1/query?query=up'
```

### 3. Sentry 이벤트 누락

```python
# Sentry 연결 테스트
import sentry_sdk
sentry_sdk.capture_message("Test message")

# DSN 확인
echo $SENTRY_DSN
```

## 📊 모니터링 모범 사례

### 1. 메트릭 명명 규칙
- **접두사**: `blogauto_`
- **단위 포함**: `_seconds`, `_bytes`, `_total`
- **레이블 사용**: 최소화하되 의미있게

### 2. 알림 설정
- **임계값**: 비즈니스 영향 기반
- **대기 시간**: 일시적 스파이크 방지
- **심각도**: critical, warning, info

### 3. 대시보드 구성
- **계층적 구조**: 개요 → 상세
- **시간 범위**: 다양한 관점 제공
- **색상 코딩**: 직관적 상태 표시

### 4. 로그 수집
- **구조화된 로그**: JSON 형식
- **적절한 레벨**: DEBUG, INFO, WARNING, ERROR
- **컨텍스트 포함**: 요청 ID, 사용자 ID

## 🔗 관련 문서

- [CI/CD Guide](./ci-cd-guide.md)
- [API Documentation](./api-documentation.md)
- [Security Guide](./security-guide.md)
- [Performance Guide](./performance-guide.md)

---

**마지막 업데이트**: 2025년 7월 12일  
**버전**: v1.0.0  
**담당자**: BlogAuto 개발팀