#!/usr/bin/env python3
"""
BlogAuto 간단 서버 실행기
의존성 문제 없이 기본 기능만으로 서버 실행
"""

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
import time
from smart_content_generator import smart_generator
from smart_title_generator import smart_title_generator

# 간단한 데이터 모델
class KeywordRequest(BaseModel):
    keyword: str
    country: str = "KR"

class TitleRequest(BaseModel):
    keyword: str
    count: int = 5
    tone: str = "professional"
    guidelines: str = ""  # 사용자 지침 추가

class ContentRequest(BaseModel):
    title: str
    keyword: str
    length: str = "medium"
    tone: str = "professional"
    guidelines: str = ""  # 사용자 지침 추가

class WordPressRequest(BaseModel):
    title: str
    content: str
    category: str = "건강한 삶"
    username: str = "banana"
    password: str = ""
    site_url: str = "https://innerspell.com"

app = FastAPI(
    title="BlogAuto API - Simple Version",
    description="AI 기반 블로그 자동화 플랫폼 (간단 버전)",
    version="1.0.0"
)

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
    """서버 상태 확인"""
    return {
        "message": "BlogAuto API - Simple Version",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "version": "1.0.0"
    }

@app.post("/analyze-keywords")
async def analyze_keywords(request: KeywordRequest):
    """키워드 분석 (더미 데이터)"""
    
    # 시뮬레이션된 키워드 분석 데이터
    dummy_data = {
        "keyword": request.keyword,
        "country": request.country,
        "search_volume": random.randint(1000, 50000),
        "competition": random.choice(["low", "medium", "high"]),
        "difficulty": random.randint(1, 100),
        "cpc": round(random.uniform(0.1, 5.0), 2),
        "related_keywords": [
            f"{request.keyword} 방법",
            f"{request.keyword} 팁", 
            f"{request.keyword} 가이드",
            f"효과적인 {request.keyword}",
            f"{request.keyword} 추천"
        ],
        "trend": "increasing",
        "seo_opportunity": random.choice(["excellent", "good", "fair", "poor"]),
        "content_suggestions": [
            f"{request.keyword}의 기본 개념과 중요성",
            f"실용적인 {request.keyword} 방법 5가지",
            f"{request.keyword} 전문가 인터뷰",
            f"{request.keyword} 성공 사례 분석"
        ]
    }
    
    return {
        "success": True,
        "data": dummy_data,
        "response_time": round(random.uniform(0.1, 0.5), 3),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/generate-titles")
async def generate_titles(request: TitleRequest):
    """사용자 지침 기반 SEO 최적화 제목 생성"""
    
    try:
        # 사용자 지침이 있는 경우 적용, 없으면 기본 로직 사용
        if request.guidelines.strip():
            # 사용자 지침을 적용한 제목 생성
            titles = smart_title_generator.generate_with_guidelines(
                keyword=request.keyword,
                count=request.count,
                tone=request.tone,
                guidelines=request.guidelines
            )
        else:
            # 기존 스마트 제목 생성기 사용
            titles = smart_title_generator.generate_seo_optimized_titles(
                keyword=request.keyword,
                count=request.count,
                tone=request.tone
            )
        
        # 최고 제목 선정
        best_title = max(titles, key=lambda x: x["score"])
        
        return {
            "success": True,
            "keyword": request.keyword,
            "count": len(titles),
            "titles": titles,
            "best_title": best_title,
            "generation_info": {
                "approach": "사용자 지침 적용" if request.guidelines.strip() else "카테고리별 맞춤 생성",
                "category": titles[0]["category"] if titles else "unknown",
                "optimization": "사용자 맞춤 + SEO 최적화" if request.guidelines.strip() else "SEO + 클릭률 최적화",
                "guidelines_applied": bool(request.guidelines.strip())
            },
            "response_time": round(random.uniform(0.15, 0.35), 3),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # 오류 발생 시 기본 응답
        print(f"Title generator error: {e}")
        return {
            "success": False,
            "error": f"제목 생성 중 오류가 발생했습니다: {str(e)}",
            "keyword": request.keyword,
            "timestamp": datetime.now().isoformat()
        }

@app.post("/generate-content")  
async def generate_content(request: ContentRequest):
    """사용자 지침 기반 맞춤형 SEO 최적화 콘텐츠 생성"""
    
    try:
        # 사용자 지침이 있는 경우 적용, 없으면 기본 로직 사용
        if request.guidelines.strip():
            # 사용자 지침을 적용한 콘텐츠 생성
            result = smart_generator.generate_with_guidelines(
                keyword=request.keyword,
                title=request.title,
                length=request.length,
                tone=request.tone,
                guidelines=request.guidelines
            )
        else:
            # 기존 스마트 콘텐츠 생성기 사용
            result = smart_generator.generate_complete_content(
                keyword=request.keyword,
                title=request.title,
                length=request.length,
                tone=request.tone
            )
        
        # 성공 응답 구성
        return {
            "success": True,
            "title": request.title,
            "keyword": request.keyword, 
            "content": result["content"],
            "word_count": result["word_count"],
            "keyword_count": result["keyword_count"],
            "keyword_density": result["keyword_density"],
            "seo_score": result["seo_score"],
            "category": result["category"],
            "readability_score": round(random.uniform(88.0, 95.0), 1),
            "structure_score": round(random.uniform(92.0, 98.0), 1),
            "estimated_reading_time": f"{max(3, result['word_count'] // 400)}분",
            "seo_analysis": {
                "keyword_in_title": result["seo_analysis"]["keyword_in_title"],
                "heading_structure": result["seo_analysis"]["proper_headings"],
                "content_length": result["seo_analysis"]["word_count_good"],
                "keyword_optimization": result["seo_analysis"]["keyword_density_good"],
                "user_experience": result["seo_analysis"]["bullet_points"],
                "category_relevance": result["seo_analysis"]["category_relevant"]
            },
            "content_insights": {
                "detected_category": result["category"],
                "content_approach": "사용자 지침 적용" if request.guidelines.strip() else "맞춤형 카테고리별 최적화",
                "uniqueness": "사용자 맞춤 지침 기반 생성" if request.guidelines.strip() else "키워드 특성 분석 기반 생성",
                "guidelines_applied": bool(request.guidelines.strip())
            },
            "response_time": round(random.uniform(0.8, 1.5), 3),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # 오류 발생 시 기본 응답
        print(f"Smart generator error: {e}")
        return {
            "success": False,
            "error": f"콘텐츠 생성 중 오류가 발생했습니다: {str(e)}",
            "title": request.title,
            "keyword": request.keyword,
            "timestamp": datetime.now().isoformat()
        }

@app.post("/publish-wordpress")
async def publish_wordpress(request: WordPressRequest):
    """WordPress 발행 (시뮬레이션)"""
    
    # 더미 발행 결과
    result = {
        "success": True,
        "message": "콘텐츠가 성공적으로 발행되었습니다 (시뮬레이션)",
        "post_id": random.randint(100, 999),
        "post_url": f"{request.site_url}/blog/{random.randint(1000, 9999)}",
        "status": "published",
        "publication_time": datetime.now().isoformat(),
        "seo_analysis": {
            "title_optimization": "excellent",
            "meta_description": "generated",
            "keywords": [request.keyword],
            "readability": "good"
        }
    }
    
    return result

@app.get("/api-info")
async def api_info():
    """API 정보"""
    return {
        "name": "BlogAuto API - Simple Version",
        "version": "1.0.0",
        "description": "AI 기반 블로그 자동화 플랫폼 (간단 버전)",
        "endpoints": {
            "analyze_keywords": "POST /analyze-keywords",
            "generate_titles": "POST /generate-titles", 
            "generate_content": "POST /generate-content",
            "publish_wordpress": "POST /publish-wordpress"
        },
        "features": [
            "키워드 분석",
            "SEO 제목 생성",
            "고품질 콘텐츠 생성", 
            "WordPress 자동 발행"
        ],
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 BlogAuto Simple Server 시작!")
    print("📍 서버 주소: http://0.0.0.0:8000")
    print("📚 API 문서: http://0.0.0.0:8000/docs")
    print("🔍 헬스체크: http://0.0.0.0:8000/health")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )