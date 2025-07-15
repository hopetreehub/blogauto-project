# BlogAuto 보안 가이드

## 📋 목차

1. [보안 개요](#보안-개요)
2. [인증 및 권한 관리](#인증-및-권한-관리)
3. [API 보안](#api-보안)
4. [데이터 보호](#데이터-보호)
5. [네트워크 보안](#네트워크-보안)
6. [보안 모니터링](#보안-모니터링)
7. [보안 체크리스트](#보안-체크리스트)
8. [사고 대응](#사고-대응)

## 🔒 보안 개요

BlogAuto는 다층 보안 전략을 채택하여 다음과 같은 보안 목표를 달성합니다:

- **기밀성**: 민감한 데이터의 무단 접근 방지
- **무결성**: 데이터 변조 방지
- **가용성**: 서비스 중단 방지
- **책임추적성**: 모든 활동 로깅 및 감사

## 🔐 인증 및 권한 관리

### 1. JWT 기반 인증

```python
# JWT 토큰 생성 및 검증
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# 비밀번호 해싱
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.environ.get("SECRET_KEY")  # 32바이트 이상
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise ValueError("Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

# 보안 의존성
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user(username=username)
    if user is None:
        raise credentials_exception
    
    return user
```

### 2. 역할 기반 접근 제어 (RBAC)

```python
from enum import Enum
from functools import wraps

class Role(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Permission(str, Enum):
    CREATE_POST = "create_post"
    EDIT_POST = "edit_post"
    DELETE_POST = "delete_post"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_USERS = "manage_users"

# 역할별 권한 매핑
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.CREATE_POST,
        Permission.EDIT_POST,
        Permission.DELETE_POST,
        Permission.VIEW_ANALYTICS,
        Permission.MANAGE_USERS,
    ],
    Role.EDITOR: [
        Permission.CREATE_POST,
        Permission.EDIT_POST,
        Permission.VIEW_ANALYTICS,
    ],
    Role.VIEWER: [
        Permission.VIEW_ANALYTICS,
    ],
}

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            user_permissions = ROLE_PERMISSIONS.get(current_user.role, [])
            
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 사용 예시
@app.post("/api/posts")
@require_permission(Permission.CREATE_POST)
async def create_post(post: PostCreate, current_user: User = Depends()):
    # 권한이 있는 사용자만 접근 가능
    return await create_new_post(post, current_user)
```

### 3. 다중 인증 (MFA)

```python
import pyotp
import qrcode
from io import BytesIO

class MFAService:
    @staticmethod
    def generate_secret():
        """TOTP 시크릿 생성"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(email: str, secret: str):
        """QR 코드 생성"""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name='BlogAuto'
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        return buf
    
    @staticmethod
    def verify_token(secret: str, token: str):
        """TOTP 토큰 검증"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)

# MFA 활성화
@app.post("/api/auth/mfa/enable")
async def enable_mfa(current_user: User = Depends(get_current_user)):
    secret = MFAService.generate_secret()
    
    # 사용자 DB에 시크릿 저장 (암호화)
    encrypted_secret = crypto_manager.encrypt(secret)
    await update_user_mfa_secret(current_user.id, encrypted_secret)
    
    # QR 코드 반환
    qr_code = MFAService.generate_qr_code(current_user.email, secret)
    return StreamingResponse(qr_code, media_type="image/png")

# MFA 로그인
@app.post("/api/auth/login/mfa")
async def login_with_mfa(
    credentials: OAuth2PasswordRequestForm = Depends(),
    mfa_token: str = Body(...),
):
    # 1단계: 비밀번호 검증
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 2단계: MFA 토큰 검증
    if user.mfa_enabled:
        decrypted_secret = crypto_manager.decrypt(user.mfa_secret)
        if not MFAService.verify_token(decrypted_secret, mfa_token):
            raise HTTPException(status_code=401, detail="Invalid MFA token")
    
    # 토큰 발급
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

## 🛡️ API 보안

### 1. Rate Limiting

```python
from rate_limiter import RateLimiter, rate_limit_middleware

# Rate Limiter 설정
rate_limiter = RateLimiter(
    redis_client=redis_client,
    default_limit=60,  # 분당 60회
    default_window=60,  # 60초 윈도우
    block_duration=300,  # 5분 차단
)

# 엔드포인트별 커스텀 제한
ENDPOINT_LIMITS = {
    "/api/content/generate": {"limit": 10, "window": 3600},  # 시간당 10회
    "/api/auth/login": {"limit": 5, "window": 300},  # 5분당 5회
    "/api/keywords/analyze": {"limit": 30, "window": 60},  # 분당 30회
}

# Rate Limiting 미들웨어
app.middleware("http")(rate_limit_middleware)

# IP 차단 관리
@app.post("/api/admin/block-ip")
@require_permission(Permission.MANAGE_USERS)
async def block_ip(
    ip_address: str,
    duration: int = 86400,  # 24시간
    reason: str = None,
    current_user: User = Depends()
):
    await rate_limiter.block_ip(ip_address, duration, reason)
    
    # 보안 이벤트 로깅
    logger.warning(
        f"IP blocked: {ip_address} by {current_user.email} for {duration}s. "
        f"Reason: {reason}"
    )
    
    return {"status": "blocked", "ip": ip_address, "duration": duration}
```

### 2. 입력 검증 및 살균

```python
from pydantic import BaseModel, validator, constr, EmailStr
import bleach
import re

class SecureContentRequest(BaseModel):
    title: constr(min_length=1, max_length=200, strip_whitespace=True)
    content: constr(min_length=10, max_length=50000)
    tags: List[constr(max_length=50)] = []
    
    @validator('title')
    def validate_title(cls, v):
        # XSS 방지
        cleaned = bleach.clean(v, tags=[], strip=True)
        
        # SQL 인젝션 패턴 검사
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER)\b)",
            r"(--|#|/\*|\*/)",
            r"(\bOR\b.*=.*)",
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                raise ValueError("Invalid characters in title")
        
        return cleaned
    
    @validator('content')
    def validate_content(cls, v):
        # 허용된 HTML 태그만 허용
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 
            'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote',
            'a', 'img', 'pre', 'code'
        ]
        
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'width', 'height'],
        }
        
        cleaned = bleach.clean(
            v,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        return cleaned
    
    @validator('tags')
    def validate_tags(cls, v):
        # 태그 정규화
        normalized_tags = []
        for tag in v:
            # 특수문자 제거
            clean_tag = re.sub(r'[^\w\s-]', '', tag)
            # 공백을 하이픈으로
            clean_tag = re.sub(r'\s+', '-', clean_tag)
            # 소문자 변환
            clean_tag = clean_tag.lower().strip('-')
            
            if clean_tag and len(clean_tag) >= 2:
                normalized_tags.append(clean_tag)
        
        return list(set(normalized_tags))[:10]  # 최대 10개

# 파일 업로드 검증
def validate_file_upload(file: UploadFile):
    # 파일 크기 제한 (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # 허용된 MIME 타입
    ALLOWED_MIME_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'application/pdf',
    ]
    
    # 허용된 확장자
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf'}
    
    # 파일 크기 검사
    file.file.seek(0, 2)  # 파일 끝으로
    file_size = file.file.tell()
    file.file.seek(0)  # 처음으로 되돌림
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE} bytes"
        )
    
    # MIME 타입 검사
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"File type not allowed. Allowed types: {ALLOWED_MIME_TYPES}"
        )
    
    # 확장자 검사
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"File extension not allowed. Allowed extensions: {ALLOWED_EXTENSIONS}"
        )
    
    # 파일 내용 검사 (매직 넘버)
    file_header = file.file.read(512)
    file.file.seek(0)
    
    if not is_valid_file_header(file_header, file.content_type):
        raise HTTPException(
            status_code=415,
            detail="File content does not match declared type"
        )
    
    return True
```

### 3. CORS 설정

```python
from fastapi.middleware.cors import CORSMiddleware

# 프로덕션 CORS 설정
origins = os.environ.get("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=3600,  # preflight 캐시 시간
)

# 동적 CORS 검증
async def validate_origin(request: Request):
    origin = request.headers.get("origin")
    
    if not origin:
        return True
    
    # 허용된 도메인 패턴
    allowed_patterns = [
        r"^https://([a-z0-9-]+\.)?blogauto\.com$",
        r"^https://localhost:\d+$",  # 개발 환경
    ]
    
    for pattern in allowed_patterns:
        if re.match(pattern, origin):
            return True
    
    return False
```

## 🔐 데이터 보호

### 1. API 키 암호화

```python
from crypto_utils import CryptoManager

# 암호화 관리자
crypto_manager = CryptoManager(
    master_password=os.environ.get("MASTER_PASSWORD")
)

# API 키 저장
@app.post("/api/secure/store-key")
async def store_api_key(
    service: str,
    api_key: str,
    current_user: User = Depends(get_current_user)
):
    # 암호화
    encrypted_key = crypto_manager.encrypt_api_key(api_key)
    
    # 저장
    await save_encrypted_key(
        user_id=current_user.id,
        service=service,
        encrypted_key=encrypted_key,
        key_hash=crypto_manager.hash_key(api_key)  # 검증용
    )
    
    # 감사 로그
    logger.info(f"API key stored for service: {service} by user: {current_user.email}")
    
    return {"status": "stored", "service": service}

# API 키 사용
@app.post("/api/content/generate")
async def generate_content(
    request: ContentRequest,
    current_user: User = Depends(get_current_user)
):
    # 암호화된 키 조회
    encrypted_key = await get_user_api_key(current_user.id, "openai")
    
    if not encrypted_key:
        raise HTTPException(status_code=400, detail="API key not configured")
    
    # 복호화
    api_key = crypto_manager.decrypt_api_key(encrypted_key)
    
    # 사용 (메모리에서만)
    try:
        result = await call_openai_api(api_key, request)
        return result
    finally:
        # 메모리에서 제거
        del api_key
```

### 2. 데이터베이스 보안

```python
# 암호화된 필드
from sqlalchemy import Column, String
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    
    # 암호화된 필드
    phone_number = Column(
        EncryptedType(String, SECRET_KEY, AesEngine, 'pkcs5'),
        nullable=True
    )
    
    api_keys = Column(
        EncryptedType(JSON, SECRET_KEY, AesEngine, 'pkcs5'),
        default={}
    )

# 쿼리 로깅 방지 (민감한 데이터)
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # 민감한 테이블 쿼리 마스킹
    if "api_keys" in statement or "passwords" in statement:
        logger.info("Sensitive query executed: [REDACTED]")
    else:
        logger.debug(f"Query: {statement[:100]}...")
```

### 3. 환경 변수 보안

```python
import hvac  # HashiCorp Vault 클라이언트

class SecretManager:
    def __init__(self):
        self.vault_url = os.environ.get("VAULT_URL", "http://localhost:8200")
        self.vault_token = os.environ.get("VAULT_TOKEN")
        
        self.client = hvac.Client(
            url=self.vault_url,
            token=self.vault_token
        )
    
    def get_secret(self, path: str, key: str):
        """Vault에서 시크릿 조회"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path
            )
            return response['data']['data'].get(key)
        except Exception as e:
            logger.error(f"Failed to get secret: {e}")
            # 폴백: 환경 변수
            return os.environ.get(key)
    
    def rotate_secret(self, path: str, key: str, new_value: str):
        """시크릿 로테이션"""
        try:
            # 새 버전 저장
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret={key: new_value}
            )
            
            # 이전 버전 보관 (롤백용)
            logger.info(f"Secret rotated: {path}/{key}")
            
        except Exception as e:
            logger.error(f"Failed to rotate secret: {e}")
            raise

# 사용 예시
secret_manager = SecretManager()

# 시크릿 조회
OPENAI_API_KEY = secret_manager.get_secret("blogauto/prod", "OPENAI_API_KEY")

# 주기적 로테이션
@app.on_event("startup")
@repeat_every(seconds=86400)  # 매일
async def rotate_secrets():
    # API 키 로테이션 로직
    pass
```

## 🌐 네트워크 보안

### 1. HTTPS 강제

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS 리다이렉트 (프로덕션)
if os.environ.get("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# HSTS 헤더 추가
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # 보안 헤더
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self' https://api.openai.com https://sentry.io"
    )
    
    return response
```

### 2. WAF 규칙

```python
# 웹 애플리케이션 방화벽 규칙
class WAFMiddleware:
    def __init__(self, app):
        self.app = app
        self.rules = self._load_rules()
    
    def _load_rules(self):
        return {
            "sql_injection": [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION)\b.*\b(FROM|WHERE|INTO)\b)",
                r"(\'|\").*(\b(OR|AND)\b).*=.*\1",
            ],
            "xss": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
            ],
            "path_traversal": [
                r"\.\./",
                r"/etc/passwd",
                r"/proc/self",
            ],
            "command_injection": [
                r";\s*(ls|cat|wget|curl|bash|sh)",
                r"\|.*\b(nc|netcat|bash|sh)\b",
            ]
        }
    
    async def __call__(self, request: Request, call_next):
        # 요청 검사
        path = request.url.path
        query = str(request.url.query)
        
        # User-Agent 검사
        user_agent = request.headers.get("user-agent", "")
        if self._is_malicious_bot(user_agent):
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden"}
            )
        
        # URL 검사
        for rule_type, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, path + query, re.IGNORECASE):
                    # 보안 이벤트 로깅
                    logger.warning(
                        f"WAF blocked {rule_type}: {request.client.host} - {path}"
                    )
                    
                    # IP 차단 고려
                    await self._consider_ip_block(request.client.host, rule_type)
                    
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Bad request"}
                    )
        
        # 요청 본문 검사 (POST, PUT)
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.body()
                body_text = body.decode('utf-8')
                
                for rule_type, patterns in self.rules.items():
                    for pattern in patterns:
                        if re.search(pattern, body_text, re.IGNORECASE):
                            logger.warning(
                                f"WAF blocked {rule_type} in body: {request.client.host}"
                            )
                            return JSONResponse(
                                status_code=400,
                                content={"detail": "Bad request"}
                            )
                
                # 요청 복원
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
                
            except Exception:
                pass
        
        response = await call_next(request)
        return response
    
    def _is_malicious_bot(self, user_agent: str) -> bool:
        malicious_patterns = [
            r"sqlmap",
            r"nikto",
            r"scanner",
            r"havij",
            r"acunetix",
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False
    
    async def _consider_ip_block(self, ip: str, rule_type: str):
        # 위반 카운트 증가
        key = f"waf_violations:{ip}"
        count = await redis_client.incr(key)
        await redis_client.expire(key, 3600)  # 1시간
        
        # 임계값 초과 시 차단
        if count >= 5:
            await rate_limiter.block_ip(
                ip, 
                duration=86400,  # 24시간
                reason=f"WAF: Multiple {rule_type} attempts"
            )

# WAF 미들웨어 추가
app.add_middleware(WAFMiddleware)
```

## 📊 보안 모니터링

### 1. 보안 이벤트 로깅

```python
import structlog
from typing import Dict, Any

# 구조화된 로깅
logger = structlog.get_logger()

class SecurityLogger:
    @staticmethod
    def log_auth_attempt(
        username: str,
        ip: str,
        success: bool,
        method: str = "password"
    ):
        logger.info(
            "auth_attempt",
            username=username,
            ip=ip,
            success=success,
            method=method,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def log_access(
        user_id: int,
        resource: str,
        action: str,
        allowed: bool
    ):
        logger.info(
            "access_control",
            user_id=user_id,
            resource=resource,
            action=action,
            allowed=allowed,
            timestamp=datetime.utcnow().isoformat()
        )
    
    @staticmethod
    def log_security_event(
        event_type: str,
        severity: str,
        details: Dict[str, Any]
    ):
        logger.warning(
            "security_event",
            event_type=event_type,
            severity=severity,
            details=details,
            timestamp=datetime.utcnow().isoformat()
        )

# 실패한 로그인 추적
class LoginAttemptTracker:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.max_attempts = 5
        self.lockout_duration = 900  # 15분
    
    async def record_attempt(self, username: str, ip: str, success: bool):
        if success:
            # 성공 시 카운터 리셋
            await self.redis.delete(f"login_attempts:{username}")
            await self.redis.delete(f"login_attempts_ip:{ip}")
        else:
            # 실패 시 카운터 증가
            user_attempts = await self.redis.incr(f"login_attempts:{username}")
            await self.redis.expire(f"login_attempts:{username}", self.lockout_duration)
            
            ip_attempts = await self.redis.incr(f"login_attempts_ip:{ip}")
            await self.redis.expire(f"login_attempts_ip:{ip}", self.lockout_duration)
            
            # 임계값 확인
            if user_attempts >= self.max_attempts:
                await self._lockout_account(username)
            
            if ip_attempts >= self.max_attempts * 2:
                await self._block_ip(ip)
    
    async def _lockout_account(self, username: str):
        await self.redis.setex(
            f"account_locked:{username}",
            self.lockout_duration,
            "locked"
        )
        
        SecurityLogger.log_security_event(
            "account_lockout",
            "high",
            {"username": username, "duration": self.lockout_duration}
        )
    
    async def _block_ip(self, ip: str):
        await rate_limiter.block_ip(ip, self.lockout_duration, "Too many login attempts")
        
        SecurityLogger.log_security_event(
            "ip_blocked",
            "high",
            {"ip": ip, "reason": "login_attempts", "duration": self.lockout_duration}
        )
```

### 2. 이상 탐지

```python
class AnomalyDetector:
    def __init__(self):
        self.patterns = {}
        self.thresholds = {
            "requests_per_minute": 100,
            "unique_endpoints_per_minute": 20,
            "error_rate": 0.1,
            "response_time_p95": 5.0,
        }
    
    async def analyze_request_pattern(self, user_id: int, request: Request):
        key = f"user_pattern:{user_id}"
        now = datetime.utcnow()
        
        # 요청 패턴 기록
        pattern = {
            "timestamp": now.isoformat(),
            "endpoint": request.url.path,
            "method": request.method,
            "ip": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
        }
        
        # Redis에 저장 (sliding window)
        await self.redis.zadd(
            key,
            {json.dumps(pattern): now.timestamp()}
        )
        
        # 오래된 데이터 제거 (1시간)
        await self.redis.zremrangebyscore(
            key,
            0,
            (now - timedelta(hours=1)).timestamp()
        )
        
        # 이상 패턴 검사
        await self._check_anomalies(user_id, key)
    
    async def _check_anomalies(self, user_id: int, key: str):
        # 최근 5분간 패턴 조회
        now = datetime.utcnow()
        five_min_ago = (now - timedelta(minutes=5)).timestamp()
        
        patterns = await self.redis.zrangebyscore(
            key,
            five_min_ago,
            now.timestamp()
        )
        
        if len(patterns) > self.thresholds["requests_per_minute"] * 5:
            SecurityLogger.log_security_event(
                "anomaly_detected",
                "medium",
                {
                    "user_id": user_id,
                    "type": "high_request_rate",
                    "count": len(patterns),
                }
            )
        
        # 고유 엔드포인트 수 확인
        endpoints = set()
        for pattern_str in patterns:
            pattern = json.loads(pattern_str)
            endpoints.add(pattern["endpoint"])
        
        if len(endpoints) > self.thresholds["unique_endpoints_per_minute"] * 5:
            SecurityLogger.log_security_event(
                "anomaly_detected",
                "high",
                {
                    "user_id": user_id,
                    "type": "endpoint_scanning",
                    "unique_endpoints": len(endpoints),
                }
            )
```

## ✅ 보안 체크리스트

### 개발 단계
- [ ] 모든 입력값에 대한 검증 구현
- [ ] SQL 인젝션 방지 (파라미터화된 쿼리)
- [ ] XSS 방지 (출력 이스케이핑)
- [ ] CSRF 토큰 구현
- [ ] 민감한 데이터 암호화
- [ ] 안전한 세션 관리
- [ ] 적절한 에러 처리 (정보 노출 방지)

### 배포 단계
- [ ] HTTPS 강제 적용
- [ ] 보안 헤더 설정
- [ ] CORS 정책 설정
- [ ] Rate Limiting 구성
- [ ] WAF 규칙 활성화
- [ ] 로깅 및 모니터링 설정
- [ ] 백업 및 복구 계획

### 운영 단계
- [ ] 정기적인 보안 패치
- [ ] 접근 권한 검토
- [ ] 로그 분석
- [ ] 침투 테스트
- [ ] 보안 교육
- [ ] 사고 대응 훈련

## 🚨 사고 대응

### 1. 사고 대응 절차

```python
class IncidentResponse:
    def __init__(self):
        self.notification_channels = {
            "email": self._send_email,
            "slack": self._send_slack,
            "pagerduty": self._send_pagerduty,
        }
    
    async def handle_incident(self, incident_type: str, details: Dict[str, Any]):
        # 1. 즉시 대응
        immediate_action = await self._immediate_response(incident_type, details)
        
        # 2. 알림 발송
        await self._notify_team(incident_type, details, immediate_action)
        
        # 3. 증거 수집
        evidence = await self._collect_evidence(incident_type, details)
        
        # 4. 상세 분석
        analysis = await self._analyze_incident(evidence)
        
        # 5. 복구 계획
        recovery_plan = await self._create_recovery_plan(analysis)
        
        # 6. 사후 보고
        await self._post_incident_report(
            incident_type, details, analysis, recovery_plan
        )
        
        return {
            "incident_id": str(uuid.uuid4()),
            "type": incident_type,
            "immediate_action": immediate_action,
            "status": "handled",
            "recovery_plan": recovery_plan,
        }
    
    async def _immediate_response(self, incident_type: str, details: Dict[str, Any]):
        actions = []
        
        if incident_type == "data_breach":
            # 영향받은 계정 비활성화
            affected_users = details.get("affected_users", [])
            for user_id in affected_users:
                await deactivate_user(user_id)
                actions.append(f"Deactivated user {user_id}")
            
            # 관련 토큰 무효화
            await invalidate_all_tokens()
            actions.append("Invalidated all access tokens")
        
        elif incident_type == "ddos_attack":
            # Rate limiting 강화
            await rate_limiter.set_emergency_mode(True)
            actions.append("Enabled emergency rate limiting")
            
            # CDN 보호 모드 활성화
            await enable_cdn_protection()
            actions.append("Enabled CDN protection mode")
        
        elif incident_type == "malware_detection":
            # 영향받은 서비스 격리
            service = details.get("service")
            await isolate_service(service)
            actions.append(f"Isolated service: {service}")
        
        return actions
```

### 2. 보안 감사

```python
# 정기 보안 감사
@app.on_event("startup")
@repeat_every(seconds=86400)  # 매일
async def security_audit():
    audit_results = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # 1. 만료된 토큰 정리
    expired_tokens = await clean_expired_tokens()
    audit_results["checks"]["expired_tokens"] = expired_tokens
    
    # 2. 비활성 계정 확인
    inactive_accounts = await find_inactive_accounts(days=90)
    audit_results["checks"]["inactive_accounts"] = len(inactive_accounts)
    
    # 3. 권한 에스컬레이션 확인
    privilege_changes = await check_privilege_escalation()
    audit_results["checks"]["privilege_changes"] = privilege_changes
    
    # 4. 비정상 API 사용 패턴
    api_anomalies = await detect_api_anomalies()
    audit_results["checks"]["api_anomalies"] = api_anomalies
    
    # 5. SSL 인증서 만료 확인
    ssl_status = await check_ssl_certificates()
    audit_results["checks"]["ssl_certificates"] = ssl_status
    
    # 보고서 생성
    await generate_audit_report(audit_results)
    
    # 이슈 발견 시 알림
    if any(audit_results["checks"].values()):
        await notify_security_team(audit_results)
```

## 🔗 관련 문서

- [API 문서](./api-documentation.md)
- [모니터링 가이드](./monitoring-guide.md)
- [배포 가이드](./deployment-guide.md)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

---

**마지막 업데이트**: 2025년 7월 12일  
**버전**: v1.0.0  
**담당자**: BlogAuto 보안팀