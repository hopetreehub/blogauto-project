"""
Rate Limiting 미들웨어
API 요청 제한 및 보안 강화
"""

import time
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import hashlib
import json

class RateLimiter:
    """
    고급 Rate Limiter
    - 슬라이딩 윈도우 방식
    - IP별, 사용자별 제한
    - 동적 제한 조정
    """
    
    def __init__(self):
        # IP별 요청 기록 {ip: deque(request_times)}
        self.ip_requests: Dict[str, deque] = defaultdict(lambda: deque())
        
        # 사용자별 요청 기록 {user_id: deque(request_times)}
        self.user_requests: Dict[str, deque] = defaultdict(lambda: deque())
        
        # 엔드포인트별 요청 기록 {endpoint: {ip: deque}}
        self.endpoint_requests: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: defaultdict(lambda: deque())
        )
        
        # 차단된 IP 목록 {ip: unblock_time}
        self.blocked_ips: Dict[str, datetime] = {}
        
        # 의심스러운 활동 패턴 감지
        self.suspicious_patterns: Dict[str, List[datetime]] = defaultdict(list)
        
        # 설정
        self.limits = {
            # 기본 제한 (분당)
            "default": {"requests": 60, "window": 60},
            
            # IP별 제한
            "ip": {"requests": 100, "window": 60},
            
            # 사용자별 제한
            "user": {"requests": 1000, "window": 60},
            
            # 엔드포인트별 특별 제한
            "endpoints": {
                "/api/keywords/analyze": {"requests": 10, "window": 60},
                "/api/titles/generate": {"requests": 20, "window": 60},
                "/api/content/generate": {"requests": 5, "window": 60},
                "/api/content/batch-generate": {"requests": 2, "window": 300},  # 5분에 2번
                "/api/auth/login": {"requests": 5, "window": 300},  # 5분에 5번
                "/api/auth/register": {"requests": 3, "window": 3600},  # 1시간에 3번
            }
        }
    
    def get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출"""
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 기본 클라이언트 IP
        return request.client.host if request.client else "unknown"
    
    def get_user_id(self, request: Request) -> Optional[str]:
        """사용자 ID 추출 (JWT 토큰에서)"""
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # 실제 구현에서는 JWT 토큰을 디코딩해서 사용자 ID 추출
                token = auth_header.split(" ")[1]
                # 임시로 토큰 해시 사용
                return hashlib.md5(token.encode()).hexdigest()[:16]
        except:
            pass
        return None
    
    def cleanup_old_requests(self, request_queue: deque, window_seconds: int):
        """오래된 요청 기록 정리"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        while request_queue and request_queue[0] < cutoff_time:
            request_queue.popleft()
    
    def is_rate_limited(self, identifier: str, limit_config: dict, request_queue: deque) -> bool:
        """Rate limit 확인"""
        current_time = time.time()
        window_seconds = limit_config["window"]
        max_requests = limit_config["requests"]
        
        # 오래된 요청 정리
        self.cleanup_old_requests(request_queue, window_seconds)
        
        # 현재 요청 수 확인
        if len(request_queue) >= max_requests:
            return True
        
        # 요청 기록 추가
        request_queue.append(current_time)
        return False
    
    def detect_suspicious_pattern(self, ip: str, endpoint: str) -> bool:
        """의심스러운 패턴 감지"""
        current_time = datetime.now()
        
        # 1분 이내 같은 IP에서 너무 많은 다양한 엔드포인트 접근
        recent_requests = [
            req_time for req_time in self.suspicious_patterns[ip]
            if current_time - req_time < timedelta(minutes=1)
        ]
        
        if len(recent_requests) > 50:  # 1분에 50개 이상
            return True
        
        # 패턴 기록 추가
        self.suspicious_patterns[ip].append(current_time)
        
        # 오래된 기록 정리 (1시간 이상)
        self.suspicious_patterns[ip] = [
            req_time for req_time in self.suspicious_patterns[ip]
            if current_time - req_time < timedelta(hours=1)
        ]
        
        return False
    
    def block_ip(self, ip: str, duration_minutes: int = 15):
        """IP 차단"""
        self.blocked_ips[ip] = datetime.now() + timedelta(minutes=duration_minutes)
    
    def is_ip_blocked(self, ip: str) -> bool:
        """IP 차단 상태 확인"""
        if ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip]:
                return True
            else:
                # 차단 해제
                del self.blocked_ips[ip]
        return False
    
    async def check_rate_limit(self, request: Request) -> Optional[JSONResponse]:
        """Rate limit 검사"""
        ip = self.get_client_ip(request)
        user_id = self.get_user_id(request)
        endpoint = request.url.path
        
        # IP 차단 확인
        if self.is_ip_blocked(ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "IP blocked due to suspicious activity",
                    "retry_after": 900  # 15분
                }
            )
        
        # 의심스러운 패턴 감지
        if self.detect_suspicious_pattern(ip, endpoint):
            self.block_ip(ip, 30)  # 30분 차단
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Suspicious activity detected. IP blocked.",
                    "retry_after": 1800  # 30분
                }
            )
        
        # 엔드포인트별 제한 확인
        if endpoint in self.limits["endpoints"]:
            endpoint_limit = self.limits["endpoints"][endpoint]
            endpoint_queue = self.endpoint_requests[endpoint][ip]
            
            if self.is_rate_limited(f"{endpoint}:{ip}", endpoint_limit, endpoint_queue):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": f"Rate limit exceeded for {endpoint}",
                        "limit": endpoint_limit["requests"],
                        "window": endpoint_limit["window"],
                        "retry_after": endpoint_limit["window"]
                    }
                )
        
        # IP별 제한 확인
        ip_queue = self.ip_requests[ip]
        if self.is_rate_limited(ip, self.limits["ip"], ip_queue):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded for IP",
                    "limit": self.limits["ip"]["requests"],
                    "window": self.limits["ip"]["window"],
                    "retry_after": self.limits["ip"]["window"]
                }
            )
        
        # 사용자별 제한 확인 (인증된 사용자)
        if user_id:
            user_queue = self.user_requests[user_id]
            if self.is_rate_limited(user_id, self.limits["user"], user_queue):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded for user",
                        "limit": self.limits["user"]["requests"],
                        "window": self.limits["user"]["window"],
                        "retry_after": self.limits["user"]["window"]
                    }
                )
        
        return None  # 제한 없음
    
    def get_stats(self) -> dict:
        """Rate limiter 통계"""
        current_time = datetime.now()
        
        return {
            "active_ips": len(self.ip_requests),
            "active_users": len(self.user_requests),
            "blocked_ips": len([
                ip for ip, unblock_time in self.blocked_ips.items()
                if current_time < unblock_time
            ]),
            "total_endpoint_requests": sum(
                len(requests) for endpoint_data in self.endpoint_requests.values()
                for requests in endpoint_data.values()
            ),
            "suspicious_ips": len(self.suspicious_patterns)
        }

# 전역 Rate Limiter 인스턴스
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting 미들웨어"""
    # Rate limit 검사
    rate_limit_response = await rate_limiter.check_rate_limit(request)
    if rate_limit_response:
        return rate_limit_response
    
    # 정상 요청 처리
    response = await call_next(request)
    
    # Rate limit 헤더 추가
    ip = rate_limiter.get_client_ip(request)
    endpoint = request.url.path
    
    # 현재 사용량 정보 헤더 추가
    if endpoint in rate_limiter.limits["endpoints"]:
        limit_info = rate_limiter.limits["endpoints"][endpoint]
        current_requests = len(rate_limiter.endpoint_requests[endpoint][ip])
        response.headers["X-RateLimit-Limit"] = str(limit_info["requests"])
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit_info["requests"] - current_requests))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + limit_info["window"])
    
    return response