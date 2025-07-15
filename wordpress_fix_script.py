#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress LiteSpeed Authorization 헤더 문제 해결 스크립트

이 스크립트는 LiteSpeed 서버에서 Authorization 헤더가 차단되는 문제를 해결합니다.
- .htaccess 파일에 Authorization 헤더 전달 규칙 추가
- wp-config.php 파일에 Authorization 헤더 처리 코드 추가
"""

import requests
import base64
import json
from datetime import datetime

def test_wordpress_connection(site_url, username, password):
    """
    WordPress REST API 연결 테스트
    """
    print(f"\n🔍 WordPress 연결 테스트 시작...")
    print(f"사이트: {site_url}")
    print(f"사용자: {username}")
    
    # Basic Auth 헤더 생성
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'User-Agent': 'BlogAuto/1.0',
        'Content-Type': 'application/json'
    }
    
    # REST API 엔드포인트 테스트
    test_url = f"{site_url}/wp-json/wp/v2/users/me"
    
    try:
        print(f"\n📡 요청 URL: {test_url}")
        print(f"📋 Authorization 헤더: Basic {encoded_credentials[:20]}...")
        
        response = requests.get(test_url, headers=headers, timeout=30)
        
        print(f"\n📊 응답 상태 코드: {response.status_code}")
        print(f"📄 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"\n✅ 연결 성공!")
            print(f"👤 사용자 정보:")
            print(f"   - ID: {user_data.get('id')}")
            print(f"   - 이름: {user_data.get('name')}")
            print(f"   - 이메일: {user_data.get('email')}")
            print(f"   - 역할: {user_data.get('roles')}")
            return True, user_data
        else:
            print(f"\n❌ 연결 실패!")
            print(f"오류 내용: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"\n💥 연결 오류: {str(e)}")
        return False, str(e)

def test_categories_and_tags(site_url, username, password):
    """
    카테고리와 태그 API 테스트
    """
    print(f"\n🏷️ 카테고리 및 태그 테스트...")
    
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'User-Agent': 'BlogAuto/1.0'
    }
    
    # 카테고리 테스트
    try:
        categories_url = f"{site_url}/wp-json/wp/v2/categories"
        response = requests.get(categories_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ 카테고리 로드 성공: {len(categories)}개")
            for cat in categories[:3]:  # 처음 3개만 표시
                print(f"   - {cat.get('name')} (ID: {cat.get('id')})")
        else:
            print(f"❌ 카테고리 로드 실패: {response.status_code}")
            
    except Exception as e:
        print(f"💥 카테고리 테스트 오류: {str(e)}")
    
    # 태그 테스트
    try:
        tags_url = f"{site_url}/wp-json/wp/v2/tags"
        response = requests.get(tags_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            tags = response.json()
            print(f"✅ 태그 로드 성공: {len(tags)}개")
            for tag in tags[:3]:  # 처음 3개만 표시
                print(f"   - {tag.get('name')} (ID: {tag.get('id')})")
        else:
            print(f"❌ 태그 로드 실패: {response.status_code}")
            
    except Exception as e:
        print(f"💥 태그 테스트 오류: {str(e)}")

def generate_htaccess_fix():
    """
    .htaccess 파일 수정 내용 생성
    """
    htaccess_content = """
# BEGIN WordPress Authorization Fix
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
# END WordPress Authorization Fix

"""
    return htaccess_content

def generate_wpconfig_fix():
    """
    wp-config.php 파일 수정 내용 생성
    """
    wpconfig_content = """
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
"""
    return wpconfig_content

def main():
    """
    메인 실행 함수
    """
    print("🚀 WordPress LiteSpeed 문제 해결 및 테스트 시작")
    print("=" * 60)
    
    # 테스트 설정
    site_url = "https://innerspell.com"
    username = "apple"
    password = "BGeb xPk6 K9B8 5dvM MDYl Fnja"
    
    # 1. 현재 상태 테스트
    print("\n📋 1단계: 현재 연결 상태 확인")
    success, result = test_wordpress_connection(site_url, username, password)
    
    if success:
        print("\n🎉 WordPress 연결이 이미 정상 작동합니다!")
        test_categories_and_tags(site_url, username, password)
        return
    
    # 2. 해결 방안 제시
    print("\n🛠️ 2단계: 해결 방안 생성")
    
    print("\n📝 .htaccess 파일에 추가할 내용:")
    print("-" * 40)
    htaccess_fix = generate_htaccess_fix()
    print(htaccess_fix)
    
    print("\n📝 wp-config.php 파일에 추가할 내용:")
    print("-" * 40)
    wpconfig_fix = generate_wpconfig_fix()
    print(wpconfig_fix)
    
    # 3. 해결 방안 파일로 저장
    print("\n💾 3단계: 해결 방안 파일 저장")
    
    with open('htaccess_fix.txt', 'w', encoding='utf-8') as f:
        f.write(htaccess_fix)
    print("✅ htaccess_fix.txt 파일 생성 완료")
    
    with open('wpconfig_fix.txt', 'w', encoding='utf-8') as f:
        f.write(wpconfig_fix)
    print("✅ wpconfig_fix.txt 파일 생성 완료")
    
    # 4. 수동 적용 안내
    print("\n📋 4단계: 수동 적용 안내")
    print("""
🔧 다음 단계를 수행하세요:

1. WordPress 사이트 (https://innerspell.com)에 FTP/cPanel로 접속
2. 루트 디렉토리의 .htaccess 파일을 열어서 맨 위에 htaccess_fix.txt 내용 추가
3. wp-config.php 파일을 열어서 '/* That's all, stop editing! */' 줄 위에 wpconfig_fix.txt 내용 추가
4. 파일 저장 후 브라우저 캐시 삭제
5. 이 스크립트를 다시 실행하여 연결 테스트

⚠️ 주의사항:
- 파일 수정 전 반드시 백업 생성
- LiteSpeed 서버는 재시작이 필요할 수 있음
- 보안 플러그인이 REST API를 차단하지 않는지 확인
    """)
    
    # 5. 대안 플러그인 안내
    print("\n🔌 5단계: 대안 플러그인 안내")
    print("""
위 방법이 작동하지 않을 경우 다음 플러그인 중 하나를 설치하세요:

1. "JSON Basic Authentication" by WP REST API Team
   - WordPress 관리자 → 플러그인 → 새로 추가 → 검색 → 설치 및 활성화

2. "JWT Authentication for WP REST API"
   - 설치 후 wp-config.php에 비밀 키 추가 필요
   - define('JWT_AUTH_SECRET_KEY', 'your-secret-key');
    """)
    
    print("\n✅ WordPress 문제 해결 가이드 생성 완료!")
    print("📁 생성된 파일: htaccess_fix.txt, wpconfig_fix.txt")

if __name__ == "__main__":
    main()