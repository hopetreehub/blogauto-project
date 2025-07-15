#!/usr/bin/env python3
"""
Grok AI API 서비스 통합
xAI의 Grok 모델을 BlogAuto 시스템에 통합
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from dataclasses import dataclass
import logging

@dataclass
class GrokConfig:
    """Grok API 설정"""
    api_key: str
    base_url: str = "https://api.x.ai/v1"
    model: str = "grok-beta"
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 60

@dataclass
class GrokResponse:
    """Grok API 응답 구조"""
    content: str
    model: str
    usage: Dict[str, int]
    response_time: float
    success: bool
    error: Optional[str] = None

class GrokAIService:
    """Grok AI API 서비스 클래스"""
    
    def __init__(self, config: GrokConfig):
        self.config = config
        self.session = None
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "BlogAuto-GrokAI/1.0"
        }
        
        # 로깅 설정
        self.logger = logging.getLogger(__name__)
        
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 시작"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def generate_content(self, prompt: str, system_prompt: Optional[str] = None) -> GrokResponse:
        """Grok을 사용한 콘텐츠 생성"""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False
        }
        
        try:
            async with self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload
            ) as response:
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    
                    return GrokResponse(
                        content=content,
                        model=data.get("model", self.config.model),
                        usage=usage,
                        response_time=response_time,
                        success=True
                    )
                else:
                    error_text = await response.text()
                    self.logger.error(f"Grok API 오류 {response.status}: {error_text}")
                    
                    return GrokResponse(
                        content="",
                        model=self.config.model,
                        usage={},
                        response_time=response_time,
                        success=False,
                        error=f"API 오류 {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Grok API 연결 오류: {str(e)}")
            
            return GrokResponse(
                content="",
                model=self.config.model,
                usage={},
                response_time=response_time,
                success=False,
                error=f"연결 오류: {str(e)}"
            )
    
    async def analyze_keywords_with_grok(self, keyword: str, country: str = "KR") -> Dict[str, Any]:
        """Grok을 사용한 키워드 분석"""
        
        system_prompt = """당신은 SEO 전문가입니다. 주어진 키워드에 대해 다음 정보를 JSON 형식으로 제공해주세요:
1. 검색 의도 분석
2. 관련 키워드 5개
3. 콘텐츠 추천 방향
4. SEO 난이도 예측 (1-10)
5. 타겟 오디언스"""
        
        prompt = f"""키워드: "{keyword}"
국가: {country}

위 키워드에 대한 상세 분석을 JSON 형식으로 제공해주세요."""

        response = await self.generate_content(prompt, system_prompt)
        
        if response.success:
            try:
                # JSON 파싱 시도
                analysis_data = json.loads(response.content)
                return {
                    "keyword": keyword,
                    "grok_analysis": analysis_data,
                    "response_time": response.response_time,
                    "model_used": response.model,
                    "success": True
                }
            except json.JSONDecodeError:
                # JSON이 아닌 경우 텍스트로 처리
                return {
                    "keyword": keyword,
                    "grok_analysis": {"raw_text": response.content},
                    "response_time": response.response_time,
                    "model_used": response.model,
                    "success": True
                }
        else:
            return {
                "keyword": keyword,
                "grok_analysis": {},
                "error": response.error,
                "success": False
            }
    
    async def generate_titles_with_grok(self, keyword: str, count: int = 5, tone: str = "professional") -> Dict[str, Any]:
        """Grok을 사용한 제목 생성"""
        
        system_prompt = f"""당신은 SEO 제목 생성 전문가입니다. 
톤: {tone}
다음 조건을 만족하는 제목들을 생성해주세요:
1. 클릭률이 높을 것
2. SEO에 최적화될 것
3. 감정적 호소력이 있을 것
4. 키워드를 자연스럽게 포함할 것
5. 각 제목에 대해 1-100점 점수도 함께 제공할 것

JSON 형식으로 응답해주세요."""

        prompt = f"""키워드: "{keyword}"
개수: {count}개
톤: {tone}

위 조건에 맞는 SEO 최적화 제목들을 생성해주세요."""

        response = await self.generate_content(prompt, system_prompt)
        
        if response.success:
            try:
                titles_data = json.loads(response.content)
                return {
                    "keyword": keyword,
                    "titles": titles_data,
                    "response_time": response.response_time,
                    "model_used": response.model,
                    "success": True
                }
            except json.JSONDecodeError:
                # 백업: 텍스트에서 제목 추출
                lines = response.content.split('\n')
                titles = []
                for i, line in enumerate(lines[:count]):
                    if line.strip():
                        titles.append({
                            "title": line.strip(),
                            "score": 85.0 + (i * 2),  # 기본 점수
                            "reason": "Grok AI 생성"
                        })
                
                return {
                    "keyword": keyword,
                    "titles": titles,
                    "response_time": response.response_time,
                    "model_used": response.model,
                    "success": True
                }
        else:
            return {
                "keyword": keyword,
                "titles": [],
                "error": response.error,
                "success": False
            }
    
    async def generate_content_with_grok(
        self, 
        title: str, 
        keyword: str, 
        length: str = "medium",
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Grok을 사용한 콘텐츠 생성"""
        
        length_mapping = {
            "short": "800-1200자",
            "medium": "1500-2500자", 
            "long": "2500-4000자"
        }
        
        target_length = length_mapping.get(length, "1500-2500자")
        
        system_prompt = f"""당신은 전문 콘텐츠 작가입니다.
다음 조건을 만족하는 고품질 블로그 글을 작성해주세요:

1. 길이: {target_length}
2. 톤: {tone}
3. SEO 최적화 포함
4. 구조화된 내용 (헤딩 사용)
5. 실용적이고 유용한 정보
6. 읽기 쉬운 문체

마크다운 형식으로 작성해주세요."""

        prompt = f"""제목: "{title}"
메인 키워드: "{keyword}"
길이: {length}
톤: {tone}

위 조건에 맞는 고품질 블로그 콘텐츠를 작성해주세요."""

        response = await self.generate_content(prompt, system_prompt)
        
        if response.success:
            content = response.content
            word_count = len(content.replace(' ', '').replace('\n', ''))
            
            # 간단한 SEO 점수 계산
            seo_score = self._calculate_seo_score(content, keyword)
            
            return {
                "title": title,
                "keyword": keyword,
                "content": content,
                "word_count": word_count,
                "seo_score": seo_score,
                "readability_score": 88.0,  # Grok의 기본 가독성
                "response_time": response.response_time,
                "model_used": response.model,
                "success": True
            }
        else:
            return {
                "title": title,
                "keyword": keyword,
                "content": "",
                "error": response.error,
                "success": False
            }
    
    def _calculate_seo_score(self, content: str, keyword: str) -> float:
        """간단한 SEO 점수 계산"""
        score = 70.0  # 기본 점수
        
        # 키워드 밀도 확인
        keyword_count = content.lower().count(keyword.lower())
        content_length = len(content)
        
        if content_length > 0:
            keyword_density = (keyword_count * len(keyword)) / content_length
            if 0.01 <= keyword_density <= 0.03:  # 1-3% 적정
                score += 10
            elif keyword_density > 0:
                score += 5
        
        # 구조 확인
        if '##' in content:  # H2 헤딩 존재
            score += 5
        if '###' in content:  # H3 헤딩 존재
            score += 3
        if '-' in content or '*' in content:  # 리스트 존재
            score += 2
        
        # 길이 확인
        if 1000 <= content_length <= 3000:
            score += 5
        elif content_length > 500:
            score += 3
        
        return min(score, 100.0)

class MultiAIGrokService:
    """다중 AI 모델과 Grok 통합 서비스"""
    
    def __init__(self, grok_config: GrokConfig, openai_api_key: str = None):
        self.grok_service = GrokAIService(grok_config)
        self.openai_api_key = openai_api_key
        
    async def __aenter__(self):
        await self.grok_service.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.grok_service.__aexit__(exc_type, exc_val, exc_tb)
    
    async def compare_ai_responses(self, prompt: str, task_type: str) -> Dict[str, Any]:
        """여러 AI 모델의 응답 비교"""
        
        results = {
            "task_type": task_type,
            "prompt": prompt,
            "responses": {},
            "comparison": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Grok 응답
        grok_response = await self.grok_service.generate_content(prompt)
        results["responses"]["grok"] = {
            "content": grok_response.content,
            "response_time": grok_response.response_time,
            "success": grok_response.success,
            "model": grok_response.model,
            "error": grok_response.error
        }
        
        # OpenAI 응답 (사용 가능한 경우)
        if self.openai_api_key:
            try:
                import openai
                openai.api_key = self.openai_api_key
                
                start_time = time.time()
                openai_response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0.7
                )
                
                results["responses"]["openai"] = {
                    "content": openai_response.choices[0].message.content,
                    "response_time": time.time() - start_time,
                    "success": True,
                    "model": "gpt-4",
                    "error": None
                }
                
            except Exception as e:
                results["responses"]["openai"] = {
                    "content": "",
                    "response_time": 0,
                    "success": False,
                    "model": "gpt-4",
                    "error": str(e)
                }
        
        # 응답 비교 분석
        results["comparison"] = self._analyze_responses(results["responses"])
        
        return results
    
    def _analyze_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """AI 응답 비교 분석"""
        
        comparison = {
            "response_count": len(responses),
            "successful_responses": 0,
            "average_response_time": 0,
            "content_lengths": {},
            "recommendations": []
        }
        
        total_time = 0
        successful_count = 0
        
        for ai_name, response in responses.items():
            if response["success"]:
                successful_count += 1
                total_time += response["response_time"]
                comparison["content_lengths"][ai_name] = len(response["content"])
            else:
                comparison["content_lengths"][ai_name] = 0
        
        comparison["successful_responses"] = successful_count
        
        if successful_count > 0:
            comparison["average_response_time"] = total_time / successful_count
        
        # 권장사항 생성
        if successful_count == 0:
            comparison["recommendations"].append("모든 AI 모델에서 응답 실패")
        elif successful_count == 1:
            comparison["recommendations"].append("단일 AI 모델만 성공")
        else:
            comparison["recommendations"].append("다중 AI 모델 성공 - 품질 비교 가능")
        
        return comparison

# 사용 예제 및 테스트 함수
async def test_grok_integration():
    """Grok 통합 테스트"""
    
    # 환경 변수에서 API 키 가져오기 (실제 사용 시)
    grok_api_key = os.environ.get("GROK_API_KEY", "test-key")
    
    config = GrokConfig(
        api_key=grok_api_key,
        model="grok-beta",
        max_tokens=2000,
        temperature=0.7
    )
    
    async with GrokAIService(config) as grok_service:
        # 키워드 분석 테스트
        keyword_result = await grok_service.analyze_keywords_with_grok("건강한 식단")
        print(f"키워드 분석 결과: {keyword_result}")
        
        # 제목 생성 테스트
        title_result = await grok_service.generate_titles_with_grok("건강한 식단", 3)
        print(f"제목 생성 결과: {title_result}")
        
        # 콘텐츠 생성 테스트
        content_result = await grok_service.generate_content_with_grok(
            "건강한 식단으로 면역력 높이기",
            "건강한 식단",
            "medium"
        )
        print(f"콘텐츠 생성 결과: {content_result}")

if __name__ == "__main__":
    asyncio.run(test_grok_integration())