#!/usr/bin/env python3
"""
AutoBlog AI Platform WordPress 연결 테스트 API 호출
새로 추가한 WordPress 연결 테스트 엔드포인트를 테스트합니다.
"""

import asyncio
import httpx
import json
from datetime import datetime

# API 설정
API_BASE_URL = "http://localhost:8000"
WORDPRESS_TEST_ENDPOINT = "/publish/test/wordpress"

# WordPress 자격 증명
WORDPRESS_CREDENTIALS = {
    "site_url": "https://innerspell.com",
    "username": "apple",
    "password": "BGeb xPk6 K9B8 5dvM MDYl Fnja"
}

# 테스트용 사용자 자격 증명 (이메일 기반 로그인)
TEST_USER = {
    "email": "test@example.com",
    "password": "Test1234!"
}

async def register_test_user():
    """테스트 사용자 등록"""
    async with httpx.AsyncClient() as client:
        register_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
            "full_name": "Test User"
        }
        
        register_response = await client.post(
            f"{API_BASE_URL}/api/v1/auth/register",
            json=register_data
        )
        
        if register_response.status_code == 201:
            print("✅ 테스트 사용자 등록 성공")
            return True
        elif register_response.status_code == 400:
            # 이미 존재하는 사용자일 수 있음
            result = register_response.json()
            if "already exists" in result.get("detail", "").lower():
                print("ℹ️ 테스트 사용자가 이미 존재합니다")
                return True
            else:
                print(f"❌ 사용자 등록 실패: {result.get('detail')}")
                return False
        else:
            print(f"❌ 사용자 등록 실패: {register_response.status_code} - {register_response.text}")
            return False

async def login_and_get_token():
    """로그인하여 JWT 토큰 획득"""
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            f"{API_BASE_URL}/api/v1/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        
        if login_response.status_code == 200:
            result = login_response.json()
            return result.get("token", {}).get("access_token")
        else:
            print(f"로그인 실패: {login_response.status_code} - {login_response.text}")
            return None

async def test_wordpress_connection_api():
    """WordPress 연결 테스트 API 호출"""
    print(f"=== AutoBlog AI Platform WordPress 연결 테스트 ===")
    print(f"API URL: {API_BASE_URL}")
    print(f"테스트 시간: {datetime.now()}")
    print("\n" + "="*50 + "\n")
    
    try:
        # 1. 테스트 사용자 등록 (필요시)
        print("1. 테스트 사용자 준비 중...")
        if not await register_test_user():
            print("❌ 테스트 사용자 준비 실패")
            return
        
        # 2. 로그인하여 토큰 획득
        print("\n2. 사용자 인증 중...")
        token = await login_and_get_token()
        
        if not token:
            print("❌ 사용자 인증 실패")
            return
        
        print(f"✅ 인증 성공 - 토큰: {token[:20]}...")
        
        # 3. WordPress 연결 테스트 API 호출
        print("\n3. WordPress 연결 테스트 API 호출 중...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{API_BASE_URL}/api/v1{WORDPRESS_TEST_ENDPOINT}",
                json=WORDPRESS_CREDENTIALS,
                headers=headers
            )
            
            print(f"   - API 응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ WordPress 연결 테스트 API 호출 성공!")
                print("\n📊 테스트 결과:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                if result.get("success"):
                    print("\n🎉 WordPress 연결 성공!")
                    user_info = result.get("user_info", {})
                    print(f"   - 사용자: {user_info.get('name')} ({user_info.get('username')})")
                    print(f"   - 역할: {user_info.get('roles', [])}")
                    print(f"   - 이메일: {user_info.get('email')}")
                    
                    permissions = result.get("permissions", {})
                    print(f"   - 포스트 읽기 권한: {'✅' if permissions.get('can_read_posts') else '❌'}")
                    print(f"   - 인증 권한: {'✅' if permissions.get('can_authenticate') else '❌'}")
                    
                else:
                    print("\n❌ WordPress 연결 실패")
                    print(f"   - 오류: {result.get('error')}")
                    details = result.get("details", {})
                    if details:
                        print("   - 상세 정보:")
                        for key, value in details.items():
                            print(f"     {key}: {value}")
                            
            elif response.status_code == 401:
                print("❌ API 인증 실패 - 토큰이 유효하지 않습니다")
                
            elif response.status_code == 422:
                print("❌ 요청 데이터 오류")
                print(f"   - 응답: {response.text}")
                
            else:
                print(f"❌ API 호출 실패: {response.status_code}")
                print(f"   - 응답: {response.text}")
                
    except httpx.TimeoutException:
        print("❌ API 호출 시간 초과")
        
    except httpx.ConnectError:
        print("❌ API 서버에 연결할 수 없습니다")
        print("💡 백엔드 서버가 실행 중인지 확인해주세요")
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        print(f"💡 오류 타입: {type(e).__name__}")

async def test_api_health():
    """API 서버 상태 확인"""
    print("\n=== API 서버 상태 확인 ===")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Health check
            health_response = await client.get(f"{API_BASE_URL}/health")
            print(f"Health check: {health_response.status_code}")
            
            # API docs 확인
            docs_response = await client.get(f"{API_BASE_URL}/docs")
            print(f"API docs: {docs_response.status_code}")
            
            if health_response.status_code == 200 or docs_response.status_code == 200:
                print("✅ API 서버가 정상 작동 중입니다")
                return True
            else:
                print("❌ API 서버에 문제가 있습니다")
                return False
                
    except Exception as e:
        print(f"❌ API 서버 연결 실패: {str(e)}")
        return False

async def main():
    """메인 테스트 실행"""
    # API 서버 상태 확인
    if await test_api_health():
        # WordPress 연결 테스트
        await test_wordpress_connection_api()
    else:
        print("\n💡 해결 방법:")
        print("   1. 백엔드 서버가 실행 중인지 확인")
        print("   2. http://localhost:8000 에 접근 가능한지 확인")
        print("   3. 방화벽 설정 확인")

if __name__ == "__main__":
    asyncio.run(main())