#!/usr/bin/env python3
"""
Sentry 설정 및 에러 추적 시스템
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.excepthook import ExcepthookIntegration
from sentry_sdk.integrations.stdlib import StdlibIntegration
from sentry_sdk.integrations.threading import ThreadingIntegration

class SentryConfig:
    """Sentry 설정 관리 클래스"""
    
    def __init__(self):
        self.environment = os.environ.get("ENVIRONMENT", "development")
        self.dsn = os.environ.get("SENTRY_DSN")
        self.release = os.environ.get("RELEASE_VERSION", "unknown")
        self.server_name = os.environ.get("SERVER_NAME", "blogauto-server")
        
    def get_integrations(self):
        """Sentry 통합 설정"""
        return [
            # 로깅 통합
            LoggingIntegration(
                level=None,  # 모든 레벨 캡처
                event_level=None  # 이벤트로 변환하지 않음
            ),
            # 예외 훅 통합
            ExcepthookIntegration(
                always_run=False
            ),
            # 표준 라이브러리 통합
            StdlibIntegration(),
            # 스레딩 통합
            ThreadingIntegration(
                propagate_hub=True
            ),
        ]
    
    def before_send(self, event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """이벤트 전송 전 처리"""
        # 개발 환경에서는 특정 에러 무시
        if self.environment == "development":
            if "logger" in event and event["logger"] == "uvicorn.error":
                return None
        
        # 민감한 정보 제거
        if "request" in event:
            self._sanitize_request(event["request"])
        
        # 커스텀 태그 추가
        event["tags"] = event.get("tags", {})
        event["tags"]["server_name"] = self.server_name
        event["tags"]["release"] = self.release
        
        # 추가 컨텍스트
        event["contexts"] = event.get("contexts", {})
        event["contexts"]["app"] = {
            "app_name": "BlogAuto",
            "app_version": self.release,
            "environment": self.environment
        }
        
        return event
    
    def _sanitize_request(self, request_data: Dict[str, Any]):
        """요청 데이터에서 민감한 정보 제거"""
        # 헤더 정리
        if "headers" in request_data:
            sensitive_headers = [
                "authorization", "x-api-key", "x-openai-key",
                "cookie", "set-cookie", "x-csrf-token"
            ]
            for header in sensitive_headers:
                if header in request_data["headers"]:
                    request_data["headers"][header] = "[REDACTED]"
        
        # 쿼리 파라미터 정리
        if "query_string" in request_data:
            request_data["query_string"] = self._sanitize_query_string(
                request_data["query_string"]
            )
        
        # 바디 데이터 정리
        if "data" in request_data:
            request_data["data"] = self._sanitize_body_data(
                request_data["data"]
            )
    
    def _sanitize_query_string(self, query_string: str) -> str:
        """쿼리 스트링에서 민감한 파라미터 제거"""
        sensitive_params = ["password", "token", "key", "secret"]
        
        if not query_string:
            return query_string
        
        params = []
        for param in query_string.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                if any(sensitive in key.lower() for sensitive in sensitive_params):
                    params.append(f"{key}=[REDACTED]")
                else:
                    params.append(param)
            else:
                params.append(param)
        
        return "&".join(params)
    
    def _sanitize_body_data(self, data: Any) -> Any:
        """바디 데이터에서 민감한 정보 제거"""
        if isinstance(data, dict):
            sanitized = {}
            sensitive_keys = ["password", "api_key", "token", "secret", "credential"]
            
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = "[REDACTED]"
                elif isinstance(value, dict):
                    sanitized[key] = self._sanitize_body_data(value)
                else:
                    sanitized[key] = value
            
            return sanitized
        
        return data
    
    def traces_sampler(self, sampling_context: Dict[str, Any]) -> float:
        """동적 트레이스 샘플링"""
        # 엔드포인트별 샘플링 레이트
        transaction_name = sampling_context.get("transaction_context", {}).get("name", "")
        
        # 헬스체크는 낮은 샘플링
        if "/health" in transaction_name or "/metrics" in transaction_name:
            return 0.01  # 1%
        
        # 중요한 비즈니스 엔드포인트는 높은 샘플링
        important_endpoints = [
            "/api/content/generate",
            "/api/wordpress/publish",
            "/api/secure/store-key"
        ]
        
        if any(endpoint in transaction_name for endpoint in important_endpoints):
            return 0.5  # 50%
        
        # 개발 환경은 높은 샘플링
        if self.environment == "development":
            return 0.3  # 30%
        
        # 프로덕션 환경은 낮은 샘플링
        if self.environment == "production":
            return 0.1  # 10%
        
        # 기본값
        return 0.2  # 20%
    
    def get_config(self) -> Dict[str, Any]:
        """Sentry 설정 반환"""
        if not self.dsn:
            return None
        
        return {
            "dsn": self.dsn,
            "environment": self.environment,
            "release": self.release,
            "server_name": self.server_name,
            "integrations": self.get_integrations(),
            "before_send": self.before_send,
            "traces_sampler": self.traces_sampler,
            "attach_stacktrace": True,
            "send_default_pii": False,
            "max_breadcrumbs": 100,
            "debug": self.environment == "development",
            "sample_rate": 1.0,  # 에러는 100% 캡처
            "profiles_sample_rate": 0.1 if self.environment == "production" else 0.3,
            "enable_tracing": True,
            "max_value_length": 1024,  # 값 길이 제한
            "in_app_include": ["blogauto", "backend"],
            "in_app_exclude": ["sentry_sdk", "urllib3", "requests"],
            "request_bodies": "small",  # 작은 요청 바디만 캡처
            "with_locals": self.environment == "development",  # 개발 환경에서만 로컬 변수 캡처
        }

class ErrorTracker:
    """에러 추적 및 분석 도구"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_patterns = {}
        self.last_errors = []
        self.max_last_errors = 100
        
    def track_error(self, error: Exception, context: Dict[str, Any] = None):
        """에러 추적"""
        error_type = type(error).__name__
        error_message = str(error)
        timestamp = datetime.utcnow()
        
        # 에러 카운트 증가
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # 에러 패턴 분석
        pattern_key = f"{error_type}:{error_message[:50]}"
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = {
                "count": 0,
                "first_seen": timestamp,
                "last_seen": timestamp,
                "contexts": []
            }
        
        pattern = self.error_patterns[pattern_key]
        pattern["count"] += 1
        pattern["last_seen"] = timestamp
        if context and len(pattern["contexts"]) < 10:
            pattern["contexts"].append(context)
        
        # 최근 에러 저장
        error_info = {
            "type": error_type,
            "message": error_message,
            "timestamp": timestamp.isoformat(),
            "context": context
        }
        
        self.last_errors.append(error_info)
        if len(self.last_errors) > self.max_last_errors:
            self.last_errors.pop(0)
        
        # Sentry로 전송
        if sentry_sdk.Hub.current.client:
            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_extra(key, value)
                scope.set_tag("error_pattern", pattern_key)
                sentry_sdk.capture_exception(error)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """에러 요약 정보 반환"""
        total_errors = sum(self.error_counts.values())
        
        # 가장 빈번한 에러 타입
        most_common_errors = sorted(
            self.error_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # 최근 증가하는 에러 패턴
        recent_patterns = []
        current_time = datetime.utcnow()
        for pattern_key, pattern_info in self.error_patterns.items():
            time_diff = (current_time - pattern_info["last_seen"]).total_seconds()
            if time_diff < 3600:  # 1시간 이내
                recent_patterns.append({
                    "pattern": pattern_key,
                    "count": pattern_info["count"],
                    "recent_count": len([
                        1 for ctx in pattern_info["contexts"]
                        if (current_time - datetime.fromisoformat(
                            ctx.get("timestamp", current_time.isoformat())
                        )).total_seconds() < 3600
                    ])
                })
        
        recent_patterns.sort(key=lambda x: x["recent_count"], reverse=True)
        
        return {
            "total_errors": total_errors,
            "error_types": len(self.error_counts),
            "most_common_errors": most_common_errors,
            "recent_patterns": recent_patterns[:5],
            "last_errors": self.last_errors[-10:],
            "summary_time": current_time.isoformat()
        }
    
    def clear_old_data(self, hours: int = 24):
        """오래된 데이터 정리"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=hours)
        
        # 오래된 패턴 정리
        patterns_to_remove = []
        for pattern_key, pattern_info in self.error_patterns.items():
            if pattern_info["last_seen"] < cutoff_time:
                patterns_to_remove.append(pattern_key)
        
        for pattern_key in patterns_to_remove:
            del self.error_patterns[pattern_key]
        
        # 오래된 최근 에러 정리
        self.last_errors = [
            error for error in self.last_errors
            if datetime.fromisoformat(error["timestamp"]) > cutoff_time
        ]

# 전역 인스턴스
sentry_config = SentryConfig()
error_tracker = ErrorTracker()

def initialize_sentry():
    """Sentry 초기화"""
    config = sentry_config.get_config()
    if config:
        sentry_sdk.init(**config)
        return True
    return False