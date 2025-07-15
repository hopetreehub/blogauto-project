"""
WordPress API Key Authentication 모듈
miniOrange REST API Authentication 플러그인을 사용하여 API 키로 인증
"""

import requests
import json
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

class WordPressAPIKeyAuth:
    def __init__(self, site_url: str, api_key: str):
        self.site_url = site_url.rstrip('/')
        self.api_key = api_key
        
    def get_headers(self) -> dict:
        """API Key 인증 헤더 반환"""
        return {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def test_connection(self) -> dict:
        """API Key 인증 테스트"""
        try:
            headers = self.get_headers()
            test_url = urljoin(self.site_url, '/wp-json/wp/v2/users/me')
            
            response = requests.get(test_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user': user_data.get('name'),
                    'id': user_data.get('id'),
                    'message': 'API Key 인증 성공'
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
                'error': f'API Key 테스트 오류: {str(e)}'
            }
    
    def create_post(self, title: str, content: str, status: str = 'draft', 
                   categories: list = None, tags: list = None,
                   featured_media_id: int = None) -> dict:
        """API Key를 사용하여 포스트 생성"""
        try:
            headers = self.get_headers()
            post_url = urljoin(self.site_url, '/wp-json/wp/v2/posts')
            
            data = {
                'title': title,
                'content': content,
                'status': status
            }
            
            if categories:
                data['categories'] = categories
            if tags:
                data['tags'] = tags
            if featured_media_id:
                data['featured_media'] = featured_media_id
            
            response = requests.post(post_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 201:
                post_data = response.json()
                return {
                    'success': True,
                    'post_id': post_data.get('id'),
                    'post_url': post_data.get('link'),
                    'message': 'API Key를 통한 포스트 생성 성공'
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
    
    def upload_media(self, image_url: str, filename: str = 'image.png') -> dict:
        """이미지 업로드"""
        try:
            # 이미지 다운로드
            img_response = requests.get(image_url)
            if img_response.status_code != 200:
                return None
            
            # WordPress에 업로드
            headers = self.get_headers()
            headers.pop('Content-Type')  # multipart/form-data로 자동 설정되도록
            
            media_url = urljoin(self.site_url, '/wp-json/wp/v2/media')
            
            files = {
                'file': (filename, img_response.content, 'image/png')
            }
            
            response = requests.post(media_url, headers=headers, files=files, timeout=60)
            
            if response.status_code == 201:
                media_data = response.json()
                return {
                    'id': media_data.get('id'),
                    'url': media_data.get('source_url'),
                    'success': True
                }
            else:
                logger.error(f"이미지 업로드 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"이미지 업로드 오류: {str(e)}")
            return None


def test_api_key_auth(site_url: str, api_key: str):
    """API Key 인증 테스트 헬퍼 함수"""
    api_auth = WordPressAPIKeyAuth(site_url, api_key)
    
    # 1. 연결 테스트
    test_result = api_auth.test_connection()
    print("API Key 인증 테스트:", json.dumps(test_result, indent=2, ensure_ascii=False))
    
    if test_result['success']:
        # 2. 포스트 생성 테스트
        post_result = api_auth.create_post(
            title="API Key 테스트 포스트",
            content="API Key 인증을 통한 테스트 포스트입니다.",
            status="draft"
        )
        print("\n포스트 생성 테스트:", json.dumps(post_result, indent=2, ensure_ascii=False))
    
    return test_result


if __name__ == "__main__":
    # 테스트 실행
    site_url = "https://innerspell.com"
    api_key = "YOUR_API_KEY_HERE"  # miniOrange 플러그인에서 생성한 API 키
    
    test_api_key_auth(site_url, api_key)