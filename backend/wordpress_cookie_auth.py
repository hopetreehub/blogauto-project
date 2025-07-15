"""
WordPress Cookie Authentication 모듈
Basic Auth가 작동하지 않을 때 쿠키 기반 인증 사용
"""

import requests
from urllib.parse import urljoin, urlparse
import re
import logging

logger = logging.getLogger(__name__)

class WordPressCookieAuth:
    def __init__(self, site_url: str):
        self.site_url = site_url.rstrip('/')
        self.session = requests.Session()
        self.logged_in = False
        self.nonce = None
        
    def login(self, username: str, password: str) -> dict:
        """WordPress 로그인 페이지를 통한 인증"""
        try:
            # 1. 로그인 페이지 접속하여 nonce 획득
            login_page_url = urljoin(self.site_url, '/wp-login.php')
            response = self.session.get(login_page_url)
            
            # 로그인 폼에서 추가 필드 추출
            redirect_to = re.search(r'name="redirect_to" value="([^"]*)"', response.text)
            redirect_value = redirect_to.group(1) if redirect_to else ''
            
            # 2. 로그인 시도
            login_data = {
                'log': username,
                'pwd': password,
                'wp-submit': 'Log In',
                'redirect_to': redirect_value,
                'testcookie': '1'
            }
            
            login_response = self.session.post(
                login_page_url,
                data=login_data,
                allow_redirects=False
            )
            
            # 3. 로그인 성공 여부 확인
            if login_response.status_code in [302, 303] and 'wordpress_logged_in' in self.session.cookies:
                self.logged_in = True
                
                # 4. REST API nonce 획득
                self.nonce = self._get_rest_nonce()
                
                return {
                    'success': True,
                    'message': '쿠키 기반 로그인 성공',
                    'cookies': dict(self.session.cookies),
                    'nonce': self.nonce
                }
            else:
                return {
                    'success': False,
                    'error': '로그인 실패',
                    'status_code': login_response.status_code,
                    'suggestion': '사용자명과 비밀번호를 확인하세요.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'로그인 오류: {str(e)}'
            }
    
    def _get_rest_nonce(self) -> str:
        """REST API nonce 획득"""
        try:
            # 관리자 페이지에서 nonce 추출
            admin_url = urljoin(self.site_url, '/wp-admin/')
            response = self.session.get(admin_url)
            
            # REST nonce 패턴 찾기
            nonce_match = re.search(r'wp\.apiFetch\.use.*?"X-WP-Nonce":"([^"]+)"', response.text)
            if not nonce_match:
                nonce_match = re.search(r'"rest_nonce":"([^"]+)"', response.text)
            
            if nonce_match:
                return nonce_match.group(1)
            
            # 대안: API 엔드포인트에서 nonce 헤더 확인
            api_response = self.session.get(urljoin(self.site_url, '/wp-json/'))
            nonce_header = api_response.headers.get('X-WP-Nonce')
            if nonce_header:
                return nonce_header
                
            return None
            
        except Exception as e:
            logger.error(f"Nonce 획득 실패: {str(e)}")
            return None
    
    def test_auth(self) -> dict:
        """쿠키 인증 테스트"""
        try:
            if not self.logged_in:
                return {
                    'success': False,
                    'error': '로그인되지 않았습니다.'
                }
            
            headers = {}
            if self.nonce:
                headers['X-WP-Nonce'] = self.nonce
            
            test_url = urljoin(self.site_url, '/wp-json/wp/v2/users/me')
            response = self.session.get(test_url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user': user_data.get('name'),
                    'id': user_data.get('id'),
                    'message': '쿠키 인증 테스트 성공'
                }
            else:
                return {
                    'success': False,
                    'error': f'인증 실패: {response.status_code}',
                    'details': response.text[:200]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'인증 테스트 오류: {str(e)}'
            }
    
    def create_post(self, title: str, content: str, status: str = 'draft') -> dict:
        """쿠키를 사용하여 포스트 생성"""
        try:
            if not self.logged_in:
                return {
                    'success': False,
                    'error': '로그인되지 않았습니다.'
                }
            
            headers = {'Content-Type': 'application/json'}
            if self.nonce:
                headers['X-WP-Nonce'] = self.nonce
            
            post_url = urljoin(self.site_url, '/wp-json/wp/v2/posts')
            data = {
                'title': title,
                'content': content,
                'status': status
            }
            
            response = self.session.post(post_url, json=data, headers=headers)
            
            if response.status_code == 201:
                post_data = response.json()
                return {
                    'success': True,
                    'post_id': post_data.get('id'),
                    'post_url': post_data.get('link'),
                    'message': '쿠키를 통한 포스트 생성 성공'
                }
            else:
                return {
                    'success': False,
                    'error': f'포스트 생성 실패: {response.status_code}',
                    'details': response.text[:200]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'포스트 생성 오류: {str(e)}'
            }


def test_cookie_auth(site_url: str, username: str, password: str):
    """쿠키 인증 테스트 헬퍼 함수"""
    cookie_auth = WordPressCookieAuth(site_url)
    
    # 1. 로그인 시도
    login_result = cookie_auth.login(username, password)
    print("쿠키 로그인 결과:", login_result)
    
    if login_result['success']:
        # 2. 인증 테스트
        test_result = cookie_auth.test_auth()
        print("\n쿠키 인증 테스트:", test_result)
        
        # 3. 포스트 생성 테스트
        post_result = cookie_auth.create_post(
            title="쿠키 테스트 포스트",
            content="쿠키 인증을 통한 테스트 포스트입니다.",
            status="draft"
        )
        print("\n포스트 생성 테스트:", post_result)
    
    return login_result


if __name__ == "__main__":
    # 테스트 실행
    site_url = "https://innerspell.com"
    username = "banana"
    password = "CRJWYclhn9m6KNq1cveBRNnV"
    
    test_cookie_auth(site_url, username, password)