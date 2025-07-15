#!/usr/bin/env python3
"""
고성능 캐싱 시스템
Step 9: 성능 최적화 및 캐싱 전략 구현
"""

import os
import json
import hashlib
import asyncio
import pickle
from typing import Any, Optional, Dict, List, Callable, Union
from datetime import datetime, timedelta
from functools import wraps
import redis.asyncio as redis
from redis.exceptions import RedisError
import logging

logger = logging.getLogger(__name__)

class CacheStrategy:
    """캐싱 전략 정의"""
    
    # TTL 설정 (초 단위)
    TTL_SHORT = 300        # 5분 - 자주 변경되는 데이터
    TTL_MEDIUM = 3600      # 1시간 - 일반 데이터
    TTL_LONG = 86400       # 24시간 - 거의 변경되지 않는 데이터
    TTL_PERMANENT = 0      # 영구 - 수동 삭제 필요
    
    # 캐시 정책
    POLICIES = {
        "keywords_analysis": {
            "ttl": TTL_MEDIUM,
            "max_size": 1000,
            "eviction": "lru",
            "compression": True
        },
        "title_generation": {
            "ttl": TTL_LONG,
            "max_size": 5000,
            "eviction": "lru",
            "compression": False
        },
        "content_generation": {
            "ttl": TTL_LONG,
            "max_size": 500,
            "eviction": "lfu",
            "compression": True
        },
        "api_responses": {
            "ttl": TTL_SHORT,
            "max_size": 2000,
            "eviction": "lru",
            "compression": False
        },
        "user_sessions": {
            "ttl": TTL_MEDIUM,
            "max_size": 10000,
            "eviction": "lru",
            "compression": False
        }
    }

class RedisCache:
    """Redis 기반 분산 캐시"""
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 password: str = None,
                 db: int = 0,
                 max_connections: int = 50):
        self.host = host or os.environ.get("REDIS_HOST", "localhost")
        self.port = port or int(os.environ.get("REDIS_PORT", 6379))
        self.password = password or os.environ.get("REDIS_PASSWORD")
        self.db = db
        self.max_connections = max_connections
        self.pool = None
        self.client = None
        self._connected = False
        
    async def connect(self):
        """Redis 연결"""
        if self._connected:
            return
            
        try:
            self.pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                decode_responses=False  # 바이너리 데이터 지원
            )
            
            self.client = redis.Redis(connection_pool=self.pool)
            
            # 연결 테스트
            await self.client.ping()
            self._connected = True
            logger.info(f"Redis connected to {self.host}:{self.port}")
            
        except RedisError as e:
            logger.error(f"Redis connection failed: {e}")
            self._connected = False
            raise
    
    async def disconnect(self):
        """Redis 연결 해제"""
        if self.client:
            await self.client.close()
            await self.pool.disconnect()
            self._connected = False
            logger.info("Redis disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if not self._connected:
            await self.connect()
            
        try:
            data = await self.client.get(key)
            if data:
                # 압축 여부 확인
                if data.startswith(b'COMPRESSED:'):
                    import zlib
                    data = zlib.decompress(data[11:])
                
                return pickle.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None, compress: bool = False) -> bool:
        """캐시에 값 저장"""
        if not self._connected:
            await self.connect()
            
        try:
            # 직렬화
            data = pickle.dumps(value)
            
            # 압축 옵션
            if compress and len(data) > 1024:  # 1KB 이상만 압축
                import zlib
                data = b'COMPRESSED:' + zlib.compress(data)
            
            # TTL 설정
            if ttl and ttl > 0:
                await self.client.setex(key, ttl, data)
            else:
                await self.client.set(key, data)
                
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        if not self._connected:
            await self.connect()
            
        try:
            result = await self.client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """키 존재 여부 확인"""
        if not self._connected:
            await self.connect()
            
        try:
            return await self.client.exists(key) > 0
            
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """TTL 업데이트"""
        if not self._connected:
            await self.connect()
            
        try:
            return await self.client.expire(key, ttl)
            
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """카운터 증가"""
        if not self._connected:
            await self.connect()
            
        try:
            return await self.client.incr(key, amount)
            
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """여러 키 조회"""
        if not self._connected:
            await self.connect()
            
        try:
            values = await self.client.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value:
                    try:
                        # 압축 해제
                        if value.startswith(b'COMPRESSED:'):
                            import zlib
                            value = zlib.decompress(value[11:])
                        
                        result[key] = pickle.loads(value)
                    except:
                        result[key] = None
                else:
                    result[key] = None
                    
            return result
            
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return {key: None for key in keys}
    
    async def set_many(self, data: Dict[str, Any], ttl: int = None, compress: bool = False) -> bool:
        """여러 키 저장"""
        if not self._connected:
            await self.connect()
            
        try:
            pipe = self.client.pipeline()
            
            for key, value in data.items():
                # 직렬화
                serialized = pickle.dumps(value)
                
                # 압축
                if compress and len(serialized) > 1024:
                    import zlib
                    serialized = b'COMPRESSED:' + zlib.compress(serialized)
                
                if ttl and ttl > 0:
                    pipe.setex(key, ttl, serialized)
                else:
                    pipe.set(key, serialized)
            
            results = await pipe.execute()
            return all(results)
            
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """패턴에 맞는 키 삭제"""
        if not self._connected:
            await self.connect()
            
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self.client.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear_pattern error for pattern {pattern}: {e}")
            return 0
    
    async def get_info(self) -> Dict[str, Any]:
        """캐시 정보 조회"""
        if not self._connected:
            await self.connect()
            
        try:
            info = await self.client.info()
            memory_info = await self.client.memory_stats()
            
            return {
                "connected": self._connected,
                "server": f"{self.host}:{self.port}",
                "clients": info.get("connected_clients", 0),
                "memory_used": info.get("used_memory_human", "0"),
                "memory_peak": info.get("used_memory_peak_human", "0"),
                "keys": info.get("db0", {}).get("keys", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
            
        except Exception as e:
            logger.error(f"Cache get_info error: {e}")
            return {"connected": False, "error": str(e)}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """캐시 히트율 계산"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

class LocalMemoryCache:
    """로컬 메모리 캐시 (L1 캐시)"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_count: Dict[str, int] = {}
        self.lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        async with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # TTL 확인
                if datetime.now() < entry["expires"]:
                    # 접근 횟수 증가
                    self.access_count[key] = self.access_count.get(key, 0) + 1
                    return entry["value"]
                else:
                    # 만료된 항목 삭제
                    del self.cache[key]
                    if key in self.access_count:
                        del self.access_count[key]
            
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """캐시에 값 저장"""
        async with self.lock:
            # 캐시 크기 확인
            if len(self.cache) >= self.max_size:
                await self._evict()
            
            # TTL 설정
            if ttl is None:
                ttl = self.ttl
                
            self.cache[key] = {
                "value": value,
                "expires": datetime.now() + timedelta(seconds=ttl),
                "created": datetime.now()
            }
            
            self.access_count[key] = 1
            return True
    
    async def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_count:
                    del self.access_count[key]
                return True
            return False
    
    async def clear(self):
        """전체 캐시 클리어"""
        async with self.lock:
            self.cache.clear()
            self.access_count.clear()
    
    async def _evict(self):
        """LRU 방식으로 캐시 제거"""
        # 만료된 항목 먼저 제거
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now >= entry["expires"]
        ]
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_count:
                del self.access_count[key]
        
        # 여전히 공간이 부족하면 LRU 제거
        if len(self.cache) >= self.max_size:
            # 접근 횟수가 가장 적은 항목 제거
            lru_key = min(self.access_count, key=self.access_count.get)
            del self.cache[lru_key]
            del self.access_count[lru_key]
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        total_size = sum(
            len(str(entry["value"])) for entry in self.cache.values()
        )
        
        return {
            "entries": len(self.cache),
            "max_size": self.max_size,
            "total_size_bytes": total_size,
            "hit_count": sum(self.access_count.values()),
            "avg_access_count": sum(self.access_count.values()) / len(self.access_count) if self.access_count else 0
        }

class HybridCache:
    """하이브리드 캐시 시스템 (L1 + L2)"""
    
    def __init__(self):
        self.l1_cache = LocalMemoryCache(max_size=500, ttl=300)
        self.l2_cache = RedisCache()
        self.initialized = False
    
    async def initialize(self):
        """캐시 시스템 초기화"""
        if not self.initialized:
            await self.l2_cache.connect()
            self.initialized = True
    
    async def get(self, key: str, use_l1: bool = True) -> Optional[Any]:
        """캐시에서 값 조회 (L1 → L2)"""
        # L1 캐시 확인
        if use_l1:
            value = await self.l1_cache.get(key)
            if value is not None:
                return value
        
        # L2 캐시 확인
        value = await self.l2_cache.get(key)
        if value is not None and use_l1:
            # L1 캐시에 저장
            await self.l1_cache.set(key, value, ttl=300)
        
        return value
    
    async def set(self, key: str, value: Any, ttl: int = None, 
                  use_l1: bool = True, compress: bool = False) -> bool:
        """캐시에 값 저장 (L1 + L2)"""
        success = True
        
        # L2 캐시 저장
        if not await self.l2_cache.set(key, value, ttl=ttl, compress=compress):
            success = False
        
        # L1 캐시 저장
        if use_l1 and ttl and ttl <= 3600:  # 1시간 이하만 L1에 저장
            await self.l1_cache.set(key, value, ttl=min(ttl, 300))
        
        return success
    
    async def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        l1_result = await self.l1_cache.delete(key)
        l2_result = await self.l2_cache.delete(key)
        return l1_result or l2_result
    
    async def clear_pattern(self, pattern: str) -> int:
        """패턴 기반 캐시 삭제"""
        # L1 캐시는 패턴 삭제 미지원, 전체 클리어
        await self.l1_cache.clear()
        
        # L2 캐시 패턴 삭제
        return await self.l2_cache.clear_pattern(pattern)

def cache_key_generator(prefix: str, *args, **kwargs) -> str:
    """캐시 키 생성기"""
    # 인자를 문자열로 변환
    key_parts = [prefix]
    
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            # 복잡한 객체는 해시
            key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
    
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}:{v}")
        else:
            key_parts.append(f"{k}:{hashlib.md5(str(v).encode()).hexdigest()[:8]}")
    
    return ":".join(key_parts)

def cached(prefix: str = None, ttl: int = 3600, 
          compress: bool = False, use_l1: bool = True):
    """캐싱 데코레이터"""
    def decorator(func: Callable):
        cache_prefix = prefix or func.__name__
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = cache_key_generator(cache_prefix, *args[1:], **kwargs)
            
            # 캐시에서 조회
            result = await cache_manager.get(cache_key, use_l1=use_l1)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 캐시에 저장
            await cache_manager.set(
                cache_key, result, ttl=ttl, 
                use_l1=use_l1, compress=compress
            )
            
            logger.debug(f"Cache miss and set for {cache_key}")
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 동기 함수는 지원하지 않음
            raise NotImplementedError("Cached decorator only supports async functions")
        
        # 캐시 무효화 메서드 추가
        async def invalidate(*args, **kwargs):
            cache_key = cache_key_generator(cache_prefix, *args[1:], **kwargs)
            return await cache_manager.delete(cache_key)
        
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper.invalidate = invalidate
        
        return wrapper
    
    return decorator

# 전역 캐시 매니저
cache_manager = HybridCache()

# 캐시 워밍 함수
async def warm_cache():
    """캐시 예열 (자주 사용되는 데이터 미리 로드)"""
    logger.info("Starting cache warming...")
    
    # 예: 인기 키워드 캐싱
    popular_keywords = ["블로그", "마케팅", "SEO", "콘텐츠", "자동화"]
    
    for keyword in popular_keywords:
        cache_key = cache_key_generator("keywords_analysis", keyword)
        # 실제로는 데이터베이스나 API에서 조회
        await cache_manager.set(cache_key, {"keyword": keyword, "warmed": True}, ttl=3600)
    
    logger.info("Cache warming completed")

# 캐시 상태 모니터링
async def get_cache_status() -> Dict[str, Any]:
    """캐시 상태 정보"""
    l1_stats = cache_manager.l1_cache.get_stats()
    l2_info = await cache_manager.l2_cache.get_info()
    
    return {
        "l1_cache": l1_stats,
        "l2_cache": l2_info,
        "timestamp": datetime.now().isoformat()
    }