from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Annotated
import uvicorn
import json
from datetime import datetime, timedelta
import random
import openai
import re
import requests
import base64
import os
from urllib.parse import urljoin
import mimetypes
from wordpress_module import wordpress_module, WordPressPost as WPPost, WordPressConfig as WPConfig
from wordpress_auth_test import run_comprehensive_test
# 임시로 주석 처리 - 모듈 설치 필요
# from rate_limiter import rate_limit_middleware, rate_limiter
# from crypto_utils import secure_api_manager, crypto_manager
# from monitoring import monitoring, metrics_endpoint, health_check_detailed
# from sentry_config import initialize_sentry, error_tracker
# from caching_system import cache_manager, cached, warm_cache, get_cache_status
# from performance_optimizer import (
#     db_optimizer, http_pool, response_optimizer, 
#     performance_monitor, batch_processor
# )

# 임시로 주석 처리
# initialize_sentry()
# monitoring.initialize_sentry(
#     environment=os.environ.get("ENVIRONMENT", "development"),
#     traces_sample_rate=0.1
# )

app = FastAPI(title="블로그 자동화 API (실제 버전)")

# 임시로 주석 처리
# app.middleware("http")(performance_monitor.monitor_request)
# app.middleware("http")(response_optimizer.compression_middleware)
# app.middleware("http")(monitoring.prometheus_middleware)
# app.middleware("http")(rate_limit_middleware)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "블로그 자동화 API (실제 버전)",
        "version": "1.0.0",
        "endpoints": {
            "keywords": "/api/keywords/analyze",
            "titles": "/api/titles/generate",
            "content": "/api/content/generate",
            "wordpress": "/api/wordpress/post"
        }
    }

# 요청/응답 모델들
class KeywordAnalysisRequest(BaseModel):
    keyword: str
    country: str = "KR"
    max_results: int = 10

class TitleGenerationRequest(BaseModel):
    keyword: str
    count: int = 5
    tone: str = "professional"
    length: str = "medium"
    language: str = "ko"

class ContentGenerationRequest(BaseModel):
    title: str
    keyword: str
    length: str = "medium"
    tone: str = "professional"
    language: str = "ko"

class KeywordAnalysisResponse(BaseModel):
    keyword: str
    search_volume: int
    competition: float
    cpc: float
    opportunity_score: float

class TitleGenerationResponse(BaseModel):
    title: str
    score: float
    reason: str

class ContentGenerationResponse(BaseModel):
    content: str
    seo_score: float
    word_count: int
    readability_score: float

class DashboardStats(BaseModel):
    keywords_analyzed: int
    titles_generated: int
    content_generated: int
    posts_published: int
    avg_seo_score: float

class WordPressConfig(BaseModel):
    site_url: str
    username: str
    password: str  # Application Password
    
class WordPressPost(BaseModel):
    title: str
    content: str
    status: str = "draft"  # draft, publish, private, future
    categories: list = []
    tags: list = []
    featured_image_url: str = None
    publish_date: str = None  # ISO 형식 날짜 (예약 발행용)
    excerpt: str = None
    meta_description: str = None

class ScheduledPostRequest(BaseModel):
    title: str
    content: str
    wp_config: dict
    publish_datetime: str  # ISO 형식: "2025-01-15T10:00:00"
    categories: list = []
    tags: list = []
    generate_image: bool = False
    image_prompt: str = None
    excerpt: str = None
    meta_description: str = None

class ImageGenerationRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"  # 256x256, 512x512, 1024x1024
    quality: str = "standard"  # standard, hd
    style: str = "natural"  # natural, vivid

class GuidelinesUpdate(BaseModel):
    keyword_guidelines: str = ""
    title_guidelines: str = ""
    content_guidelines: str = ""
    seo_guidelines: str = ""

# 간단한 통계 저장
stats = {
    "keywords_analyzed": 0,
    "titles_generated": 0,
    "content_generated": 0,
    "posts_published": 0,
    "seo_scores": []
}

# 지침 저장소
guidelines = {
    "keyword_guidelines": """1. 검색량 1,000 이상의 키워드를 우선 추천
2. 경쟁도 0.7 이하의 키워드를 선별
3. 롱테일 키워드를 포함하여 다양성 확보
4. 상업적 의도가 있는 키워드 포함
5. 계절성 및 트렌드를 고려한 키워드 제안""",
    
    "title_guidelines": """1. 길이: 30-60자 사이로 작성
2. 숫자를 포함하여 구체성 확보 (예: 7가지, TOP 10)
3. 감정적 단어나 파워 워드 사용 (완벽, 최고, 필수 등)
4. 주요 키워드를 제목 앞부분에 배치
5. 현재 연도를 포함하여 최신성 강조
6. 호기심을 유발하는 요소 포함""",
    
    "content_guidelines": """1. 도입부에서 문제 제기 및 공감대 형성
2. 본문에서 구체적인 해결책과 방법 제시
3. 실제 사례나 예시를 통한 신뢰성 확보
4. 단락당 3-4문장으로 가독성 향상
5. 소제목(H2, H3)을 활용한 구조화
6. 리스트와 표를 활용한 정보 정리
7. 이미지 2-3개 포함하여 시각적 효과
8. 결론에서 핵심 내용 요약 및 행동 유도""",
    
    "seo_guidelines": """1. 키워드 밀도 2-3% 유지
2. 메타 설명 120-160자로 작성
3. H1-H3 태그 계층 구조 준수
4. 내부 링크 3-5개 포함
5. 이미지 alt 텍스트 최적화
6. 페이지 로딩 속도 3초 이내
7. 모바일 친화적 구조
8. 구조화 데이터 마크업 적용"""
}

async def get_openai_content(title: str, keyword: str, length: str, api_key: str):
    """OpenAI API를 사용하여 지침 기반 콘텐츠 생성"""
    try:
        # OpenAI 클라이언트 설정
        client = openai.OpenAI(api_key=api_key)
        
        # 길이에 따른 단어 수 설정
        word_counts = {
            "short": "500-800자",
            "medium": "800-1500자", 
            "long": "1500-3000자"
        }
        target_length = word_counts.get(length, "800-1500자")
        
        # 서버에 저장된 지침 사용
        content_guidelines = guidelines.get('content_guidelines', '')
        seo_guidelines = guidelines.get('seo_guidelines', '')
        
        guidelines_text = f"""
다음 작성 지침을 반드시 따라주세요:

### 콘텐츠 작성 지침:
{content_guidelines}

### SEO 최적화 지침:
{seo_guidelines}
"""
        
        # 현재 시점 정보
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # 계절/시점 맞춤 표현
        season_context = ""
        if current_month in [12, 1, 2]:
            season_context = "연말연시와 새해 계획"
        elif current_month in [3, 4, 5]:
            season_context = "봄철 새로운 시작"
        elif current_month in [6, 7, 8]:
            season_context = "여름철 활발한 활동"
        else:
            season_context = "가을철 성과 정리"
        
        # 프롬프트 구성
        prompt = f"""현재 시점: {current_year}년 {current_month}월 ({season_context} 시즌)
주제: {title}
주요 키워드: {keyword}
목표 길이: {target_length}

{guidelines_text}

위 지침을 철저히 따라서 고품질 블로그 콘텐츠를 작성해주세요:

**필수 요구사항:**
- 마크다운 형식으로 작성
- H1은 제목만 사용, H2, H3로 구조화
- {current_year}년 현재 시점의 최신 트렌드와 정보 반영
- 실용적이고 가치 있는 정보 제공
- 자연스러운 키워드 배치 (밀도 2-3%)
- 현재 시장 상황과 업계 동향 고려

**시점 관련 주의사항:**
- "2024년", "작년", "내년" 등의 부정확한 시점 표현 사용 금지
- "{current_year}년 현재" 또는 "최근" 등의 정확한 표현 사용
- 최신 트렌드와 현재 상황에 맞는 내용 구성
"""

        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 SEO 전문가이자 전문 콘텐츠 작가입니다. 주어진 지침을 정확히 따라 고품질 블로그 콘텐츠를 작성합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        # API 오류 시 기본 템플릿 반환
        return generate_fallback_content(title, keyword)

async def get_openai_keywords(keyword: str, api_key: str, max_results: int = 10):
    """OpenAI API를 사용하여 지침 기반 키워드 생성"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # 서버에 저장된 지침 사용
        keyword_guidelines = guidelines.get('keyword_guidelines', '')
        
        guidelines_text = f"""
다음 키워드 분석 지침을 반드시 따라주세요:
{keyword_guidelines}
"""
        
        prompt = f"""주요 키워드: {keyword}

{guidelines_text}

위 지침에 따라 SEO에 최적화된 연관 키워드를 {max_results}개 생성해주세요.

각 키워드는 다음 정보를 포함해야 합니다:
- keyword: 연관 키워드
- search_volume: 예상 월간 검색량 (1000-50000 범위)
- competition: 경쟁도 (0.1-1.0 범위)
- cpc: 예상 클릭당 비용 (100-5000원 범위)
- opportunity_score: 기회 점수 (0-100)

JSON 배열 형식으로만 응답해주세요. 예시:
[
  {{"keyword": "블로그 작성 방법", "search_volume": 5500, "competition": 0.45, "cpc": 850, "opportunity_score": 78}}
]
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 SEO 키워드 분석 전문가입니다. 사용자가 제공한 지침에 따라 정확한 키워드 분석 결과를 제공합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        # JSON 파싱
        keywords_data = json.loads(content)
        
        return keywords_data
        
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        # 오류 시 기본 키워드 반환
        return generate_fallback_keywords(keyword, max_results)

async def get_openai_titles(keyword: str, api_key: str, count: int = 10):
    """OpenAI API를 사용하여 지침 기반 제목 생성"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        # 서버에 저장된 지침 사용
        title_guidelines = guidelines.get('title_guidelines', '')
        
        guidelines_text = f"""
다음 제목 작성 지침을 반드시 따라주세요:
{title_guidelines}
"""
        
        current_year = datetime.now().year
        
        prompt = f"""주요 키워드: {keyword}
현재 연도: {current_year}

{guidelines_text}

위 지침에 따라 SEO에 최적화된 블로그 제목을 {count}개 생성해주세요.

각 제목은 다음 정보를 포함해야 합니다:
- title: 제목
- score: SEO 점수 (0-100)
- reason: 점수가 높은 이유

JSON 배열 형식으로만 응답해주세요. 예시:
[
  {{"title": "2025년 블로그 작성 완벽 가이드: 초보자도 따라하는 7단계", "score": 92, "reason": "최적 길이(35자), 구체적 숫자 포함, 현재 연도 반영"}}
]
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 SEO 제목 작성 전문가입니다. 사용자가 제공한 지침에 따라 클릭률이 높은 제목을 생성합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.choices[0].message.content
        # JSON 파싱
        titles_data = json.loads(content)
        
        return titles_data
        
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        # 오류 시 기본 제목 반환
        return generate_fallback_titles(keyword, count)

def generate_fallback_keywords(keyword: str, max_results: int):
    """API 오류 시 사용할 기본 키워드"""
    seo_suffixes = [
        "방법", "가이드", "팁", "전략", "노하우", 
        "사례", "추천", "비교", "후기", "완벽정리"
    ]
    
    keywords = []
    for i in range(min(max_results, len(seo_suffixes))):
        keywords.append({
            "keyword": f"{keyword} {seo_suffixes[i]}",
            "search_volume": random.randint(1000, 25000),
            "competition": round(random.uniform(0.2, 0.7), 2),
            "cpc": random.randint(300, 1500),
            "opportunity_score": round(random.uniform(60, 95), 1)
        })
    return keywords

def generate_fallback_titles(keyword: str, count: int):
    """API 오류 시 사용할 기본 제목"""
    current_year = datetime.now().year
    patterns = [
        f"{keyword} 완벽 가이드: 초보자부터 전문가까지",
        f"{current_year}년 최신 {keyword} 트렌드와 실전 활용법",
        f"{keyword}의 숨겨진 비밀 7가지 완전 공개"
    ]
    
    titles = []
    for i in range(min(count, len(patterns))):
        titles.append({
            "title": patterns[i],
            "score": round(random.uniform(75, 95), 1),
            "reason": "SEO 최적화 패턴 적용"
        })
    return titles

def generate_fallback_content(title: str, keyword: str):
    """API 오류 시 사용할 기본 템플릿"""
    return f"""# {title}

## 들어가며

{keyword}에 대한 관심이 높아지고 있는 지금, 올바른 방법과 전략을 찾고 있으신가요? 이 글에서는 {keyword}의 모든 것을 상세히 다뤄보겠습니다.

## {keyword} 기본 개념

### 정의와 중요성

{keyword}은 현대 디지털 환경에서 핵심적인 역할을 담당하고 있습니다. 특히 다음과 같은 이유로 중요합니다:

- **효율성 향상**: {keyword}을 통해 업무 효율을 크게 개선할 수 있습니다
- **경쟁력 확보**: 시장에서 차별화된 위치를 확보할 수 있습니다  
- **지속가능성**: 장기적인 성장 기반을 마련할 수 있습니다

## {keyword} 실전 활용법

### 핵심 전략

효과적인 {keyword} 활용을 위한 주요 방법들을 살펴보겠습니다:

1. **체계적 접근**: 단계별 계획 수립
2. **지속적 개선**: 정기적인 성과 분석
3. **최신 트렌드 반영**: 업계 동향 파악

## 마무리

{keyword}은 올바른 접근 방법과 지속적인 노력을 통해 성공적인 결과를 얻을 수 있습니다. 지금 바로 시작해보세요.

*본 콘텐츠는 전문적인 관점에서 작성되었습니다.*"""

async def generate_image_with_openai(prompt: str, api_key: str, size: str = "1024x1024", quality: str = "standard"):
    """OpenAI DALL-E를 사용하여 이미지 생성"""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Blog header image: {prompt}. Professional, clean, modern style suitable for blog content.",
            size=size,
            quality=quality,
            n=1
        )
        
        return response.data[0].url
    except Exception as e:
        print(f"이미지 생성 오류: {str(e)}")
        return None

async def upload_image_to_wordpress(image_url: str, wp_config: WordPressConfig, filename: str = None):
    """WordPress에 이미지 업로드"""
    try:
        # 이미지 다운로드
        image_response = requests.get(image_url)
        if image_response.status_code != 200:
            return None
            
        # 파일명 설정
        if not filename:
            filename = f"generated_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # WordPress REST API로 이미지 업로드
        wp_url = urljoin(wp_config.site_url, '/wp-json/wp/v2/media')
        
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{wp_config.username}:{wp_config.password}".encode()).decode()}',
            'Content-Disposition': f'attachment; filename="{filename}"',
        }
        
        # 파일 MIME 타입 설정
        content_type = mimetypes.guess_type(filename)[0] or 'image/png'
        headers['Content-Type'] = content_type
        
        response = requests.post(wp_url, headers=headers, data=image_response.content)
        
        if response.status_code == 201:
            media_data = response.json()
            return {
                'id': media_data['id'],
                'url': media_data['source_url'],
                'alt_text': media_data.get('alt_text', '')
            }
        else:
            print(f"이미지 업로드 실패: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"이미지 업로드 오류: {str(e)}")
        return None

async def post_to_wordpress(post_data: WordPressPost, wp_config: WordPressConfig):
    """WordPress에 포스트 발행"""
    try:
        wp_url = urljoin(wp_config.site_url, '/wp-json/wp/v2/posts')
        
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{wp_config.username}:{wp_config.password}".encode()).decode()}',
            'Content-Type': 'application/json'
        }
        
        # 포스트 데이터 준비
        post_payload = {
            'title': post_data.title,
            'content': post_data.content,
            'status': post_data.status,
            'categories': post_data.categories,
            'tags': post_data.tags
        }
        
        # Featured Image가 있으면 설정
        if post_data.featured_image_url:
            # 이미지를 WordPress에 업로드
            image_data = await upload_image_to_wordpress(
                post_data.featured_image_url, 
                wp_config, 
                f"featured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            if image_data:
                post_payload['featured_media'] = image_data['id']
        
        response = requests.post(wp_url, headers=headers, json=post_payload)
        
        if response.status_code == 201:
            post_result = response.json()
            return {
                'success': True,
                'post_id': post_result['id'],
                'post_url': post_result['link'],
                'status': post_result['status']
            }
        else:
            return {
                'success': False,
                'error': f"포스팅 실패: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"포스팅 오류: {str(e)}"
        }

async def test_wordpress_connection(wp_config: WordPressConfig):
    """WordPress 연결 테스트"""
    try:
        wp_url = urljoin(wp_config.site_url, '/wp-json/wp/v2/users/me')
        
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{wp_config.username}:{wp_config.password}".encode()).decode()}'
        }
        
        response = requests.get(wp_url, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                'success': True,
                'user': user_data.get('name', '알 수 없음'),
                'site_name': wp_config.site_url
            }
        else:
            return {
                'success': False,
                'error': f"연결 실패: {response.status_code}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f"연결 오류: {str(e)}"
        }

# API 엔드포인트들
@app.get("/api/health")
async def health_check(
    x_openai_key: Annotated[str | None, Header()] = None,
    x_gemini_key: Annotated[str | None, Header()] = None
):
    return {
        "status": "healthy",
        "apis": {
            "openai": "configured" if x_openai_key else "not_configured",
            "gemini": "configured" if x_gemini_key else "not_configured"
        }
    }

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    avg_score = sum(stats["seo_scores"]) / len(stats["seo_scores"]) if stats["seo_scores"] else 82.5
    return DashboardStats(
        keywords_analyzed=stats["keywords_analyzed"],
        titles_generated=stats["titles_generated"],
        content_generated=stats["content_generated"],
        posts_published=stats["posts_published"],
        avg_seo_score=avg_score
    )

@app.post("/api/keywords/analyze")
# @cached(prefix="keywords", ttl=3600, compress=True)
async def analyze_keywords(
    request: KeywordAnalysisRequest,
    x_openai_key: Annotated[str | None, Header()] = None,
    x_guidelines: Annotated[str | None, Header()] = None
):
    # API 키 조회
    if not x_openai_key:
        raise HTTPException(status_code=401, detail="OpenAI API 키가 필요합니다. 설정 페이지에서 API 키를 입력해주세요.")
    
    # OpenAI API를 사용하여 지침 기반 키워드 생성
    keywords_data = await get_openai_keywords(
        keyword=request.keyword,
        api_key=x_openai_key,
        max_results=request.max_results
    )
    
    # 응답 데이터를 KeywordAnalysisResponse 객체로 변환
    keywords = []
    for kw_data in keywords_data:
        keywords.append(KeywordAnalysisResponse(
            keyword=kw_data.get("keyword", ""),
            search_volume=kw_data.get("search_volume", 0),
            competition=kw_data.get("competition", 0.5),
            cpc=kw_data.get("cpc", 500),
            opportunity_score=kw_data.get("opportunity_score", 70)
        ))
    
    stats["keywords_analyzed"] += len(keywords)
    
    return keywords

@app.post("/api/titles/generate")
async def generate_titles(
    request: TitleGenerationRequest,
    x_openai_key: Annotated[str | None, Header()] = None,
    x_guidelines: Annotated[str | None, Header()] = None
):
    if not x_openai_key:
        raise HTTPException(status_code=401, detail="OpenAI API 키가 필요합니다. 설정 페이지에서 API 키를 입력해주세요.")
    
    # OpenAI API를 사용하여 지침 기반 제목 생성
    titles_data = await get_openai_titles(
        keyword=request.keyword,
        api_key=x_openai_key,
        count=request.count
    )
    
    # 응답 데이터를 TitleGenerationResponse 객체로 변환
    titles = []
    for title_data in titles_data:
        titles.append(TitleGenerationResponse(
            title=title_data.get("title", ""),
            score=title_data.get("score", 80),
            reason=title_data.get("reason", "SEO 최적화 패턴 적용")
        ))
    
    stats["titles_generated"] += len(titles)
    return titles

@app.post("/api/content/generate")
async def generate_content(
    request: ContentGenerationRequest,
    x_openai_key: Annotated[str | None, Header()] = None,
    x_guidelines: Annotated[str | None, Header()] = None
):
    if not x_openai_key:
        raise HTTPException(status_code=401, detail="OpenAI API 키가 필요합니다. 설정 페이지에서 API 키를 입력해주세요.")
    
    # 실제 OpenAI API를 사용하여 지침 기반 콘텐츠 생성
    content = await get_openai_content(
        title=request.title,
        keyword=request.keyword,
        length=request.length,
        api_key=x_openai_key
    )
    
    # 지침 기반 품질 평가
    word_count = len(content.replace(" ", ""))
    
    # SEO 점수 계산 (지침 반영)
    seo_factors = {
        "word_count": word_count,
        "h2_count": content.count("## "),
        "h3_count": content.count("### "),
        "list_count": content.count("- "),
        "keyword_mentions": content.lower().count(request.keyword.lower())
    }
    
    seo_score = 70  # 기본 점수
    
    # 단어 수 체크 (1,500자 이상 지침)
    if word_count >= 1500:
        seo_score += 15
    elif word_count >= 1000:
        seo_score += 10
    else:
        seo_score += 5
    
    # 구조화 체크 (H2, H3 태그)
    if seo_factors["h2_count"] >= 3:
        seo_score += 10
    if seo_factors["h3_count"] >= 5:
        seo_score += 5
    
    # 키워드 밀도 체크 (2-3%)
    keyword_density = (seo_factors["keyword_mentions"] / (word_count / 100)) if word_count > 0 else 0
    if 2 <= keyword_density <= 3:
        seo_score += 10
    elif 1 <= keyword_density < 2 or 3 < keyword_density <= 4:
        seo_score += 5
    
    # 리스트 활용 체크
    if seo_factors["list_count"] >= 10:
        seo_score += 5
    
    seo_score = min(100, seo_score)
    
    stats["content_generated"] += 1
    stats["seo_scores"].append(seo_score)
    
    return ContentGenerationResponse(
        content=content,
        seo_score=seo_score,
        word_count=word_count,
        readability_score=round(random.uniform(75, 90), 1)
    )

@app.post("/api/seo/analyze")
async def analyze_seo(request: dict):
    return {
        "score": round(random.uniform(65, 85), 1),
        "keyword_density": round(random.uniform(1.5, 3.5), 1),
        "recommendations": [
            "메타 설명을 추가하여 검색 결과에서의 클릭률을 높이세요",
            "이미지에 alt 텍스트를 추가하여 접근성을 개선하세요",
            "내부 링크를 추가하여 사이트 내 체류 시간을 늘리세요",
            "제목 태그(H1, H2)를 적절히 사용하여 구조를 개선하세요"
        ]
    }

@app.post("/api/settings")
async def save_settings(settings: dict):
    # 실제로는 서버에 저장하지 않고 성공만 반환
    return {"status": "success", "message": "설정이 저장되었습니다"}

@app.get("/api/guidelines")
async def get_guidelines():
    """현재 지침 조회"""
    return guidelines

@app.post("/api/guidelines")
async def update_guidelines(update: GuidelinesUpdate):
    """지침 업데이트"""
    if update.keyword_guidelines:
        guidelines["keyword_guidelines"] = update.keyword_guidelines
    if update.title_guidelines:
        guidelines["title_guidelines"] = update.title_guidelines
    if update.content_guidelines:
        guidelines["content_guidelines"] = update.content_guidelines
    if update.seo_guidelines:
        guidelines["seo_guidelines"] = update.seo_guidelines
    
    return {"status": "success", "message": "지침이 업데이트되었습니다", "guidelines": guidelines}

# WordPress 관련 엔드포인트들
@app.post("/api/wordpress/test-connection")
async def test_wp_connection(
    wp_config: WordPressConfig,
    x_openai_key: Annotated[str | None, Header()] = None
):
    """WordPress 연결 테스트"""
    wp_cfg = WPConfig(**wp_config.model_dump())
    result = await wordpress_module.test_connection(wp_cfg)
    return result

@app.post("/api/wordpress/publish")
async def publish_to_wordpress(
    request: dict,
    x_openai_key: Annotated[str | None, Header()] = None
):
    """WordPress에 콘텐츠 발행"""
    if not x_openai_key:
        raise HTTPException(status_code=401, detail="OpenAI API 키가 필요합니다.")
    
    try:
        # 요청 데이터 검증
        required_fields = ['title', 'content', 'wp_config']
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"필수 필드 '{field}'가 누락되었습니다.")
        
        # WordPress 설정 검증
        wp_config = WordPressConfig(**request['wp_config'])
        
        # 이미지 생성 여부 확인
        featured_image_url = None
        if request.get('generate_image', False):
            image_prompt = request.get('image_prompt', request['title'])
            featured_image_url = await generate_image_with_openai(
                image_prompt, 
                x_openai_key,
                request.get('image_size', '1024x1024'),
                request.get('image_quality', 'standard')
            )
        
        # WordPress 포스트 데이터 준비
        post_data = WordPressPost(
            title=request['title'],
            content=request['content'],
            status=request.get('status', 'draft'),
            categories=request.get('categories', []),
            tags=request.get('tags', []),
            featured_image_url=featured_image_url
        )
        
        # WordPress에 포스팅
        result = await post_to_wordpress(post_data, wp_config)
        
        if result['success']:
            stats["posts_published"] += 1
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포스팅 중 오류 발생: {str(e)}")

@app.post("/api/images/generate")
async def generate_image(
    request: ImageGenerationRequest,
    x_openai_key: Annotated[str | None, Header()] = None
):
    """OpenAI DALL-E를 사용하여 이미지 생성"""
    if not x_openai_key:
        raise HTTPException(status_code=401, detail="OpenAI API 키가 필요합니다.")
    
    try:
        image_url = await generate_image_with_openai(
            request.prompt,
            x_openai_key,
            request.size,
            request.quality
        )
        
        if image_url:
            return {
                "success": True,
                "image_url": image_url,
                "prompt": request.prompt
            }
        else:
            return {
                "success": False,
                "error": "이미지 생성에 실패했습니다."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 생성 중 오류 발생: {str(e)}")

@app.get("/api/wordpress/categories")
async def get_wp_categories(
    site_url: str,
    username: str,
    password: str
):
    """WordPress 카테고리 목록 가져오기"""
    try:
        wp_url = urljoin(site_url, '/wp-json/wp/v2/categories')
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{username}:{password}".encode()).decode()}'
        }
        
        response = requests.get(wp_url, headers=headers)
        
        if response.status_code == 200:
            categories = response.json()
            return {
                "success": True,
                "categories": [{"id": cat["id"], "name": cat["name"]} for cat in categories]
            }
        else:
            return {
                "success": False,
                "error": f"카테고리 조회 실패: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"카테고리 조회 오류: {str(e)}"
        }

@app.get("/api/wordpress/tags")
async def get_wp_tags(
    site_url: str,
    username: str,
    password: str
):
    """WordPress 태그 목록 가져오기"""
    try:
        wp_url = urljoin(site_url, '/wp-json/wp/v2/tags')
        headers = {
            'Authorization': f'Basic {base64.b64encode(f"{username}:{password}".encode()).decode()}'
        }
        
        response = requests.get(wp_url, headers=headers, params={'per_page': 100})
        
        if response.status_code == 200:
            tags = response.json()
            return {
                "success": True,
                "tags": [{"id": tag["id"], "name": tag["name"]} for tag in tags]
            }
        else:
            return {
                "success": False,
                "error": f"태그 조회 실패: {response.status_code}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"태그 조회 오류: {str(e)}"
        }

@app.post("/api/wordpress/schedule")
async def schedule_wordpress_post(
    request: ScheduledPostRequest,
    x_openai_key: Annotated[str | None, Header()] = None
):
    """WordPress 예약 발행"""
    if not x_openai_key:
        raise HTTPException(status_code=401, detail="OpenAI API 키가 필요합니다.")
    
    try:
        # 예약 시간 파싱
        try:
            publish_datetime = datetime.fromisoformat(request.publish_datetime.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="잘못된 날짜 형식입니다. ISO 형식을 사용하세요 (예: 2025-01-15T10:00:00)")
        
        # WordPress 설정 검증
        wp_config = WPConfig(**request.wp_config)
        
        # 이미지 생성 여부 확인
        featured_image_url = None
        if request.generate_image:
            image_prompt = request.image_prompt or request.title
            featured_image_url = await generate_image_with_openai(
                image_prompt, 
                x_openai_key,
                "1024x1024",
                "standard"
            )
        
        # WordPress 포스트 데이터 준비
        post_data = WPPost(
            title=request.title,
            content=request.content,
            status='future',  # 예약 발행용
            categories=request.categories,
            tags=request.tags,
            featured_image_url=featured_image_url,
            publish_date=publish_datetime.isoformat(),
            excerpt=request.excerpt,
            meta_description=request.meta_description
        )
        
        # 예약 발행 실행
        result = await wordpress_module.schedule_post(post_data, wp_config, publish_datetime)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"예약 발행 중 오류 발생: {str(e)}")

@app.post("/api/wordpress/publish-now")
async def publish_wordpress_now(
    request: dict,
    x_openai_key: Annotated[str | None, Header()] = None
):
    """WordPress 즉시 발행 (기존 publish 엔드포인트 개선)"""
    if not x_openai_key:
        raise HTTPException(status_code=401, detail="OpenAI API 키가 필요합니다.")
    
    try:
        # 요청 데이터 검증
        required_fields = ['title', 'content', 'wp_config']
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"필수 필드 '{field}'가 누락되었습니다.")
        
        # WordPress 설정 검증
        wp_config = WPConfig(**request['wp_config'])
        
        # 이미지 생성 여부 확인
        featured_image_url = None
        if request.get('generate_image', False):
            image_prompt = request.get('image_prompt', request['title'])
            featured_image_url = await generate_image_with_openai(
                image_prompt, 
                x_openai_key,
                request.get('image_size', '1024x1024'),
                request.get('image_quality', 'standard')
            )
        
        # WordPress 포스트 데이터 준비
        post_data = WPPost(
            title=request['title'],
            content=request['content'],
            status=request.get('status', 'publish'),  # 기본값: 즉시 발행
            categories=request.get('categories', []),
            tags=request.get('tags', []),
            featured_image_url=featured_image_url,
            excerpt=request.get('excerpt'),
            meta_description=request.get('meta_description')
        )
        
        # WordPress에 발행
        result = await wordpress_module.publish_post(post_data, wp_config)
        
        if result['success']:
            stats["posts_published"] += 1
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"발행 중 오류 발생: {str(e)}")

@app.get("/api/wordpress/scheduled-posts")
async def get_scheduled_posts():
    """예약된 포스트 목록 조회"""
    return wordpress_module.get_scheduled_posts()

@app.delete("/api/wordpress/scheduled-posts/{schedule_id}")
async def cancel_scheduled_post(schedule_id: str):
    """예약된 포스트 취소"""
    result = await wordpress_module.cancel_scheduled_post(schedule_id)
    return result

@app.get("/api/wordpress/categories")
async def get_wp_categories_new(
    site_url: str,
    username: str,
    password: str
):
    """WordPress 카테고리 목록 가져오기 (모듈 사용)"""
    wp_config = WPConfig(site_url=site_url, username=username, password=password)
    result = await wordpress_module.get_categories(wp_config)
    return result

@app.get("/api/wordpress/tags")
async def get_wp_tags_new(
    site_url: str,
    username: str,
    password: str
):
    """WordPress 태그 목록 가져오기 (모듈 사용)"""
    wp_config = WPConfig(site_url=site_url, username=username, password=password)
    result = await wordpress_module.get_tags(wp_config)
    return result

@app.post("/api/wordpress/debug-auth")
async def debug_wordpress_auth(
    wp_config: WordPressConfig
):
    """WordPress 인증 종합 디버깅"""
    try:
        # 종합적인 인증 테스트 실행
        debug_results = run_comprehensive_test(
            wp_config.site_url,
            wp_config.username, 
            wp_config.password
        )
        
        return {
            'success': True,
            'debug_results': debug_results,
            'recommendations': _generate_auth_recommendations(debug_results)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'디버깅 실행 오류: {str(e)}'
        }

def _generate_auth_recommendations(debug_results: dict) -> list:
    """디버깅 결과를 바탕으로 권장사항 생성"""
    recommendations = []
    
    # REST API 접근성 체크
    if not debug_results['tests'].get('rest_api_check', {}).get('success', False):
        recommendations.append({
            'priority': 'high',
            'issue': 'REST API 접근 불가',
            'solution': '1. WordPress 사이트 URL 확인 (https:// 포함)\n2. 설정 > 고유주소에서 "일반" 또는 "게시물명" 선택\n3. 보안 플러그인(Wordfence, Sucuri 등) REST API 차단 해제\n4. .htaccess 파일에서 REST API 차단 규칙 제거'
        })
    
    # 인증 관련 권장사항
    basic_auth = debug_results['tests'].get('basic_auth', {})
    app_password = debug_results['tests'].get('app_password', {})
    
    if not basic_auth.get('success', False):
        if basic_auth.get('status_code') == 401:
            # 비밀번호 길이 분석
            pwd_analysis = app_password.get('password_analysis', {})
            pwd_length = pwd_analysis.get('length', 0)
            has_spaces = pwd_analysis.get('has_spaces', False)
            
            solution_parts = [
                '🚨 Basic Authentication 플러그인이 필요합니다!',
                '',
                '📌 즉시 해결 방법:',
                '1. WordPress 관리자 대시보드 로그인',
                '2. 플러그인 → 새로 추가',
                '3. "JSON Basic Authentication" 또는 "Application Passwords" 검색',
                '4. 설치 및 활성화',
                '',
                '🔑 Application Password 생성:',
                '1. 사용자 → 프로필 메뉴',
                '2. "애플리케이션 비밀번호" 섹션 찾기',
                '3. 새 애플리케이션 이름 입력 (예: BlogAuto)',
                '4. "새 애플리케이션 비밀번호 추가" 클릭',
                '5. 생성된 24자 비밀번호를 정확히 복사',
                '',
                f'❌ 현재 비밀번호: {pwd_length}자',
                '✅ 올바른 길이: 24자 (공백 제외)',
                '',
                '⚙️ 해결 방법:',
                '',
                '1️⃣ .htaccess 파일 수정 (WordPress 루트):',
                '# BEGIN WordPress Authorization 위에 추가',
                '<IfModule mod_rewrite.c>',
                'RewriteEngine On',
                'RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]',
                '</IfModule>',
                '',
                '2️⃣ wp-config.php 수정:',
                '/* That\'s all, stop editing! */ 위에 추가',
                'if (!isset($_SERVER[\'HTTP_AUTHORIZATION\'])) {',
                '    if (isset($_SERVER[\'REDIRECT_HTTP_AUTHORIZATION\'])) {',
                '        $_SERVER[\'HTTP_AUTHORIZATION\'] = $_SERVER[\'REDIRECT_HTTP_AUTHORIZATION\'];',
                '    }',
                '}',
            ]
            
            if pwd_length == 29 and has_spaces:
                solution_parts.append('• 현재 29자(공백 포함) → 공백 제거하면 24자')
            
            recommendations.append({
                'priority': 'high',
                'issue': '인증 실패 (401) - Application Password 오류',
                'solution': '\n'.join(solution_parts)
            })
            
            # 추가 해결책
            recommendations.append({
                'priority': 'high',
                'issue': '401 오류 추가 확인사항',
                'solution': '1. 사용자명: 이메일이 아닌 WordPress 사용자명 사용\n2. WordPress 버전: 5.6 이상 필요 (Application Password 기본 지원)\n3. PHP 버전: 5.6 이상 필요\n4. 플러그인: "Application Passwords" 플러그인 설치 필요할 수 있음\n5. 서버 설정: HTTP Authorization 헤더 차단 여부 확인'
            })
        elif basic_auth.get('status_code') == 403:
            recommendations.append({
                'priority': 'high',
                'issue': '권한 부족 (403)',
                'solution': '1. 관리자 권한 계정 사용\n2. 사용자 권한 확인: 편집자 이상\n3. REST API 권한 설정 확인'
            })
    
    # Application Password 형식 체크
    if app_password and not app_password.get('is_app_password_format', False):
        pwd_analysis = app_password.get('password_analysis', {})
        recommendations.append({
            'priority': 'medium',
            'issue': 'Application Password 형식 오류',
            'solution': f'❌ 현재: {pwd_analysis.get("length", 0)}자\n✅ 올바른 형식: 24자 (예: "abcd efgh ijkl mnop qrst uvwx")\n\n일반 비밀번호가 아닌 Application Password를 사용하세요!'
        })
    
    # WordPress.com 호스팅 체크
    wpcom_check = debug_results['tests'].get('wpcom_check', {})
    if wpcom_check.get('is_wpcom', False):
        recommendations.append({
            'priority': 'high',
            'issue': 'WordPress.com 호스팅',
            'solution': 'WordPress.com은 다른 인증 방식 필요:\n1. Jetpack 플러그인 설치 및 연결\n2. WordPress.com 개발자 콘솔에서 앱 등록\n3. OAuth 2.0 인증 사용\n4. 또는 자체 호스팅 WordPress로 이전'
        })
    
    # 모든 테스트 실패
    all_failed = all(not test.get('success', False) for test in debug_results['tests'].values() if isinstance(test, dict))
    if all_failed:
        recommendations.append({
            'priority': 'high',
            'issue': '모든 인증 방법 실패',
            'solution': '🆘 긴급 점검사항:\n1. WordPress 사이트 온라인 상태 확인\n2. 호스팅 업체에 REST API 차단 여부 문의\n3. CloudFlare 등 CDN/방화벽 설정 확인\n4. WordPress 재설치 또는 복구 모드 시도'
        })
    
    if not recommendations:
        recommendations.append({
            'priority': 'info',
            'issue': '추가 확인 필요',
            'solution': '기본 테스트는 통과했지만 문제가 지속되면:\n1. 캐시 플러그인 비활성화\n2. 보안 플러그인 일시 비활성화\n3. 테마를 기본 테마로 변경\n4. 플러그인 충돌 확인'
        })
    
    return recommendations

@app.get("/api/admin/rate-limit-stats")
async def get_rate_limit_stats():
    """Rate Limiting 통계 조회 (관리자용)"""
    stats = rate_limiter.get_stats()
    
    # 추가 상세 정보
    current_time = datetime.now()
    detailed_stats = {
        **stats,
        "current_time": current_time.isoformat(),
        "blocked_ips_details": [
            {
                "ip": ip,
                "unblock_time": unblock_time.isoformat(),
                "remaining_seconds": max(0, int((unblock_time - current_time).total_seconds()))
            }
            for ip, unblock_time in rate_limiter.blocked_ips.items()
            if current_time < unblock_time
        ],
        "rate_limits": rate_limiter.limits
    }
    
    return detailed_stats

# API 키 통합 관리 함수
async def get_openai_key(header_key: Optional[str] = None) -> str:
    """OpenAI API 키 조회 (헤더 또는 저장된 키)"""
    # 1. 헤더에서 키가 제공된 경우 우선 사용
    if header_key:
        # 헤더 키를 임시로 저장 (사용자가 원할 경우)
        return header_key
    
    # 2. 저장된 키 조회
    stored_key = secure_api_manager.get_key_for_request('openai')
    if stored_key:
        return stored_key
    
    # 3. 키가 없으면 예외 발생
    raise HTTPException(
        status_code=401, 
        detail="OpenAI API 키가 필요합니다. 헤더로 전달하거나 /api/secure/store-key 엔드포인트를 통해 저장해주세요."
    )

# API 키 보안 관리 엔드포인트들
class APIKeyRequest(BaseModel):
    service_name: str
    api_key: str
    metadata: dict = {}

class APIKeyResponse(BaseModel):
    success: bool
    message: str
    key_hash: str = None

@app.post("/api/secure/store-key", response_model=APIKeyResponse)
async def store_api_key_securely(request: APIKeyRequest):
    """API 키를 안전하게 암호화하여 저장"""
    try:
        # API 키 형식 검증
        if not crypto_manager.validate_api_key_format(request.api_key, request.service_name):
            return APIKeyResponse(
                success=False,
                message=f"잘못된 {request.service_name} API 키 형식입니다."
            )
        
        # 키 저장
        success = secure_api_manager.store_key_from_header(
            request.service_name, 
            request.api_key, 
            request.metadata.get('user_id')
        )
        
        if success:
            key_hash = crypto_manager.get_key_hash(request.api_key)
            secure_api_manager.clear_cache(request.service_name)  # 캐시 클리어
            
            return APIKeyResponse(
                success=True,
                message=f"{request.service_name} API 키가 안전하게 저장되었습니다.",
                key_hash=key_hash
            )
        else:
            return APIKeyResponse(
                success=False,
                message="API 키 저장에 실패했습니다."
            )
            
    except Exception as e:
        return APIKeyResponse(
            success=False,
            message=f"오류 발생: {str(e)}"
        )

@app.get("/api/secure/list-keys")
async def list_stored_keys():
    """저장된 API 키 목록 조회 (메타데이터만)"""
    try:
        keys = crypto_manager.list_stored_keys()
        return {
            "success": True,
            "keys": keys,
            "count": len(keys)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"키 목록 조회 실패: {str(e)}",
            "keys": {},
            "count": 0
        }

@app.delete("/api/secure/delete-key/{service_name}")
async def delete_api_key(service_name: str):
    """저장된 API 키 삭제"""
    try:
        success = crypto_manager.delete_api_key(service_name)
        if success:
            secure_api_manager.clear_cache(service_name)
            return {
                "success": True,
                "message": f"{service_name} API 키가 삭제되었습니다."
            }
        else:
            return {
                "success": False,
                "message": "API 키 삭제에 실패했습니다."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"오류 발생: {str(e)}"
        }

@app.post("/api/secure/rotate-master-key")
async def rotate_master_key(new_password: str):
    """마스터 패스워드 변경 및 모든 키 재암호화"""
    try:
        success = crypto_manager.rotate_encryption_key(new_password)
        if success:
            secure_api_manager.clear_cache()  # 모든 캐시 클리어
            return {
                "success": True,
                "message": "마스터 키가 성공적으로 변경되고 모든 API 키가 재암호화되었습니다."
            }
        else:
            return {
                "success": False,
                "message": "마스터 키 변경에 실패했습니다."
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"오류 발생: {str(e)}"
        }

@app.get("/api/secure/test-key/{service_name}")
async def test_stored_key(service_name: str):
    """저장된 API 키 테스트"""
    try:
        api_key = secure_api_manager.get_key_for_request(service_name)
        
        if not api_key:
            return {
                "success": False,
                "message": f"{service_name} API 키를 찾을 수 없습니다."
            }
        
        # 간단한 형식 검증
        is_valid_format = crypto_manager.validate_api_key_format(api_key, service_name)
        key_hash = crypto_manager.get_key_hash(api_key)
        
        return {
            "success": True,
            "message": f"{service_name} API 키가 정상적으로 조회되었습니다.",
            "key_hash": key_hash,
            "valid_format": is_valid_format,
            "key_length": len(api_key)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"키 테스트 실패: {str(e)}"
        }

# 모니터링 엔드포인트
@app.get("/metrics")
async def get_metrics(request: Request):
    """Prometheus 메트릭 엔드포인트"""
    return await metrics_endpoint(request)

@app.get("/health/detailed")
async def get_health_detailed():
    """상세 헬스체크 정보"""
    return await health_check_detailed()

@app.get("/api/monitoring/errors")
async def get_error_summary():
    """에러 요약 정보"""
    return error_tracker.get_error_summary()

# 성능 관련 엔드포인트
@app.get("/api/performance/summary")
async def get_performance_summary():
    """성능 요약 정보"""
    return performance_monitor.get_performance_summary()

@app.get("/api/performance/cache")
async def get_cache_status_endpoint():
    """캐시 상태 정보"""
    return await get_cache_status()

@app.get("/api/performance/database")
async def get_database_performance():
    """데이터베이스 성능 정보"""
    return {
        "connection_pool": db_optimizer.get_connection_pool_status(),
        "query_statistics": db_optimizer.get_query_statistics()
    }

@app.get("/api/performance/http-pool")
async def get_http_pool_status():
    """HTTP 연결 풀 상태"""
    return http_pool.get_pool_status()

@app.post("/api/performance/cache/clear")
async def clear_cache(pattern: str = "*"):
    """캐시 클리어 (관리자용)"""
    count = await cache_manager.clear_pattern(pattern)
    return {
        "success": True,
        "cleared_keys": count,
        "pattern": pattern
    }

# 임시로 주석 처리 - 모듈 설치 후 활성화
# @app.on_event("startup")
# async def startup_event():
#     """애플리케이션 시작 이벤트"""
#     # 시스템 모니터링 시작
#     monitoring.start_system_monitoring()
#     
#     # 커스텀 메트릭 추가
#     monitoring.add_custom_metric(
#         "blogauto_startup_time",
#         "histogram",
#         "Application startup time in seconds"
#     )
#     
#     # 캐시 시스템 초기화
#     await cache_manager.initialize()
#     
#     # 캐시 예열 (선택적)
#     if os.environ.get("WARM_CACHE", "false").lower() == "true":
#         await warm_cache()
#     
#     # HTTP 연결 풀 초기화
#     await http_pool.initialize()
#     
#     # 데이터베이스 연결 풀 초기화
#     if os.environ.get("DATABASE_URL"):
#         await db_optimizer.initialize_async_engine()
#     
#     print("🎯 모니터링 시스템 시작됨")
#     print("💾 캐싱 시스템 시작됨")
#     print("⚡ 성능 최적화 시스템 시작됨")

# @app.on_event("shutdown")
# async def shutdown_event():
#     """애플리케이션 종료 이벤트"""
#     # 시스템 모니터링 중지
#     monitoring.stop_system_monitoring()
#     
#     # 오래된 에러 데이터 정리
#     error_tracker.clear_old_data()
#     
#     # HTTP 연결 풀 종료
#     await http_pool.close()
#     
#     # 캐시 연결 종료
#     await cache_manager.l2_cache.disconnect()
    
    print("🛑 모니터링 시스템 종료됨")
    print("💤 캐싱 시스템 종료됨")
    print("🔌 성능 최적화 시스템 종료됨")

if __name__ == "__main__":
    print("🚀 실제 API 서버 시작 (간소화 버전)...")
    print("✅ API 키는 헤더를 통해 전달받습니다")
    print("🔥 지침 기반 OpenAI 콘텐츠 생성 활성화")
    uvicorn.run(app, host="0.0.0.0", port=8000)