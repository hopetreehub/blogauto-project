# BlogAuto 성능 최적화 가이드

## 📋 목차

1. [성능 최적화 개요](#성능-최적화-개요)
2. [캐싱 전략](#캐싱-전략)
3. [데이터베이스 최적화](#데이터베이스-최적화)
4. [API 성능 개선](#api-성능-개선)
5. [프론트엔드 최적화](#프론트엔드-최적화)
6. [인프라 최적화](#인프라-최적화)
7. [모니터링 및 프로파일링](#모니터링-및-프로파일링)
8. [성능 테스트](#성능-테스트)

## 🚀 성능 최적화 개요

BlogAuto는 다음과 같은 성능 목표를 가지고 있습니다:

- **API 응답 시간**: 95% 요청이 2초 이내
- **동시 사용자**: 1,000명 이상 처리
- **처리량**: 초당 100개 이상의 요청 처리
- **가용성**: 99.9% 이상

## 💾 캐싱 전략

### 1. 하이브리드 캐싱 시스템

BlogAuto는 L1(메모리) + L2(Redis) 하이브리드 캐싱을 사용합니다.

```python
# 캐싱 설정 예제
from caching_system import cached, cache_manager

# 캐싱 데코레이터 사용
@cached(prefix="keywords", ttl=3600, compress=True)
async def analyze_keywords(keyword: str, country: str = "KR"):
    # 비용이 많이 드는 작업
    return expensive_operation(keyword, country)

# 수동 캐시 관리
cache_key = "user_settings:123"
await cache_manager.set(cache_key, settings, ttl=7200)
settings = await cache_manager.get(cache_key)
```

### 2. 캐싱 정책

| 데이터 타입 | TTL | 캐시 레벨 | 압축 여부 |
|------------|-----|-----------|----------|
| 키워드 분석 | 1시간 | L1 + L2 | Yes |
| 제목 생성 | 24시간 | L2 | No |
| 콘텐츠 생성 | 24시간 | L2 | Yes |
| API 응답 | 5분 | L1 + L2 | No |
| 사용자 세션 | 1시간 | L1 + L2 | No |

### 3. 캐시 무효화 전략

```python
# 패턴 기반 캐시 삭제
await cache_manager.clear_pattern("keywords:*")

# 특정 캐시 삭제
await analyze_keywords.invalidate("python", "KR")

# 전체 캐시 클리어 (주의!)
await cache_manager.l1_cache.clear()
```

### 4. 캐시 워밍

```python
# 인기 키워드 미리 로드
async def warm_popular_keywords():
    popular_keywords = ["블로그", "마케팅", "SEO", "콘텐츠"]
    
    for keyword in popular_keywords:
        await analyze_keywords(keyword, "KR")
    
    logger.info(f"Warmed {len(popular_keywords)} keywords")

# 애플리케이션 시작 시 실행
@app.on_event("startup")
async def startup_event():
    await cache_manager.initialize()
    await warm_popular_keywords()
```

## 🗄️ 데이터베이스 최적화

### 1. 연결 풀 설정

```python
# SQLAlchemy 연결 풀 최적화
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # 기본 풀 크기
    max_overflow=10,       # 최대 오버플로우
    pool_timeout=30,       # 연결 대기 시간
    pool_recycle=3600,     # 연결 재활용 (1시간)
    pool_pre_ping=True,    # 연결 상태 확인
)
```

### 2. 쿼리 최적화

```python
# 효율적인 쿼리 작성
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload

# N+1 문제 방지 - Eager Loading
stmt = select(BlogPost).options(
    joinedload(BlogPost.author),
    selectinload(BlogPost.tags)
).limit(20)

# 집계 쿼리 최적화
keyword_stats = await session.execute(
    select(
        Keyword.name,
        func.count(KeywordAnalysis.id).label('analysis_count'),
        func.avg(KeywordAnalysis.search_volume).label('avg_volume')
    ).join(KeywordAnalysis)
    .group_by(Keyword.name)
    .having(func.count(KeywordAnalysis.id) > 10)
)

# 인덱스 활용
# SQL: CREATE INDEX idx_created_at ON blog_posts(created_at DESC);
recent_posts = await session.execute(
    select(BlogPost)
    .order_by(BlogPost.created_at.desc())
    .limit(10)
)
```

### 3. 데이터베이스 인덱스

```sql
-- 자주 조회되는 컬럼에 인덱스 추가
CREATE INDEX idx_keywords_name ON keywords(name);
CREATE INDEX idx_analysis_keyword_date ON keyword_analysis(keyword_id, created_at DESC);
CREATE INDEX idx_posts_status_date ON blog_posts(status, published_at DESC);

-- 복합 인덱스 (WHERE 절 순서와 일치)
CREATE INDEX idx_posts_author_status ON blog_posts(author_id, status);

-- 부분 인덱스 (특정 조건만)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;

-- 전문 검색 인덱스
CREATE INDEX idx_content_search ON blog_posts USING gin(to_tsvector('korean', content));
```

### 4. 쿼리 분석 및 튜닝

```sql
-- 쿼리 실행 계획 분석
EXPLAIN ANALYZE SELECT * FROM keyword_analysis 
WHERE keyword_id = 123 
ORDER BY created_at DESC 
LIMIT 10;

-- 느린 쿼리 로깅 활성화
ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1초 이상
SELECT pg_reload_conf();

-- 테이블 통계 업데이트
ANALYZE keywords;
VACUUM ANALYZE keyword_analysis;
```

## ⚡ API 성능 개선

### 1. 비동기 처리

```python
# 병렬 처리로 성능 향상
async def analyze_multiple_keywords(keywords: List[str]):
    tasks = [analyze_keywords(keyword) for keyword in keywords]
    results = await asyncio.gather(*tasks)
    return results

# 백그라운드 작업
from fastapi import BackgroundTasks

@app.post("/api/content/generate")
async def generate_content(
    request: ContentRequest,
    background_tasks: BackgroundTasks
):
    # 즉시 응답
    task_id = str(uuid.uuid4())
    
    # 백그라운드에서 처리
    background_tasks.add_task(
        process_content_generation,
        task_id,
        request
    )
    
    return {"task_id": task_id, "status": "processing"}
```

### 2. 응답 압축

```python
# Gzip 압축 미들웨어
from performance_optimizer import response_optimizer

app.middleware("http")(response_optimizer.compression_middleware)

# 커스텀 압축 설정
response_optimizer.min_compress_size = 1024  # 1KB 이상만 압축
response_optimizer.compress_level = 6        # 압축 레벨 (1-9)
```

### 3. 페이지네이션 최적화

```python
# 커서 기반 페이지네이션
@app.get("/api/posts")
async def get_posts(
    cursor: Optional[str] = None,
    limit: int = Query(20, le=100)
):
    query = select(BlogPost).order_by(BlogPost.id.desc())
    
    if cursor:
        decoded_cursor = base64.b64decode(cursor).decode()
        query = query.where(BlogPost.id < int(decoded_cursor))
    
    posts = await session.execute(query.limit(limit + 1))
    posts = posts.scalars().all()
    
    has_next = len(posts) > limit
    if has_next:
        posts = posts[:-1]
    
    next_cursor = None
    if has_next and posts:
        next_cursor = base64.b64encode(
            str(posts[-1].id).encode()
        ).decode()
    
    return {
        "items": posts,
        "next_cursor": next_cursor,
        "has_next": has_next
    }
```

### 4. HTTP 연결 풀링

```python
# aiohttp 세션 재사용
from performance_optimizer import http_pool

# 초기화
await http_pool.initialize()

# API 호출 시 연결 재사용
response = await http_pool.request(
    "POST",
    "https://api.openai.com/v1/chat/completions",
    json=payload,
    headers=headers
)

# 연결 풀 상태 확인
pool_status = http_pool.get_pool_status()
print(f"Active connections: {pool_status['connections']}")
```

## 🎨 프론트엔드 최적화

### 1. 번들 최적화

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true
        }
      }
    },
    minimizer: [
      new TerserPlugin({
        parallel: true,
        terserOptions: {
          compress: {
            drop_console: true,
          },
        },
      }),
    ],
  }
};
```

### 2. 이미지 최적화

```javascript
// Next.js 이미지 최적화
import Image from 'next/image';

<Image
  src="/images/hero.jpg"
  alt="Hero Image"
  width={1200}
  height={600}
  placeholder="blur"
  loading="lazy"
  quality={85}
/>

// 반응형 이미지
<picture>
  <source
    srcSet="/images/hero-mobile.webp"
    media="(max-width: 768px)"
    type="image/webp"
  />
  <source
    srcSet="/images/hero-desktop.webp"
    media="(min-width: 769px)"
    type="image/webp"
  />
  <img src="/images/hero.jpg" alt="Hero" />
</picture>
```

### 3. 코드 스플리팅

```javascript
// 동적 임포트
const DashboardComponent = lazy(() => import('./Dashboard'));

// 라우트 기반 스플리팅
const routes = [
  {
    path: '/dashboard',
    component: lazy(() => import('./pages/Dashboard'))
  },
  {
    path: '/analytics',
    component: lazy(() => import('./pages/Analytics'))
  }
];

// 조건부 로딩
if (userRole === 'admin') {
  const AdminPanel = await import('./AdminPanel');
  AdminPanel.init();
}
```

### 4. 상태 관리 최적화

```javascript
// Redux Toolkit 최적화
import { createSlice, createSelector } from '@reduxjs/toolkit';

// 메모이제이션된 셀렉터
const selectPosts = state => state.posts.items;
const selectFilter = state => state.posts.filter;

export const selectFilteredPosts = createSelector(
  [selectPosts, selectFilter],
  (posts, filter) => {
    return posts.filter(post => 
      post.status === filter.status &&
      post.title.includes(filter.search)
    );
  }
);

// React.memo로 리렌더링 방지
export const PostItem = React.memo(({ post, onEdit }) => {
  return (
    <div className="post-item">
      <h3>{post.title}</h3>
      <button onClick={() => onEdit(post.id)}>Edit</button>
    </div>
  );
}, (prevProps, nextProps) => {
  return prevProps.post.id === nextProps.post.id &&
         prevProps.post.updatedAt === nextProps.post.updatedAt;
});
```

## 🏗️ 인프라 최적화

### 1. Docker 최적화

```dockerfile
# 멀티 스테이지 빌드
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim

# 보안 사용자
RUN useradd -m -u 1000 appuser

WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

### 2. Nginx 튜닝

```nginx
# nginx.conf 최적화
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # 파일 캐싱
    open_file_cache max=10000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;

    # 버퍼 크기 최적화
    client_body_buffer_size 16K;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 16k;
    client_max_body_size 50m;

    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/x-font-ttf font/opentype image/svg+xml;

    # 정적 파일 캐싱
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
    }

    # API 프록시 캐싱
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;
    
    location /api/keywords/suggestions {
        proxy_cache api_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_key "$request_method$request_uri$args";
        add_header X-Cache-Status $upstream_cache_status;
        proxy_pass http://backend:8000;
    }
}
```

### 3. 시스템 튜닝

```bash
# /etc/sysctl.conf 최적화
net.core.somaxconn = 65535
net.ipv4.tcp_max_tw_buckets = 1440000
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_keepalive_time = 300
net.ipv4.tcp_keepalive_probes = 5
net.ipv4.tcp_keepalive_intvl = 15

# 파일 디스크립터 제한 증가
echo "* soft nofile 65535" >> /etc/security/limits.conf
echo "* hard nofile 65535" >> /etc/security/limits.conf

# 적용
sysctl -p
```

## 📊 모니터링 및 프로파일링

### 1. 성능 메트릭 수집

```python
# 커스텀 메트릭 정의
from prometheus_client import Counter, Histogram, Gauge

# 요청 카운터
request_count = Counter(
    'blogauto_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

# 응답 시간 히스토그램
request_duration = Histogram(
    'blogauto_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# 활성 연결 게이지
active_connections = Gauge(
    'blogauto_active_connections',
    'Number of active connections'
)

# 메트릭 수집 미들웨어
@app.middleware("http")
async def collect_metrics(request: Request, call_next):
    start_time = time.time()
    
    # 활성 연결 증가
    active_connections.inc()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # 메트릭 기록
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response
    finally:
        # 활성 연결 감소
        active_connections.dec()
```

### 2. 프로파일링

```python
# cProfile 사용
import cProfile
import pstats

def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # 상위 20개 함수
        
        return result
    return wrapper

@profile_function
def expensive_operation():
    # 프로파일링할 코드
    pass

# 메모리 프로파일링
from memory_profiler import profile

@profile
def memory_intensive_function():
    # 메모리 사용량을 추적할 코드
    large_list = [i for i in range(1000000)]
    return sum(large_list)
```

### 3. APM (Application Performance Monitoring)

```python
# Sentry Performance Monitoring
import sentry_sdk
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=SENTRY_DSN,
    traces_sample_rate=0.1,  # 10% 샘플링
    profiles_sample_rate=0.1,  # 10% 프로파일링
    integrations=[
        SqlalchemyIntegration(),
    ],
)

# 트랜잭션 추적
with sentry_sdk.start_transaction(op="task", name="generate_content") as transaction:
    with transaction.start_child(op="db", description="fetch_keywords"):
        keywords = await fetch_keywords()
    
    with transaction.start_child(op="http", description="call_openai"):
        content = await generate_with_ai(keywords)
    
    return content
```

## 🧪 성능 테스트

### 1. 부하 테스트 (Locust)

```python
# locustfile.py
from locust import HttpUser, task, between

class BlogAutoUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # 로그인 또는 초기 설정
        self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "testpass"
        })
    
    @task(3)
    def analyze_keyword(self):
        self.client.post("/api/keywords/analyze", json={
            "keyword": "python programming",
            "country": "KR"
        })
    
    @task(2)
    def generate_title(self):
        self.client.post("/api/titles/generate", json={
            "keyword": "web development",
            "count": 5
        })
    
    @task(1)
    def generate_content(self):
        self.client.post("/api/content/generate", json={
            "title": "10 Best Python Libraries",
            "keyword": "python libraries"
        })

# 실행: locust -f locustfile.py --host=http://localhost:8000
```

### 2. 성능 벤치마크

```bash
# Apache Bench (ab)
ab -n 1000 -c 50 -T application/json -p request.json \
   http://localhost:8000/api/keywords/analyze

# wrk 사용
wrk -t12 -c400 -d30s --latency \
    -s script.lua http://localhost:8000/api/health

# k6 스크립트
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% 요청이 2초 이내
    http_req_failed: ['rate<0.05'],    // 에러율 5% 미만
  },
};

export default function() {
  let response = http.get('http://localhost:8000/api/health');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

### 3. 성능 목표 검증

```python
# 성능 테스트 자동화
async def test_performance_requirements():
    results = {
        "api_response_time": await test_api_response_time(),
        "concurrent_users": await test_concurrent_users(),
        "throughput": await test_throughput(),
        "cache_hit_rate": await test_cache_performance()
    }
    
    # 검증
    assert results["api_response_time"]["p95"] < 2.0, "API 응답 시간 초과"
    assert results["concurrent_users"]["max"] >= 1000, "동시 사용자 처리 부족"
    assert results["throughput"]["rps"] >= 100, "처리량 부족"
    assert results["cache_hit_rate"] >= 0.8, "캐시 히트율 부족"
    
    return results
```

## 📈 성능 모범 사례

### 1. 일반 원칙

- **측정 먼저**: 최적화 전에 항상 측정
- **병목 지점 찾기**: 프로파일링으로 실제 문제 파악
- **점진적 개선**: 한 번에 하나씩 변경
- **모니터링**: 변경 후 영향 추적

### 2. 코드 레벨

```python
# ❌ 나쁜 예
for keyword in keywords:
    result = await analyze_keyword(keyword)  # 순차 처리
    results.append(result)

# ✅ 좋은 예
results = await asyncio.gather(*[
    analyze_keyword(keyword) for keyword in keywords
])  # 병렬 처리

# ❌ 나쁜 예
users = session.query(User).all()
for user in users:
    posts = session.query(Post).filter_by(user_id=user.id).all()  # N+1

# ✅ 좋은 예
users = session.query(User).options(
    joinedload(User.posts)
).all()  # Eager loading
```

### 3. 인프라 레벨

- **수평 확장**: 로드 밸런서 + 여러 인스턴스
- **CDN 사용**: 정적 자원 배포
- **오토스케일링**: 트래픽에 따른 자동 확장
- **데이터베이스 복제**: 읽기 전용 복제본 사용

## 🔗 관련 문서

- [캐싱 시스템 문서](./caching-system.md)
- [모니터링 가이드](./monitoring-guide.md)
- [데이터베이스 가이드](./database-guide.md)
- [API 문서](./api-documentation.md)

---

**마지막 업데이트**: 2025년 7월 12일  
**버전**: v1.0.0  
**담당자**: BlogAuto 개발팀