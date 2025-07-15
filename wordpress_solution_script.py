#!/usr/bin/env python3
"""
WordPress 연결 문제 해결 스크립트
LiteSpeed 서버의 Authorization 헤더 차단 문제를 해결하는 방법을 제공합니다.
"""

import os
from datetime import datetime

def generate_htaccess_fix():
    """LiteSpeed용 .htaccess 수정 코드 생성"""
    htaccess_code = '''
# WordPress REST API Authorization 헤더 수정 (LiteSpeed 서버용)
# 이 코드를 WordPress 루트 디렉토리의 .htaccess 파일에 추가하세요

# BEGIN WordPress REST API Authorization Fix
<IfModule mod_rewrite.c>
RewriteEngine On

# Authorization 헤더가 전달되도록 설정
RewriteCond %{HTTP:Authorization} ^(.*)
RewriteRule ^(.*) - [E=HTTP_AUTHORIZATION:%1]

# REMOTE_USER 환경 변수 설정
RewriteCond %{HTTP:Authorization} ^Basic\s+(.*)$
RewriteRule ^(.*)$ - [E=REMOTE_USER:%1]

# LiteSpeed 전용 Authorization 헤더 처리
SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1
</IfModule>

# LiteSpeed Cache 플러그인이 설치된 경우
<IfModule LiteSpeed>
# REST API 경로를 캐시에서 제외
SetEnv noabort 1
SetEnv no-gzip 1
</IfModule>
# END WordPress REST API Authorization Fix
'''
    
    return htaccess_code

def generate_wpconfig_fix():
    """wp-config.php 수정 코드 생성"""
    wpconfig_code = '''
// WordPress REST API Authorization 수정 (wp-config.php에 추가)
// 이 코드를 wp-config.php 파일의 "/* That's all, stop editing!" 라인 위에 추가하세요

// HTTP_AUTHORIZATION 헤더 강제 설정
if (!isset($_SERVER['HTTP_AUTHORIZATION'])) {
    if (isset($_SERVER['REDIRECT_HTTP_AUTHORIZATION'])) {
        $_SERVER['HTTP_AUTHORIZATION'] = $_SERVER['REDIRECT_HTTP_AUTHORIZATION'];
    } elseif (isset($_SERVER['PHP_AUTH_USER'])) {
        $basic_pass = isset($_SERVER['PHP_AUTH_PW']) ? $_SERVER['PHP_AUTH_PW'] : '';
        $_SERVER['HTTP_AUTHORIZATION'] = 'Basic ' . base64_encode($_SERVER['PHP_AUTH_USER'] . ':' . $basic_pass);
    } elseif (isset($_SERVER['PHP_AUTH_DIGEST'])) {
        $_SERVER['HTTP_AUTHORIZATION'] = $_SERVER['PHP_AUTH_DIGEST'];
    }
}

// Application Password 기능 강제 활성화
if (!defined('WP_APPLICATION_PASSWORDS')) {
    define('WP_APPLICATION_PASSWORDS', true);
}

// REST API 디버깅 활성화 (선택사항)
if (!defined('WP_DEBUG_LOG')) {
    define('WP_DEBUG_LOG', true);
}
'''
    
    return wpconfig_code

def generate_plugin_recommendations():
    """대안 플러그인 추천"""
    plugins = {
        "JSON Basic Authentication": {
            "url": "https://github.com/WP-API/Basic-Auth",
            "description": "WordPress REST API용 기본 인증 플러그인",
            "installation": "GitHub에서 다운로드 후 플러그인 폴더에 업로드"
        },
        "JWT Authentication for WP REST API": {
            "url": "https://wordpress.org/plugins/jwt-authentication-for-wp-rest-api/",
            "description": "JWT 토큰 기반 인증 플러그인",
            "installation": "WordPress 관리자 > 플러그인 > 새로 추가에서 설치"
        },
        "Application Passwords": {
            "url": "https://wordpress.org/plugins/application-passwords/",
            "description": "WordPress 5.6 이전 버전용 애플리케이션 패스워드 플러그인",
            "installation": "WordPress 관리자 > 플러그인 > 새로 추가에서 설치"
        }
    }
    
    return plugins

def create_solution_files():
    """해결책 파일들 생성"""
    print("=== WordPress 연결 문제 해결책 생성 ===")
    print(f"생성 시간: {datetime.now()}")
    print("\n" + "="*50 + "\n")
    
    # .htaccess 수정 파일 생성
    htaccess_fix = generate_htaccess_fix()
    with open("htaccess_fix_litespeed.txt", "w", encoding="utf-8") as f:
        f.write(htaccess_fix)
    print("✅ htaccess_fix_litespeed.txt 파일 생성 완료")
    
    # wp-config.php 수정 파일 생성
    wpconfig_fix = generate_wpconfig_fix()
    with open("wpconfig_fix_litespeed.txt", "w", encoding="utf-8") as f:
        f.write(wpconfig_fix)
    print("✅ wpconfig_fix_litespeed.txt 파일 생성 완료")
    
    # 종합 해결 가이드 생성
    guide_content = f'''
# WordPress LiteSpeed 서버 연결 문제 해결 가이드

생성 시간: {datetime.now()}
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
curl -X GET "https://innerspell.com/wp-json/wp/v2/users/me" \
     -H "Authorization: Basic YXBwbGU6QkdlYiB4UGs2IEs5QjggNWR2TSBNRFlsIEZuamE=" \
     -H "Content-Type: application/json"
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
'''
    
    with open("wordpress_litespeed_solution_guide.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    print("✅ wordpress_litespeed_solution_guide.md 파일 생성 완료")
    
    print("\n" + "="*50 + "\n")
    print("🎯 해결책 요약:")
    print("")
    print("1. ✅ WordPress REST API는 정상 작동 중")
    print("2. ❌ LiteSpeed 서버가 Authorization 헤더를 차단")
    print("3. 🔧 .htaccess 또는 wp-config.php 수정 필요")
    print("4. 🔌 대안으로 인증 플러그인 설치 가능")
    print("")
    print("📁 생성된 파일:")
    print("   - htaccess_fix_litespeed.txt")
    print("   - wpconfig_fix_litespeed.txt")
    print("   - wordpress_litespeed_solution_guide.md")
    print("")
    print("💡 다음 단계:")
    print("   1. 생성된 파일의 내용을 WordPress 서버에 적용")
    print("   2. AutoBlog AI Platform에서 연결 테스트 재실행")
    print("   3. 성공 시 자동 게시 기능 사용 가능")

if __name__ == "__main__":
    create_solution_files()