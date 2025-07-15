# WordPress REST API 401 오류 해결 가이드

## 문제 원인
LiteSpeed 서버가 Authorization 헤더를 차단하여 WordPress가 인증 정보를 받지 못함

## 해결 방법 (우선순위 순)

### 1. .htaccess 파일 수정 (가장 중요)
WordPress 루트 디렉토리의 `.htaccess` 파일 맨 위에 다음 추가:

```apache
# BEGIN WordPress Authorization
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteRule .* - [E=REMOTE_USER:%{HTTP:Authorization}]
</IfModule>

# LiteSpeed 전용 설정
<IfModule Litespeed>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1
</IfModule>
# END WordPress Authorization

# 기존 WordPress 규칙 아래에...
```

### 2. wp-config.php 파일 수정
`wp-config.php` 파일에서 `/* That's all, stop editing! */` 줄 위에 추가:

```php
// LiteSpeed Authorization 헤더 수정
if (!isset($_SERVER['HTTP_AUTHORIZATION'])) {
    if (isset($_SERVER['REDIRECT_HTTP_AUTHORIZATION'])) {
        $_SERVER['HTTP_AUTHORIZATION'] = $_SERVER['REDIRECT_HTTP_AUTHORIZATION'];
    } elseif (isset($_SERVER['HTTP_AUTHORIZATION'])) {
        $_SERVER['HTTP_AUTHORIZATION'] = $_SERVER['HTTP_AUTHORIZATION'];
    } elseif (isset($_SERVER['REDIRECT_REMOTE_USER'])) {
        $_SERVER['HTTP_AUTHORIZATION'] = $_SERVER['REDIRECT_REMOTE_USER'];
    }
}

// Application Password 강제 활성화
add_filter('wp_is_application_passwords_available', '__return_true');
```

### 3. 플러그인 설치 (위 방법이 안 될 경우)
WordPress 관리자 페이지에서:
1. 플러그인 → 새로 추가
2. "Basic Auth" 검색
3. "JSON Basic Authentication" by WP REST API Team 설치 및 활성화

### 4. LiteSpeed Cache 플러그인 설정
LiteSpeed Cache 플러그인이 설치된 경우:
1. LiteSpeed Cache → 설정 → 고급
2. "Login Cookie" 설정에서 REST API 제외
3. "REST API를 캐시하지 않음" 옵션 활성화

### 5. 대안: JWT Authentication 플러그인
Basic Auth가 계속 작동하지 않으면:
1. "JWT Authentication for WP REST API" 플러그인 설치
2. wp-config.php에 비밀 키 추가:
   ```php
   define('JWT_AUTH_SECRET_KEY', 'your-top-secret-key');
   ```

## 테스트 방법
```bash
# 1단계 완료 후 테스트
curl -X GET https://innerspell.com/wp-json/wp/v2/users/me \
  -H "Authorization: Basic YmFuYW5hOkNSSldZY2xobjltNktOcTFjdmVCUk5uVg==" \
  -H "User-Agent: BlogAuto/1.0"
```

## 주의사항
- .htaccess 수정 후 브라우저 캐시 삭제
- LiteSpeed 서버는 재시작이 필요할 수 있음
- 보안 플러그인이 REST API를 차단하고 있지 않은지 확인

## 현재 상태
- ✅ REST API 활성화됨
- ✅ Application Password 기능 지원됨
- ❌ Authorization 헤더가 전달되지 않음 (LiteSpeed 문제)

이 가이드의 1번과 2번을 적용하면 문제가 해결될 것입니다.