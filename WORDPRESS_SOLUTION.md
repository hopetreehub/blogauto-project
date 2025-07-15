# WordPress REST API 401 오류 최종 해결 가이드

## 문제 상황
- 사이트: https://innerspell.com (LiteSpeed 서버)
- 오류: 401 "현재 로그인 상태가 아닙니다"
- 원인: LiteSpeed 서버가 Authorization 헤더를 차단

## 해결 방법 (우선순위 순)

### 방법 1: miniOrange API Authentication 플러그인 (가장 쉬움) ✅

1. WordPress 관리자로 로그인
2. 플러그인 → 새로 추가
3. "miniOrange API Authentication" 검색
4. 설치 및 활성화
5. 플러그인 설정에서:
   - API Key Authentication 선택
   - 새 API Key 생성
   - 생성된 API Key를 복사
6. 블로그 자동화 앱에서:
   - 사용자명: 그대로 유지
   - 비밀번호: 생성된 API Key 입력

### 방법 2: JWT Authentication 플러그인

1. "JWT Authentication for WP REST API" 플러그인 설치
2. wp-config.php에 추가:
   ```php
   define('JWT_AUTH_SECRET_KEY', 'your-top-secret-key');
   define('JWT_AUTH_CORS_ENABLE', true);
   ```
3. .htaccess에 추가:
   ```apache
   RewriteCond %{HTTP:Authorization} ^(.*)
   RewriteRule ^(.*) - [E=HTTP_AUTHORIZATION:%1]
   ```

### 방법 3: Basic Auth 플러그인 + 서버 설정

1. "JSON Basic Authentication" 플러그인 설치 (WP REST API Team 제작)
2. .htaccess 파일 수정:
   ```apache
   # WordPress 루트 디렉토리 .htaccess 맨 위에 추가
   <IfModule mod_rewrite.c>
   RewriteEngine On
   RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
   RewriteRule .* - [E=REMOTE_USER:%{HTTP:Authorization}]
   </IfModule>
   ```
3. wp-config.php 수정:
   ```php
   // /* That's all, stop editing! */ 위에 추가
   if (!isset($_SERVER['HTTP_AUTHORIZATION'])) {
       if (isset($_SERVER['REDIRECT_HTTP_AUTHORIZATION'])) {
           $_SERVER['HTTP_AUTHORIZATION'] = $_SERVER['REDIRECT_HTTP_AUTHORIZATION'];
       }
   }
   ```

## 추가 확인사항

1. **LiteSpeed Cache 플러그인 설정**
   - 설정 → 캐시 → REST API를 캐시하지 않음 활성화
   - 모든 캐시 제거

2. **WordPress 버전**
   - 5.6 이상 필요 (Application Password 기본 지원)

3. **보안 플러그인**
   - Wordfence, Sucuri 등이 REST API 차단하지 않도록 설정

## 테스트 방법

설정 완료 후:
1. 브라우저 캐시 삭제 (Ctrl+Shift+Del)
2. 블로그 자동화 앱에서 "연결 테스트" 클릭

## 권장사항

**miniOrange API Authentication** 플러그인이 가장 간단하고 확실한 해결책입니다.
- 설치만 하면 즉시 작동
- API Key 방식으로 안전
- LiteSpeed 서버 설정 변경 불필요