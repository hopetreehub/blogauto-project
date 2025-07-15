"""
최적화된 API 구현
- 응답 압축
- 비동기 처리
- 스트리밍 응답
- 연결 풀링
"""

from fastapi import FastAPI, Response, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import aiohttp
import json
from typing import AsyncGenerator
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import uvloop

# uvloop으로 더 빠른 이벤트 루프 사용
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = FastAPI(title="최적화된 블로그 자동화 API")

# Gzip 압축 미들웨어 추가
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 스레드 풀 설정
thread_pool = ThreadPoolExecutor(max_workers=10)

# 연결 풀 설정
class ConnectionPool:
    def __init__(self):
        self.session = None
    
    async def get_session(self):
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(
                limit=100,  # 전체 연결 제한
                limit_per_host=30,  # 호스트당 연결 제한
                ttl_dns_cache=300  # DNS 캐시 5분
            )
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
        return self.session
    
    async def close(self):
        if self.session:
            await self.session.close()

connection_pool = ConnectionPool()

# 응답 시간 측정 미들웨어
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response

# 비동기 캐싱 데코레이터
def async_cache(ttl: int = 300):
    cache = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 캐시 확인
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if time.time() - cached_time < ttl:
                    return cached_data
            
            # 함수 실행
            result = await func(*args, **kwargs)
            
            # 캐시 저장
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    
    return decorator

# 스트리밍 콘텐츠 생성
async def stream_content_generation(title: str, keyword: str) -> AsyncGenerator[str, None]:
    """콘텐츠를 청크 단위로 스트리밍"""
    
    # 모의 콘텐츠 생성 (실제로는 AI API 호출)
    sections = [
        f"# {title}\n\n",
        f"## 서론\n{keyword}에 대한 포괄적인 가이드를 제공합니다.\n\n",
        f"## 주요 내용\n{keyword}의 핵심 개념과 실용적인 팁을 다룹니다.\n\n",
        f"## 실전 활용\n실제 사례와 함께 {keyword}를 활용하는 방법을 알아봅니다.\n\n",
        f"## 결론\n{keyword}의 중요성과 향후 전망을 정리합니다.\n"
    ]
    
    for section in sections:
        await asyncio.sleep(0.1)  # 실제 생성 시뮬레이션
        yield section

# 최적화된 엔드포인트들
@app.get("/api/health")
async def health_check():
    """헬스 체크 - 최소한의 처리"""
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/keywords/analyze-fast")
@async_cache(ttl=3600)  # 1시간 캐싱
async def analyze_keyword_optimized(keyword: str):
    """최적화된 키워드 분석"""
    
    # 병렬 처리로 여러 소스에서 데이터 수집
    async def fetch_data(source: str):
        await asyncio.sleep(0.1)  # 실제 API 호출 시뮬레이션
        return {
            "source": source,
            "data": f"{keyword} 관련 데이터"
        }
    
    # 동시에 여러 소스에서 데이터 수집
    tasks = [
        fetch_data("google"),
        fetch_data("naver"),
        fetch_data("internal_db")
    ]
    
    results = await asyncio.gather(*tasks)
    
    return {
        "keyword": keyword,
        "analysis": results,
        "cached": False
    }

@app.post("/api/titles/generate-batch")
async def generate_titles_batch(keywords: list[str], count: int = 5):
    """배치 제목 생성 - 여러 키워드를 한 번에 처리"""
    
    async def generate_for_keyword(keyword: str):
        await asyncio.sleep(0.2)  # AI 생성 시뮬레이션
        return {
            "keyword": keyword,
            "titles": [f"{keyword} 관련 제목 {i+1}" for i in range(count)]
        }
    
    # 모든 키워드에 대해 병렬 처리
    tasks = [generate_for_keyword(kw) for kw in keywords]
    results = await asyncio.gather(*tasks)
    
    return {
        "results": results,
        "total_keywords": len(keywords),
        "titles_per_keyword": count
    }

@app.post("/api/content/generate-stream")
async def generate_content_stream(title: str, keyword: str):
    """스트리밍 콘텐츠 생성"""
    
    async def event_generator():
        async for chunk in stream_content_generation(title, keyword):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        yield "data: {\"done\": true}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Nginx 버퍼링 비활성화
        }
    )

@app.post("/api/wordpress/bulk-publish")
async def bulk_publish_optimized(posts: list[dict]):
    """대량 WordPress 포스팅 최적화"""
    
    session = await connection_pool.get_session()
    
    async def publish_single(post: dict):
        try:
            # WordPress API 호출 시뮬레이션
            async with session.post(
                f"{post['site_url']}/wp-json/wp/v2/posts",
                json=post['data'],
                headers=post.get('headers', {})
            ) as response:
                return {
                    "title": post['data']['title'],
                    "status": response.status,
                    "success": response.status == 201
                }
        except Exception as e:
            return {
                "title": post['data']['title'],
                "status": 0,
                "error": str(e)
            }
    
    # 동시에 여러 포스트 발행 (최대 5개씩)
    results = []
    for i in range(0, len(posts), 5):
        batch = posts[i:i+5]
        batch_results = await asyncio.gather(*[publish_single(p) for p in batch])
        results.extend(batch_results)
    
    return {
        "total_posts": len(posts),
        "successful": sum(1 for r in results if r.get("success")),
        "results": results
    }

# 프리페치 및 워밍업
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 캐시 워밍업"""
    
    # 인기 키워드 미리 분석
    popular_keywords = ["SEO", "블로그", "마케팅"]
    for keyword in popular_keywords:
        asyncio.create_task(analyze_keyword_optimized(keyword))
    
    print("✅ API 최적화 완료 - 캐시 워밍업 시작")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 정리"""
    await connection_pool.close()
    thread_pool.shutdown(wait=True)

# 성능 메트릭 엔드포인트
@app.get("/api/metrics")
async def get_performance_metrics():
    """성능 메트릭 반환"""
    
    # 이벤트 루프 상태
    loop = asyncio.get_event_loop()
    
    return {
        "event_loop": {
            "pending_tasks": len(asyncio.all_tasks(loop)),
            "running": loop.is_running()
        },
        "thread_pool": {
            "active_threads": thread_pool._threads,
            "queued_tasks": thread_pool._work_queue.qsize() if hasattr(thread_pool._work_queue, 'qsize') else 0
        },
        "optimization_features": {
            "gzip_compression": True,
            "connection_pooling": True,
            "async_caching": True,
            "streaming_responses": True,
            "batch_processing": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    # 성능 최적화 설정
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001,
        loop="uvloop",  # 더 빠른 이벤트 루프
        workers=1,  # 멀티 프로세스는 별도 관리
        access_log=False,  # 액세스 로그 비활성화로 성능 향상
        limit_concurrency=1000,  # 동시 연결 제한
        limit_max_requests=10000  # 재시작 전 최대 요청 수
    )