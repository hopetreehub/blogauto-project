"""
WordPress 자동 포스팅 모듈
예약 발행, 즉시 발행, 임시저장 기능을 포함한 완전한 WordPress 연동 모듈
"""

from datetime import datetime, timedelta
import requests
import base64
import json
import asyncio
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import mimetypes
import logging
from pydantic import BaseModel

# 로그 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordPressConfig(BaseModel):
    site_url: str
    username: str
    password: str

class WordPressPost(BaseModel):
    title: str
    content: str
    status: str = "draft"  # draft, publish, private, future
    categories: List[int] = []
    tags: List[int] = []
    featured_image_url: Optional[str] = None
    publish_date: Optional[str] = None  # ISO 형식 날짜 (예: "2025-01-15T10:00:00")
    excerpt: Optional[str] = None
    meta_description: Optional[str] = None

class ScheduledPost(BaseModel):
    id: str
    title: str
    content: str
    wp_config: WordPressConfig
    publish_date: datetime
    featured_image_url: Optional[str] = None
    categories: List[int] = []
    tags: List[int] = []
    status: str = "scheduled"  # scheduled, published, failed

class WordPressModule:
    def __init__(self):
        self.scheduled_posts: Dict[str, ScheduledPost] = {}
        self.auth_cache: Dict[str, Dict] = {}
    
    def _get_auth_headers(self, wp_config: WordPressConfig) -> Dict[str, str]:
        """WordPress 인증 헤더 생성"""
        auth_string = f"{wp_config.username}:{wp_config.password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        return {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
    
    async def test_connection(self, wp_config: WordPressConfig) -> Dict[str, Any]:
        """WordPress 연결 테스트"""
        try:
            # 사이트 URL 정규화
            site_url = wp_config.site_url.rstrip('/')
            if not site_url.startswith(('http://', 'https://')):
                site_url = 'https://' + site_url
            
            # 1단계: REST API 기본 엔드포인트 테스트
            rest_url = urljoin(site_url, '/wp-json/wp/v2')
            basic_response = requests.get(rest_url, timeout=15)
            
            if basic_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'WordPress REST API에 접근할 수 없습니다 ({basic_response.status_code})',
                    'suggestion': 'WordPress 사이트 URL이 올바른지 확인하고, REST API가 활성화되어 있는지 확인하세요.'
                }
            
            # 2단계: 인증 테스트
            wp_url = urljoin(site_url, '/wp-json/wp/v2/users/me')
            headers = self._get_auth_headers(wp_config)
            headers.pop('Content-Type')  # GET 요청에서는 불필요
            
            # 디버깅 정보 로깅
            logger.info(f"WordPress 연결 테스트 시도: {wp_url}")
            logger.info(f"사용자명: {wp_config.username}")
            logger.info(f"비밀번호 길이: {len(wp_config.password)}자")
            
            response = requests.get(wp_url, headers=headers, timeout=30)
            logger.info(f"응답 코드: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                
                # 캐시에 저장
                cache_key = f"{site_url}:{wp_config.username}"
                self.auth_cache[cache_key] = {
                    'valid': True,
                    'user_data': user_data,
                    'timestamp': datetime.now()
                }
                
                return {
                    'success': True,
                    'user': user_data.get('name', '알 수 없음'),
                    'user_id': user_data.get('id'),
                    'site_name': site_url,
                    'capabilities': user_data.get('capabilities', {}),
                    'rest_api_available': True
                }
            elif response.status_code == 401:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                    
                error_msg = error_data.get('message', '인증 실패')
                error_code = error_data.get('code', 'unknown')
                
                logger.error(f"401 인증 실패 - 사이트: {site_url}, 사용자: {wp_config.username}, 오류: {error_msg}")
                
                # 사용자명과 비밀번호를 Base64로 디버깅
                import base64
                auth_string = f"{wp_config.username}:{wp_config.password}"
                auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
                logger.info(f"Auth header: Basic {auth_b64[:20]}...")
                
                # 추가 디버깅 정보
                debug_info = {
                    'tested_url': wp_url,
                    'username_length': len(wp_config.username),
                    'password_length': len(wp_config.password),
                    'password_format': 'contains_spaces' if ' ' in wp_config.password else 'no_spaces',
                    'response_headers': dict(response.headers),
                    'full_response': response.text[:500] if response.text else None
                }
                
                return {
                    'success': False,
                    'error': f'인증 오류 (401): {error_msg}',
                    'suggestion': '다음을 확인해주세요:\n1. WordPress 사이트에 정상 로그인 가능\n2. 애플리케이션 비밀번호 사용 (일반 비밀번호 X)\n3. 사용자명이 정확한지 확인\n4. 비밀번호에 공백이 없는지 확인',
                    'username': wp_config.username,
                    'site_url': site_url,
                    'error_code': error_code,
                    'debug_info': debug_info
                }
            elif response.status_code == 403:
                return {
                    'success': False,
                    'error': '권한 부족 (403): 사용자에게 충분한 권한이 없습니다',
                    'suggestion': '관리자 권한이 있는 사용자를 사용하세요.'
                }
            else:
                logger.error(f"WordPress 연결 실패: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"연결 실패: HTTP {response.status_code}",
                    'details': response.text[:200],
                    'suggestion': 'WordPress 사이트와 인증 정보를 다시 확인해주세요.'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "연결 시간 초과 (30초)",
                'suggestion': '사이트가 느리거나 응답하지 않습니다. 사이트 URL을 확인하세요.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': "연결 오류: 사이트에 접근할 수 없습니다",
                'suggestion': 'WordPress 사이트 URL이 올바른지 확인하고, 인터넷 연결을 확인하세요.'
            }
        except Exception as e:
            logger.error(f"WordPress 연결 테스트 오류: {str(e)}")
            return {
                'success': False,
                'error': f"연결 오류: {str(e)}",
                'suggestion': '사이트 URL과 인증 정보를 다시 확인해주세요.'
            }
    
    async def upload_image_to_wordpress(self, image_url: str, wp_config: WordPressConfig, filename: str = None) -> Optional[Dict[str, Any]]:
        """WordPress에 이미지 업로드"""
        try:
            # 이미지 다운로드
            image_response = requests.get(image_url, timeout=60)
            if image_response.status_code != 200:
                logger.error(f"이미지 다운로드 실패: {image_response.status_code}")
                return None
                
            # 파일명 설정
            if not filename:
                filename = f"ai_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # WordPress REST API로 이미지 업로드
            wp_url = urljoin(wp_config.site_url, '/wp-json/wp/v2/media')
            
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"{wp_config.username}:{wp_config.password}".encode()).decode()}',
                'Content-Disposition': f'attachment; filename="{filename}"',
            }
            
            # 파일 MIME 타입 설정
            content_type = mimetypes.guess_type(filename)[0] or 'image/png'
            headers['Content-Type'] = content_type
            
            response = requests.post(wp_url, headers=headers, data=image_response.content, timeout=60)
            
            if response.status_code == 201:
                media_data = response.json()
                logger.info(f"이미지 업로드 성공: {media_data['id']}")
                return {
                    'id': media_data['id'],
                    'url': media_data['source_url'],
                    'alt_text': media_data.get('alt_text', ''),
                    'title': media_data.get('title', {}).get('rendered', '')
                }
            else:
                logger.error(f"이미지 업로드 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"이미지 업로드 오류: {str(e)}")
            return None
    
    async def publish_post(self, post_data: WordPressPost, wp_config: WordPressConfig) -> Dict[str, Any]:
        """WordPress에 즉시 포스트 발행"""
        try:
            wp_url = urljoin(wp_config.site_url, '/wp-json/wp/v2/posts')
            headers = self._get_auth_headers(wp_config)
            
            # 포스트 데이터 준비
            post_payload = {
                'title': post_data.title,
                'content': post_data.content,
                'status': post_data.status,
                'categories': post_data.categories,
                'tags': post_data.tags
            }
            
            # 발행 날짜 설정 (예약 발행용)
            if post_data.publish_date and post_data.status == 'future':
                post_payload['date'] = post_data.publish_date
            
            # 메타 설명 추가
            if post_data.meta_description:
                post_payload['meta'] = {
                    'description': post_data.meta_description
                }
            
            # 발췌문 추가
            if post_data.excerpt:
                post_payload['excerpt'] = post_data.excerpt
            
            # Featured Image 처리
            if post_data.featured_image_url:
                image_data = await self.upload_image_to_wordpress(
                    post_data.featured_image_url, 
                    wp_config, 
                    f"featured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                if image_data:
                    post_payload['featured_media'] = image_data['id']
                    logger.info(f"대표 이미지 설정: {image_data['id']}")
            
            response = requests.post(wp_url, headers=headers, json=post_payload, timeout=60)
            
            if response.status_code == 201:
                post_result = response.json()
                logger.info(f"포스트 발행 성공: {post_result['id']}")
                
                # 상태에 따른 메시지
                status_messages = {
                    'publish': '즉시 발행',
                    'draft': '임시저장',
                    'private': '비공개',
                    'future': '예약 발행'
                }
                
                return {
                    'success': True,
                    'post_id': post_result['id'],
                    'post_url': post_result['link'],
                    'status': post_result['status'],
                    'status_message': status_messages.get(post_result['status'], post_result['status']),
                    'published_date': post_result.get('date', ''),
                    'modified_date': post_result.get('modified', '')
                }
            else:
                logger.error(f"포스트 발행 실패: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"포스팅 실패: HTTP {response.status_code}",
                    'details': response.text[:300]
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "포스팅 시간 초과 (60초)"
            }
        except Exception as e:
            logger.error(f"포스팅 오류: {str(e)}")
            return {
                'success': False,
                'error': f"포스팅 오류: {str(e)}"
            }
    
    async def schedule_post(self, post_data: WordPressPost, wp_config: WordPressConfig, publish_datetime: datetime) -> Dict[str, Any]:
        """포스트 예약 발행"""
        try:
            # 예약 시간이 현재보다 이후인지 확인
            if publish_datetime <= datetime.now():
                return {
                    'success': False,
                    'error': "예약 시간은 현재 시간보다 이후여야 합니다"
                }
            
            # ISO 형식으로 변환
            iso_date = publish_datetime.isoformat()
            
            # WordPress future 상태로 설정
            post_data.status = 'future'
            post_data.publish_date = iso_date
            
            # 즉시 WordPress에 예약 포스트로 등록
            result = await self.publish_post(post_data, wp_config)
            
            if result['success']:
                # 로컬 스케줄러에도 등록 (백업용)
                schedule_id = f"scheduled_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{result['post_id']}"
                scheduled_post = ScheduledPost(
                    id=schedule_id,
                    title=post_data.title,
                    content=post_data.content,
                    wp_config=wp_config,
                    publish_date=publish_datetime,
                    featured_image_url=post_data.featured_image_url,
                    categories=post_data.categories,
                    tags=post_data.tags,
                    status="scheduled"
                )
                
                self.scheduled_posts[schedule_id] = scheduled_post
                
                return {
                    'success': True,
                    'schedule_id': schedule_id,
                    'post_id': result['post_id'],
                    'post_url': result['post_url'],
                    'publish_datetime': publish_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'scheduled',
                    'message': f"{publish_datetime.strftime('%Y-%m-%d %H:%M:%S')}에 자동 발행 예약됨"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"예약 발행 오류: {str(e)}")
            return {
                'success': False,
                'error': f"예약 발행 오류: {str(e)}"
            }
    
    async def get_categories(self, wp_config: WordPressConfig) -> Dict[str, Any]:
        """WordPress 카테고리 목록 가져오기"""
        try:
            wp_url = urljoin(wp_config.site_url, '/wp-json/wp/v2/categories')
            headers = self._get_auth_headers(wp_config)
            headers.pop('Content-Type')
            
            response = requests.get(wp_url, headers=headers, params={'per_page': 100}, timeout=30)
            
            if response.status_code == 200:
                categories = response.json()
                return {
                    "success": True,
                    "categories": [{"id": cat["id"], "name": cat["name"]} for cat in categories]
                }
            else:
                return {
                    "success": False,
                    "error": f"카테고리 조회 실패: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"카테고리 조회 오류: {str(e)}")
            return {
                "success": False,
                "error": f"카테고리 조회 오류: {str(e)}"
            }
    
    async def get_tags(self, wp_config: WordPressConfig) -> Dict[str, Any]:
        """WordPress 태그 목록 가져오기"""
        try:
            wp_url = urljoin(wp_config.site_url, '/wp-json/wp/v2/tags')
            headers = self._get_auth_headers(wp_config)
            headers.pop('Content-Type')
            
            response = requests.get(wp_url, headers=headers, params={'per_page': 100}, timeout=30)
            
            if response.status_code == 200:
                tags = response.json()
                return {
                    "success": True,
                    "tags": [{"id": tag["id"], "name": tag["name"]} for tag in tags]
                }
            else:
                return {
                    "success": False,
                    "error": f"태그 조회 실패: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"태그 조회 오류: {str(e)}")
            return {
                "success": False,
                "error": f"태그 조회 오류: {str(e)}"
            }
    
    def get_scheduled_posts(self) -> Dict[str, Any]:
        """예약된 포스트 목록 조회"""
        return {
            'success': True,
            'scheduled_posts': [
                {
                    'id': post.id,
                    'title': post.title,
                    'publish_date': post.publish_date.isoformat(),
                    'status': post.status
                }
                for post in self.scheduled_posts.values()
            ]
        }
    
    async def cancel_scheduled_post(self, schedule_id: str) -> Dict[str, Any]:
        """예약된 포스트 취소"""
        try:
            if schedule_id not in self.scheduled_posts:
                return {
                    'success': False,
                    'error': '예약된 포스트를 찾을 수 없습니다'
                }
            
            # 로컬 스케줄에서 제거
            del self.scheduled_posts[schedule_id]
            
            return {
                'success': True,
                'message': '예약이 취소되었습니다'
            }
            
        except Exception as e:
            logger.error(f"예약 취소 오류: {str(e)}")
            return {
                'success': False,
                'error': f"예약 취소 오류: {str(e)}"
            }

# 전역 WordPress 모듈 인스턴스
wordpress_module = WordPressModule()