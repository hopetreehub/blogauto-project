from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import traceback
from typing import Union
from logger import app_logger, api_logger

class BlogAutoException(Exception):
    """커스텀 애플리케이션 예외"""
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class AIServiceException(BlogAutoException):
    """AI 서비스 관련 예외"""
    def __init__(self, message: str, service: str = "unknown"):
        super().__init__(
            message=f"AI Service Error ({service}): {message}",
            error_code="AI_SERVICE_ERROR",
            status_code=503
        )
        self.service = service

class DatabaseException(BlogAutoException):
    """데이터베이스 관련 예외"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Database Error: {message}",
            error_code="DATABASE_ERROR",
            status_code=500
        )

class AuthenticationException(BlogAutoException):
    """인증 관련 예외"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            status_code=401
        )

class ValidationException(BlogAutoException):
    """유효성 검증 관련 예외"""
    def __init__(self, message: str):
        super().__init__(
            message=f"Validation Error: {message}",
            error_code="VALIDATION_ERROR",
            status_code=400
        )

def create_error_response(
    error_code: str,
    message: str,
    status_code: int = 500,
    details: dict = None
) -> JSONResponse:
    """표준화된 에러 응답 생성"""
    error_data = {
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": app_logger.logger.handlers[0].formatter.formatTime(
                app_logger.logger.makeRecord(
                    "error", 40, "", 0, "", (), None
                )
            )
        }
    }
    
    if details:
        error_data["error"]["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )

async def blogauto_exception_handler(request: Request, exc: BlogAutoException):
    """커스텀 예외 핸들러"""
    api_logger.log_error(
        endpoint=str(request.url.path),
        error=exc,
        user_id=getattr(request.state, 'user_id', None)
    )
    
    return create_error_response(
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 핸들러"""
    api_logger.log_error(
        endpoint=str(request.url.path),
        error=exc,
        user_id=getattr(request.state, 'user_id', None)
    )
    
    return create_error_response(
        error_code="HTTP_ERROR",
        message=exc.detail,
        status_code=exc.status_code
    )

async def validation_exception_handler(request: Request, exc: ValidationError):
    """Pydantic 유효성 검증 예외 핸들러"""
    api_logger.log_error(
        endpoint=str(request.url.path),
        error=exc,
        user_id=getattr(request.state, 'user_id', None)
    )
    
    # Pydantic 에러를 더 읽기 쉽게 변환
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        error_code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=422,
        details={"validation_errors": error_details}
    )

async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """데이터베이스 예외 핸들러"""
    api_logger.log_error(
        endpoint=str(request.url.path),
        error=exc,
        user_id=getattr(request.state, 'user_id', None)
    )
    
    return create_error_response(
        error_code="DATABASE_ERROR",
        message="Database operation failed",
        status_code=500
    )

async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    app_logger.error(
        f"Unexpected error at {request.url.path}",
        error=exc,
        endpoint=str(request.url.path),
        method=request.method,
        traceback=traceback.format_exc()
    )
    
    return create_error_response(
        error_code="INTERNAL_ERROR",
        message="Internal server error occurred",
        status_code=500
    )

def safe_execute(func, *args, fallback_value=None, log_error=True, **kwargs):
    """안전한 함수 실행 래퍼"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            app_logger.error(f"Error executing {func.__name__}", error=e)
        return fallback_value

async def safe_execute_async(func, *args, fallback_value=None, log_error=True, **kwargs):
    """안전한 비동기 함수 실행 래퍼"""
    try:
        return await func(*args, **kwargs)
    except Exception as e:
        if log_error:
            app_logger.error(f"Error executing {func.__name__}", error=e)
        return fallback_value