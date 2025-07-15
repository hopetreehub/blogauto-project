#!/usr/bin/env python3
"""
WordPress 인증 방법 다중 테스트
추정 금지 - 여러 인증 방법을 직접 시도
"""

import requests
import base64
import json
from datetime import datetime

class WordPressAuthTester:
    def __init__(self):
        self.site_url = "https://innerspell.com"
        self.username = "banana"
        self.password = "Hjhv Pp7n L4RC Op8N fqQg A9SO"
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        
    def test_method_1_basic_auth(self):
        """Method 1: Basic Authentication 테스트"""
        print("🔍 Method 1: Basic Authentication 테스트...")
        
        try:
            credentials = f"{self.username}:{self.password}"
            token = base64.b64encode(credentials.encode()).decode('utf-8')
            headers = {
                'Authorization': f'Basic {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_base}/users/me",
                headers=headers,
                timeout=30
            )
            
            print(f"   응답 코드: {response.status_code}")
            print(f"   응답 헤더: {dict(response.headers)}")
            print(f"   응답 내용: {response.text[:200]}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"   오류: {str(e)}")
            return False
    
    def test_method_2_application_password(self):
        """Method 2: Application Password 테스트"""
        print("\\n🔍 Method 2: Application Password 테스트...")
        
        try:
            # 응용 프로그램 비밀번호는 다른 형식일 수 있음
            # 공백 제거된 버전 시도
            clean_password = self.password.replace(" ", "")
            
            credentials = f"{self.username}:{clean_password}"
            token = base64.b64encode(credentials.encode()).decode('utf-8')
            headers = {
                'Authorization': f'Basic {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.api_base}/users/me",
                headers=headers,
                timeout=30
            )
            
            print(f"   응답 코드: {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"   오류: {str(e)}")
            return False
    
    def test_method_3_posts_anonymous(self):
        """Method 3: 익명 포스트 조회 테스트"""
        print("\\n🔍 Method 3: 익명 포스트 조회 테스트...")
        
        try:
            response = requests.get(
                f"{self.api_base}/posts",
                timeout=30
            )
            
            print(f"   응답 코드: {response.status_code}")
            if response.status_code == 200:
                posts = response.json()
                print(f"   포스트 수: {len(posts)}")
                if posts:
                    print(f"   첫 번째 포스트 제목: {posts[0].get('title', {}).get('rendered', 'N/A')}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"   오류: {str(e)}")
            return False
    
    def test_method_4_categories_anonymous(self):
        """Method 4: 익명 카테고리 조회 테스트"""
        print("\\n🔍 Method 4: 익명 카테고리 조회 테스트...")
        
        try:
            response = requests.get(
                f"{self.api_base}/categories",
                timeout=30
            )
            
            print(f"   응답 코드: {response.status_code}")
            if response.status_code == 200:
                categories = response.json()
                print(f"   카테고리 수: {len(categories)}")
                for cat in categories[:3]:
                    print(f"   - {cat.get('name', 'N/A')} (ID: {cat.get('id', 'N/A')})")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"   오류: {str(e)}")
            return False
    
    def test_method_5_direct_login(self):
        """Method 5: WordPress 로그인 페이지 접근 테스트"""
        print("\\n🔍 Method 5: WordPress 로그인 페이지 접근 테스트...")
        
        try:
            # wp-login.php 페이지 확인
            response = requests.get(
                f"{self.site_url}/wp-login.php",
                timeout=30
            )
            
            print(f"   wp-login.php 응답 코드: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                print(f"   페이지에 로그인 폼 포함: {'form' in content.lower()}")
                print(f"   WordPress 로그인 페이지: {'wp-login' in content}")
            
            # wp-admin 페이지 확인  
            response2 = requests.get(
                f"{self.site_url}/wp-admin/",
                timeout=30
            )
            
            print(f"   wp-admin 응답 코드: {response2.status_code}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"   오류: {str(e)}")
            return False
    
    def test_method_6_alternative_format(self):
        """Method 6: 대안 비밀번호 형식 테스트"""
        print("\\n🔍 Method 6: 대안 비밀번호 형식 테스트...")
        
        # 가능한 비밀번호 형식들
        password_variants = [
            "HjhvPp7nL4RCOp8NfqQgA9SO",  # 공백 제거
            "Hjhv_Pp7n_L4RC_Op8N_fqQg_A9SO",  # 언더스코어로 대체
            "Hjhv-Pp7n-L4RC-Op8N-fqQg-A9SO",  # 하이픈으로 대체
            self.password,  # 원본
        ]
        
        for i, pwd in enumerate(password_variants):
            print(f"\\n   시도 {i+1}: {pwd}")
            
            try:
                credentials = f"{self.username}:{pwd}"
                token = base64.b64encode(credentials.encode()).decode('utf-8')
                headers = {
                    'Authorization': f'Basic {token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(
                    f"{self.api_base}/users/me",
                    headers=headers,
                    timeout=30
                )
                
                print(f"      응답 코드: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"      ✅ 성공! 올바른 비밀번호: {pwd}")
                    return True
                elif response.status_code == 401:
                    print(f"      ❌ 인증 실패")
                else:
                    print(f"      ⚠️ 기타 응답: {response.text[:100]}")
                    
            except Exception as e:
                print(f"      💥 오류: {str(e)}")
        
        return False
    
    def test_method_7_post_creation_test(self):
        """Method 7: 포스트 생성 권한 테스트 (인증 없이)"""
        print("\\n🔍 Method 7: 포스트 생성 권한 테스트...")
        
        try:
            # 인증 없이 포스트 생성 시도 (당연히 실패할 것이지만 서버 응답 확인)
            post_data = {
                "title": "테스트 포스트",
                "content": "이것은 테스트입니다.",
                "status": "draft"
            }
            
            response = requests.post(
                f"{self.api_base}/posts",
                json=post_data,
                timeout=30
            )
            
            print(f"   응답 코드: {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}")
            
            # 401이나 403이 정상적인 응답
            return response.status_code in [401, 403]
            
        except Exception as e:
            print(f"   오류: {str(e)}")
            return False

def main():
    print("🎯 WordPress 인증 방법 다중 테스트")
    print("⚠️ innerspell.com 사이트에 대한 다양한 인증 방법 시도")
    print("=" * 70)
    
    tester = WordPressAuthTester()
    results = {}
    
    # 모든 테스트 방법 실행
    results["basic_auth"] = tester.test_method_1_basic_auth()
    results["app_password"] = tester.test_method_2_application_password()
    results["anonymous_posts"] = tester.test_method_3_posts_anonymous()
    results["anonymous_categories"] = tester.test_method_4_categories_anonymous()
    results["login_page"] = tester.test_method_5_direct_login()
    results["alternative_format"] = tester.test_method_6_alternative_format()
    results["post_creation"] = tester.test_method_7_post_creation_test()
    
    # 결과 요약
    print("\\n" + "=" * 70)
    print("📊 테스트 결과 요약")
    print("=" * 70)
    
    for method, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{method}: {status}")
    
    # 성공한 방법들
    successful_methods = [method for method, success in results.items() if success]
    
    if successful_methods:
        print(f"\\n🎉 성공한 방법들: {', '.join(successful_methods)}")
        
        if "alternative_format" in successful_methods:
            print("\\n💡 대안 비밀번호 형식이 성공했습니다!")
            print("   이 형식을 사용하여 실제 포스트 발행을 시도할 수 있습니다.")
        elif "anonymous_posts" in successful_methods or "anonymous_categories" in successful_methods:
            print("\\n💡 익명 접근은 가능하지만 포스트 발행에는 인증이 필요합니다.")
            print("   WordPress 관리자에서 Application Password를 다시 확인해주세요.")
    else:
        print("\\n❌ 모든 인증 방법이 실패했습니다.")
        print("\\n💡 다음 사항을 확인해주세요:")
        print("   1. 사용자명 'banana'가 정확한지 확인")
        print("   2. Application Password가 올바르게 생성되었는지 확인")
        print("   3. WordPress REST API가 활성화되어 있는지 확인")
        print("   4. 보안 플러그인이 API 접근을 차단하고 있는지 확인")
    
    # 결과를 파일로 저장
    with open("wordpress_auth_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "site": "innerspell.com",
            "username": "banana", 
            "results": results,
            "successful_methods": successful_methods
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\\n📄 테스트 결과가 wordpress_auth_test_results.json에 저장되었습니다.")

if __name__ == "__main__":
    main()