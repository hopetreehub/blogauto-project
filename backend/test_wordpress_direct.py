#!/usr/bin/env python3
"""
WordPress REST API 직접 테스트 - LiteSpeed 서버 대응
"""

import requests
import base64
import json
from urllib.parse import urljoin

# 테스트 정보
SITE_URL = "https://innerspell.com"
USERNAME = "banana"
PASSWORD = "CRJWYclhn9m6KNq1cveBRNnV"

def test_with_different_headers():
    """다양한 헤더 조합으로 테스트"""
    
    # Basic Auth 준비
    auth_string = f"{USERNAME}:{PASSWORD}"
    auth_b64 = base64.b64encode(auth_string.encode()).decode('ascii')
    
    # 테스트할 헤더 조합들
    header_combinations = [
        {
            "name": "표준 Authorization 헤더",
            "headers": {
                'Authorization': f'Basic {auth_b64}',
                'User-Agent': 'BlogAuto/1.0'
            }
        },
        {
            "name": "PHP-CGI 우회 헤더",
            "headers": {
                'HTTP_AUTHORIZATION': f'Basic {auth_b64}',
                'User-Agent': 'BlogAuto/1.0'
            }
        },
        {
            "name": "X-Authorization 헤더",
            "headers": {
                'X-Authorization': f'Basic {auth_b64}',
                'User-Agent': 'BlogAuto/1.0'
            }
        },
        {
            "name": "REDIRECT_HTTP_AUTHORIZATION",
            "headers": {
                'REDIRECT_HTTP_AUTHORIZATION': f'Basic {auth_b64}',
                'User-Agent': 'BlogAuto/1.0'
            }
        }
    ]
    
    # 각 헤더 조합으로 테스트
    for combo in header_combinations:
        print(f"\n=== {combo['name']} 테스트 ===")
        
        try:
            url = urljoin(SITE_URL, '/wp-json/wp/v2/users/me')
            response = requests.get(url, headers=combo['headers'], timeout=10)
            
            print(f"상태 코드: {response.status_code}")
            print(f"응답 헤더: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 성공! 사용자: {data.get('name')}")
                return True
            else:
                print(f"❌ 실패: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 오류: {str(e)}")
    
    return False

def test_with_url_auth():
    """URL에 인증 정보 포함하여 테스트"""
    print("\n=== URL 인증 테스트 ===")
    
    try:
        # URL에 인증 정보 포함
        auth_url = f"https://{USERNAME}:{PASSWORD}@innerspell.com/wp-json/wp/v2/users/me"
        response = requests.get(auth_url, timeout=10)
        
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공! 사용자: {data.get('name')}")
            return True
        else:
            print(f"❌ 실패: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
    
    return False

def test_with_query_params():
    """쿼리 파라미터로 인증 테스트"""
    print("\n=== 쿼리 파라미터 인증 테스트 ===")
    
    try:
        # 쿼리 파라미터로 인증 정보 전달
        url = urljoin(SITE_URL, '/wp-json/wp/v2/users/me')
        params = {
            'username': USERNAME,
            'password': PASSWORD,
            '_envelope': '1'  # 일부 플러그인에서 사용
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공! 응답: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}")
            return True
        else:
            print(f"❌ 실패: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
    
    return False

def check_api_availability():
    """REST API 기본 접근성 확인"""
    print("=== REST API 접근성 확인 ===")
    
    endpoints = [
        '/wp-json',
        '/wp-json/wp/v2',
        '/?rest_route=/',
        '/index.php/wp-json/wp/v2'
    ]
    
    for endpoint in endpoints:
        try:
            url = urljoin(SITE_URL, endpoint)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - 접근 가능")
                
                # Application Password 지원 확인
                if 'authentication' in response.text.lower():
                    data = response.json()
                    auth_methods = data.get('authentication', {})
                    print(f"   지원되는 인증 방법: {list(auth_methods.keys()) if isinstance(auth_methods, dict) else 'N/A'}")
            else:
                print(f"❌ {endpoint} - 상태 코드: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - 오류: {str(e)}")

if __name__ == "__main__":
    print("WordPress REST API 테스트 시작")
    print(f"사이트: {SITE_URL}")
    print(f"사용자: {USERNAME}")
    print(f"비밀번호 길이: {len(PASSWORD)}자")
    print("=" * 50)
    
    # 1. API 접근성 확인
    check_api_availability()
    
    # 2. 다양한 헤더로 테스트
    if not test_with_different_headers():
        print("\n모든 헤더 테스트 실패")
        
        # 3. URL 인증 테스트
        if not test_with_url_auth():
            print("\nURL 인증도 실패")
            
            # 4. 쿼리 파라미터 테스트
            if not test_with_query_params():
                print("\n쿼리 파라미터 인증도 실패")
                
                print("\n💡 해결 방법:")
                print("1. WordPress 관리자에서 .htaccess 파일 수정")
                print("2. LiteSpeed Cache 플러그인 설정 확인")
                print("3. Application Password 플러그인 설치 필요할 수 있음")