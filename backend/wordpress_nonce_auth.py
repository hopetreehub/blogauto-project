"""
WordPress Nonce Authentication 모듈
쿠키와 Nonce를 사용한 인증 (웹 검색 결과 기반)
"""

import requests
from urllib.parse import urljoin
import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WordPressNonceAuth:
    def __init__(self, site_url: str):
        self.site_url = site_url.rstrip('/')
        self.session = requests.Session()
        self.nonce = None
        self.logged_in = False
        
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """WordPress 로그인 후 Nonce 획득"""
        try:
            # 1. 로그인 페이지에서 쿠키 설정
            login_page_url = urljoin(self.site_url, '/wp-login.php')
            login_response = self.session.get(login_page_url)
            
            # 2. 로그인 수행
            login_data = {
                'log': username,
                'pwd': password,
                'wp-submit': 'Log In',
                'testcookie': '1',
                'redirect_to': urljoin(self.site_url, '/wp-admin/')
            }
            
            post_response = self.session.post(
                login_page_url,
                data=login_data,
                allow_redirects=True
            )
            
            # 3. 로그인 성공 확인
            if 'wordpress_logged_in' in self.session.cookies:
                self.logged_in = True
                
                # 4. Nonce 획득 시도
                self.nonce = self._get_nonce()
                
                return {
                    'success': True,
                    'message': '로그인 성공',
                    'nonce': self.nonce,
                    'cookies': {k: v for k, v in self.session.cookies.items()}
                }
            else:
                return {
                    'success': False,
                    'error': '로그인 실패 - 쿠키가 설정되지 않음'
                }
                
        except Exception as e:
            logger.error(f"로그인 오류: {str(e)}")
            return {
                'success': False,
                'error': f'로그인 오류: {str(e)}'
            }
    
    def _get_nonce(self) -> str:
        """WordPress nonce 획득"""
        try:
            # 여러 방법으로 nonce 획득 시도
            
            # 방법 1: 관리자 페이지에서 추출
            admin_url = urljoin(self.site_url, '/wp-admin/')
            admin_response = self.session.get(admin_url)
            
            # wpApiSettings에서 nonce 찾기
            nonce_match = re.search(r'wpApiSettings.*?"nonce":"([^"]+)"', admin_response.text)
            if nonce_match:
                return nonce_match.group(1)
            
            # 방법 2: REST API nonce 찾기
            nonce_match = re.search(r'"rest_nonce":"([^"]+)"', admin_response.text)
            if nonce_match:
                return nonce_match.group(1)
            
            # 방법 3: 직접 nonce 생성 요청
            nonce_url = urljoin(self.site_url, '/wp-admin/admin-ajax.php')
            nonce_data = {
                'action': 'rest-nonce'
            }
            nonce_response = self.session.post(nonce_url, data=nonce_data)
            if nonce_response.text:
                return nonce_response.text.strip()
                
            return None
            
        except Exception as e:
            logger.error(f"Nonce 획득 실패: {str(e)}")
            return None
    
    def test_api_with_nonce(self) -> Dict[str, Any]:
        """Nonce를 사용한 API 테스트"""
        try:
            if not self.logged_in:
                return {
                    'success': False,
                    'error': '로그인되지 않았습니다'
                }
            
            headers = {
                'X-WP-Nonce': self.nonce,
                'Content-Type': 'application/json'
            } if self.nonce else {}
            
            # REST API 테스트
            api_url = urljoin(self.site_url, '/wp-json/wp/v2/users/me')
            response = self.session.get(api_url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user': user_data.get('name'),
                    'id': user_data.get('id'),
                    'message': 'Nonce 인증 성공'
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'API 테스트 오류: {str(e)}'
            }
    
    def create_post_with_nonce(self, title: str, content: str, status: str = 'draft') -> Dict[str, Any]:
        """Nonce를 사용하여 포스트 생성"""
        try:
            if not self.logged_in:
                return {
                    'success': False,
                    'error': '로그인되지 않았습니다'
                }
            
            headers = {
                'X-WP-Nonce': self.nonce,
                'Content-Type': 'application/json'
            } if self.nonce else {'Content-Type': 'application/json'}
            
            post_data = {
                'title': title,
                'content': content,
                'status': status
            }
            
            post_url = urljoin(self.site_url, '/wp-json/wp/v2/posts')
            response = self.session.post(post_url, json=post_data, headers=headers)
            
            if response.status_code == 201:
                post_info = response.json()
                return {
                    'success': True,
                    'post_id': post_info.get('id'),
                    'post_url': post_info.get('link'),
                    'message': 'Nonce를 통한 포스트 생성 성공'
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'포스트 생성 오류: {str(e)}'
            }


def test_nonce_auth(site_url: str, username: str, password: str):
    """Nonce 인증 테스트"""
    print("=== WordPress Nonce 인증 테스트 ===")
    
    auth = WordPressNonceAuth(site_url)
    
    # 1. 로그인
    login_result = auth.login(username, password)
    print(f"\n로그인 결과: {json.dumps(login_result, indent=2, ensure_ascii=False)}")
    
    if login_result['success']:
        # 2. API 테스트
        api_result = auth.test_api_with_nonce()
        print(f"\nAPI 테스트 결과: {json.dumps(api_result, indent=2, ensure_ascii=False)}")
        
        if api_result['success']:
            # 3. 포스트 생성 테스트
            post_result = auth.create_post_with_nonce(
                title="Nonce 인증 테스트 포스트",
                content="Nonce와 쿠키를 사용한 인증 테스트입니다.",
                status="draft"
            )
            print(f"\n포스트 생성 결과: {json.dumps(post_result, indent=2, ensure_ascii=False)}")
    
    return login_result


if __name__ == "__main__":
    site_url = "https://innerspell.com"
    username = "banana"
    password = "CRJWYclhn9m6KNq1cveBRNnV"
    
    test_nonce_auth(site_url, username, password)