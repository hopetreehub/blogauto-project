"""
WordPress JWT Authentication 모듈
Basic Auth가 작동하지 않을 때 대안으로 사용
"""

import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class WordPressJWTAuth:
    def __init__(self, site_url: str):
        self.site_url = site_url.rstrip('/')
        self.token = None
        self.token_expiry = None
        
    def login(self, username: str, password: str) -> dict:
        """JWT 토큰 획득"""
        try:
            # JWT 인증 엔드포인트 (JWT Authentication for WP REST API 플러그인 필요)
            login_url = urljoin(self.site_url, '/wp-json/jwt-auth/v1/token')
            
            data = {
                'username': username,
                'password': password
            }
            
            response = requests.post(login_url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get('token')
                # 토큰은 보통 1주일 유효
                self.token_expiry = datetime.now() + timedelta(days=7)
                
                return {
                    'success': True,
                    'token': self.token,
                    'user_email': result.get('user_email'),
                    'user_display_name': result.get('user_display_name'),
                    'message': 'JWT 인증 성공'
                }
            else:
                return {
                    'success': False,
                    'error': 'JWT 인증 실패',
                    'details': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'JWT 로그인 오류: {str(e)}',
                'suggestion': 'JWT Authentication for WP REST API 플러그인이 설치되어 있는지 확인하세요.'
            }
    
    def get_headers(self) -> dict:
        """JWT 인증 헤더 반환"""
        if not self.token:
            raise ValueError("토큰이 없습니다. 먼저 login()을 호출하세요.")
            
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def test_auth(self) -> dict:
        """JWT 인증 테스트"""
        try:
            if not self.token:
                return {
                    'success': False,
                    'error': '토큰이 없습니다.'
                }
                
            headers = self.get_headers()
            test_url = urljoin(self.site_url, '/wp-json/wp/v2/users/me')
            
            response = requests.get(test_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user': user_data.get('name'),
                    'id': user_data.get('id'),
                    'message': 'JWT 인증 테스트 성공'
                }
            else:
                return {
                    'success': False,
                    'error': f'인증 실패: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'JWT 테스트 오류: {str(e)}'
            }
    
    def create_post(self, title: str, content: str, status: str = 'draft') -> dict:
        """JWT를 사용하여 포스트 생성"""
        try:
            headers = self.get_headers()
            post_url = urljoin(self.site_url, '/wp-json/wp/v2/posts')
            
            data = {
                'title': title,
                'content': content,
                'status': status
            }
            
            response = requests.post(post_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 201:
                post_data = response.json()
                return {
                    'success': True,
                    'post_id': post_data.get('id'),
                    'post_url': post_data.get('link'),
                    'message': 'JWT를 통한 포스트 생성 성공'
                }
            else:
                return {
                    'success': False,
                    'error': f'포스트 생성 실패: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'포스트 생성 오류: {str(e)}'
            }


def test_jwt_auth(site_url: str, username: str, password: str):
    """JWT 인증 테스트 헬퍼 함수"""
    jwt_auth = WordPressJWTAuth(site_url)
    
    # 1. 로그인 시도
    login_result = jwt_auth.login(username, password)
    print("JWT 로그인 결과:", json.dumps(login_result, indent=2, ensure_ascii=False))
    
    if login_result['success']:
        # 2. 인증 테스트
        test_result = jwt_auth.test_auth()
        print("\nJWT 인증 테스트:", json.dumps(test_result, indent=2, ensure_ascii=False))
        
        # 3. 포스트 생성 테스트
        post_result = jwt_auth.create_post(
            title="JWT 테스트 포스트",
            content="JWT 인증을 통한 테스트 포스트입니다.",
            status="draft"
        )
        print("\n포스트 생성 테스트:", json.dumps(post_result, indent=2, ensure_ascii=False))
    
    return login_result


if __name__ == "__main__":
    # 테스트 실행
    site_url = "https://innerspell.com"
    username = "banana"
    password = "CRJWYclhn9m6KNq1cveBRNnV"
    
    test_jwt_auth(site_url, username, password)