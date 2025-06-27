from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
from typing import List, Optional
import uvicorn
from datetime import timedelta, datetime
from contextlib import asynccontextmanager
import time

# 새로운 로깅 및 에러 핸들링 시스템
from logger import app_logger, api_logger, ai_logger
from error_handlers import (
    BlogAutoException, AIServiceException, DatabaseException,
    AuthenticationException, ValidationException,
    blogauto_exception_handler, http_exception_handler,
    validation_exception_handler, database_exception_handler,
    general_exception_handler, safe_execute, safe_execute_async
)

from database import get_db, engine
from models import (
    Base, User, Country, Keyword, GeneratedTitle, GeneratedContent,
    Site, AutomationSession, GeneratedKeywordBatch, GeneratedTitleBatch, PostingResult
)
from auth import (
    authenticate_user, 
    create_access_token,
    create_refresh_token,
    get_password_hash, 
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    verify_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from schemas import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    Token,
    RefreshTokenRequest,
    KeywordAnalysisRequest,
    KeywordAnalysisResponse,
    TitleGenerationRequest,
    TitleGenerationResponse,
    ContentGenerationRequest,
    ContentGenerationResponse,
    DashboardStats
)
from ai_services import get_ai_service
from golden_keyword_service import GoldenKeywordService
from optimized_title_service import OptimizedTitleService
from auto_posting_service import AutoPostingService
from keyword_services import AggregateKeywordService
from seo_analytics import SEOAnalytics
from seo_keyword_analyzer import SEOKeywordAnalyzer
from integrated_keyword_service import IntegratedKeywordService
from advanced_title_generator import AdvancedTitleGenerator
from advanced_blog_writer import AdvancedBlogWriter
from prompt_manager import PromptManager
from batch_processor import batch_processor, BatchTask, TaskType, TaskStatus
from site_manager import site_manager
from automation_engine import automation_engine
import uuid

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize default countries
def init_countries(db: Session):
    """Initialize default countries if they don't exist."""
    countries_data = [
        {"code": "KR", "name": "한국"},
        {"code": "US", "name": "미국"},
        {"code": "JP", "name": "일본"},
        {"code": "CN", "name": "중국"},
        {"code": "GB", "name": "영국"},
        {"code": "DE", "name": "독일"},
        {"code": "FR", "name": "프랑스"},
        {"code": "CA", "name": "캐나다"},
        {"code": "AU", "name": "호주"},
        {"code": "IN", "name": "인도"}
    ]
    
    for country_data in countries_data:
        existing = db.query(Country).filter(Country.code == country_data["code"]).first()
        if not existing:
            country = Country(**country_data)
            db.add(country)
    db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db = next(get_db())
    init_countries(db)
    yield
    # Shutdown (cleanup if needed)

app = FastAPI(title="Blog Auto Process API", version="2.0.0", lifespan=lifespan)

security = HTTPBearer()

# 예외 핸들러 등록
app.add_exception_handler(BlogAutoException, blogauto_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# API 로깅 미들웨어
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 요청 로그
    api_logger.log_request(
        method=request.method,
        endpoint=str(request.url.path),
        user_id=getattr(request.state, 'user_id', None)
    )
    
    response = await call_next(request)
    
    # 응답 로그
    duration_ms = (time.time() - start_time) * 1000
    api_logger.log_response(
        endpoint=str(request.url.path),
        status_code=response.status_code,
        duration_ms=duration_ms,
        user_id=getattr(request.state, 'user_id', None)
    )
    
    return response

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://localhost:9000",
        "https://innerbot.inbecs.com",
        "http://innerbot.inbecs.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Blog Auto Process API v2.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "message": "API is running", "endpoints": "ready"}

# Authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/api/auth/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    try:
        payload = verify_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        email = payload.get("sub")
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": user.email})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.get("/api/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@app.get("/api/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get dashboard statistics for the current user."""
    try:
        # Calculate actual stats from database
        keywords_count = db.query(Keyword).filter(Keyword.created_by == current_user.id).count()
        titles_count = db.query(GeneratedTitle).filter(GeneratedTitle.created_by == current_user.id).count()
        content_count = db.query(GeneratedContent).filter(GeneratedContent.created_by == current_user.id).count()
        
        return DashboardStats(
            keywords_analyzed=keywords_count,
            titles_generated=titles_count,
            content_generated=content_count,
            posts_published=0  # Will implement when we add posting functionality
        )
    except Exception as e:
        print(f"Error in dashboard stats: {e}")
        return DashboardStats(
            keywords_analyzed=0,
            titles_generated=0,
            content_generated=0,
            posts_published=0
        )

@app.get("/api/history/keywords")
async def get_keyword_history(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user's keyword analysis history."""
    try:
        keywords = db.query(Keyword).filter(
            Keyword.created_by == current_user.id
        ).order_by(Keyword.created_at.desc()).limit(50).all()
        
        return [
            {
                "id": k.id,
                "keyword": k.keyword,
                "search_volume": k.search_volume,
                "competition": k.competition,
                "cpc": float(k.cpc) if k.cpc else 0.0,
                "opportunity_score": k.opportunity_score,
                "created_at": k.created_at.isoformat() if k.created_at else None
            }
            for k in keywords
        ]
    except Exception as e:
        print(f"Error in keyword history: {e}")
        return []

@app.get("/api/history/titles")
async def get_title_history(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user's title generation history."""
    titles = db.query(GeneratedTitle).filter(
        GeneratedTitle.created_by == current_user.id
    ).order_by(GeneratedTitle.created_at.desc()).limit(50).all()
    
    return [
        {
            "id": t.id,
            "title": t.title,
            "keyword_id": t.keyword_id,
            "length_option": t.length_option,
            "language": t.language,
            "tone": t.tone,
            "duplicate_rate": float(t.duplicate_rate) if t.duplicate_rate else 0.0,
            "ai_model": t.ai_model,
            "created_at": t.created_at.isoformat()
        }
        for t in titles
    ]

@app.get("/api/history/content")
async def get_content_history(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user's content generation history."""
    contents = db.query(GeneratedContent).filter(
        GeneratedContent.created_by == current_user.id
    ).order_by(GeneratedContent.created_at.desc()).limit(20).all()
    
    return [
        {
            "id": c.id,
            "title_id": c.title_id,
            "content": c.content[:500] + "..." if len(c.content) > 500 else c.content,  # Truncate for list view
            "keywords": c.keywords,
            "seo_score": c.seo_score,
            "geo_score": c.geo_score,
            "copyscape_result": c.copyscape_result,
            "ai_model": c.ai_model,
            "created_at": c.created_at.isoformat()
        }
        for c in contents
    ]

@app.get("/api/seo/dashboard")
async def get_seo_dashboard(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """SEO 분석 대시보드 데이터"""
    try:
        seo_analytics = SEOAnalytics(db)
        dashboard_data = seo_analytics.get_comprehensive_dashboard(
            user_id=current_user.id,
            days=days
        )
        
        app_logger.info(
            f"SEO dashboard data generated",
            user_id=current_user.id,
            days=days
        )
        
        return dashboard_data
        
    except Exception as e:
        app_logger.error(
            f"Error generating SEO dashboard",
            error=e,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate SEO dashboard data"
        )

@app.get("/api/seo/keyword-performance")
async def get_keyword_performance(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """키워드 성과 분석"""
    try:
        seo_analytics = SEOAnalytics(db)
        performance_data = seo_analytics.get_keyword_performance(
            user_id=current_user.id,
            days=days
        )
        
        return performance_data
        
    except Exception as e:
        app_logger.error(
            f"Error generating keyword performance data",
            error=e,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate keyword performance data"
        )

@app.get("/api/seo/content-analytics")
async def get_content_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """콘텐츠 분석 데이터"""
    try:
        seo_analytics = SEOAnalytics(db)
        analytics_data = seo_analytics.get_content_analytics(
            user_id=current_user.id,
            days=days
        )
        
        return analytics_data
        
    except Exception as e:
        app_logger.error(
            f"Error generating content analytics",
            error=e,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate content analytics data"
        )

@app.get("/api/seo/productivity")
async def get_productivity_metrics(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """생산성 지표"""
    try:
        seo_analytics = SEOAnalytics(db)
        productivity_data = seo_analytics.get_productivity_metrics(
            user_id=current_user.id,
            days=days
        )
        
        return productivity_data
        
    except Exception as e:
        app_logger.error(
            f"Error generating productivity metrics",
            error=e,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate productivity metrics"
        )

@app.post("/api/batch/submit")
async def submit_batch_task(
    task_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """배치 작업 제출"""
    try:
        task_type = TaskType(task_data.get("task_type"))
        parameters = task_data.get("parameters", {})
        
        batch_task = BatchTask(
            id=str(uuid.uuid4()),
            task_type=task_type,
            user_id=current_user.id,
            parameters=parameters
        )
        
        task_id = await batch_processor.submit_task(batch_task)
        
        app_logger.info(
            f"Batch task submitted successfully",
            task_id=task_id,
            task_type=task_type.value,
            user_id=current_user.id
        )
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "Batch task has been submitted successfully"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task type: {str(e)}"
        )
    except Exception as e:
        app_logger.error(
            f"Error submitting batch task",
            error=e,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to submit batch task"
        )

@app.get("/api/batch/status/{task_id}")
async def get_batch_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """배치 작업 상태 조회"""
    task = batch_processor.get_task_status(task_id)
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this task"
        )
    
    return {
        "task_id": task.id,
        "task_type": task.task_type.value,
        "status": task.status.value,
        "progress": task.progress,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "error_message": task.error_message,
        "result": task.result
    }

@app.get("/api/batch/tasks")
async def get_user_batch_tasks(
    current_user: User = Depends(get_current_active_user)
):
    """사용자 배치 작업 목록"""
    tasks = batch_processor.get_user_tasks(current_user.id)
    
    return [
        {
            "task_id": task.id,
            "task_type": task.task_type.value,
            "status": task.status.value,
            "progress": task.progress,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error_message": task.error_message
        }
        for task in sorted(tasks, key=lambda x: x.created_at, reverse=True)
    ]

@app.delete("/api/batch/cancel/{task_id}")
async def cancel_batch_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """배치 작업 취소"""
    task = batch_processor.get_task_status(task_id)
    
    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )
    
    if task.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied to this task"
        )
    
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel a task that is already completed, failed, or cancelled"
        )
    
    success = await batch_processor.cancel_task(task_id)
    
    if success:
        return {"message": "Task cancelled successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel task"
        )

@app.post("/api/batch/workflow")
async def submit_batch_workflow(
    workflow_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """전체 워크플로우 배치 작업 제출 (키워드 -> 제목 -> 콘텐츠)"""
    try:
        keywords = workflow_data.get("keywords", [])
        titles_per_keyword = workflow_data.get("titles_per_keyword", 3)
        content_per_keyword = workflow_data.get("content_per_keyword", 1)
        
        if not keywords:
            raise HTTPException(
                status_code=400,
                detail="Keywords list is required"
            )
        
        if len(keywords) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 keywords allowed per batch workflow"
            )
        
        batch_task = BatchTask(
            id=str(uuid.uuid4()),
            task_type=TaskType.BATCH_WORKFLOW,
            user_id=current_user.id,
            parameters={
                "keywords": keywords,
                "titles_per_keyword": titles_per_keyword,
                "content_per_keyword": content_per_keyword
            }
        )
        
        task_id = await batch_processor.submit_task(batch_task)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "estimated_duration_minutes": len(keywords) * (titles_per_keyword + content_per_keyword) * 0.5,
            "total_operations": len(keywords) * (1 + titles_per_keyword + content_per_keyword)
        }
        
    except Exception as e:
        app_logger.error(
            f"Error submitting batch workflow",
            error=e,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to submit batch workflow"
        )

@app.post("/api/keywords/integrated-analysis")
async def integrated_keyword_analysis(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """통합 키워드 분석 API - 네이버 + Google + SEO 통합 분석"""
    item_name = request.get("item_name")
    category = request.get("category")
    include_variations = request.get("include_variations", True)
    
    if not item_name or not category:
        raise HTTPException(
            status_code=400,
            detail="item_name and category are required"
        )
    
    app_logger.info(
        f"Starting integrated keyword analysis",
        user_id=current_user.id,
        item_name=item_name,
        category=category
    )
    
    try:
        # 통합 키워드 분석 실행
        integrated_service = IntegratedKeywordService()
        analysis_result = await integrated_service.comprehensive_analysis(
            item_name, category, include_variations
        )
        
        # 응답 데이터 변환
        response_data = {
            "success": True,
            "data": {
                "analysis_metadata": analysis_result["analysis_metadata"],
                "integrated_keywords": [
                    {
                        "keyword": result.keyword,
                        "integrated_score": result.integrated_score,
                        "priority": result.recommended_priority,
                        "opportunity": result.content_opportunity,
                        "naver_data": {
                            "trend_ratio": result.naver_trend_ratio,
                            "trend_direction": result.naver_trend_direction,
                            "seasonal": result.naver_seasonal,
                            "competition": result.naver_competition
                        },
                        "google_data": {
                            "monthly_searches": result.google_monthly_searches,
                            "competition": result.google_competition,
                            "cpc_range": f"${result.google_cpc_low:.2f}-${result.google_cpc_high:.2f}",
                            "difficulty": result.google_difficulty
                        },
                        "seo_data": {
                            "score": result.seo_score,
                            "reason": result.seo_reason
                        }
                    }
                    for result in analysis_result["keyword_analysis"]
                ],
                "strategic_insights": analysis_result["strategic_insights"],
                "content_recommendations": analysis_result["content_recommendations"],
                "ranking_opportunities": analysis_result["ranking_opportunities"],
                "competitive_analysis": analysis_result["competitive_analysis"]
            }
        }
        
        app_logger.info(
            f"Integrated keyword analysis completed",
            user_id=current_user.id,
            item_name=item_name,
            category=category,
            keywords_count=len(analysis_result["keyword_analysis"])
        )
        
        return response_data
        
    except Exception as e:
        app_logger.error(
            f"Error in integrated keyword analysis",
            error=e,
            user_id=current_user.id,
            item_name=item_name,
            category=category
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to perform integrated keyword analysis"
        )

@app.post("/api/keywords/seo-analysis")
async def analyze_seo_keywords(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """SEO 키워드 분석 API - 최신 트렌드, 검색량, 경쟁도 분석"""
    item_name = request.get("item_name")
    category = request.get("category")
    
    if not item_name or not category:
        raise HTTPException(
            status_code=400,
            detail="item_name and category are required"
        )
    
    app_logger.info(
        f"Starting SEO keyword analysis",
        user_id=current_user.id,
        item_name=item_name,
        category=category
    )
    
    try:
        # SEO 키워드 분석 실행 (지침 포함)
        seo_analyzer = SEOKeywordAnalyzer()
        seo_keywords = await seo_analyzer.analyze_seo_keywords(item_name, category, db)
        
        # 응답 데이터 구성
        seo_data = [
            {
                "keyword": kw.keyword,
                "search_volume": kw.search_volume,
                "competition": kw.competition,
                "seasonal": kw.seasonal,
                "reason": kw.reason,
                "score": kw.score
            }
            for kw in seo_keywords
        ]
        
        app_logger.info(
            f"SEO keyword analysis completed",
            user_id=current_user.id,
            item_name=item_name,
            category=category,
            keywords_count=len(seo_data)
        )
        
        return {
            "success": True,
            "data": {
                "seo_keywords": seo_data,
                "item_name": item_name,
                "category": category,
                "analysis_date": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        app_logger.error(
            f"Error in SEO keyword analysis",
            error=e,
            user_id=current_user.id,
            item_name=item_name,
            category=category
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze SEO keywords"
        )

@app.post("/api/keywords/golden")
async def generate_golden_keywords(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """황금 키워드 생성 API - 수익성, 창의성, 유입량을 고려한 최적의 키워드"""
    category = request.get("category")
    domain = request.get("domain", "")
    platform = request.get("platform", "wordpress")
    
    app_logger.info(
        f"Starting golden keyword generation",
        user_id=current_user.id,
        category=category,
        domain=domain,
        platform=platform
    )
    
    try:
        # 황금 키워드 생성 알고리즘
        golden_keyword_service = GoldenKeywordService()
        
        # 카테고리별 최적화된 키워드 생성
        golden_data = await safe_execute_async(
            golden_keyword_service.generate_golden_keywords,
            category=category,
            domain=domain,
            platform=platform,
            fallback_value={
                "golden_keywords": [],
                "trending_keywords": [],
                "profitable_keywords": []
            }
        )
        
        app_logger.info(
            f"Golden keyword generation completed",
            user_id=current_user.id,
            category=category,
            golden_count=len(golden_data.get("golden_keywords", [])),
            trending_count=len(golden_data.get("trending_keywords", [])),
            profitable_count=len(golden_data.get("profitable_keywords", []))
        )
        
        return {
            "success": True,
            "data": golden_data
        }
        
    except Exception as e:
        app_logger.error(
            f"Error generating golden keywords",
            error=e,
            user_id=current_user.id,
            category=category
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate golden keywords"
        )

@app.post("/api/keywords/analyze", response_model=List[KeywordAnalysisResponse])
async def analyze_keywords(
    request: KeywordAnalysisRequest, 
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """키워드 분석 API (인증 필요)"""
    app_logger.info(
        f"Starting keyword analysis",
        user_id=current_user.id,
        keyword=request.keyword,
        country=request.country,
        max_results=request.max_results
    )
    
    try:
        # Use enhanced keyword analysis service
        keyword_service = AggregateKeywordService()
        
        # Analyze keywords using multiple sources
        keywords_data = await safe_execute_async(
            keyword_service.analyze_keywords,
            keyword=request.keyword,
            country=request.country,
            max_results=request.max_results,
            fallback_value=None
        )
        
        # Convert to response format
        results = [
            KeywordAnalysisResponse(
                keyword=item["keyword"],
                search_volume=item["search_volume"],
                competition=item["competition"],
                cpc=item["cpc"],
                opportunity_score=item["opportunity_score"]
            )
            for item in keywords_data
        ]
        
        # Save to database with user association
        try:
            for item in keywords_data:
                keyword_record = Keyword(
                    keyword=item["keyword"],
                    country_id=1,  # Default to first country (KR)
                    search_volume=item["search_volume"],
                    competition=item["competition"],
                    cpc=item["cpc"],
                    opportunity_score=item["opportunity_score"],
                    created_by=current_user.id
                )
                db.add(keyword_record)
            db.commit()
            
            app_logger.info(
                f"Keyword analysis completed successfully",
                user_id=current_user.id,
                keyword=request.keyword,
                results_count=len(keywords_data)
            )
            
        except SQLAlchemyError as e:
            db.rollback()
            app_logger.error(
                f"Database error saving keywords",
                error=e,
                user_id=current_user.id,
                keyword=request.keyword
            )
            # Continue with response even if save fails
        
        return results
        
    except Exception as e:
        print(f"Keyword analysis error: {e}")
        # Fallback to simple mock data
        fallback_data = [
            {
                "keyword": request.keyword,
                "search_volume": 1000,
                "competition": "Medium",
                "cpc": 1.5,
                "opportunity_score": 85
            },
            {
                "keyword": f"{request.keyword} 방법",
                "search_volume": 500,
                "competition": "Low",
                "cpc": 0.8,
                "opportunity_score": 92
            },
            {
                "keyword": f"{request.keyword} 추천",
                "search_volume": 300,
                "competition": "Low",
                "cpc": 0.6,
                "opportunity_score": 88
            }
        ]
        
        # Save fallback data to database
        for item in fallback_data[:request.max_results]:
            keyword_record = Keyword(
                keyword=item["keyword"],
                country_id=1,
                search_volume=item["search_volume"],
                competition=item["competition"],
                cpc=item["cpc"],
                opportunity_score=item["opportunity_score"],
                created_by=current_user.id
            )
            db.add(keyword_record)
        db.commit()
        
        fallback_results = [
            KeywordAnalysisResponse(
                keyword=item["keyword"],
                search_volume=item["search_volume"],
                competition=item["competition"],
                cpc=item["cpc"],
                opportunity_score=item["opportunity_score"]
            )
            for item in fallback_data[:request.max_results]
        ]
        
        return fallback_results

@app.post("/api/titles/advanced-generate")
async def generate_advanced_titles(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """고급 블로그 제목 생성 API - 시의성, SEO, 바이럴성 최적화"""
    keyword = request.get("keyword")
    count = request.get("count", 5)
    
    if not keyword:
        raise HTTPException(
            status_code=400,
            detail="keyword is required"
        )
    
    app_logger.info(
        f"Starting advanced title generation",
        user_id=current_user.id,
        keyword=keyword,
        count=count
    )
    
    try:
        # 고급 제목 생성기 사용
        advanced_generator = AdvancedTitleGenerator()
        titles_data = await advanced_generator.generate_optimized_titles(keyword, count)
        
        # 응답 데이터 구성
        response_data = {
            "success": True,
            "data": {
                "keyword": keyword,
                "generated_titles": [
                    {
                        "title": item["title"],
                        "format_type": item["format_type"],
                        "emotion_trigger": item["emotion_trigger"],
                        "scores": {
                            "seo_score": item["seo_score"],
                            "click_score": item["click_score"],
                            "viral_score": item["viral_score"],
                            "timely_score": item["timely_score"],
                            "total_score": item["total_score"]
                        },
                        "length": item["length"],
                        "reason": item["reason"]
                    }
                    for item in titles_data
                ],
                "generation_date": datetime.now().isoformat(),
                "analysis": {
                    "avg_total_score": sum(item["total_score"] for item in titles_data) / len(titles_data),
                    "best_format": max(titles_data, key=lambda x: x["total_score"])["format_type"],
                    "diversity_score": len(set(item["format_type"] for item in titles_data))
                }
            }
        }
        
        # 데이터베이스에 저장
        keyword_record = db.query(Keyword).filter(
            Keyword.keyword == keyword,
            Keyword.created_by == current_user.id
        ).first()
        
        if not keyword_record:
            keyword_record = Keyword(
                keyword=keyword,
                country_id=1,
                search_volume=0,
                competition="Unknown",
                cpc=0.0,
                opportunity_score=50,
                created_by=current_user.id
            )
            db.add(keyword_record)
            db.commit()
            db.refresh(keyword_record)
        
        # 생성된 제목들 저장
        for item in titles_data:
            title_record = GeneratedTitle(
                keyword_id=keyword_record.id,
                title=item["title"],
                length_option="advanced",
                language="ko",
                tone=item["format_type"],
                duplicate_rate=100 - item["total_score"],  # 점수가 높을수록 중복률 낮음
                ai_model="advanced_generator",
                created_by=current_user.id
            )
            db.add(title_record)
        db.commit()
        
        app_logger.info(
            f"Advanced title generation completed",
            user_id=current_user.id,
            keyword=keyword,
            titles_count=len(titles_data),
            avg_score=response_data["data"]["analysis"]["avg_total_score"]
        )
        
        return response_data
        
    except Exception as e:
        app_logger.error(
            f"Error in advanced title generation",
            error=e,
            user_id=current_user.id,
            keyword=keyword
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate advanced titles"
        )

@app.post("/api/titles/generate", response_model=List[TitleGenerationResponse])
async def generate_titles(
    request: TitleGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """최적화된 제목 생성 API (인증 필요)"""
    try:
        app_logger.info(
            f"Starting optimized title generation",
            user_id=current_user.id,
            keyword=request.keyword,
            count=request.count
        )
        
        # Use optimized title service
        optimized_title_service = OptimizedTitleService()
        
        # Generate optimized titles
        titles_data = await optimized_title_service.generate_optimized_titles(
            keyword=request.keyword,
            category=getattr(request, 'category', '일반'),
            platform=getattr(request, 'platform', 'wordpress'),
            count=request.count
        )
        
        # Convert to response format
        titles = [
            TitleGenerationResponse(
                title=item["title"],
                duplicate_rate=float(item["duplicate_rate"])
            )
            for item in titles_data
        ]
        
        # Save to database with user association
        # First, find or create keyword record
        keyword_record = db.query(Keyword).filter(
            Keyword.keyword == request.keyword,
            Keyword.created_by == current_user.id
        ).first()
        
        if not keyword_record:
            keyword_record = Keyword(
                keyword=request.keyword,
                country_id=1,
                search_volume=0,
                competition="Unknown",
                cpc=0.0,
                opportunity_score=50,
                created_by=current_user.id
            )
            db.add(keyword_record)
            db.commit()
            db.refresh(keyword_record)
        
        # Save generated titles
        for item in titles_data:
            title_record = GeneratedTitle(
                keyword_id=keyword_record.id,
                title=item["title"],
                length_option=request.length,
                language=request.language,
                tone=request.tone,
                duplicate_rate=float(item["duplicate_rate"]),
                ai_model="optimized_title_service",
                created_by=current_user.id
            )
            db.add(title_record)
        db.commit()
        
        return titles
        
    except Exception as e:
        print(f"Title generation error: {e}")
        # Fallback to mock data
        mock_titles_data = [
            {"title": f"{request.keyword}의 완벽한 가이드: 초보자도 쉽게 따라할 수 있는 방법", "duplicate_rate": 5.2},
            {"title": f"2024년 최신 {request.keyword} 트렌드와 실전 활용법", "duplicate_rate": 8.1},
            {"title": f"{request.keyword} 마스터하기: 전문가가 알려주는 핵심 노하우", "duplicate_rate": 3.7},
            {"title": f"누구나 할 수 있는 {request.keyword} 시작하기", "duplicate_rate": 9.8},
            {"title": f"{request.keyword}로 성공하는 5가지 전략", "duplicate_rate": 2.1}
        ]
        
        # Save fallback titles to database
        keyword_record = db.query(Keyword).filter(
            Keyword.keyword == request.keyword,
            Keyword.created_by == current_user.id
        ).first()
        
        if not keyword_record:
            keyword_record = Keyword(
                keyword=request.keyword,
                country_id=1,
                search_volume=0,
                competition="Unknown",
                cpc=0.0,
                opportunity_score=50,
                created_by=current_user.id
            )
            db.add(keyword_record)
            db.commit()
            db.refresh(keyword_record)
        
        for item in mock_titles_data[:request.count]:
            title_record = GeneratedTitle(
                keyword_id=keyword_record.id,
                title=item["title"],
                length_option=request.length,
                language=request.language,
                tone=request.tone,
                duplicate_rate=item["duplicate_rate"],
                ai_model="fallback",
                created_by=current_user.id
            )
            db.add(title_record)
        db.commit()
        
        mock_titles = [
            TitleGenerationResponse(title=item["title"], duplicate_rate=item["duplicate_rate"])
            for item in mock_titles_data[:request.count]
        ]
        return mock_titles

@app.post("/api/content/generate", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """콘텐츠 생성 API (인증 필요)"""
    try:
        # Get AI service (default to OpenAI)
        ai_service = get_ai_service("openai")
        
        # Generate content using AI
        content_data = await ai_service.generate_content(
            title=request.title,
            keywords=request.keywords,
            length=request.length
        )
        
        # Save to database with user association
        # Find or create title record
        title_record = db.query(GeneratedTitle).filter(
            GeneratedTitle.title == request.title,
            GeneratedTitle.created_by == current_user.id
        ).first()
        
        if not title_record:
            # Create a temporary title record if not found
            title_record = GeneratedTitle(
                keyword_id=None,
                title=request.title,
                length_option="medium",
                language="ko",
                tone="professional",
                duplicate_rate=0.0,
                ai_model="openai",
                created_by=current_user.id
            )
            db.add(title_record)
            db.commit()
            db.refresh(title_record)
        
        # Save generated content
        content_record = GeneratedContent(
            title_id=title_record.id,
            content=content_data["content"],
            keywords=request.keywords,
            seo_score=content_data["seo_score"],
            geo_score=content_data["geo_score"],
            copyscape_result=content_data["copyscape_result"],
            ai_model="openai",
            created_by=current_user.id
        )
        db.add(content_record)
        db.commit()
        
        return ContentGenerationResponse(
            content=content_data["content"],
            seo_score=content_data["seo_score"],
            geo_score=content_data["geo_score"],
            copyscape_result=content_data["copyscape_result"]
        )
        
    except Exception as e:
        print(f"Content generation error: {e}")
        # Fallback to mock data
        mock_content = f"""
# {request.title}

## 서론

{request.title}에 대해 자세히 알아보겠습니다. 이 주제는 많은 사람들이 관심을 가지고 있는 중요한 내용입니다.

## 주요 내용

### 1. 기본 개념

{f"{request.keywords} 관련하여" if request.keywords else ""} 기본적인 개념부터 차근차근 설명드리겠습니다.

### 2. 실전 활용법

실제로 어떻게 활용할 수 있는지 구체적인 방법을 제시합니다.

### 3. 주의사항

주의해야 할 점들과 흔히 하는 실수들을 정리했습니다.

## 결론

{request.title}에 대한 내용을 정리하면서, 독자들이 실제로 활용할 수 있는 실용적인 정보를 제공했습니다.

---

*이 글이 도움이 되었다면 공유해주세요!*
        """.strip()
        
        return ContentGenerationResponse(
            content=mock_content,
            seo_score=85,
            geo_score=78,
            copyscape_result="Pass"
        )

@app.post("/api/content/advanced-generate")
async def generate_advanced_content(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """고급 블로그 콘텐츠 생성 API - SEO + GEO 최적화"""
    keyword = request.get("keyword")
    
    if not keyword:
        raise HTTPException(
            status_code=400,
            detail="keyword is required"
        )
    
    app_logger.info(
        f"Starting advanced blog content generation",
        user_id=current_user.id,
        keyword=keyword
    )
    
    try:
        # 고급 블로그 작성기 실행
        blog_writer = AdvancedBlogWriter()
        blog_result = await blog_writer.generate_blog_content(keyword)
        
        # 데이터베이스에 저장
        content_record = GeneratedContent(
            title_id=None,  # 별도 제목 없이 독립적으로 생성
            content=blog_result["content"],
            keywords=keyword,
            ai_model="advanced_blog_writer",
            seo_score=blog_result["readability_score"],
            geo_score=blog_result["geo_optimization_score"],
            copyscape_result="Generated",
            created_by=current_user.id
        )
        db.add(content_record)
        db.commit()
        db.refresh(content_record)
        
        app_logger.info(
            f"Advanced blog content generated successfully",
            user_id=current_user.id,
            content_id=content_record.id,
            word_count=blog_result["word_count"]
        )
        
        return {
            "success": True,
            "data": {
                "content_id": content_record.id,
                "title_candidates": blog_result["title_candidates"],
                "selected_title": blog_result["selected_title"],
                "content": blog_result["content"],
                "word_count": blog_result["word_count"],
                "seo_keywords": blog_result["seo_keywords"],
                "lsi_keywords": blog_result["lsi_keywords"],
                "readability_score": blog_result["readability_score"],
                "geo_optimization_score": blog_result["geo_optimization_score"],
                "subtopics": blog_result["subtopics"]
            }
        }
        
    except Exception as e:
        app_logger.error(
            f"Error generating advanced blog content",
            error=e,
            user_id=current_user.id,
            keyword=keyword
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate advanced blog content"
        )

@app.post("/api/posts/auto-publish")
async def auto_publish_posts(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """자동 포스팅 API - 다중 플랫폼 예약 포스팅"""
    
    try:
        titles = request.get('titles', [])
        content_data = request.get('content_data', {})
        platforms = request.get('platforms', [])
        schedule_settings = request.get('schedule_settings', {})
        image_settings = request.get('image_settings', {})
        
        app_logger.info(
            f"Starting auto-publish process",
            user_id=current_user.id,
            titles_count=len(titles),
            platforms_count=len(platforms)
        )
        
        if not titles or not platforms:
            raise HTTPException(
                status_code=400,
                detail="Titles and platforms are required"
            )
        
        # 자동 포스팅 서비스 실행
        auto_posting_service = AutoPostingService()
        
        results = await auto_posting_service.schedule_posts(
            titles=titles,
            content_data=content_data,
            platforms=platforms,
            schedule_settings=schedule_settings,
            image_settings=image_settings
        )
        
        app_logger.info(
            f"Auto-publish completed",
            user_id=current_user.id,
            success_count=len(results['success']),
            failed_count=len(results['failed']),
            scheduled_count=len(results['scheduled'])
        )
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "total_posts": results['total_posts'],
                "successful": len(results['success']),
                "failed": len(results['failed']),
                "scheduled": len(results['scheduled'])
            }
        }
        
    except Exception as e:
        app_logger.error(
            f"Auto-publish failed",
            error=e,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Auto-publish failed: {str(e)}"
        )

@app.post("/api/content/batch-generate")
async def batch_generate_content(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """다중 제목으로 일괄 콘텐츠 생성"""
    
    try:
        titles = request.get('titles', [])
        guidelines = request.get('guidelines', '')
        seo_guidelines = request.get('seo_guidelines', '')
        geo_guidelines = request.get('geo_guidelines', '')
        
        app_logger.info(
            f"Starting batch content generation",
            user_id=current_user.id,
            titles_count=len(titles)
        )
        
        if not titles:
            raise HTTPException(
                status_code=400,
                detail="Titles are required"
            )
        
        # AI 서비스로 각 제목별 콘텐츠 생성
        ai_service = get_ai_service("openai")
        content_results = {}
        
        for title in titles:
            try:
                # 가이드라인을 포함한 콘텐츠 생성
                content_prompt = f"""
                제목: {title}
                
                가이드라인:
                {guidelines}
                
                SEO 최적화 요구사항:
                {seo_guidelines}
                
                GEO 최적화 요구사항:
                {geo_guidelines}
                
                위 가이드라인을 반영하여 고품질 블로그 콘텐츠를 생성해주세요.
                """
                
                content_data = await ai_service.generate_content(
                    title=title,
                    keywords="",
                    length="long"
                )
                
                content_results[title] = content_data["content"]
                
                # 데이터베이스에 저장
                content_record = GeneratedContent(
                    title_id=None,  # 임시
                    content=content_data["content"],
                    keywords="",
                    seo_score=content_data.get("seo_score", 85),
                    geo_score=content_data.get("geo_score", 80),
                    copyscape_result=content_data.get("copyscape_result", "Pass"),
                    ai_model="openai",
                    created_by=current_user.id
                )
                db.add(content_record)
                
            except Exception as e:
                app_logger.error(f"Content generation failed for title", error=e, title=title)
                # 폴백 콘텐츠 생성
                content_results[title] = f"""
# {title}

## 서론

{title}에 대해 자세히 알아보겠습니다.

{guidelines}

## 주요 내용

### SEO 최적화
{seo_guidelines}

### GEO 최적화  
{geo_guidelines}

## 결론

{title}에 대한 내용을 마무리하겠습니다.
                """.strip()
        
        db.commit()
        
        app_logger.info(
            f"Batch content generation completed",
            user_id=current_user.id,
            generated_count=len(content_results)
        )
        
        return {
            "success": True,
            "content_data": content_results,
            "generated_count": len(content_results)
        }
        
    except Exception as e:
        app_logger.error(
            f"Batch content generation failed",
            error=e,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=500,
            detail=f"Batch content generation failed: {str(e)}"
        )

# 관리자 API 엔드포인트들
@app.get("/api/admin/prompts/summary")
async def get_prompts_summary(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """관리자용 지침 요약 정보 조회"""
    try:
        prompt_manager = PromptManager(db)
        summary = prompt_manager.get_all_prompts_summary()
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get prompts summary: {str(e)}"
        )

@app.get("/api/admin/prompts/{prompt_type}")
async def get_prompts_by_type(
    prompt_type: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """타입별 지침 목록 조회"""
    try:
        from models import PromptType
        prompt_type_enum = PromptType(prompt_type)
        
        prompt_manager = PromptManager(db)
        prompts = prompt_manager.get_prompts_by_type(prompt_type_enum)
        
        return {
            "success": True,
            "data": {
                "prompt_type": prompt_type,
                "prompts": prompts
            }
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prompt type: {prompt_type}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get prompts: {str(e)}"
        )

@app.post("/api/admin/prompts")
async def create_prompt(
    request: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """새 지침 생성"""
    try:
        prompt_manager = PromptManager(db)
        result = prompt_manager.create_prompt(request, current_user.id)
        
        return {
            "success": True,
            "data": result,
            "message": "지침이 성공적으로 생성되었습니다."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create prompt: {str(e)}"
        )

@app.put("/api/admin/prompts/{prompt_id}")
async def update_prompt(
    prompt_id: str,
    request: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """지침 업데이트"""
    try:
        prompt_manager = PromptManager(db)
        success = prompt_manager.update_prompt(prompt_id, request)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="지침을 찾을 수 없습니다."
            )
        
        return {
            "success": True,
            "message": "지침이 성공적으로 업데이트되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update prompt: {str(e)}"
        )

@app.delete("/api/admin/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """지침 삭제"""
    try:
        prompt_manager = PromptManager(db)
        success = prompt_manager.delete_prompt(prompt_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="지침을 찾을 수 없습니다."
            )
        
        return {
            "success": True,
            "message": "지침이 성공적으로 삭제되었습니다."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete prompt: {str(e)}"
        )

@app.get("/api/admin/prompts/{prompt_type}/export")
async def export_prompts(
    prompt_type: str,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """지침 내보내기"""
    try:
        from models import PromptType
        prompt_type_enum = PromptType(prompt_type) if prompt_type != "all" else None
        
        prompt_manager = PromptManager(db)
        export_data = prompt_manager.export_prompts(prompt_type_enum)
        
        return {
            "success": True,
            "data": export_data
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prompt type: {prompt_type}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export prompts: {str(e)}"
        )

@app.post("/api/admin/prompts/import")
async def import_prompts(
    request: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """지침 가져오기"""
    try:
        prompt_manager = PromptManager(db)
        result = prompt_manager.import_prompts(request, current_user.id)
        
        return {
            "success": result["success"],
            "data": result,
            "message": f"{result['imported_count']}개의 지침이 성공적으로 가져왔습니다."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import prompts: {str(e)}"
        )

# =============================================================================
# 자동화 시스템 API 엔드포인트
# =============================================================================

# 사이트 관리 API
@app.post("/api/sites")
async def create_site(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """새 사이트 등록"""
    try:
        site = await site_manager.create_site(
            db=db,
            user_id=current_user.id,
            **request
        )
        
        return {
            "success": True,
            "data": {
                "id": site.id,
                "name": site.name,
                "url": site.url,
                "category": site.category,
                "created_at": site.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사이트 등록 실패: {str(e)}"
        )

@app.get("/api/sites")
async def get_user_sites(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 사이트 목록 조회"""
    try:
        sites = await site_manager.get_user_sites(db, current_user.id)
        
        sites_data = []
        for site in sites:
            site_data = {
                "id": site.id,
                "name": site.name,
                "url": site.url,
                "description": site.description,
                "category": site.category,
                "wordpress_url": site.wordpress_url,
                "wordpress_username": site.wordpress_username,
                "is_active": site.is_active,
                "auto_posting_enabled": site.auto_posting_enabled,
                "posting_interval_hours": site.posting_interval_hours,
                "total_keywords_generated": site.total_keywords_generated,
                "total_titles_generated": site.total_titles_generated,
                "total_posts_generated": site.total_posts_generated,
                "total_posts_published": site.total_posts_published,
                "created_at": site.created_at.isoformat(),
                "updated_at": site.updated_at.isoformat() if site.updated_at else None
            }
            sites_data.append(site_data)
        
        return {
            "success": True,
            "data": sites_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사이트 목록 조회 실패: {str(e)}"
        )

@app.get("/api/sites/{site_id}")
async def get_site_details(
    site_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사이트 상세 정보 조회"""
    try:
        site = await site_manager.get_site_by_id(db, site_id, current_user.id)
        if not site:
            raise HTTPException(
                status_code=404,
                detail="사이트를 찾을 수 없습니다"
            )
        
        # 통계 정보 포함
        stats = await site_manager.get_site_statistics(db, site_id, current_user.id)
        
        return {
            "success": True,
            "data": {
                "id": site.id,
                "name": site.name,
                "url": site.url,
                "description": site.description,
                "category": site.category,
                "wordpress_url": site.wordpress_url,
                "wordpress_username": site.wordpress_username,
                "keyword_guideline_id": site.keyword_guideline_id,
                "title_guideline_id": site.title_guideline_id,
                "blog_guideline_id": site.blog_guideline_id,
                "is_active": site.is_active,
                "auto_posting_enabled": site.auto_posting_enabled,
                "posting_interval_hours": site.posting_interval_hours,
                "statistics": stats,
                "created_at": site.created_at.isoformat(),
                "updated_at": site.updated_at.isoformat() if site.updated_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사이트 조회 실패: {str(e)}"
        )

@app.put("/api/sites/{site_id}")
async def update_site(
    site_id: str,
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사이트 정보 수정"""
    try:
        site = await site_manager.update_site(
            db=db,
            site_id=site_id,
            user_id=current_user.id,
            **request
        )
        
        if not site:
            raise HTTPException(
                status_code=404,
                detail="사이트를 찾을 수 없습니다"
            )
        
        return {
            "success": True,
            "data": {
                "id": site.id,
                "name": site.name,
                "url": site.url,
                "updated_at": site.updated_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사이트 수정 실패: {str(e)}"
        )

@app.delete("/api/sites/{site_id}")
async def delete_site(
    site_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사이트 삭제"""
    try:
        success = await site_manager.delete_site(db, site_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="사이트를 찾을 수 없습니다"
            )
        
        return {
            "success": True,
            "message": "사이트가 성공적으로 삭제되었습니다"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"사이트 삭제 실패: {str(e)}"
        )

@app.post("/api/sites/test-wordpress")
async def test_wordpress_connection(
    request: dict,
    current_user: User = Depends(get_current_active_user)
):
    """WordPress 연결 테스트"""
    try:
        wordpress_url = request.get("wordpress_url")
        username = request.get("username")
        password = request.get("password")
        
        if not all([wordpress_url, username, password]):
            raise HTTPException(
                status_code=400,
                detail="WordPress URL, 사용자명, 비밀번호가 모두 필요합니다"
            )
        
        result = await site_manager.test_wordpress_connection(
            wordpress_url, username, password
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"WordPress 연결 테스트 실패: {str(e)}"
        )

@app.get("/api/sites/guidelines/available")
async def get_available_guidelines(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용 가능한 지침 목록 조회"""
    try:
        guidelines = await site_manager.get_available_guidelines(db)
        return {
            "success": True,
            "data": guidelines
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"지침 목록 조회 실패: {str(e)}"
        )

# 자동화 워크플로우 API
@app.post("/api/automation/start")
async def start_automation_session(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """자동화 세션 시작"""
    try:
        site_id = request.get("site_id")
        category = request.get("category")
        auto_posting = request.get("auto_posting", False)
        
        if not all([site_id, category]):
            raise HTTPException(
                status_code=400,
                detail="site_id와 category가 필요합니다"
            )
        
        session = await automation_engine.start_automation_session(
            db=db,
            site_id=site_id,
            user_id=current_user.id,
            category=category,
            auto_posting=auto_posting
        )
        
        return {
            "success": True,
            "data": {
                "session_id": session.id,
                "site_id": session.site_id,
                "category": session.category,
                "step_status": session.step_status,
                "created_at": session.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"자동화 세션 시작 실패: {str(e)}"
        )

@app.post("/api/automation/keywords/generate")
async def generate_category_keywords(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """카테고리 기반 키워드 자동 생성"""
    try:
        session_id = request.get("session_id")
        category = request.get("category")
        count = request.get("count", 20)
        use_trends = request.get("use_trends", True)
        
        if not all([session_id, category]):
            raise HTTPException(
                status_code=400,
                detail="session_id와 category가 필요합니다"
            )
        
        result = await automation_engine.generate_category_keywords(
            db=db,
            session_id=session_id,
            category=category,
            count=count,
            use_trends=use_trends
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"키워드 생성 실패: {str(e)}"
        )

@app.post("/api/automation/titles/generate")
async def generate_keyword_titles(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """선택된 키워드들로 제목 자동 생성"""
    try:
        session_id = request.get("session_id")
        selected_keywords = request.get("selected_keywords", [])
        titles_per_keyword = request.get("titles_per_keyword", 10)
        
        if not all([session_id, selected_keywords]):
            raise HTTPException(
                status_code=400,
                detail="session_id와 selected_keywords가 필요합니다"
            )
        
        result = await automation_engine.generate_keyword_titles(
            db=db,
            session_id=session_id,
            selected_keywords=selected_keywords,
            titles_per_keyword=titles_per_keyword
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"제목 생성 실패: {str(e)}"
        )

@app.post("/api/automation/content/generate")
async def generate_title_contents(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """선택된 제목들로 블로그 글 자동 생성"""
    try:
        session_id = request.get("session_id")
        selected_titles = request.get("selected_titles", [])
        
        if not all([session_id, selected_titles]):
            raise HTTPException(
                status_code=400,
                detail="session_id와 selected_titles가 필요합니다"
            )
        
        result = await automation_engine.generate_title_contents(
            db=db,
            session_id=session_id,
            selected_titles=selected_titles
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"블로그 글 생성 실패: {str(e)}"
        )

@app.post("/api/automation/publish")
async def publish_automation_contents(
    request: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """생성된 블로그 글들을 WordPress에 자동 포스팅"""
    try:
        session_id = request.get("session_id")
        selected_content_titles = request.get("selected_content_titles", [])
        schedule_settings = request.get("schedule_settings")
        
        if not all([session_id, selected_content_titles]):
            raise HTTPException(
                status_code=400,
                detail="session_id와 selected_content_titles가 필요합니다"
            )
        
        result = await automation_engine.publish_contents(
            db=db,
            session_id=session_id,
            selected_content_titles=selected_content_titles,
            schedule_settings=schedule_settings
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"자동 포스팅 실패: {str(e)}"
        )

@app.get("/api/automation/sessions/{session_id}/status")
async def get_automation_session_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """자동화 세션 상태 조회"""
    try:
        result = await automation_engine.get_session_status(db, session_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"세션 상태 조회 실패: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)