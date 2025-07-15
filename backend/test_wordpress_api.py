import requests
import base64
import json

# WordPress 사이트 정보
site_url = "https://innerspell.com"
username = "banana"
app_password = "CRJWYclhn9m6KNq1cveBRNnV"

# Basic Authentication 헤더 생성
credentials = f"{username}:{app_password}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json"
}

def test_api_connection():
    """REST API 연결 테스트"""
    print("1. REST API 활성화 확인...")
    response = requests.get(f"{site_url}/wp-json/")
    if response.status_code == 200:
        print("✅ REST API가 활성화되어 있습니다.")
    else:
        print("❌ REST API에 접근할 수 없습니다.")
        return False
    
    print("\n2. 인증 없이 게시물 목록 가져오기...")
    response = requests.get(f"{site_url}/wp-json/wp/v2/posts")
    print(f"상태 코드: {response.status_code}")
    
    print("\n3. Application Password로 인증하여 게시물 목록 가져오기...")
    response = requests.get(f"{site_url}/wp-json/wp/v2/posts", headers=headers)
    print(f"상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 인증 성공!")
        posts = response.json()
        print(f"게시물 수: {len(posts)}")
    else:
        print("❌ 인증 실패")
        print(f"응답: {response.text}")
    
    return response.status_code == 200

def create_test_post():
    """테스트 게시물 생성"""
    post_data = {
        "title": "REST API 테스트 게시물",
        "content": "Application Password를 사용한 테스트 게시물입니다.",
        "status": "draft"
    }
    
    print("\n4. 테스트 게시물 생성 시도...")
    response = requests.post(
        f"{site_url}/wp-json/wp/v2/posts",
        headers=headers,
        data=json.dumps(post_data)
    )
    
    if response.status_code == 201:
        print("✅ 게시물 생성 성공!")
        post = response.json()
        print(f"게시물 ID: {post['id']}")
        print(f"게시물 URL: {post['link']}")
    else:
        print("❌ 게시물 생성 실패")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {response.text}")

if __name__ == "__main__":
    print("WordPress REST API 인증 테스트")
    print("=" * 50)
    
    if test_api_connection():
        create_test_post()
    else:
        print("\n⚠️  먼저 API 연결 문제를 해결해야 합니다.")
        print("\n해결 방법:")
        print("1. .htaccess 파일에 Authorization 헤더 설정 추가")
        print("2. 보안 플러그인 일시 비활성화")
        print("3. Application Password 재생성 (/wp-admin/profile.php에서)")