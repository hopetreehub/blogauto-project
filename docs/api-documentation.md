# Blog Auto Process - API 문서

## 기본 정보

- Base URL: `http://localhost:8000`
- API 문서: `http://localhost:8000/docs`
- Content-Type: `application/json`

## 인증

현재 버전에서는 기본 인증이 구현되어 있지 않습니다. 향후 버전에서 JWT 토큰 기반 인증이 추가될 예정입니다.

## API 엔드포인트

### 1. 키워드 분석

#### POST /api/keywords/analyze
키워드를 분석하여 검색량, 경쟁도, CPC, 기회점수를 반환합니다.

**Request Body:**
```json
{
  "keyword": "블로그 마케팅",
  "country": "KR",
  "max_results": 10
}
```

**Parameters:**
- `keyword` (string, required): 분석할 키워드
- `country` (string, optional): 국가 코드 (기본값: "KR")
- `max_results` (integer, optional): 최대 결과 수 (기본값: 10)

**Response:**
```json
[
  {
    "keyword": "블로그 마케팅",
    "search_volume": 1200,
    "competition": "Medium",
    "cpc": 1.5,
    "opportunity_score": 85
  }
]
```

### 2. 제목 생성

#### POST /api/titles/generate
AI를 사용하여 키워드 기반 제목을 생성합니다.

**Request Body:**
```json
{
  "keyword": "블로그 마케팅",
  "length": "medium",
  "language": "ko",
  "tone": "professional",
  "count": 5
}
```

**Parameters:**
- `keyword` (string, required): 제목에 포함할 키워드
- `length` (string, optional): 제목 길이 ("short", "medium", "long")
- `language` (string, optional): 언어 ("ko", "en")
- `tone` (string, optional): 톤 ("professional", "casual", "exciting")
- `count` (integer, optional): 생성할 제목 수 (기본값: 5)

**Response:**
```json
[
  {
    "title": "블로그 마케팅 완벽 가이드: 2024년 최신 전략",
    "duplicate_rate": 5.2
  }
]
```

### 3. 콘텐츠 생성

#### POST /api/content/generate
제목을 기반으로 블로그 콘텐츠를 생성합니다.

**Request Body:**
```json
{
  "title": "블로그 마케팅 완벽 가이드: 2024년 최신 전략",
  "keywords": "SEO, 콘텐츠 마케팅, 블로그 운영",
  "length": "medium"
}
```

**Parameters:**
- `title` (string, required): 콘텐츠 제목
- `keywords` (string, optional): 추가 키워드 (쉼표로 구분)
- `length` (string, optional): 콘텐츠 길이 ("short", "medium", "long")

**Response:**
```json
{
  "content": "# 블로그 마케팅 완벽 가이드: 2024년 최신 전략\n\n## 서론\n...",
  "seo_score": 85,
  "geo_score": 78,
  "copyscape_result": "Pass"
}
```

## 에러 응답

모든 API는 일관된 에러 형식을 사용합니다:

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "status_code": 400
}
```

### 주요 에러 코드

- `400 Bad Request`: 잘못된 요청 파라미터
- `401 Unauthorized`: 인증 실패
- `404 Not Found`: 존재하지 않는 리소스
- `429 Too Many Requests`: API 사용량 한도 초과
- `500 Internal Server Error`: 서버 내부 오류

## 사용 예시

### cURL 예시

```bash
# 키워드 분석
curl -X POST "http://localhost:8000/api/keywords/analyze" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "블로그", "country": "KR"}'

# 제목 생성
curl -X POST "http://localhost:8000/api/titles/generate" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "블로그", "language": "ko", "count": 3}'

# 콘텐츠 생성
curl -X POST "http://localhost:8000/api/content/generate" \
  -H "Content-Type: application/json" \
  -d '{"title": "블로그 시작하기", "keywords": "워드프레스, SEO"}'
```

### JavaScript 예시

```javascript
// 키워드 분석
const analyzeKeywords = async (keyword) => {
  const response = await fetch('http://localhost:8000/api/keywords/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      keyword: keyword,
      country: 'KR',
      max_results: 10
    })
  });
  
  const data = await response.json();
  return data;
};

// 제목 생성
const generateTitles = async (keyword) => {
  const response = await fetch('http://localhost:8000/api/titles/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      keyword: keyword,
      language: 'ko',
      tone: 'professional',
      count: 5
    })
  });
  
  const data = await response.json();
  return data;
};
```

## 제한사항

### 사용량 제한
- 키워드 분석: 시간당 100회
- 제목 생성: 시간당 50회  
- 콘텐츠 생성: 시간당 20회

### 콘텐츠 제한
- 키워드 길이: 최대 500자
- 제목 길이: 최대 200자
- 생성 콘텐츠: 최대 5000자

## 향후 추가 예정 기능

### 인증 API
- `POST /api/auth/login` - 로그인
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/refresh` - 토큰 갱신

### 사용자 관리 API
- `GET /api/user/profile` - 프로필 조회
- `PUT /api/user/profile` - 프로필 수정
- `GET /api/user/history` - 사용 이력

### 플랫폼 연동 API
- `POST /api/platforms/wordpress/publish` - 워드프레스 포스팅
- `POST /api/platforms/blogspot/publish` - 블로그스팟 포스팅
- `GET /api/platforms/status` - 포스팅 상태 확인

### 분석 API
- `GET /api/analytics/keywords` - 키워드 분석 통계
- `GET /api/analytics/content` - 콘텐츠 성과 분석
- `GET /api/analytics/seo` - SEO 분석 리포트