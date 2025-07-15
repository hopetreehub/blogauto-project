"""
다중 AI 제공자 통합 시스템
무료 우선 모드와 성능 우선 모드 지원
"""
import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
import aiohttp
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    
try:
    from groq import Groq
except ImportError:
    Groq = None
    
import openai
from abc import ABC, abstractmethod

# AI 제공자 타입 정의
AIProvider = Literal["gemini", "groq", "deepseek", "huggingface", "openrouter", "openai", "grok"]
AIMode = Literal["free_first", "performance_first"]

class BaseAIProvider(ABC):
    """AI 제공자 기본 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.is_free = False
        self.rate_limit = 60  # 분당 요청 수
        self.max_tokens = 4096
        self.name = ""
        
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """콘텐츠 생성"""
        pass
    
    @abstractmethod
    async def check_availability(self) -> bool:
        """API 사용 가능 여부 확인"""
        pass

class GeminiProvider(BaseAIProvider):
    """Google Gemini (무료)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.is_free = True
        self.name = "Gemini"
        self.rate_limit = 60
        self.max_tokens = 8192
        
    async def generate_content(self, prompt: str, **kwargs) -> str:
        if not genai:
            raise Exception("google-generativeai 패키지가 설치되지 않았습니다")
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini 오류: {str(e)}")
    
    async def check_availability(self) -> bool:
        return bool(self.api_key) and genai is not None

class GroqProvider(BaseAIProvider):
    """Groq (무료 티어 제공)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.is_free = True  # 무료 티어 있음
        self.name = "Groq"
        self.rate_limit = 30
        self.max_tokens = 4096
        
    async def generate_content(self, prompt: str, **kwargs) -> str:
        if not Groq:
            raise Exception("groq 패키지가 설치되지 않았습니다")
        try:
            client = Groq(api_key=self.api_key)
            completion = client.chat.completions.create(
                model="mixtral-8x7b-32768",  # 무료 모델
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=self.max_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq 오류: {str(e)}")
    
    async def check_availability(self) -> bool:
        return bool(self.api_key) and Groq is not None

class DeepSeekProvider(BaseAIProvider):
    """DeepSeek (저렴한 가격)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.is_free = False
        self.name = "DeepSeek"
        self.rate_limit = 100
        self.max_tokens = 16384
        self.base_url = "https://api.deepseek.com/v1"
        
    async def generate_content(self, prompt: str, **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": self.max_tokens
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"DeepSeek 오류: {str(e)}")
    
    async def check_availability(self) -> bool:
        return bool(self.api_key)

class HuggingFaceProvider(BaseAIProvider):
    """Hugging Face (무료 티어 제공)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.is_free = True  # 무료 티어 있음
        self.name = "HuggingFace"
        self.rate_limit = 30
        self.max_tokens = 1024
        self.base_url = "https://api-inference.huggingface.co/models"
        
    async def generate_content(self, prompt: str, model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1", **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": self.max_tokens,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{model}",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                    return str(result)
        except Exception as e:
            raise Exception(f"HuggingFace 오류: {str(e)}")
    
    async def check_availability(self) -> bool:
        return bool(self.api_key)

class OpenRouterProvider(BaseAIProvider):
    """OpenRouter (다양한 모델 제공)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.is_free = False
        self.name = "OpenRouter"
        self.rate_limit = 100
        self.max_tokens = 4096
        self.base_url = "https://openrouter.ai/api/v1"
        
    async def generate_content(self, prompt: str, model: str = "meta-llama/llama-2-70b-chat", **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://blogauto.com",
                "X-Title": "BlogAuto"
            }
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": self.max_tokens
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"OpenRouter 오류: {str(e)}")
    
    async def check_availability(self) -> bool:
        return bool(self.api_key)

class GrokProvider(BaseAIProvider):
    """Grok AI (X.AI)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.is_free = False
        self.name = "Grok"
        self.rate_limit = 60
        self.max_tokens = 8192
        self.base_url = "https://api.x.ai/v1"
        
    async def generate_content(self, prompt: str, **kwargs) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "grok-1",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": self.max_tokens
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Grok 오류: {str(e)}")
    
    async def check_availability(self) -> bool:
        return bool(self.api_key)

class OpenAIProvider(BaseAIProvider):
    """OpenAI (유료)"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.is_free = False
        self.name = "OpenAI"
        self.rate_limit = 3000
        self.max_tokens = 4096
        
    async def generate_content(self, prompt: str, model: str = "gpt-3.5-turbo", **kwargs) -> str:
        try:
            openai.api_key = self.api_key
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI 오류: {str(e)}")
    
    async def check_availability(self) -> bool:
        return bool(self.api_key)

class MultiAIProvider:
    """다중 AI 제공자 관리 시스템"""
    
    def __init__(self, config_path: str = "ai_config.json"):
        self.config_path = config_path
        self.providers: Dict[str, BaseAIProvider] = {}
        self.mode: AIMode = "free_first"
        self.load_config()
    
    def load_config(self):
        """설정 파일 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.mode = config.get("mode", "free_first")
                
                # 각 제공자 초기화
                api_keys = config.get("api_keys", {})
                
                if api_keys.get("gemini"):
                    self.providers["gemini"] = GeminiProvider(api_keys["gemini"])
                
                if api_keys.get("groq"):
                    self.providers["groq"] = GroqProvider(api_keys["groq"])
                
                if api_keys.get("deepseek"):
                    self.providers["deepseek"] = DeepSeekProvider(api_keys["deepseek"])
                
                if api_keys.get("huggingface"):
                    self.providers["huggingface"] = HuggingFaceProvider(api_keys["huggingface"])
                
                if api_keys.get("openrouter"):
                    self.providers["openrouter"] = OpenRouterProvider(api_keys["openrouter"])
                
                if api_keys.get("grok"):
                    self.providers["grok"] = GrokProvider(api_keys["grok"])
                
                if api_keys.get("openai"):
                    self.providers["openai"] = OpenAIProvider(api_keys["openai"])
    
    def save_config(self, api_keys: Dict[str, str], mode: AIMode):
        """설정 저장"""
        config = {
            "mode": mode,
            "api_keys": api_keys,
            "updated_at": datetime.now().isoformat()
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 제공자 재초기화
        self.providers.clear()
        self.load_config()
    
    async def get_available_providers(self) -> List[str]:
        """사용 가능한 제공자 목록"""
        available = []
        for name, provider in self.providers.items():
            if await provider.check_availability():
                available.append(name)
        return available
    
    def get_providers_by_mode(self) -> List[BaseAIProvider]:
        """모드별 제공자 정렬"""
        providers = list(self.providers.values())
        
        if self.mode == "free_first":
            # 무료 제공자 우선
            providers.sort(key=lambda p: (not p.is_free, p.name))
        else:
            # 성능 우선 (rate_limit과 max_tokens 고려)
            providers.sort(key=lambda p: (-p.rate_limit, -p.max_tokens, p.name))
        
        return providers
    
    async def generate_content(self, prompt: str, provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """콘텐츠 생성"""
        # 특정 제공자 지정시
        if provider and provider in self.providers:
            try:
                content = await self.providers[provider].generate_content(prompt, **kwargs)
                return {
                    "success": True,
                    "content": content,
                    "provider": provider,
                    "is_free": self.providers[provider].is_free
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "provider": provider
                }
        
        # 모드별 자동 선택
        providers = self.get_providers_by_mode()
        errors = []
        
        for provider in providers:
            if await provider.check_availability():
                try:
                    content = await provider.generate_content(prompt, **kwargs)
                    return {
                        "success": True,
                        "content": content,
                        "provider": provider.name.lower(),
                        "is_free": provider.is_free
                    }
                except Exception as e:
                    errors.append(f"{provider.name}: {str(e)}")
                    continue
        
        return {
            "success": False,
            "error": "모든 AI 제공자 실패",
            "details": errors
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """제공자 정보 조회"""
        info = {
            "mode": self.mode,
            "providers": {}
        }
        
        for name, provider in self.providers.items():
            info["providers"][name] = {
                "available": True,
                "is_free": provider.is_free,
                "rate_limit": provider.rate_limit,
                "max_tokens": provider.max_tokens
            }
        
        # 사용 가능하지 않은 제공자도 표시
        all_providers = ["gemini", "groq", "deepseek", "huggingface", "openrouter", "grok", "openai"]
        for name in all_providers:
            if name not in info["providers"]:
                info["providers"][name] = {
                    "available": False,
                    "is_free": name in ["gemini", "groq", "huggingface"],
                    "rate_limit": 0,
                    "max_tokens": 0
                }
        
        return info

# 전역 인스턴스
multi_ai_provider = MultiAIProvider()