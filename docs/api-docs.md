# BlogAuto API Documentation

## 📋 목차

1. [API 개요](#api-개요)
2. [인증](#인증)
3. [엔드포인트](#엔드포인트)
   - [키워드 분석](#키워드-분석)
   - [제목 생성](#제목-생성)
   - [콘텐츠 생성](#콘텐츠-생성)
   - [WordPress 연동](#wordpress-연동)
   - [보안 API](#보안-api)
   - [성능 모니터링](#성능-모니터링)
4. [에러 처리](#에러-처리)
5. [Rate Limiting](#rate-limiting)
6. [예제 코드](#예제-코드)

## 🌐 API 개요

### Base URL
```
Production: https://api.blogauto.com
Development: http://localhost:8000
```

### API 버전
현재 버전: v1

### 응답 형식
모든 응답은 JSON 형식으로 반환됩니다.

### 공통 헤더
```http
Content-Type: application/json
Accept: application/json
X-API-Version: v1
```

## 🔐 인증

### JWT 토큰 인증

모든 API 요청은 Bearer 토큰을 필요로 합니다.

#### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "your_password"
}
```

**응답**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 인증된 요청
```http
GET /api/protected-endpoint
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📚 엔드포인트

### 키워드 분석

#### 키워드 분석 실행
```http
POST /api/keywords/analyze
Authorization: Bearer {token}
Content-Type: application/json

{
  "keyword": "블로그 마케팅",
  "country": "KR",
  "max_results": 10
}
```

**요청 파라미터**:
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| keyword | string | Yes | 분석할 키워드 |
| country | string | No | 국가 코드 (기본: KR) |
| max_results | integer | No | 최대 결과 수 (기본: 10) |

**응답**:
```json
{
  "keyword": "블로그 마케팅",
  "search_volume": 8100,
  "competition": 0.65,
  "cpc": 2500,
  "opportunity_score": 78.5,
  "related_keywords": [
    {
      "keyword": "블로그 마케팅 전략",
      "search_volume": 1600,
      "competition": 0.45
    }
  ],
  "trend_data": {
    "2025-01": 7500,
    "2025-02": 8100,
    "2025-03": 8900
  }
}
```

#### 키워드 제안
```http
GET /api/keywords/suggestions?base_keyword=블로그
Authorization: Bearer {token}
```

**쿼리 파라미터**:
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| base_keyword | string | Yes | 기본 키워드 |
| limit | integer | No | 제안 수 (기본: 20) |

**응답**:
```json
{
  "suggestions": [
    "블로그 만들기",
    "블로그 수익화",
    "블로그 플랫폼",
    "블로그 SEO"
  ]
}
```

### 제목 생성

#### 제목 생성
```http
POST /api/titles/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "keyword": "파이썬 프로그래밍",
  "count": 5,
  "tone": "professional",
  "length": "medium",
  "language": "ko"
}
```

**요청 파라미터**:
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| keyword | string | Yes | 제목 키워드 |
| count | integer | No | 생성할 제목 수 (기본: 5) |
| tone | string | No | 톤 (professional, casual, friendly) |
| length | string | No | 길이 (short, medium, long) |
| language | string | No | 언어 코드 (기본: ko) |

**응답**:
```json
{
  "titles": [
    {
      "title": "2025년 파이썬 프로그래밍 완벽 가이드",
      "score": 92.5,
      "reason": "트렌드 키워드와 숫자를 포함하여 클릭률 향상"
    },
    {
      "title": "초보자를 위한 파이썬 프로그래밍 10가지 핵심 팁",
      "score": 89.3,
      "reason": "타겟 독자층 명시와 구체적인 숫자 제시"
    }
  ]
}
```

### 콘텐츠 생성

#### 콘텐츠 생성
```http
POST /api/content/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "2025년 파이썬 프로그래밍 완벽 가이드",
  "keyword": "파이썬 프로그래밍",
  "length": "long",
  "tone": "professional",
  "language": "ko",
  "include_images": true,
  "seo_optimization": true
}
```

**요청 파라미터**:
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| title | string | Yes | 콘텐츠 제목 |
| keyword | string | Yes | 주요 키워드 |
| length | string | No | 길이 (short: 500자, medium: 1000자, long: 2000자+) |
| tone | string | No | 톤 스타일 |
| language | string | No | 언어 코드 |
| include_images | boolean | No | 이미지 포함 여부 |
| seo_optimization | boolean | No | SEO 최적화 여부 |

**응답**:
```json
{
  "content": "# 2025년 파이썬 프로그래밍 완벽 가이드\n\n## 서론\n파이썬은...",
  "seo_score": 94.2,
  "word_count": 2150,
  "readability_score": 88.5,
  "images": [
    {
      "url": "https://images.unsplash.com/photo-xxx",
      "alt_text": "Python programming concept",
      "caption": "파이썬 프로그래밍 개념도"
    }
  ],
  "meta_description": "2025년 최신 파이썬 프로그래밍 가이드. 초보자부터 전문가까지 필요한 모든 정보를 담았습니다.",
  "tags": ["파이썬", "프로그래밍", "개발", "코딩"]
}
```

### WordPress 연동

#### WordPress 게시물 발행
```http
POST /api/wordpress/publish
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "2025년 파이썬 프로그래밍 완벽 가이드",
  "content": "게시물 내용...",
  "status": "publish",
  "categories": ["Programming", "Python"],
  "tags": ["파이썬", "프로그래밍", "2025"],
  "featured_image_url": "https://example.com/image.jpg",
  "schedule_date": "2025-07-15T09:00:00Z"
}
```

**요청 파라미터**:
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| title | string | Yes | 게시물 제목 |
| content | string | Yes | 게시물 내용 (HTML) |
| status | string | No | 상태 (draft, publish, future) |
| categories | array | No | 카테고리 목록 |
| tags | array | No | 태그 목록 |
| featured_image_url | string | No | 대표 이미지 URL |
| schedule_date | string | No | 예약 발행 시간 (ISO 8601) |

**응답**:
```json
{
  "post_id": 12345,
  "url": "https://your-blog.com/2025/07/python-programming-guide",
  "status": "published",
  "published_at": "2025-07-12T10:30:00Z"
}
```

#### WordPress 연결 테스트
```http
POST /api/wordpress/test-connection
Authorization: Bearer {token}
Content-Type: application/json

{
  "url": "https://your-blog.com",
  "username": "admin",
  "password": "app_password"
}
```

**응답**:
```json
{
  "connected": true,
  "site_info": {
    "name": "My Blog",
    "description": "A blog about programming",
    "url": "https://your-blog.com",
    "wordpress_version": "6.5.0"
  }
}
```

### 보안 API

#### API 키 저장
```http
POST /api/secure/store-key
Authorization: Bearer {token}
Content-Type: application/json

{
  "service": "openai",
  "api_key": "sk-xxxxxxxxxxxxxxxx"
}
```

**응답**:
```json
{
  "status": "stored",
  "service": "openai",
  "stored_at": "2025-07-12T10:30:00Z"
}
```

#### API 키 조회
```http
GET /api/secure/keys
Authorization: Bearer {token}
```

**응답**:
```json
{
  "keys": [
    {
      "service": "openai",
      "is_configured": true,
      "last_updated": "2025-07-12T10:30:00Z"
    },
    {
      "service": "google",
      "is_configured": false,
      "last_updated": null
    }
  ]
}
```

### 성능 모니터링

#### 성능 요약
```http
GET /api/performance/summary
Authorization: Bearer {token}
```

**응답**:
```json
{
  "uptime_seconds": 86400,
  "total_requests": 15420,
  "requests_per_second": 0.178,
  "error_rate": 0.0012,
  "slow_request_rate": 0.025,
  "response_times": {
    "average": 0.245,
    "p95": 0.890,
    "p99": 1.230
  },
  "slowest_endpoints": [
    {
      "endpoint": "POST /api/content/generate",
      "avg_time": 5.234,
      "count": 342
    }
  ]
}
```

#### 캐시 상태
```http
GET /api/performance/cache
Authorization: Bearer {token}
```

**응답**:
```json
{
  "l1_cache": {
    "entries": 234,
    "max_size": 500,
    "hit_rate": 0.823,
    "total_size_bytes": 1048576
  },
  "l2_cache": {
    "connected": true,
    "server": "redis:6379",
    "memory_used": "45.2MB",
    "keys": 1523,
    "hit_rate": 0.756
  }
}
```

#### 캐시 클리어
```http
POST /api/performance/cache/clear?pattern=keywords:*
Authorization: Bearer {token}
```

**쿼리 파라미터**:
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| pattern | string | No | 삭제할 캐시 키 패턴 |

**응답**:
```json
{
  "success": true,
  "cleared_keys": 45,
  "pattern": "keywords:*"
}
```

## ❌ 에러 처리

### 에러 응답 형식
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "keyword": ["This field is required"],
      "max_results": ["Must be between 1 and 100"]
    }
  },
  "request_id": "req_12345",
  "timestamp": "2025-07-12T10:30:00Z"
}
```

### 에러 코드

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|-----------|------|
| 400 | VALIDATION_ERROR | 입력값 검증 실패 |
| 401 | UNAUTHORIZED | 인증 실패 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 리소스를 찾을 수 없음 |
| 429 | RATE_LIMIT_EXCEEDED | Rate limit 초과 |
| 500 | INTERNAL_ERROR | 서버 내부 오류 |
| 503 | SERVICE_UNAVAILABLE | 서비스 일시 중단 |

## ⏱️ Rate Limiting

### Rate Limit 정책

| 엔드포인트 | 제한 | 윈도우 |
|------------|------|--------|
| /api/keywords/analyze | 30회 | 1분 |
| /api/titles/generate | 20회 | 1분 |
| /api/content/generate | 10회 | 1시간 |
| /api/wordpress/publish | 60회 | 1시간 |
| 기타 엔드포인트 | 60회 | 1분 |

### Rate Limit 헤더
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1625234567
```

### Rate Limit 초과 응답
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retry_after": 45
  }
}
```

## 💻 예제 코드

### Python
```python
import requests
import json

class BlogAutoAPI:
    def __init__(self, api_key):
        self.base_url = "https://api.blogauto.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_keyword(self, keyword, country="KR"):
        endpoint = f"{self.base_url}/api/keywords/analyze"
        payload = {
            "keyword": keyword,
            "country": country,
            "max_results": 10
        }
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def generate_content(self, title, keyword):
        endpoint = f"{self.base_url}/api/content/generate"
        payload = {
            "title": title,
            "keyword": keyword,
            "length": "long",
            "seo_optimization": True
        }
        
        response = requests.post(endpoint, json=payload, headers=self.headers)
        response.raise_for_status()
        
        return response.json()

# 사용 예시
api = BlogAutoAPI("your_api_key")

# 키워드 분석
keyword_data = api.analyze_keyword("파이썬 프로그래밍")
print(f"검색량: {keyword_data['search_volume']}")

# 콘텐츠 생성
content_data = api.generate_content(
    "2025년 파이썬 프로그래밍 가이드",
    "파이썬 프로그래밍"
)
print(f"SEO 점수: {content_data['seo_score']}")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

class BlogAutoAPI {
  constructor(apiKey) {
    this.baseURL = 'https://api.blogauto.com';
    this.client = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async analyzeKeyword(keyword, country = 'KR') {
    try {
      const response = await this.client.post('/api/keywords/analyze', {
        keyword,
        country,
        max_results: 10
      });
      
      return response.data;
    } catch (error) {
      console.error('Error analyzing keyword:', error.response?.data);
      throw error;
    }
  }

  async generateContent(title, keyword) {
    try {
      const response = await this.client.post('/api/content/generate', {
        title,
        keyword,
        length: 'long',
        seo_optimization: true
      });
      
      return response.data;
    } catch (error) {
      console.error('Error generating content:', error.response?.data);
      throw error;
    }
  }
}

// 사용 예시
const api = new BlogAutoAPI('your_api_key');

(async () => {
  // 키워드 분석
  const keywordData = await api.analyzeKeyword('JavaScript 프레임워크');
  console.log(`검색량: ${keywordData.search_volume}`);
  
  // 콘텐츠 생성
  const contentData = await api.generateContent(
    '2025년 JavaScript 프레임워크 비교',
    'JavaScript 프레임워크'
  );
  console.log(`SEO 점수: ${contentData.seo_score}`);
})();
```

### cURL
```bash
# 로그인
curl -X POST https://api.blogauto.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password"}'

# 키워드 분석
curl -X POST https://api.blogauto.com/api/keywords/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keyword":"블로그 마케팅","country":"KR"}'

# 콘텐츠 생성
curl -X POST https://api.blogauto.com/api/content/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"효과적인 블로그 마케팅 전략",
    "keyword":"블로그 마케팅",
    "length":"long"
  }'
```

## 🔗 관련 문서

- [보안 가이드](./security-guide.md)
- [성능 가이드](./performance-guide.md)
- [배포 가이드](./deployment-guide.md)
- [모니터링 가이드](./monitoring-guide.md)

## 📞 지원

API 관련 문의사항은 다음 채널을 통해 연락주세요:

- 이메일: api-support@blogauto.com
- 개발자 포럼: https://forum.blogauto.com
- GitHub Issues: https://github.com/blogauto/api-issues

---

**마지막 업데이트**: 2025년 7월 12일  
**API 버전**: v1.0.0  
**담당자**: BlogAuto API 팀