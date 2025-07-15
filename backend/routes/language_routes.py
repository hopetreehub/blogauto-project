from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import asyncio

router = APIRouter(prefix="/api/language", tags=["language"])

# 지원 언어 목록
SUPPORTED_LANGUAGES = {
    "ko": {"name": "Korean", "native": "한국어", "rtl": False},
    "en": {"name": "English", "native": "English", "rtl": False},
    "ja": {"name": "Japanese", "native": "日本語", "rtl": False},
    "zh": {"name": "Chinese", "native": "中文", "rtl": False},
    "es": {"name": "Spanish", "native": "Español", "rtl": False},
    "fr": {"name": "French", "native": "Français", "rtl": False},
    "de": {"name": "German", "native": "Deutsch", "rtl": False},
    "pt": {"name": "Portuguese", "native": "Português", "rtl": False},
    "ru": {"name": "Russian", "native": "Русский", "rtl": False},
    "ar": {"name": "Arabic", "native": "العربية", "rtl": True},
    "hi": {"name": "Hindi", "native": "हिन्दी", "rtl": False},
    "vi": {"name": "Vietnamese", "native": "Tiếng Việt", "rtl": False},
    "th": {"name": "Thai", "native": "ไทย", "rtl": False},
    "id": {"name": "Indonesian", "native": "Bahasa Indonesia", "rtl": False}
}

class TranslationRequest(BaseModel):
    source_text: str
    source_language: str = "ko"
    target_languages: List[str]
    content_type: str = "blog"  # blog, title, meta
    preserve_formatting: bool = True
    
class TranslationResponse(BaseModel):
    source_language: str
    target_language: str
    original_text: str
    translated_text: str
    quality_score: float
    word_count: int
    estimated_cost: float
    
class LanguageDetectionRequest(BaseModel):
    text: str
    
class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    alternatives: List[Dict[str, float]]

@router.get("/languages")
async def get_supported_languages():
    """지원되는 언어 목록 조회"""
    return {
        "languages": [
            {
                "code": code,
                "name": info["name"],
                "native_name": info["native"],
                "rtl": info["rtl"]
            }
            for code, info in SUPPORTED_LANGUAGES.items()
        ],
        "total": len(SUPPORTED_LANGUAGES)
    }

@router.post("/translate")
async def translate_content(request: TranslationRequest):
    """콘텐츠 번역"""
    translations = []
    
    for target_lang in request.target_languages:
        if target_lang not in SUPPORTED_LANGUAGES:
            continue
            
        # 실제로는 번역 API 호출
        # 여기서는 시뮬레이션
        translated_text = await simulate_translation(
            request.source_text,
            request.source_language,
            target_lang,
            request.content_type
        )
        
        word_count = len(translated_text.split())
        quality_score = calculate_quality_score(request.source_text, translated_text)
        estimated_cost = calculate_translation_cost(word_count, target_lang)
        
        translations.append(TranslationResponse(
            source_language=request.source_language,
            target_language=target_lang,
            original_text=request.source_text,
            translated_text=translated_text,
            quality_score=quality_score,
            word_count=word_count,
            estimated_cost=estimated_cost
        ))
    
    return {
        "translations": translations,
        "total_cost": sum(t.estimated_cost for t in translations),
        "timestamp": datetime.utcnow()
    }

@router.post("/detect-language")
async def detect_language(request: LanguageDetectionRequest):
    """텍스트 언어 감지"""
    # 실제로는 언어 감지 API 사용
    # 여기서는 간단한 시뮬레이션
    
    detected = detect_language_simple(request.text)
    
    return LanguageDetectionResponse(
        detected_language=detected["language"],
        confidence=detected["confidence"],
        alternatives=detected["alternatives"]
    )

@router.post("/optimize-seo/{target_language}")
async def optimize_seo_for_language(target_language: str, content: Dict):
    """특정 언어에 맞게 SEO 최적화"""
    if target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="지원하지 않는 언어입니다")
    
    # SEO 최적화 로직
    optimized_content = {
        "title": optimize_title_for_language(content.get("title", ""), target_language),
        "meta_description": optimize_meta_for_language(content.get("meta_description", ""), target_language),
        "keywords": localize_keywords(content.get("keywords", []), target_language),
        "content": optimize_content_for_language(content.get("content", ""), target_language)
    }
    
    return {
        "language": target_language,
        "optimized_content": optimized_content,
        "seo_score": calculate_seo_score(optimized_content, target_language),
        "recommendations": get_language_specific_recommendations(target_language)
    }

@router.get("/translation-memory")
async def get_translation_memory(source_lang: str, target_lang: str):
    """번역 메모리 조회 (이전 번역 재사용)"""
    # 실제로는 데이터베이스에서 조회
    memory_entries = [
        {
            "source": "AI 시대의 콘텐츠 마케팅",
            "translation": "Content Marketing in the AI Era",
            "usage_count": 15,
            "last_used": "2025-07-12T10:00:00Z"
        },
        {
            "source": "블로그 자동화",
            "translation": "Blog Automation",
            "usage_count": 23,
            "last_used": "2025-07-13T08:30:00Z"
        }
    ]
    
    return {
        "source_language": source_lang,
        "target_language": target_lang,
        "entries": memory_entries,
        "total_entries": len(memory_entries)
    }

@router.post("/glossary")
async def manage_glossary(action: str, terms: List[Dict]):
    """용어집 관리 (일관된 번역을 위한)"""
    if action == "add":
        # 용어 추가
        return {"message": f"{len(terms)}개 용어가 추가되었습니다", "status": "success"}
    elif action == "update":
        # 용어 업데이트
        return {"message": f"{len(terms)}개 용어가 업데이트되었습니다", "status": "success"}
    elif action == "delete":
        # 용어 삭제
        return {"message": f"{len(terms)}개 용어가 삭제되었습니다", "status": "success"}
    else:
        raise HTTPException(status_code=400, detail="잘못된 액션입니다")

# 헬퍼 함수들
async def simulate_translation(text: str, source_lang: str, target_lang: str, content_type: str) -> str:
    """번역 시뮬레이션"""
    await asyncio.sleep(0.5)  # API 호출 시뮬레이션
    
    # 실제로는 번역 API 사용
    translations = {
        "en": "AI-powered content marketing strategies are transforming how businesses engage with their audiences.",
        "ja": "AIを活用したコンテンツマーケティング戦略は、企業が顧客と関わる方法を変革しています。",
        "zh": "AI驱动的内容营销策略正在改变企业与受众互动的方式。",
        "es": "Las estrategias de marketing de contenidos impulsadas por IA están transformando la forma en que las empresas interactúan con sus audiencias."
    }
    
    return translations.get(target_lang, text)

def calculate_quality_score(source: str, translated: str) -> float:
    """번역 품질 점수 계산"""
    # 실제로는 더 복잡한 알고리즘 사용
    base_score = 85.0
    
    # 길이 비교
    length_ratio = len(translated) / len(source)
    if 0.8 <= length_ratio <= 1.2:
        base_score += 5
    
    # 기타 품질 지표 추가...
    
    return min(base_score + (len(translated) % 10), 100.0)

def calculate_translation_cost(word_count: int, target_lang: str) -> float:
    """번역 비용 계산"""
    base_rate = 0.05  # 단어당 기본 요금
    
    # 언어별 가중치
    language_rates = {
        "en": 1.0,
        "ja": 1.2,
        "zh": 1.2,
        "ar": 1.3,
        "ko": 1.1
    }
    
    rate = base_rate * language_rates.get(target_lang, 1.0)
    return round(word_count * rate, 2)

def detect_language_simple(text: str) -> Dict:
    """간단한 언어 감지"""
    # 실제로는 ML 모델 사용
    # 여기서는 간단한 규칙 기반
    
    if any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in text):
        return {
            "language": "ko",
            "confidence": 0.95,
            "alternatives": [{"en": 0.03}, {"ja": 0.02}]
        }
    elif any(ord(char) >= 0x4E00 and ord(char) <= 0x9FFF for char in text):
        return {
            "language": "zh",
            "confidence": 0.90,
            "alternatives": [{"ja": 0.08}, {"ko": 0.02}]
        }
    else:
        return {
            "language": "en",
            "confidence": 0.85,
            "alternatives": [{"es": 0.10}, {"fr": 0.05}]
        }

def optimize_title_for_language(title: str, lang: str) -> str:
    """언어별 제목 최적화"""
    # 실제로는 각 언어의 SEO 규칙 적용
    if lang == "ja":
        return f"【最新】{title}｜完全ガイド"
    elif lang == "en":
        return f"{title} - Complete Guide 2025"
    return title

def optimize_meta_for_language(meta: str, lang: str) -> str:
    """언어별 메타 설명 최적화"""
    # 각 언어별 최적 길이와 스타일 적용
    max_lengths = {
        "en": 160,
        "ko": 80,
        "ja": 120,
        "zh": 100
    }
    
    max_len = max_lengths.get(lang, 150)
    if len(meta) > max_len:
        return meta[:max_len-3] + "..."
    return meta

def localize_keywords(keywords: List[str], lang: str) -> List[str]:
    """키워드 현지화"""
    # 실제로는 각 언어별 키워드 데이터베이스 사용
    localized = []
    for keyword in keywords:
        # 간단한 매핑 예시
        if lang == "en" and keyword == "블로그":
            localized.append("blog")
        elif lang == "ja" and keyword == "마케팅":
            localized.append("マーケティング")
        else:
            localized.append(keyword)
    
    return localized

def optimize_content_for_language(content: str, lang: str) -> str:
    """콘텐츠 언어별 최적화"""
    # 각 언어의 문체와 표현 방식에 맞게 조정
    return content

def calculate_seo_score(content: Dict, lang: str) -> int:
    """언어별 SEO 점수 계산"""
    score = 70
    
    # 제목 길이 확인
    title_len = len(content.get("title", ""))
    if lang == "en" and 50 <= title_len <= 60:
        score += 10
    elif lang == "ko" and 25 <= title_len <= 35:
        score += 10
    
    # 메타 설명 확인
    if content.get("meta_description"):
        score += 10
    
    # 키워드 확인
    if len(content.get("keywords", [])) >= 3:
        score += 10
    
    return min(score, 100)

def get_language_specific_recommendations(lang: str) -> List[str]:
    """언어별 SEO 권장사항"""
    recommendations = {
        "ko": [
            "제목은 25-35자 이내로 작성하세요",
            "네이버 검색을 고려하여 키워드를 선정하세요",
            "한국식 표현과 어투를 사용하세요"
        ],
        "en": [
            "Use 50-60 characters for titles",
            "Include long-tail keywords",
            "Write in active voice"
        ],
        "ja": [
            "タイトルは32文字以内が理想的です",
            "カタカナ表記も含めてください",
            "です・ます調で統一してください"
        ]
    }
    
    return recommendations.get(lang, ["일반적인 SEO 가이드라인을 따르세요"])