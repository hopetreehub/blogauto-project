import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

class StructuredLogger:
    """구조화된 로깅 시스템"""
    
    def __init__(self, name: str = "blogauto", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 기존 핸들러 제거
        self.logger.handlers.clear()
        
        # 로그 디렉토리 생성
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 파일 핸들러 설정
        if not log_file:
            log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        console_handler = logging.StreamHandler(sys.stdout)
        
        # 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """정보 로그"""
        extra_data = json.dumps(kwargs, ensure_ascii=False) if kwargs else ""
        self.logger.info(f"{message} {extra_data}")
    
    def warning(self, message: str, **kwargs):
        """경고 로그"""
        extra_data = json.dumps(kwargs, ensure_ascii=False) if kwargs else ""
        self.logger.warning(f"{message} {extra_data}")
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """에러 로그"""
        extra_data = json.dumps(kwargs, ensure_ascii=False) if kwargs else ""
        error_info = f" | Error: {str(error)}" if error else ""
        self.logger.error(f"{message} {extra_data}{error_info}")
    
    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        extra_data = json.dumps(kwargs, ensure_ascii=False) if kwargs else ""
        self.logger.debug(f"{message} {extra_data}")

class APILogger:
    """API 요청/응답 로깅"""
    
    def __init__(self):
        self.logger = StructuredLogger("api")
    
    def log_request(self, method: str, endpoint: str, user_id: Optional[str] = None, **kwargs):
        """API 요청 로그"""
        self.logger.info(
            f"API Request: {method} {endpoint}",
            user_id=user_id,
            method=method,
            endpoint=endpoint,
            **kwargs
        )
    
    def log_response(self, endpoint: str, status_code: int, duration_ms: float, user_id: Optional[str] = None):
        """API 응답 로그"""
        self.logger.info(
            f"API Response: {endpoint} - {status_code}",
            user_id=user_id,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms
        )
    
    def log_error(self, endpoint: str, error: Exception, user_id: Optional[str] = None, **kwargs):
        """API 에러 로그"""
        self.logger.error(
            f"API Error: {endpoint}",
            error=error,
            user_id=user_id,
            endpoint=endpoint,
            **kwargs
        )

class AIServiceLogger:
    """AI 서비스 전용 로깅"""
    
    def __init__(self):
        self.logger = StructuredLogger("ai_service")
    
    def log_generation(self, service: str, operation: str, user_id: str, success: bool, **kwargs):
        """AI 생성 작업 로그"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"AI {operation}: {service} - {status}",
            service=service,
            operation=operation,
            user_id=user_id,
            success=success,
            **kwargs
        )
    
    def log_api_usage(self, service: str, tokens_used: Optional[int] = None, cost: Optional[float] = None):
        """AI API 사용량 로그"""
        self.logger.info(
            f"AI API Usage: {service}",
            service=service,
            tokens_used=tokens_used,
            cost=cost
        )

# 글로벌 로거 인스턴스
app_logger = StructuredLogger()
api_logger = APILogger()
ai_logger = AIServiceLogger()