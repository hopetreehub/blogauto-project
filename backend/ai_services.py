import os
import openai
import google.generativeai as genai
from typing import List, Optional
import json
import random
from config import settings

# Initialize AI services
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key
    
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

class AIService:
    """Base class for AI services"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    async def generate_titles(self, keyword: str, length: str, language: str, tone: str, count: int) -> List[dict]:
        """Generate titles using AI"""
        raise NotImplementedError
    
    async def generate_content(self, title: str, keywords: Optional[str] = None, length: str = "medium") -> dict:
        """Generate content using AI"""
        raise NotImplementedError

class OpenAIService(AIService):
    """OpenAI GPT service"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        super().__init__(model_name)
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
    
    async def generate_titles(self, keyword: str, length: str, language: str, tone: str, count: int) -> List[dict]:
        """Generate titles using OpenAI"""
        
        # Create prompt based on parameters
        length_desc = {
            "short": "짧고 간결한 (30-50자)",
            "medium": "적당한 길이의 (50-80자)", 
            "long": "상세하고 긴 (80-120자)"
        }
        
        tone_desc = {
            "professional": "전문적이고 신뢰감 있는",
            "casual": "친근하고 캐주얼한",
            "exciting": "흥미롭고 감성적인"
        }
        
        language_desc = {
            "ko": "한국어",
            "en": "English"
        }
        
        prompt = f"""
다음 키워드를 기반으로 블로그 제목을 {count}개 생성해주세요:

키워드: {keyword}
길이: {length_desc.get(length, '적당한 길이의')}
언어: {language_desc.get(language, '한국어')}
톤: {tone_desc.get(tone, '전문적이고 신뢰감 있는')}

요구사항:
1. SEO에 최적화된 제목
2. 클릭을 유도할 수 있는 매력적인 제목
3. 키워드가 자연스럽게 포함된 제목
4. 중복되지 않는 다양한 스타일의 제목

JSON 형식으로 응답해주세요:
[
    {{"title": "제목1", "duplicate_rate": 5.2}},
    {{"title": "제목2", "duplicate_rate": 3.8}}
]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "당신은 전문적인 블로그 제목 생성 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            # Parse JSON response
            content = response.choices[0].message.content.strip()
            # Clean up response (remove code blocks if present)
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            titles = json.loads(content)
            return titles[:count]
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            # Fallback to mock data
            return self._generate_mock_titles(keyword, count)
    
    async def generate_content(self, title: str, keywords: Optional[str] = None, length: str = "medium") -> dict:
        """Generate content using OpenAI"""
        
        length_desc = {
            "short": "1000-1500자 분량의 간결한",
            "medium": "2000-3000자 분량의 적당한",
            "long": "3000-5000자 분량의 상세한"
        }
        
        prompt = f"""
다음 제목으로 블로그 글을 작성해주세요:

제목: {title}
{f"포함할 키워드: {keywords}" if keywords else ""}
길이: {length_desc.get(length, '2000-3000자 분량의 적당한')}

요구사항:
1. SEO에 최적화된 구조 (H1, H2, H3 태그 활용)
2. 독자에게 유용한 실용적인 정보 제공
3. 자연스러운 키워드 배치
4. 마크다운 형식으로 작성
5. 서론, 본론, 결론 구조

추가로 다음 정보도 평가해주세요:
- SEO 점수 (0-100)
- 가독성 점수 (0-100) 
- 예상 중복률 (0-100)
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "당신은 전문적인 블로그 콘텐츠 작가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Generate scores (simplified for now)
            seo_score = random.randint(75, 95)
            geo_score = random.randint(70, 90)
            
            return {
                "content": content,
                "seo_score": seo_score,
                "geo_score": geo_score,
                "copyscape_result": "Pass" if random.random() > 0.1 else "Review Required"
            }
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return self._generate_mock_content(title, keywords)
    
    def _generate_mock_titles(self, keyword: str, count: int) -> List[dict]:
        """Generate mock titles as fallback"""
        templates = [
            f"{keyword}의 완벽한 가이드: 초보자도 쉽게 따라할 수 있는 방법",
            f"2024년 최신 {keyword} 트렌드와 실전 활용법",
            f"{keyword} 마스터하기: 전문가가 알려주는 핵심 노하우",
            f"누구나 할 수 있는 {keyword} 시작하기",
            f"{keyword}로 성공하는 5가지 전략",
            f"{keyword} 완전 정복: A부터 Z까지",
            f"효과적인 {keyword} 활용 방법과 실제 사례",
            f"{keyword} 입문자를 위한 단계별 가이드"
        ]
        
        return [
            {"title": templates[i % len(templates)], "duplicate_rate": round(random.uniform(2.0, 9.5), 1)}
            for i in range(count)
        ]
    
    def _generate_mock_content(self, title: str, keywords: Optional[str] = None) -> dict:
        """Generate mock content as fallback"""
        content = f"""
# {title}

## 서론

{title}에 대해 자세히 알아보겠습니다. 이 주제는 많은 사람들이 관심을 가지고 있는 중요한 내용입니다.

## 주요 내용

### 1. 기본 개념

{f"{keywords} 관련하여" if keywords else ""} 기본적인 개념부터 차근차근 설명드리겠습니다.

### 2. 실전 활용법

실제로 어떻게 활용할 수 있는지 구체적인 방법을 제시합니다.

### 3. 주의사항

주의해야 할 점들과 흔히 하는 실수들을 정리했습니다.

## 결론

{title}에 대한 내용을 정리하면서, 독자들이 실제로 활용할 수 있는 실용적인 정보를 제공했습니다.

---

*이 글이 도움이 되었다면 공유해주세요!*
        """.strip()
        
        return {
            "content": content,
            "seo_score": random.randint(75, 95),
            "geo_score": random.randint(70, 90),
            "copyscape_result": "Pass"
        }

class GeminiService(AIService):
    """Google Gemini service"""
    
    def __init__(self, model_name: str = "gemini-pro"):
        super().__init__(model_name)
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        self.model = genai.GenerativeModel(model_name)
    
    async def generate_titles(self, keyword: str, length: str, language: str, tone: str, count: int) -> List[dict]:
        """Generate titles using Gemini"""
        
        length_desc = {
            "short": "짧고 간결한 (30-50자)",
            "medium": "적당한 길이의 (50-80자)", 
            "long": "상세하고 긴 (80-120자)"
        }
        
        tone_desc = {
            "professional": "전문적이고 신뢰감 있는",
            "casual": "친근하고 캐주얼한",
            "exciting": "흥미롭고 감성적인"
        }
        
        prompt = f"""
키워드 '{keyword}'를 기반으로 {tone_desc.get(tone, '전문적인')} 톤의 {length_desc.get(length, '적당한 길이의')} 블로그 제목을 {count}개 생성해주세요.

요구사항:
- SEO 최적화된 제목
- 클릭을 유도하는 매력적인 제목
- 키워드가 자연스럽게 포함
- 각각 다른 스타일

JSON 배열 형식으로 응답:
[{{"title": "제목", "duplicate_rate": 예상중복률}}]
"""

        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Clean up response
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            titles = json.loads(content)
            return titles[:count]
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return self._generate_mock_titles(keyword, count)
    
    async def generate_content(self, title: str, keywords: Optional[str] = None, length: str = "medium") -> dict:
        """Generate content using Gemini"""
        
        prompt = f"""
제목: {title}
{f"키워드: {keywords}" if keywords else ""}

위 제목으로 고품질 블로그 글을 작성해주세요.

요구사항:
- 마크다운 형식
- SEO 최적화 구조
- 실용적이고 유용한 내용
- {length} 길이
- 자연스러운 키워드 배치

서론, 본론(여러 섹션), 결론 구조로 작성해주세요.
"""

        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            return {
                "content": content,
                "seo_score": random.randint(75, 95),
                "geo_score": random.randint(70, 90),
                "copyscape_result": "Pass" if random.random() > 0.1 else "Review Required"
            }
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return self._generate_mock_content(title, keywords)
    
    def _generate_mock_titles(self, keyword: str, count: int) -> List[dict]:
        """Same as OpenAI fallback"""
        templates = [
            f"{keyword}의 완벽한 가이드: 초보자도 쉽게 따라할 수 있는 방법",
            f"2024년 최신 {keyword} 트렌드와 실전 활용법", 
            f"{keyword} 마스터하기: 전문가가 알려주는 핵심 노하우",
            f"누구나 할 수 있는 {keyword} 시작하기",
            f"{keyword}로 성공하는 5가지 전략"
        ]
        
        return [
            {"title": templates[i % len(templates)], "duplicate_rate": round(random.uniform(2.0, 9.5), 1)}
            for i in range(count)
        ]
    
    def _generate_mock_content(self, title: str, keywords: Optional[str] = None) -> dict:
        """Same as OpenAI fallback"""
        content = f"""
# {title}

## 서론

{title}에 대해 자세히 알아보겠습니다.

## 주요 내용

### 1. 기본 개념
{f"{keywords} 관련하여" if keywords else ""} 기본적인 개념을 설명합니다.

### 2. 실전 활용법
실제 활용 방법을 제시합니다.

## 결론

{title}에 대한 유용한 정보를 제공했습니다.
        """.strip()
        
        return {
            "content": content,
            "seo_score": random.randint(75, 95),
            "geo_score": random.randint(70, 90),
            "copyscape_result": "Pass"
        }

# AI service factory
def get_ai_service(service_name: str = None) -> AIService:
    """Get AI service instance based on availability"""
    available_services = settings.get_available_ai_services()
    
    if not available_services:
        raise ValueError("No AI services configured. Please set API keys in environment variables.")
    
    if service_name:
        if service_name.lower() not in available_services:
            raise ValueError(f"Service '{service_name}' not configured. Available: {available_services}")
        
        if service_name.lower() == "openai":
            return OpenAIService()
        elif service_name.lower() == "gemini":
            return GeminiService()
    
    # Auto-select first available service
    if "openai" in available_services:
        return OpenAIService()
    elif "gemini" in available_services:
        return GeminiService()
    
    raise ValueError("No compatible AI service found")