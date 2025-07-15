#!/usr/bin/env python3
"""
다중 AI 모델 통합 엔진
OpenAI GPT, Google Gemini, xAI Grok을 통합한 고급 콘텐츠 생성 시스템
"""

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import hashlib

# Grok 서비스 import
from grok_ai_service import GrokAIService, GrokConfig

class AIModel(Enum):
    """지원하는 AI 모델들"""
    OPENAI_GPT4 = "openai-gpt4"
    OPENAI_GPT35 = "openai-gpt3.5"
    GOOGLE_GEMINI = "google-gemini"
    XAI_GROK = "xai-grok"

@dataclass
class AIModelConfig:
    """AI 모델 설정"""
    name: str
    api_key: str
    base_url: str
    model_name: str
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 60
    enabled: bool = True

@dataclass
class AIResponse:
    """AI 응답 통합 구조"""
    model: str
    content: str
    response_time: float
    success: bool
    usage: Dict[str, int]
    metadata: Dict[str, Any]
    error: Optional[str] = None
    confidence_score: float = 0.0

@dataclass
class MultiAIResult:
    """다중 AI 결과 구조"""
    task_type: str
    input_data: Dict[str, Any]
    responses: List[AIResponse]
    best_response: Optional[AIResponse]
    consensus_result: Optional[Dict[str, Any]]
    comparison_analysis: Dict[str, Any]
    timestamp: str
    total_time: float

class MultiAIEngine:
    """다중 AI 모델 통합 엔진"""
    
    def __init__(self):
        self.models: Dict[str, AIModelConfig] = {}
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # 성능 및 품질 메트릭
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "model_performance": {},
            "average_response_time": 0.0
        }
        
    def add_model(self, config: AIModelConfig):
        """AI 모델 추가"""
        self.models[config.name] = config
        self.performance_metrics["model_performance"][config.name] = {
            "requests": 0,
            "successes": 0,
            "total_time": 0.0,
            "average_score": 0.0
        }
        
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 시작"""
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()
    
    async def _call_openai_gpt(self, config: AIModelConfig, messages: List[Dict], **kwargs) -> AIResponse:
        """OpenAI GPT 모델 호출"""
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            **kwargs
        }
        
        try:
            async with self.session.post(
                f"{config.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    
                    # 품질 점수 계산
                    confidence_score = self._calculate_content_quality(content)
                    
                    return AIResponse(
                        model=config.name,
                        content=content,
                        response_time=response_time,
                        success=True,
                        usage=usage,
                        metadata={"finish_reason": data["choices"][0].get("finish_reason")},
                        confidence_score=confidence_score
                    )
                else:
                    error_text = await response.text()
                    return AIResponse(
                        model=config.name,
                        content="",
                        response_time=response_time,
                        success=False,
                        usage={},
                        metadata={},
                        error=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            return AIResponse(
                model=config.name,
                content="",
                response_time=time.time() - start_time,
                success=False,
                usage={},
                metadata={},
                error=str(e)
            )
    
    async def _call_google_gemini(self, config: AIModelConfig, messages: List[Dict], **kwargs) -> AIResponse:
        """Google Gemini 모델 호출"""
        start_time = time.time()
        
        # Gemini API 형식으로 변환
        prompt = "\\n".join([msg["content"] for msg in messages if msg["role"] == "user"])
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": config.temperature,
                "maxOutputTokens": config.max_tokens
            }
        }
        
        url = f"{config.base_url}/v1/models/{config.model_name}:generateContent?key={config.api_key}"
        
        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    if "candidates" in data and data["candidates"]:
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        
                        # 사용량 정보 (Gemini는 다른 형식)
                        usage = {
                            "prompt_tokens": data.get("usageMetadata", {}).get("promptTokenCount", 0),
                            "completion_tokens": data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                            "total_tokens": data.get("usageMetadata", {}).get("totalTokenCount", 0)
                        }
                        
                        confidence_score = self._calculate_content_quality(content)
                        
                        return AIResponse(
                            model=config.name,
                            content=content,
                            response_time=response_time,
                            success=True,
                            usage=usage,
                            metadata={"safety_ratings": data["candidates"][0].get("safetyRatings", [])},
                            confidence_score=confidence_score
                        )
                    else:
                        return AIResponse(
                            model=config.name,
                            content="",
                            response_time=response_time,
                            success=False,
                            usage={},
                            metadata={},
                            error="No content in Gemini response"
                        )
                else:
                    error_text = await response.text()
                    return AIResponse(
                        model=config.name,
                        content="",
                        response_time=response_time,
                        success=False,
                        usage={},
                        metadata={},
                        error=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            return AIResponse(
                model=config.name,
                content="",
                response_time=time.time() - start_time,
                success=False,
                usage={},
                metadata={},
                error=str(e)
            )
    
    async def _call_xai_grok(self, config: AIModelConfig, messages: List[Dict], **kwargs) -> AIResponse:
        """xAI Grok 모델 호출"""
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config.model_name,
            "messages": messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "stream": False,
            **kwargs
        }
        
        try:
            async with self.session.post(
                f"{config.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    usage = data.get("usage", {})
                    
                    confidence_score = self._calculate_content_quality(content)
                    
                    return AIResponse(
                        model=config.name,
                        content=content,
                        response_time=response_time,
                        success=True,
                        usage=usage,
                        metadata={"model_version": data.get("model", config.model_name)},
                        confidence_score=confidence_score
                    )
                else:
                    error_text = await response.text()
                    return AIResponse(
                        model=config.name,
                        content="",
                        response_time=response_time,
                        success=False,
                        usage={},
                        metadata={},
                        error=f"HTTP {response.status}: {error_text}"
                    )
                    
        except Exception as e:
            return AIResponse(
                model=config.name,
                content="",
                response_time=time.time() - start_time,
                success=False,
                usage={},
                metadata={},
                error=str(e)
            )
    
    async def generate_content_multi_ai(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        task_type: str = "content_generation",
        use_models: Optional[List[str]] = None,
        consensus_mode: bool = True
    ) -> MultiAIResult:
        """다중 AI 모델을 사용한 콘텐츠 생성"""
        
        start_time = time.time()
        
        # 사용할 모델 결정
        if use_models is None:
            use_models = [name for name, config in self.models.items() if config.enabled]
        
        # 메시지 구성
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # 병렬로 모든 모델 호출
        tasks = []
        for model_name in use_models:
            if model_name not in self.models:
                continue
                
            config = self.models[model_name]
            if not config.enabled:
                continue
            
            if config.name.startswith("openai"):
                task = self._call_openai_gpt(config, messages)
            elif config.name.startswith("google"):
                task = self._call_google_gemini(config, messages)
            elif config.name.startswith("xai"):
                task = self._call_xai_grok(config, messages)
            else:
                continue
                
            tasks.append(task)
        
        # 모든 응답 대기
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 예외 처리된 응답들을 AIResponse로 변환
        valid_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                # 예외를 AIResponse로 변환
                model_name = use_models[i] if i < len(use_models) else "unknown"
                error_response = AIResponse(
                    model=model_name,
                    content="",
                    response_time=0.0,
                    success=False,
                    usage={},
                    metadata={},
                    error=str(response)
                )
                valid_responses.append(error_response)
            else:
                valid_responses.append(response)
        
        # 성능 메트릭 업데이트
        self._update_performance_metrics(valid_responses)
        
        # 최고 응답 선택
        best_response = self._select_best_response(valid_responses)
        
        # 컨센서스 결과 생성 (가능한 경우)
        consensus_result = None
        if consensus_mode and len([r for r in valid_responses if r.success]) >= 2:
            consensus_result = self._generate_consensus(valid_responses)
        
        # 비교 분석
        comparison_analysis = self._analyze_responses(valid_responses)
        
        total_time = time.time() - start_time
        
        return MultiAIResult(
            task_type=task_type,
            input_data={"prompt": prompt, "system_prompt": system_prompt},
            responses=valid_responses,
            best_response=best_response,
            consensus_result=consensus_result,
            comparison_analysis=comparison_analysis,
            timestamp=datetime.now().isoformat(),
            total_time=total_time
        )
    
    def _calculate_content_quality(self, content: str) -> float:
        """콘텐츠 품질 점수 계산"""
        if not content or len(content.strip()) == 0:
            return 0.0
        
        score = 50.0  # 기본 점수
        
        # 길이 점수 (적정 길이)
        length = len(content)
        if 500 <= length <= 3000:
            score += 20
        elif 200 <= length <= 5000:
            score += 15
        elif length > 100:
            score += 10
        
        # 구조 점수
        if '\\n\\n' in content:  # 문단 구분
            score += 5
        if any(marker in content for marker in ['##', '###', '####']):  # 헤딩
            score += 10
        if any(marker in content for marker in ['-', '*', '1.']):  # 리스트
            score += 5
        
        # 문장 다양성
        sentences = content.split('.')
        if len(sentences) > 3:
            avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences)
            if 20 <= avg_sentence_length <= 100:
                score += 10
        
        return min(score, 100.0)
    
    def _select_best_response(self, responses: List[AIResponse]) -> Optional[AIResponse]:
        """최고 응답 선택"""
        successful_responses = [r for r in responses if r.success]
        
        if not successful_responses:
            return None
        
        # 품질 점수 기준으로 선택
        return max(successful_responses, key=lambda r: r.confidence_score)
    
    def _generate_consensus(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """컨센서스 결과 생성"""
        successful_responses = [r for r in responses if r.success]
        
        if len(successful_responses) < 2:
            return {}
        
        # 평균 품질 점수
        avg_quality = sum(r.confidence_score for r in successful_responses) / len(successful_responses)
        
        # 평균 응답 시간
        avg_time = sum(r.response_time for r in successful_responses) / len(successful_responses)
        
        # 콘텐츠 길이 분석
        lengths = [len(r.content) for r in successful_responses]
        avg_length = sum(lengths) / len(lengths)
        
        # 공통 키워드 추출 (간단한 버전)
        all_words = []
        for response in successful_responses:
            words = response.content.lower().split()
            all_words.extend([w for w in words if len(w) > 3])
        
        # 빈도 계산
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        common_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "consensus_quality_score": avg_quality,
            "average_response_time": avg_time,
            "average_content_length": avg_length,
            "participating_models": [r.model for r in successful_responses],
            "common_keywords": [kw[0] for kw in common_keywords],
            "agreement_level": self._calculate_agreement_level(successful_responses)
        }
    
    def _calculate_agreement_level(self, responses: List[AIResponse]) -> float:
        """응답 간 일치도 계산"""
        if len(responses) < 2:
            return 100.0
        
        # 간단한 일치도: 콘텐츠 길이 유사성 기반
        lengths = [len(r.content) for r in responses]
        avg_length = sum(lengths) / len(lengths)
        
        # 표준편차 계산
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        std_dev = variance ** 0.5
        
        # 일치도 점수 (낮은 표준편차 = 높은 일치도)
        if avg_length > 0:
            agreement = max(0, 100 - (std_dev / avg_length * 100))
        else:
            agreement = 0
        
        return min(agreement, 100.0)
    
    def _analyze_responses(self, responses: List[AIResponse]) -> Dict[str, Any]:
        """응답 분석"""
        total_responses = len(responses)
        successful_responses = [r for r in responses if r.success]
        failed_responses = [r for r in responses if not r.success]
        
        analysis = {
            "total_models": total_responses,
            "successful_models": len(successful_responses),
            "failed_models": len(failed_responses),
            "success_rate": len(successful_responses) / total_responses * 100 if total_responses > 0 else 0,
            "model_performance": {},
            "recommendations": []
        }
        
        # 모델별 성능 분석
        for response in responses:
            analysis["model_performance"][response.model] = {
                "success": response.success,
                "response_time": response.response_time,
                "content_length": len(response.content),
                "quality_score": response.confidence_score,
                "error": response.error
            }
        
        # 추천사항 생성
        if len(successful_responses) == 0:
            analysis["recommendations"].append("모든 AI 모델 실패 - API 키 및 설정 확인 필요")
        elif len(successful_responses) == 1:
            analysis["recommendations"].append("단일 모델만 성공 - 다른 모델 설정 확인 권장")
        elif len(successful_responses) >= 2:
            analysis["recommendations"].append("다중 모델 성공 - 컨센서스 결과 활용 가능")
        
        # 최고 성능 모델 식별
        if successful_responses:
            best_model = max(successful_responses, key=lambda r: r.confidence_score)
            analysis["best_performing_model"] = best_model.model
            analysis["recommendations"].append(f"최고 성능 모델: {best_model.model}")
        
        return analysis
    
    def _update_performance_metrics(self, responses: List[AIResponse]):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_requests"] += len(responses)
        
        for response in responses:
            model_name = response.model
            if model_name not in self.performance_metrics["model_performance"]:
                self.performance_metrics["model_performance"][model_name] = {
                    "requests": 0,
                    "successes": 0,
                    "total_time": 0.0,
                    "average_score": 0.0
                }
            
            metrics = self.performance_metrics["model_performance"][model_name]
            metrics["requests"] += 1
            metrics["total_time"] += response.response_time
            
            if response.success:
                metrics["successes"] += 1
                self.performance_metrics["successful_requests"] += 1
                
                # 평균 점수 업데이트
                current_avg = metrics["average_score"]
                success_count = metrics["successes"]
                metrics["average_score"] = (current_avg * (success_count - 1) + response.confidence_score) / success_count
    
    def get_performance_report(self) -> Dict[str, Any]:
        """성능 보고서 생성"""
        total_requests = self.performance_metrics["total_requests"]
        successful_requests = self.performance_metrics["successful_requests"]
        
        report = {
            "overall_statistics": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": successful_requests / total_requests * 100 if total_requests > 0 else 0,
                "total_models_configured": len(self.models)
            },
            "model_statistics": {},
            "recommendations": []
        }
        
        # 모델별 통계
        for model_name, metrics in self.performance_metrics["model_performance"].items():
            if metrics["requests"] > 0:
                report["model_statistics"][model_name] = {
                    "requests": metrics["requests"],
                    "successes": metrics["successes"],
                    "success_rate": metrics["successes"] / metrics["requests"] * 100,
                    "average_response_time": metrics["total_time"] / metrics["requests"],
                    "average_quality_score": metrics["average_score"]
                }
        
        # 추천사항 생성
        if total_requests == 0:
            report["recommendations"].append("아직 요청이 없습니다.")
        else:
            # 최고 성능 모델 찾기
            best_model = None
            best_score = 0
            
            for model_name, stats in report["model_statistics"].items():
                if stats["success_rate"] > 80 and stats["average_quality_score"] > best_score:
                    best_model = model_name
                    best_score = stats["average_quality_score"]
            
            if best_model:
                report["recommendations"].append(f"최고 성능 모델: {best_model}")
            
            # 개선이 필요한 모델
            for model_name, stats in report["model_statistics"].items():
                if stats["success_rate"] < 50:
                    report["recommendations"].append(f"{model_name} 모델 설정 확인 필요")
        
        return report

# 설정 도우미 함수
def create_standard_multi_ai_engine() -> MultiAIEngine:
    """표준 다중 AI 엔진 생성"""
    engine = MultiAIEngine()
    
    # OpenAI GPT-4 설정
    if os.environ.get("OPENAI_API_KEY"):
        openai_config = AIModelConfig(
            name="openai-gpt4",
            api_key=os.environ["OPENAI_API_KEY"],
            base_url="https://api.openai.com/v1",
            model_name="gpt-4",
            max_tokens=2000,
            temperature=0.7,
            enabled=True
        )
        engine.add_model(openai_config)
    
    # Google Gemini 설정
    if os.environ.get("GEMINI_API_KEY"):
        gemini_config = AIModelConfig(
            name="google-gemini",
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com",
            model_name="gemini-pro",
            max_tokens=2000,
            temperature=0.7,
            enabled=True
        )
        engine.add_model(gemini_config)
    
    # xAI Grok 설정
    if os.environ.get("GROK_API_KEY"):
        grok_config = AIModelConfig(
            name="xai-grok",
            api_key=os.environ["GROK_API_KEY"],
            base_url="https://api.x.ai/v1",
            model_name="grok-beta",
            max_tokens=2000,
            temperature=0.7,
            enabled=True
        )
        engine.add_model(grok_config)
    
    return engine

# 테스트 함수
async def test_multi_ai_engine():
    """다중 AI 엔진 테스트"""
    
    engine = create_standard_multi_ai_engine()
    
    async with engine:
        # 테스트 프롬프트
        prompt = "건강한 아침 식사의 중요성에 대해 500자 내외로 설명해주세요."
        system_prompt = "당신은 영양학 전문가입니다. 과학적 근거를 바탕으로 설명해주세요."
        
        # 다중 AI 콘텐츠 생성
        result = await engine.generate_content_multi_ai(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type="nutrition_content",
            consensus_mode=True
        )
        
        # 결과 출력
        print("=== 다중 AI 콘텐츠 생성 결과 ===")
        print(f"작업 유형: {result.task_type}")
        print(f"총 소요 시간: {result.total_time:.2f}초")
        print(f"참여 모델 수: {len(result.responses)}")
        
        for response in result.responses:
            print(f"\\n--- {response.model} ---")
            print(f"성공: {response.success}")
            print(f"응답 시간: {response.response_time:.2f}초")
            if response.success:
                print(f"품질 점수: {response.confidence_score:.1f}")
                print(f"콘텐츠 길이: {len(response.content)}자")
                print(f"내용 미리보기: {response.content[:100]}...")
            else:
                print(f"오류: {response.error}")
        
        if result.best_response:
            print(f"\\n=== 최고 응답 ({result.best_response.model}) ===")
            print(result.best_response.content)
        
        if result.consensus_result:
            print(f"\\n=== 컨센서스 결과 ===")
            print(json.dumps(result.consensus_result, indent=2, ensure_ascii=False))
        
        # 성능 보고서
        performance = engine.get_performance_report()
        print(f"\\n=== 성능 보고서 ===")
        print(json.dumps(performance, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_multi_ai_engine())