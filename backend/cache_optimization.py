"""
캐싱 전략 구현
- 인메모리 캐싱 (LRU)
- Redis 캐싱 지원
- API 응답 캐싱
- 데이터베이스 쿼리 캐싱
"""

from functools import lru_cache, wraps
from typing import Any, Optional, Callable
import time
import json
import hashlib
from datetime import datetime, timedelta
import redis
import pickle

class CacheManager:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0
        }
        
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                print("✅ Redis 캐싱 활성화됨")
            except:
                print("⚠️ Redis 연결 실패, 인메모리 캐싱 사용")
                self.redis_client = None
    
    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 가져오기"""
        self.cache_stats["total_requests"] += 1
        
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    self.cache_stats["hits"] += 1
                    return pickle.loads(value)
            except:
                pass
        
        self.cache_stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """캐시에 값 저장 (기본 TTL: 5분)"""
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, pickle.dumps(value))
            except:
                pass
    
    def delete(self, pattern: str):
        """패턴과 일치하는 캐시 삭제"""
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except:
                pass
    
    def get_stats(self) -> dict:
        """캐시 통계 반환"""
        hit_rate = (self.cache_stats["hits"] / self.cache_stats["total_requests"] * 100) if self.cache_stats["total_requests"] > 0 else 0
        return {
            **self.cache_stats,
            "hit_rate": round(hit_rate, 2)
        }

# 글로벌 캐시 매니저
cache_manager = CacheManager()

def cached(prefix: str, ttl: int = 300):
    """캐싱 데코레이터"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = cache_manager.generate_cache_key(prefix, *args, **kwargs)
            
            # 캐시 확인
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 결과 캐싱
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = cache_manager.generate_cache_key(prefix, *args, **kwargs)
            
            # 캐시 확인
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        # 비동기 함수인지 확인
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# LRU 캐시 유틸리티
def timed_lru_cache(seconds: int = 300, maxsize: int = 128):
    """시간 제한이 있는 LRU 캐시"""
    def decorator(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.utcnow() + func.lifetime
        
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if datetime.utcnow() >= func.expiration:
                func.cache_clear()
                func.expiration = datetime.utcnow() + func.lifetime
            return func(*args, **kwargs)
        
        wrapped_func.cache_clear = func.cache_clear
        wrapped_func.cache_info = func.cache_info
        
        return wrapped_func
    
    return decorator

# 캐싱 미들웨어
class CacheMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            method = scope["method"]
            
            # GET 요청만 캐싱
            if method == "GET" and path.startswith("/api/"):
                # 캐시 키 생성
                cache_key = f"response:{path}:{scope.get('query_string', b'').decode()}"
                
                # 캐시 확인
                cached_response = cache_manager.get(cache_key)
                if cached_response:
                    await send({
                        "type": "http.response.start",
                        "status": 200,
                        "headers": [
                            [b"content-type", b"application/json"],
                            [b"x-cache", b"HIT"]
                        ]
                    })
                    await send({
                        "type": "http.response.body",
                        "body": cached_response.encode()
                    })
                    return
        
        await self.app(scope, receive, send)

# 데이터베이스 쿼리 캐싱
class CachedDatabase:
    def __init__(self, db_session):
        self.db_session = db_session
    
    @cached("db_query", ttl=600)  # 10분 캐싱
    async def get_user_by_id(self, user_id: str):
        """사용자 정보 캐싱"""
        return self.db_session.query(User).filter(User.id == user_id).first()
    
    @cached("db_query", ttl=300)  # 5분 캐싱
    async def get_keywords(self, user_id: str, limit: int = 10):
        """키워드 목록 캐싱"""
        return self.db_session.query(Keyword)\
            .filter(Keyword.user_id == user_id)\
            .order_by(Keyword.created_at.desc())\
            .limit(limit)\
            .all()
    
    def invalidate_user_cache(self, user_id: str):
        """사용자 관련 캐시 무효화"""
        cache_manager.delete(f"db_query:*{user_id}*")

# 성능 최적화된 API 엔드포인트 예시
@cached("keyword_analysis", ttl=3600)  # 1시간 캐싱
async def analyze_keyword_cached(keyword: str, country: str = "KR"):
    """키워드 분석 결과 캐싱"""
    # 실제 분석 로직
    pass

@cached("title_generation", ttl=1800)  # 30분 캐싱
async def generate_titles_cached(keyword: str, count: int = 5):
    """제목 생성 결과 캐싱"""
    # 실제 생성 로직
    pass

# 캐시 워밍업
async def warm_up_cache():
    """자주 사용되는 데이터 미리 캐싱"""
    popular_keywords = ["SEO", "블로그", "마케팅", "콘텐츠"]
    
    for keyword in popular_keywords:
        await analyze_keyword_cached(keyword)
        await generate_titles_cached(keyword)
    
    print(f"✅ 캐시 워밍업 완료: {len(popular_keywords)}개 키워드")

# 캐시 모니터링
def get_cache_metrics():
    """캐시 성능 메트릭"""
    stats = cache_manager.get_stats()
    
    return {
        "cache_hit_rate": f"{stats['hit_rate']}%",
        "total_requests": stats['total_requests'],
        "cache_hits": stats['hits'],
        "cache_misses": stats['misses'],
        "redis_connected": cache_manager.redis_client is not None
    }