"""
WordPress 인증 테스트 및 디버깅 도구
다양한 WordPress 호스팅 환경에서의 인증 방법을 테스트합니다.
"""

import requests
import base64
import json
from urllib.parse import urljoin
import urllib3
from typing import Dict, Any

# SSL 경고 비활성화 (테스트 목적)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WordPressAuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # SSL 검증 비활성화 (테스트용)
        
    def test_multiple_auth_methods(self, site_url: str, username: str, password: str) -> Dict[str, Any]:
        """다양한 인증 방법으로 WordPress 연결 테스트"""
        
        # URL 정규화
        site_url = site_url.rstrip('/')
        if not site_url.startswith(('http://', 'https://')):
            site_url = 'https://' + site_url
            
        results = {
            'site_url': site_url,
            'username': username,
            'tests': {}
        }
        
        # 1. 기본 REST API 확인
        results['tests']['rest_api_check'] = self._test_rest_api_availability(site_url)
        
        # 2. 표준 Basic Auth 테스트
        results['tests']['basic_auth'] = self._test_basic_auth(site_url, username, password)
        
        # 3. Application Password 직접 테스트
        results['tests']['app_password'] = self._test_application_password(site_url, username, password)
        
        # 4. 다른 엔드포인트 테스트
        results['tests']['posts_endpoint'] = self._test_posts_endpoint(site_url, username, password)
        
        # 5. WordPress.com 호스팅 테스트
        results['tests']['wpcom_check'] = self._test_wpcom_hosting(site_url)
        
        return results
    
    def _test_rest_api_availability(self, site_url: str) -> Dict[str, Any]:
        """WordPress REST API 기본 접근성 테스트"""
        try:
            # 다양한 REST API 엔드포인트 테스트
            endpoints = [
                '/wp-json',
                '/wp-json/wp/v2',
                '/?rest_route=/',
                '/index.php/wp-json/wp/v2'
            ]
            
            for endpoint in endpoints:
                url = urljoin(site_url, endpoint)
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else None
                        return {
                            'success': True,
                            'endpoint': endpoint,
                            'status_code': response.status_code,
                            'data': data
                        }
                except Exception as e:
                    continue
                    
            return {
                'success': False,
                'error': 'REST API 엔드포인트에 접근할 수 없습니다',
                'tested_endpoints': endpoints
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'REST API 테스트 오류: {str(e)}'
            }
    
    def _test_basic_auth(self, site_url: str, username: str, password: str) -> Dict[str, Any]:
        """표준 Basic Authentication 테스트"""
        try:
            # 다양한 users 엔드포인트 테스트
            endpoints = [
                '/wp-json/wp/v2/users/me',
                '/?rest_route=/wp/v2/users/me',
                '/index.php/wp-json/wp/v2/users/me'
            ]
            
            auth_string = f"{username}:{password}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'User-Agent': 'BlogAuto/1.0'
            }
            
            for endpoint in endpoints:
                url = urljoin(site_url, endpoint)
                try:
                    response = self.session.get(url, headers=headers, timeout=15)
                    
                    result = {
                        'endpoint': endpoint,
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'auth_header_sent': f"Basic {auth_b64[:20]}..."
                    }
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            result.update({
                                'success': True,
                                'user_data': data
                            })
                            return result
                        except:
                            result['success'] = False
                            result['error'] = 'JSON 응답이 아님'
                    else:
                        try:
                            error_data = response.json()
                            result.update({
                                'success': False,
                                'error_data': error_data,
                                'response_text': response.text[:500]
                            })
                        except:
                            result.update({
                                'success': False,
                                'response_text': response.text[:500]
                            })
                    
                    if endpoint == endpoints[0]:  # 첫 번째 엔드포인트 결과는 항상 반환
                        return result
                        
                except Exception as e:
                    continue
                    
            return {
                'success': False,
                'error': '모든 사용자 엔드포인트에 접근 실패',
                'tested_endpoints': endpoints
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Basic Auth 테스트 오류: {str(e)}'
            }
    
    def _test_application_password(self, site_url: str, username: str, password: str) -> Dict[str, Any]:
        """WordPress Application Password 특별 테스트"""
        try:
            # Application Password 형식 검증
            is_app_password = len(password.replace(' ', '')) == 24 and all(c.isalnum() or c == ' ' for c in password)
            
            # 공백 제거 버전으로도 테스트
            clean_password = password.replace(' ', '')
            
            results = []
            
            for test_password in [password, clean_password]:
                auth_string = f"{username}:{test_password}"
                auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
                
                headers = {
                    'Authorization': f'Basic {auth_b64}',
                    'User-Agent': 'BlogAuto/1.0',
                    'Content-Type': 'application/json'
                }
                
                url = urljoin(site_url, '/wp-json/wp/v2/users/me')
                
                try:
                    response = self.session.get(url, headers=headers, timeout=15)
                    
                    result = {
                        'password_version': 'original' if test_password == password else 'cleaned',
                        'password_length': len(test_password),
                        'status_code': response.status_code,
                        'success': response.status_code == 200
                    }
                    
                    if response.status_code == 200:
                        try:
                            result['user_data'] = response.json()
                        except:
                            pass
                    else:
                        try:
                            result['error_data'] = response.json()
                        except:
                            result['response_text'] = response.text[:200]
                    
                    results.append(result)
                    
                except Exception as e:
                    results.append({
                        'password_version': 'original' if test_password == password else 'cleaned',
                        'error': str(e)
                    })
            
            return {
                'is_app_password_format': is_app_password,
                'password_analysis': {
                    'length': len(password),
                    'has_spaces': ' ' in password,
                    'cleaned_length': len(clean_password)
                },
                'test_results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Application Password 테스트 오류: {str(e)}'
            }
    
    def _test_posts_endpoint(self, site_url: str, username: str, password: str) -> Dict[str, Any]:
        """Posts 엔드포인트로 권한 테스트"""
        try:
            auth_string = f"{username}:{password}"
            auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_b64}',
                'User-Agent': 'BlogAuto/1.0'
            }
            
            url = urljoin(site_url, '/wp-json/wp/v2/posts')
            response = self.session.get(url, headers=headers, timeout=15, params={'per_page': 1})
            
            return {
                'status_code': response.status_code,
                'success': response.status_code in [200, 401, 403],  # 401/403도 인증은 도달했다는 의미
                'can_read_posts': response.status_code == 200,
                'response_info': response.text[:300] if response.status_code != 200 else 'Success'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Posts 엔드포인트 테스트 오류: {str(e)}'
            }
    
    def _test_wpcom_hosting(self, site_url: str) -> Dict[str, Any]:
        """WordPress.com 호스팅 여부 확인"""
        try:
            is_wpcom = 'wordpress.com' in site_url.lower()
            
            # WordPress.com의 경우 특별한 인증 방법 필요
            if is_wpcom:
                return {
                    'is_wpcom': True,
                    'notice': 'WordPress.com 호스팅은 OAuth 또는 Jetpack 연결이 필요할 수 있습니다.'
                }
            else:
                return {
                    'is_wpcom': False,
                    'hosting_type': 'self_hosted_or_other'
                }
                
        except Exception as e:
            return {
                'error': f'호스팅 타입 확인 오류: {str(e)}'
            }

# 테스트 함수
def run_comprehensive_test(site_url: str, username: str, password: str) -> Dict[str, Any]:
    """종합적인 WordPress 인증 테스트 실행"""
    tester = WordPressAuthTester()
    return tester.test_multiple_auth_methods(site_url, username, password)

if __name__ == "__main__":
    # 테스트 실행 예시
    print("WordPress 인증 테스트 도구")
    print("이 도구는 다양한 WordPress 호스팅 환경에서의 인증을 테스트합니다.")