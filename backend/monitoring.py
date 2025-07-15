#!/usr/bin/env python3
"""
통합 모니터링 시스템
Step 8: 모니터링 시스템 구축 - Sentry, Prometheus, Custom Metrics
"""

import os
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from contextlib import asynccontextmanager

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from fastapi import Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
import psutil
import aioredis

# 로거 설정
logger = logging.getLogger(__name__)

# Prometheus 메트릭 레지스트리
registry = CollectorRegistry()

# 메트릭 정의
# 1. API 요청 카운터
api_requests_total = Counter(
    'blogauto_api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

# 2. API 응답 시간 히스토그램
api_request_duration_seconds = Histogram(
    'blogauto_api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

# 3. 활성 요청 게이지
api_requests_in_progress = Gauge(
    'blogauto_api_requests_in_progress',
    'Number of API requests in progress',
    ['method', 'endpoint'],
    registry=registry
)

# 4. 비즈니스 메트릭
business_metrics = {
    'keywords_analyzed': Counter(
        'blogauto_keywords_analyzed_total',
        'Total number of keywords analyzed',
        registry=registry
    ),
    'titles_generated': Counter(
        'blogauto_titles_generated_total',
        'Total number of titles generated',
        registry=registry
    ),
    'content_generated': Counter(
        'blogauto_content_generated_total',
        'Total number of content pieces generated',
        registry=registry
    ),
    'wordpress_posts_published': Counter(
        'blogauto_wordpress_posts_published_total',
        'Total number of WordPress posts published',
        ['status'],
        registry=registry
    ),
    'api_keys_stored': Counter(
        'blogauto_api_keys_stored_total',
        'Total number of API keys stored',
        ['service'],
        registry=registry
    )
}

# 5. 시스템 메트릭
system_metrics = {
    'cpu_usage': Gauge(
        'blogauto_cpu_usage_percent',
        'CPU usage percentage',
        registry=registry
    ),
    'memory_usage': Gauge(
        'blogauto_memory_usage_bytes',
        'Memory usage in bytes',
        registry=registry
    ),
    'disk_usage': Gauge(
        'blogauto_disk_usage_percent',
        'Disk usage percentage',
        registry=registry
    ),
    'active_connections': Gauge(
        'blogauto_active_connections',
        'Number of active connections',
        ['type'],
        registry=registry
    )
}

# 6. 에러 카운터
error_counter = Counter(
    'blogauto_errors_total',
    'Total number of errors',
    ['type', 'endpoint'],
    registry=registry
)

# 7. Rate Limiting 메트릭
rate_limit_metrics = {
    'rejected_requests': Counter(
        'blogauto_rate_limit_rejected_total',
        'Total number of rate-limited requests',
        ['endpoint'],
        registry=registry
    ),
    'blocked_ips': Gauge(
        'blogauto_blocked_ips_total',
        'Number of blocked IPs',
        registry=registry
    )
}

class MonitoringSystem:
    """통합 모니터링 시스템"""
    
    def __init__(self):
        self.sentry_initialized = False
        self.metrics_enabled = True
        self.system_monitor_task = None
        self.custom_metrics = {}
        
    def initialize_sentry(
        self,
        dsn: Optional[str] = None,
        environment: str = "development",
        traces_sample_rate: float = 0.1,
        profiles_sample_rate: float = 0.1
    ):
        """Sentry 초기화"""
        dsn = dsn or os.environ.get("SENTRY_DSN")
        
        if not dsn:
            logger.warning("Sentry DSN not provided, skipping initialization")
            return
        
        try:
            sentry_sdk.init(
                dsn=dsn,
                environment=environment,
                traces_sample_rate=traces_sample_rate,
                profiles_sample_rate=profiles_sample_rate,
                integrations=[
                    FastApiIntegration(transaction_style="endpoint"),
                    SqlalchemyIntegration(),
                ],
                before_send=self._before_send_sentry,
                attach_stacktrace=True,
                send_default_pii=False,  # PII 정보 제외
            )
            
            self.sentry_initialized = True
            logger.info(f"Sentry initialized for {environment} environment")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
    
    def _before_send_sentry(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Sentry 이벤트 전송 전 필터링"""
        # 민감한 정보 제거
        if 'request' in event and 'headers' in event['request']:
            sensitive_headers = ['authorization', 'x-api-key', 'x-openai-key']
            for header in sensitive_headers:
                if header in event['request']['headers']:
                    event['request']['headers'][header] = '[REDACTED]'
        
        # 특정 에러 필터링
        if 'exception' in event:
            for exception in event['exception']['values']:
                # 404 에러는 전송하지 않음
                if exception.get('type') == 'HTTPException' and '404' in str(exception.get('value', '')):
                    return None
        
        return event
    
    async def prometheus_middleware(self, request: Request, call_next):
        """Prometheus 메트릭 수집 미들웨어"""
        if not self.metrics_enabled:
            return await call_next(request)
        
        method = request.method
        endpoint = request.url.path
        
        # 활성 요청 증가
        api_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        # 시작 시간 기록
        start_time = time.time()
        
        try:
            # 요청 처리
            response = await call_next(request)
            status = response.status_code
            
            # 메트릭 업데이트
            api_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            
            return response
            
        except Exception as e:
            # 에러 카운터 증가
            error_counter.labels(type=type(e).__name__, endpoint=endpoint).inc()
            
            # Sentry로 에러 전송
            if self.sentry_initialized:
                sentry_sdk.capture_exception(e)
            
            raise
            
        finally:
            # 응답 시간 기록
            duration = time.time() - start_time
            api_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
            
            # 활성 요청 감소
            api_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
    
    def track_business_metric(self, metric_name: str, value: float = 1, labels: Dict[str, str] = None):
        """비즈니스 메트릭 추적"""
        if metric_name in business_metrics:
            metric = business_metrics[metric_name]
            if labels and hasattr(metric, 'labels'):
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)
    
    def track_rate_limit_rejection(self, endpoint: str):
        """Rate Limit 거부 추적"""
        rate_limit_metrics['rejected_requests'].labels(endpoint=endpoint).inc()
    
    def update_blocked_ips_count(self, count: int):
        """차단된 IP 수 업데이트"""
        rate_limit_metrics['blocked_ips'].set(count)
    
    async def collect_system_metrics(self):
        """시스템 메트릭 수집"""
        while self.metrics_enabled:
            try:
                # CPU 사용률
                cpu_percent = psutil.cpu_percent(interval=1)
                system_metrics['cpu_usage'].set(cpu_percent)
                
                # 메모리 사용량
                memory = psutil.virtual_memory()
                system_metrics['memory_usage'].set(memory.used)
                
                # 디스크 사용률
                disk = psutil.disk_usage('/')
                system_metrics['disk_usage'].set(disk.percent)
                
                # 활성 연결 수 (예시)
                connections = psutil.net_connections()
                system_metrics['active_connections'].labels(type='tcp').set(
                    len([c for c in connections if c.type == 1])
                )
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
            
            await asyncio.sleep(30)  # 30초마다 수집
    
    def start_system_monitoring(self):
        """시스템 모니터링 시작"""
        if not self.system_monitor_task:
            self.system_monitor_task = asyncio.create_task(self.collect_system_metrics())
    
    def stop_system_monitoring(self):
        """시스템 모니터링 중지"""
        if self.system_monitor_task:
            self.system_monitor_task.cancel()
            self.system_monitor_task = None
    
    def get_metrics(self) -> str:
        """Prometheus 형식의 메트릭 반환"""
        return generate_latest(registry)
    
    def create_metric_decorator(self, metric_name: str):
        """메트릭 수집 데코레이터 생성"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    self.track_business_metric(metric_name)
                    return result
                except Exception as e:
                    error_counter.labels(type=type(e).__name__, endpoint=metric_name).inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    if metric_name in self.custom_metrics:
                        self.custom_metrics[metric_name].observe(duration)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.track_business_metric(metric_name)
                    return result
                except Exception as e:
                    error_counter.labels(type=type(e).__name__, endpoint=metric_name).inc()
                    raise
                finally:
                    duration = time.time() - start_time
                    if metric_name in self.custom_metrics:
                        self.custom_metrics[metric_name].observe(duration)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def add_custom_metric(self, name: str, metric_type: str, description: str, labels: List[str] = None):
        """커스텀 메트릭 추가"""
        if metric_type == 'counter':
            metric = Counter(name, description, labels or [], registry=registry)
        elif metric_type == 'histogram':
            metric = Histogram(name, description, labels or [], registry=registry)
        elif metric_type == 'gauge':
            metric = Gauge(name, description, labels or [], registry=registry)
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")
        
        self.custom_metrics[name] = metric
        return metric
    
    @asynccontextmanager
    async def track_operation(self, operation_name: str, labels: Dict[str, str] = None):
        """컨텍스트 매니저로 작업 추적"""
        start_time = time.time()
        
        # 작업 시작 로깅
        logger.info(f"Starting operation: {operation_name}")
        
        try:
            yield
            
            # 성공 로깅
            duration = time.time() - start_time
            logger.info(f"Operation {operation_name} completed in {duration:.2f}s")
            
            # 메트릭 업데이트
            if operation_name in self.custom_metrics:
                metric = self.custom_metrics[operation_name]
                if labels and hasattr(metric, 'labels'):
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
                    
        except Exception as e:
            # 실패 로깅
            duration = time.time() - start_time
            logger.error(f"Operation {operation_name} failed after {duration:.2f}s: {e}")
            
            # 에러 메트릭 업데이트
            error_counter.labels(type=type(e).__name__, endpoint=operation_name).inc()
            
            # Sentry로 전송
            if self.sentry_initialized:
                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("operation", operation_name)
                    scope.set_extra("duration", duration)
                    if labels:
                        for key, value in labels.items():
                            scope.set_extra(key, value)
                    sentry_sdk.capture_exception(e)
            
            raise

# 전역 모니터링 시스템 인스턴스
monitoring = MonitoringSystem()

# FastAPI 엔드포인트를 위한 메트릭 핸들러
async def metrics_endpoint(request: Request) -> Response:
    """Prometheus 메트릭 엔드포인트"""
    metrics_data = monitoring.get_metrics()
    return PlainTextResponse(content=metrics_data, media_type=CONTENT_TYPE_LATEST)

# 헬스체크 엔드포인트를 위한 상세 정보
async def health_check_detailed() -> Dict[str, Any]:
    """상세 헬스체크 정보"""
    try:
        # 시스템 정보
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 프로세스 정보
        process = psutil.Process()
        process_info = {
            'pid': process.pid,
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'threads': process.num_threads(),
            'open_files': len(process.open_files()),
        }
        
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024,
            },
            'process': process_info,
            'monitoring': {
                'sentry_initialized': monitoring.sentry_initialized,
                'metrics_enabled': monitoring.metrics_enabled,
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }