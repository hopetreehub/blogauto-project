from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="블로그 자동화 API (데모버전)")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청 모델들
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

# 응답 모델들
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

# API 엔드포인트들
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running", "endpoints": "ready"}

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    return DashboardStats(
        keywords_analyzed=25,
        titles_generated=150,
        content_generated=42,
        posts_published=0
    )

@app.post("/api/keywords/analyze", response_model=List[KeywordAnalysisResponse])
async def analyze_keywords(request: KeywordAnalysisRequest):
    # 데모 응답 데이터
    demo_keywords = [
        {
            "keyword": f"{request.keyword} 방법",
            "search_volume": 12000,
            "competition": 0.65,
            "cpc": 850.0,
            "opportunity_score": 78.5
        },
        {
            "keyword": f"{request.keyword} 가이드",
            "search_volume": 8500,
            "competition": 0.45,
            "cpc": 720.0,
            "opportunity_score": 82.3
        },
        {
            "keyword": f"{request.keyword} 팁",
            "search_volume": 15000,
            "competition": 0.78,
            "cpc": 920.0,
            "opportunity_score": 75.2
        },
        {
            "keyword": f"{request.keyword} 노하우",
            "search_volume": 6800,
            "competition": 0.35,
            "cpc": 650.0,
            "opportunity_score": 85.7
        },
        {
            "keyword": f"{request.keyword} 전략",
            "search_volume": 9200,
            "competition": 0.58,
            "cpc": 780.0,
            "opportunity_score": 79.1
        }
    ]
    
    return [KeywordAnalysisResponse(**kw) for kw in demo_keywords[:request.max_results]]

@app.post("/api/titles/generate", response_model=List[TitleGenerationResponse])
async def generate_titles(request: TitleGenerationRequest):
    demo_titles = [
        {
            "title": f"🚀 {request.keyword}으로 성공하는 5가지 핵심 전략",
            "score": 88.5,
            "reason": "높은 클릭률을 유도하는 숫자와 이모지 활용"
        },
        {
            "title": f"{request.keyword} 완전 정복: 초보자를 위한 단계별 가이드",
            "score": 85.2,
            "reason": "타겟 독자 명시와 구체적인 혜택 제시"
        },
        {
            "title": f"전문가가 알려주는 {request.keyword}의 모든 것",
            "score": 82.7,
            "reason": "권위성과 전문성을 강조한 제목"
        },
        {
            "title": f"{request.keyword}로 월 수익 100만원? 실제 성공 사례 공개",
            "score": 90.1,
            "reason": "구체적인 숫자와 호기심 유발 요소"
        },
        {
            "title": f"2024년 최신 {request.keyword} 트렌드와 실전 활용법",
            "score": 86.8,
            "reason": "시의성과 실용성을 강조한 제목"
        }
    ]
    
    return [TitleGenerationResponse(**title) for title in demo_titles[:request.count]]

@app.post("/api/content/generate", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    demo_content = f"""
# {request.title}

## 들어가며

{request.keyword}에 대한 관심이 높아지고 있는 요즘, 많은 분들이 효과적인 방법을 찾고 계실 것입니다. 

## 핵심 포인트

### 1. 기본 원리 이해하기
{request.keyword}의 기본 개념과 원리를 이해하는 것이 첫 번째 단계입니다.

### 2. 실전 적용 방법
이론을 바탕으로 실제 상황에 적용하는 구체적인 방법들을 알아보겠습니다.

### 3. 주의사항 및 팁
- 꾸준한 학습과 실습이 중요합니다
- 최신 트렌드를 파악하여 적용하세요
- 데이터를 기반으로 한 의사결정을 하세요

## 마무리

{request.keyword}은 올바른 접근 방법과 꾸준한 노력으로 충분히 성공할 수 있는 영역입니다. 
이 글이 여러분의 성공에 도움이 되기를 바랍니다.

*이 콘텐츠는 AI가 생성한 데모 버전입니다.*
"""
    
    return ContentGenerationResponse(
        content=demo_content.strip(),
        seo_score=85.4,
        word_count=len(demo_content.replace(" ", "")),
        readability_score=78.2
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)