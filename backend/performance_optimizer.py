#!/usr/bin/env python3
"""
성능 최적화 시스템
데이터베이스 쿼리 최적화, 응답 압축, 연결 풀링 등
"""

import os
import gzip
import time
import asyncio
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from contextlib import asynccontextmanager
import logging

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy import create_engine, pool, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool, StaticPool
import aiohttp

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """데이터베이스 성능 최적화"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.environ.get("DATABASE_URL")
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        
        # 연결 풀 설정
        self.pool_config = {
            "pool_size": 20,          # 기본 풀 크기
            "max_overflow": 10,       # 최대 오버플로우
            "pool_timeout": 30,       # 연결 대기 시간
            "pool_recycle": 3600,     # 연결 재활용 시간 (1시간)
            "pool_pre_ping": True,    # 연결 상태 확인
            "echo_pool": False        # 풀 디버깅
        }
        
        # 쿼리 통계
        self.query_stats = {
            "total_queries": 0,
            "slow_queries": 0,
            "query_times": [],
            "slow_query_threshold": 1.0  # 1초 이상
        }
    
    def initialize_sync_engine(self):
        """동기 엔진 초기화"""
        if not self.engine:
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                **self.pool_config
            )
            
            # 이벤트 리스너 등록
            self._register_event_listeners(self.engine)
            
            # 세션 팩토리 생성
            self.session_factory = sessionmaker(
                bind=self.engine,
                expire_on_commit=False
            )
            
            logger.info("Sync database engine initialized with connection pooling")
    
    async def initialize_async_engine(self):
        """비동기 엔진 초기화"""
        if not self.async_engine:
            # PostgreSQL용 비동기 URL 변환
            async_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            ).replace(
                "postgres://", "postgresql+asyncpg://"
            )
            
            self.async_engine = create_async_engine(
                async_url,
                pool_size=self.pool_config["pool_size"],
                max_overflow=self.pool_config["max_overflow"],
                pool_timeout=self.pool_config["pool_timeout"],
                pool_recycle=self.pool_config["pool_recycle"],
                pool_pre_ping=self.pool_config["pool_pre_ping"],
                echo_pool=self.pool_config["echo_pool"]
            )
            
            # 비동기 세션 팩토리 생성
            self.async_session_factory = sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("Async database engine initialized with connection pooling")
    
    def _register_event_listeners(self, engine):
        """이벤트 리스너 등록"""
        @event.listens_for(engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
        
        @event.listens_for(engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            start_time = conn.info['query_start_time'].pop(-1)
            query_time = time.time() - start_time
            
            # 통계 업데이트
            self.query_stats["total_queries"] += 1
            self.query_stats["query_times"].append(query_time)
            
            # 느린 쿼리 감지
            if query_time > self.query_stats["slow_query_threshold"]:
                self.query_stats["slow_queries"] += 1
                logger.warning(f"Slow query detected ({query_time:.2f}s): {statement[:100]}...")
            
            # 메모리 관리를 위해 최근 1000개만 유지
            if len(self.query_stats["query_times"]) > 1000:
                self.query_stats["query_times"] = self.query_stats["query_times"][-1000:]
    
    @asynccontextmanager
    async def get_async_session(self):
        """비동기 세션 컨텍스트 매니저"""
        if not self.async_engine:
            await self.initialize_async_engine()
        
        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    def get_connection_pool_status(self) -> Dict[str, Any]:
        """연결 풀 상태 조회"""
        if self.engine:
            pool = self.engine.pool
            return {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "total": pool.total()
            }
        return {}
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """쿼리 통계 조회"""
        if self.query_stats["query_times"]:
            avg_time = sum(self.query_stats["query_times"]) / len(self.query_stats["query_times"])
            max_time = max(self.query_stats["query_times"])
            min_time = min(self.query_stats["query_times"])
        else:
            avg_time = max_time = min_time = 0
        
        return {
            "total_queries": self.query_stats["total_queries"],
            "slow_queries": self.query_stats["slow_queries"],
            "slow_query_ratio": self.query_stats["slow_queries"] / max(1, self.query_stats["total_queries"]),
            "avg_query_time": avg_time,
            "max_query_time": max_time,
            "min_query_time": min_time
        }

class HTTPConnectionPool:
    """HTTP 연결 풀 관리"""
    
    def __init__(self):
        self.session = None
        self.connector = None
        self.config = {
            "limit": 100,                # 전체 연결 제한
            "limit_per_host": 30,        # 호스트별 연결 제한
            "ttl_dns_cache": 300,        # DNS 캐시 TTL
            "enable_cleanup_closed": True # 닫힌 연결 정리
        }
    
    async def initialize(self):
        """연결 풀 초기화"""
        if not self.session:
            self.connector = aiohttp.TCPConnector(
                limit=self.config["limit"],
                limit_per_host=self.config["limit_per_host"],
                ttl_dns_cache=self.config["ttl_dns_cache"],
                enable_cleanup_closed=self.config["enable_cleanup_closed"]
            )
            
            timeout = aiohttp.ClientTimeout(
                total=30,      # 전체 시간 제한
                connect=5,     # 연결 시간 제한
                sock_connect=5, # 소켓 연결 시간 제한
                sock_read=10   # 소켓 읽기 시간 제한
            )
            
            self.session = aiohttp.ClientSession(
                connector=self.connector,
                timeout=timeout
            )
            
            logger.info("HTTP connection pool initialized")
    
    async def close(self):
        """연결 풀 종료"""
        if self.session:
            await self.session.close()
            self.session = None
            self.connector = None
            logger.info("HTTP connection pool closed")
    
    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """HTTP 요청 실행"""
        if not self.session:
            await self.initialize()
        
        return await self.session.request(method, url, **kwargs)
    
    def get_pool_status(self) -> Dict[str, Any]:
        """연결 풀 상태 조회"""
        if self.connector:
            return {
                "limit": self.connector.limit,
                "limit_per_host": self.connector.limit_per_host,
                "connections": len(self.connector._conns),
                "acquired": len(self.connector._acquired),
                "acquired_per_host": {
                    str(key): len(conns) 
                    for key, conns in self.connector._acquired_per_host.items()
                }
            }
        return {}

class ResponseOptimizer:
    """응답 최적화 미들웨어"""
    
    def __init__(self):
        self.min_compress_size = 1024  # 1KB 이상만 압축
        self.compress_level = 6        # gzip 압축 레벨 (1-9)
        self.cache_control_config = {
            "static": "public, max-age=31536000",  # 1년
            "api": "private, max-age=0, no-cache",
            "content": "public, max-age=3600"       # 1시간
        }
    
    async def compression_middleware(self, request: Request, call_next):
        """응답 압축 미들웨어"""
        # 요청 처리
        response = await call_next(request)
        
        # 압축 가능 여부 확인
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return response
        
        # 응답 본문 읽기
        if hasattr(response, "body_iterator"):
            # 스트리밍 응답
            return await self._compress_streaming_response(response)
        else:
            # 일반 응답
            return await self._compress_response(response)
    
    async def _compress_response(self, response: Response) -> Response:
        """일반 응답 압축"""
        # Content-Type 확인
        content_type = response.headers.get("content-type", "")
        if not self._should_compress(content_type):
            return response
        
        # 응답 크기 확인
        body = b"".join([chunk async for chunk in response.body_iterator])
        if len(body) < self.min_compress_size:
            response.body = body
            return response
        
        # gzip 압축
        compressed_body = gzip.compress(body, compresslevel=self.compress_level)
        
        # 압축률이 낮으면 원본 사용
        if len(compressed_body) >= len(body) * 0.9:
            response.body = body
            return response
        
        # 압축된 응답 반환
        response.body = compressed_body
        response.headers["content-encoding"] = "gzip"
        response.headers["content-length"] = str(len(compressed_body))
        response.headers["vary"] = "Accept-Encoding"
        
        return response
    
    async def _compress_streaming_response(self, response: StreamingResponse) -> StreamingResponse:
        """스트리밍 응답 압축"""
        content_type = response.headers.get("content-type", "")
        if not self._should_compress(content_type):
            return response
        
        async def compressed_generator():
            from io import BytesIO
            buffer = BytesIO()
            compressor = gzip.GzipFile(mode='wb', fileobj=buffer, compresslevel=self.compress_level)
            
            async for chunk in response.body_iterator:
                compressor.write(chunk)
                compressor.flush()
                
                # 버퍼에서 압축된 데이터 읽기
                buffer.seek(0)
                compressed_chunk = buffer.read()
                if compressed_chunk:
                    yield compressed_chunk
                buffer.seek(0)
                buffer.truncate(0)
            
            # 마지막 처리
            compressor.close()
            buffer.seek(0)
            final_chunk = buffer.read()
            if final_chunk:
                yield final_chunk
            buffer.close()
        
        response.body_iterator = compressed_generator()
        response.headers["content-encoding"] = "gzip"
        response.headers["vary"] = "Accept-Encoding"
        del response.headers["content-length"]  # 스트리밍이므로 길이 알 수 없음
        
        return response
    
    def _should_compress(self, content_type: str) -> bool:
        """압축 가능한 콘텐츠 타입 확인"""
        compressible_types = [
            "text/", "application/json", "application/xml",
            "application/javascript", "application/x-javascript"
        ]
        
        return any(ct in content_type.lower() for ct in compressible_types)
    
    def set_cache_headers(self, response: Response, cache_type: str = "api"):
        """캐시 헤더 설정"""
        if cache_type in self.cache_control_config:
            response.headers["cache-control"] = self.cache_control_config[cache_type]
        
        # ETag 생성 (간단한 구현)
        if hasattr(response, "body"):
            import hashlib
            etag = hashlib.md5(response.body).hexdigest()
            response.headers["etag"] = f'"{etag}"'

class PerformanceMonitor:
    """성능 모니터링 및 분석"""
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "response_times": [],
            "endpoint_stats": {},
            "error_count": 0,
            "slow_requests": 0,
            "slow_threshold": 2.0  # 2초 이상
        }
        self.start_time = time.time()
    
    async def monitor_request(self, request: Request, call_next):
        """요청 성능 모니터링"""
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            # 요청 처리
            response = await call_next(request)
            
            # 응답 시간 계산
            response_time = time.time() - start_time
            
            # 메트릭 업데이트
            self._update_metrics(endpoint, response_time, response.status_code)
            
            # 응답 헤더에 성능 정보 추가
            response.headers["X-Response-Time"] = f"{response_time:.3f}"
            response.headers["X-Server-Timing"] = f"total;dur={response_time * 1000:.1f}"
            
            return response
            
        except Exception as e:
            # 에러 카운트
            self.metrics["error_count"] += 1
            raise
    
    def _update_metrics(self, endpoint: str, response_time: float, status_code: int):
        """메트릭 업데이트"""
        # 전체 통계
        self.metrics["request_count"] += 1
        self.metrics["response_times"].append(response_time)
        
        # 느린 요청 감지
        if response_time > self.metrics["slow_threshold"]:
            self.metrics["slow_requests"] += 1
            logger.warning(f"Slow request detected: {endpoint} took {response_time:.2f}s")
        
        # 엔드포인트별 통계
        if endpoint not in self.metrics["endpoint_stats"]:
            self.metrics["endpoint_stats"][endpoint] = {
                "count": 0,
                "total_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "status_codes": {}
            }
        
        stats = self.metrics["endpoint_stats"][endpoint]
        stats["count"] += 1
        stats["total_time"] += response_time
        stats["min_time"] = min(stats["min_time"], response_time)
        stats["max_time"] = max(stats["max_time"], response_time)
        stats["status_codes"][status_code] = stats["status_codes"].get(status_code, 0) + 1
        
        # 메모리 관리
        if len(self.metrics["response_times"]) > 10000:
            self.metrics["response_times"] = self.metrics["response_times"][-5000:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보"""
        uptime = time.time() - self.start_time
        
        if self.metrics["response_times"]:
            avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            p95_response_time = sorted(self.metrics["response_times"])[int(len(self.metrics["response_times"]) * 0.95)]
            p99_response_time = sorted(self.metrics["response_times"])[int(len(self.metrics["response_times"]) * 0.99)]
        else:
            avg_response_time = p95_response_time = p99_response_time = 0
        
        # 엔드포인트별 요약
        endpoint_summary = []
        for endpoint, stats in self.metrics["endpoint_stats"].items():
            endpoint_summary.append({
                "endpoint": endpoint,
                "count": stats["count"],
                "avg_time": stats["total_time"] / stats["count"] if stats["count"] > 0 else 0,
                "min_time": stats["min_time"],
                "max_time": stats["max_time"],
                "success_rate": sum(
                    count for code, count in stats["status_codes"].items() 
                    if 200 <= code < 300
                ) / stats["count"] if stats["count"] > 0 else 0
            })
        
        # 가장 느린 엔드포인트 정렬
        endpoint_summary.sort(key=lambda x: x["avg_time"], reverse=True)
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.metrics["request_count"],
            "requests_per_second": self.metrics["request_count"] / uptime if uptime > 0 else 0,
            "error_rate": self.metrics["error_count"] / max(1, self.metrics["request_count"]),
            "slow_request_rate": self.metrics["slow_requests"] / max(1, self.metrics["request_count"]),
            "response_times": {
                "average": avg_response_time,
                "p95": p95_response_time,
                "p99": p99_response_time
            },
            "slowest_endpoints": endpoint_summary[:10],
            "timestamp": datetime.now().isoformat()
        }

# 전역 인스턴스
db_optimizer = DatabaseOptimizer()
http_pool = HTTPConnectionPool()
response_optimizer = ResponseOptimizer()
performance_monitor = PerformanceMonitor()

# 최적화된 비동기 작업 배치 처리
class BatchProcessor:
    """배치 처리 최적화"""
    
    def __init__(self, batch_size: int = 10, timeout: float = 0.1):
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending_tasks = []
        self.results = {}
        self.processing = False
        self.lock = asyncio.Lock()
    
    async def add_task(self, task_id: str, coroutine):
        """작업 추가"""
        async with self.lock:
            self.pending_tasks.append((task_id, coroutine))
            
            # 배치 크기에 도달하면 즉시 처리
            if len(self.pending_tasks) >= self.batch_size:
                await self._process_batch()
            else:
                # 타임아웃 후 처리
                asyncio.create_task(self._delayed_process())
    
    async def _delayed_process(self):
        """지연 처리"""
        await asyncio.sleep(self.timeout)
        async with self.lock:
            if self.pending_tasks and not self.processing:
                await self._process_batch()
    
    async def _process_batch(self):
        """배치 처리 실행"""
        if not self.pending_tasks or self.processing:
            return
        
        self.processing = True
        batch = self.pending_tasks[:self.batch_size]
        self.pending_tasks = self.pending_tasks[self.batch_size:]
        
        # 병렬 처리
        tasks = []
        task_ids = []
        
        for task_id, coroutine in batch:
            tasks.append(coroutine)
            task_ids.append(task_id)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 저장
            for task_id, result in zip(task_ids, results):
                self.results[task_id] = result
                
        finally:
            self.processing = False
    
    async def get_result(self, task_id: str, timeout: float = 5.0):
        """결과 조회"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if task_id in self.results:
                result = self.results.pop(task_id)
                if isinstance(result, Exception):
                    raise result
                return result
            
            await asyncio.sleep(0.01)
        
        raise TimeoutError(f"Task {task_id} timeout")

# 전역 배치 프로세서
batch_processor = BatchProcessor()