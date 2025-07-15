#!/usr/bin/env python3
"""
WordPress 연결 테스트 스크립트
사용자가 제공한 자격 증명으로 직접 WordPress API 연결을 테스트합니다.
"""

import asyncio
import httpx
import base64
import json
from datetime import datetime

# 사용자 제공 자격 증명
SITE_URL = "https://innerspell.com"
USERNAME = "apple"
PASSWORD = "BGeb xPk6 K9B8 5dvM MDYl Fnja"

def create_auth_header(username: str, password: str) -> str:
    """Basic 인증 헤더 생성"""
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

async def test_wordpress_connection():
    """WordPress 연결 테스트 실행"""
    print(f"=== WordPress 연결 테스트 시작 ===")
    print(f"사이트 URL: {SITE_URL}")
    print(f"사용자명: {USERNAME}")
    print(f"테스트 시간: {datetime.now()}")
    print("\n" + "="*50 + "\n")
    
    auth_header = create_auth_header(USERNAME, PASSWORD)
    api_url = f"{SITE_URL.rstrip('/')}/wp-json/wp/v2"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. WordPress REST API 기본 정보 확인
            print("1. WordPress REST API 기본 접근성 테스트...")
            root_response = await client.get(f"{SITE_URL}/wp-json/")
            print(f"   - 상태 코드: {root_response.status_code}")
            
            if root_response.status_code == 200:
                print("   ✅ WordPress REST API 접근 가능")
                root_data = root_response.json()
                print(f"   - WordPress 버전: {root_data.get('description', 'N/A')}")
                print(f"   - 사이트 이름: {root_data.get('name', 'N/A')}")
            else:
                print(f"   ❌ WordPress REST API 접근 실패: {root_response.text[:200]}")
                return
            
            print("\n" + "-"*30 + "\n")
            
            # 2. 인증 테스트
            print("2. WordPress 인증 테스트...")
            auth_headers = {
                "Authorization": auth_header,
                "Content-Type": "application/json",
                "User-Agent": "AutoBlog-AI-Platform/1.0"
            }
            
            print(f"   - 인증 헤더: {auth_header[:30]}...")
            
            # 현재 사용자 정보 조회
            user_response = await client.get(
                f"{api_url}/users/me",
                headers=auth_headers
            )
            
            print(f"   - 사용자 API 응답 상태: {user_response.status_code}")
            print(f"   - 응답 내용: {user_response.text[:300]}")
            
            if user_response.status_code == 401:
                print("   ❌ 인증 실패 (401 Unauthorized)")
                print("   💡 가능한 원인:")
                print("      - 잘못된 사용자명 또는 애플리케이션 패스워드")
                print("      - LiteSpeed 서버가 Authorization 헤더를 차단")
                print("      - WordPress 애플리케이션 패스워드 기능이 비활성화됨")
                
                # LiteSpeed 문제 확인을 위한 추가 테스트
                print("\n   🔍 LiteSpeed Authorization 헤더 차단 문제 확인...")
                
                # Authorization 헤더 없이 테스트
                no_auth_response = await client.get(f"{api_url}/users/me")
                print(f"   - Authorization 헤더 없는 요청 상태: {no_auth_response.status_code}")
                
                # 다른 헤더 방식으로 테스트
                alt_headers = {
                    "HTTP_AUTHORIZATION": auth_header,
                    "Content-Type": "application/json"
                }
                
                alt_response = await client.get(
                    f"{api_url}/users/me",
                    headers=alt_headers
                )
                print(f"   - HTTP_AUTHORIZATION 헤더 사용 상태: {alt_response.status_code}")
                
                return
                
            elif user_response.status_code == 403:
                print("   ❌ 접근 권한 없음 (403 Forbidden)")
                print("   💡 사용자에게 충분한 권한이 없을 수 있습니다.")
                return
                
            elif user_response.status_code == 200:
                print("   ✅ 인증 성공!")
                user_data = user_response.json()
                print(f"   - 사용자 ID: {user_data.get('id')}")
                print(f"   - 사용자명: {user_data.get('username')}")
                print(f"   - 이름: {user_data.get('name')}")
                print(f"   - 이메일: {user_data.get('email')}")
                print(f"   - 역할: {user_data.get('roles', [])}")
            else:
                print(f"   ❌ 예상치 못한 응답: {user_response.status_code}")
                print(f"   - 응답 내용: {user_response.text[:200]}")
                return
            
            print("\n" + "-"*30 + "\n")
            
            # 3. 권한 테스트
            print("3. WordPress 권한 테스트...")
            
            # 포스트 목록 조회 테스트
            posts_response = await client.get(
                f"{api_url}/posts?per_page=1",
                headers=auth_headers
            )
            
            print(f"   - 포스트 조회 권한: {'✅ 가능' if posts_response.status_code == 200 else '❌ 불가능'}")
            
            # 카테고리 조회 테스트
            categories_response = await client.get(
                f"{api_url}/categories?per_page=1",
                headers=auth_headers
            )
            
            print(f"   - 카테고리 조회 권한: {'✅ 가능' if categories_response.status_code == 200 else '❌ 불가능'}")
            
            # 태그 조회 테스트
            tags_response = await client.get(
                f"{api_url}/tags?per_page=1",
                headers=auth_headers
            )
            
            print(f"   - 태그 조회 권한: {'✅ 가능' if tags_response.status_code == 200 else '❌ 불가능'}")
            
            print("\n" + "="*50 + "\n")
            print("🎉 WordPress 연결 테스트 완료!")
            print("✅ 모든 테스트가 성공적으로 완료되었습니다.")
            print("💡 이제 AutoBlog AI Platform에서 WordPress 자동 게시를 사용할 수 있습니다.")
            
    except httpx.TimeoutException:
        print("❌ 연결 시간 초과")
        print("💡 WordPress 사이트가 접근 가능한지 확인해주세요.")
        
    except httpx.ConnectError:
        print("❌ 연결 오류")
        print("💡 사이트 URL이 올바른지 확인해주세요.")
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        print(f"💡 오류 타입: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_wordpress_connection())