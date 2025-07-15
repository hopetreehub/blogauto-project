# WordPress REST API 인증 문제 해결 체크리스트

## 1. 서버 설정 확인
- [ ] `.htaccess` 파일에 Authorization 헤더 설정 추가
- [ ] LiteSpeed 웹 관리자 콘솔에서 "Use Client IP in Header" 설정을 "Trusted IP Only"로 변경
- [ ] SSL/HTTPS가 활성화되어 있는지 확인 (https://innerspell.com)

## 2. WordPress 설정 확인
- [ ] REST API 활성화 확인: https://innerspell.com/wp-json/ 접속 시 JSON 응답 확인
- [ ] Application Password가 `/wp-admin/profile.php`에서 생성되었는지 확인
- [ ] 사용자(banana)가 필요한 권한을 가지고 있는지 확인

## 3. 플러그인 충돌 확인
다음 플러그인들이 REST API를 차단할 수 있습니다:
- [ ] Wordfence Security
- [ ] iThemes Security
- [ ] Simple JWT Login
- [ ] WP-SpamShield
- [ ] Jetpack (REST API 모듈)
- [ ] LiteSpeed Cache Plugin (버전 6.2에서 문제 보고됨)

## 4. 인증 테스트
```bash
# Base64 인코딩된 인증 정보로 테스트
curl -H "Authorization: Basic $(echo -n 'banana:CRJWYclhn9m6KNq1cveBRNnV' | base64)" \
     -X GET https://innerspell.com/wp-json/wp/v2/posts
```

## 5. 추가 해결책
- [ ] LiteSpeed Cache 플러그인 사용 중이라면 버전 6.1로 다운그레이드 시도
- [ ] REST API 엔드포인트 `/litespeed/v1`과 `/litespeed/v3`를 방화벽 허용 목록에 추가
- [ ] 일시적으로 모든 보안 플러그인 비활성화 후 테스트