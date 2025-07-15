
# WordPress LiteSpeed 서버 연결 문제 해결 가이드

생성 시간: 2025-07-11 19:34:45.067270
사이트: https://innerspell.com
문제: LiteSpeed 서버가 Authorization 헤더를 차단하여 401 인증 오류 발생

## 🔧 해결 방법 (우선순위 순)

### 방법 1: .htaccess 파일 수정 (권장)
1. WordPress 루트 디렉토리의 .htaccess 파일을 편집
2. htaccess_fix_litespeed.txt 파일의 내용을 .htaccess 파일에 추가
3. 파일 저장 후 권한 확인 (644 권한 권장)

### 방법 2: wp-config.php 파일 수정
1. WordPress 루트 디렉토리의 wp-config.php 파일을 편집
2. wpconfig_fix_litespeed.txt 파일의 내용을 추가
3. "/* That's all, stop editing!" 라인 위에 추가
4. 파일 저장

### 방법 3: 플러그인 설치 (대안)
다음 플러그인 중 하나를 설치:

1. **JSON Basic Authentication** (권장)
   - GitHub: https://github.com/WP-API/Basic-Auth
   - 다운로드 후 /wp-content/plugins/ 폴더에 업로드
   - WordPress 관리자에서 활성화

2. **JWT Authentication for WP REST API**
   - WordPress 플러그인 저장소에서 설치
   - 추가 설정 필요 (JWT 시크릿 키)

## 🧪 테스트 방법

수정 후 다음 명령어로 연결 테스트:
```bash
curl -X GET "https://innerspell.com/wp-json/wp/v2/users/me"      -H "Authorization: Basic YXBwbGU6QkdlYiB4UGs2IEs5QjggNWR2TSBNRFlsIEZuamE="      -H "Content-Type: application/json"
```

성공 시 사용자 정보가 JSON 형태로 반환됩니다.

## 🚨 주의사항

1. 파일 수정 전 반드시 백업 생성
2. FTP/SFTP 또는 호스팅 제공업체의 파일 관리자 사용
3. 수정 후 사이트가 정상 작동하는지 확인
4. 문제 발생 시 백업 파일로 복원

## 📞 추가 지원

- LiteSpeed 서버 설정은 호스팅 제공업체에 문의
- WordPress 관리자 권한 필요
- 서버 관리자 권한이 있는 경우 LiteSpeed 설정에서 직접 수정 가능

## ✅ 성공 확인

수정 완료 후 AutoBlog AI Platform에서 WordPress 연결 테스트를 다시 실행하세요.
연결이 성공하면 자동 게시 기능을 사용할 수 있습니다.
