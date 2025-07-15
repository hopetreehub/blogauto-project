# WordPress REST API 인증 플러그인 추천

## 1. JWT Authentication for WP REST API
- **설치**: https://wordpress.org/plugins/jwt-authentication-for-wp-rest-api/
- **장점**: 토큰 기반 인증으로 더 안전
- **설정 필요사항**:
  ```php
  // wp-config.php에 추가
  define('JWT_AUTH_SECRET_KEY', 'your-top-secret-key');
  define('JWT_AUTH_CORS_ENABLE', true);
  ```

## 2. Basic Authentication Plugin (개발용)
- **GitHub**: https://github.com/WP-API/Basic-Auth
- **주의**: 개발 환경에서만 사용, 프로덕션에서는 권장하지 않음
- **장점**: 설정이 간단함

## 3. REST API Authentication for WP (프리미엄)
- **특징**: JWT와 Basic Auth 모두 지원
- **보안**: HMAC 알고리즘으로 토큰 검증

## 플러그인 없이 해결하기 (권장)
Application Password는 WordPress 5.6+에 내장되어 있으므로, 위의 .htaccess 설정만으로도 충분히 작동해야 합니다.