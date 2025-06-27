"""
자동 포스팅 서비스
- WordPress, BlogSpot, Tistory 자동 포스팅
- 예약 포스팅 기능
- 이미지 자동 생성 및 업로드
- 다중 플랫폼 동시 포스팅
"""

import asyncio
import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import base64
import aiohttp
from logger import app_logger
import openai
from PIL import Image
import io
import os


class AutoPostingService:
    """다중 플랫폼 자동 포스팅 서비스"""
    
    def __init__(self):
        self.supported_platforms = ['wordpress', 'blogspot', 'tistory']
        self.image_generators = ['dall-e', 'midjourney', 'stable-diffusion']
    
    async def schedule_posts(
        self,
        titles: List[str],
        content_data: Dict[str, str],
        platforms: List[Dict[str, Any]],
        schedule_settings: Dict[str, Any],
        image_settings: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """예약 포스팅 메인 함수"""
        
        try:
            app_logger.info(
                f"Starting scheduled posting process",
                titles_count=len(titles),
                platforms_count=len(platforms),
                schedule_settings=schedule_settings
            )
            
            results = {
                'success': [],
                'failed': [],
                'scheduled': [],
                'total_posts': len(titles) * len(platforms)
            }
            
            # 각 제목별로 포스팅 처리
            for i, title in enumerate(titles):
                content = content_data.get(title, '')
                
                # 이미지 생성 (필요한 경우)
                image_data = None
                if image_settings and image_settings.get('auto_generate', False):
                    image_data = await self._generate_post_image(title, image_settings)
                elif image_settings and image_settings.get('user_image'):
                    image_data = await self._process_user_image(image_settings['user_image'])
                
                # 각 플랫폼에 포스팅
                for platform_config in platforms:
                    try:
                        # 스케줄링 시간 계산
                        post_time = self._calculate_post_time(
                            schedule_settings, 
                            i, 
                            len(platforms),
                            platforms.index(platform_config)
                        )
                        
                        if post_time <= datetime.now():
                            # 즉시 포스팅
                            result = await self._post_immediately(
                                title, content, platform_config, image_data
                            )
                            if result['success']:
                                results['success'].append(result)
                            else:
                                results['failed'].append(result)
                        else:
                            # 예약 포스팅
                            result = await self._schedule_post(
                                title, content, platform_config, image_data, post_time
                            )
                            results['scheduled'].append(result)
                            
                    except Exception as e:
                        app_logger.error(
                            f"Error posting to platform",
                            error=e,
                            title=title,
                            platform=platform_config.get('name')
                        )
                        results['failed'].append({
                            'title': title,
                            'platform': platform_config.get('name'),
                            'error': str(e),
                            'success': False
                        })
            
            app_logger.info(
                f"Posting process completed",
                success_count=len(results['success']),
                failed_count=len(results['failed']),
                scheduled_count=len(results['scheduled'])
            )
            
            return results
            
        except Exception as e:
            app_logger.error(f"Error in schedule_posts", error=e)
            raise
    
    async def _generate_post_image(self, title: str, image_settings: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """포스트용 이미지 자동 생성"""
        
        try:
            generator = image_settings.get('generator', 'dall-e')
            style = image_settings.get('style', 'blog-thumbnail')
            
            if generator == 'dall-e':
                return await self._generate_dalle_image(title, style)
            elif generator == 'stable-diffusion':
                return await self._generate_sd_image(title, style)
            else:
                app_logger.warning(f"Unsupported image generator: {generator}")
                return None
                
        except Exception as e:
            app_logger.error(f"Error generating image", error=e, title=title)
            return None
    
    async def _generate_dalle_image(self, title: str, style: str) -> Dict[str, Any]:
        """DALL-E를 사용한 이미지 생성"""
        
        # 제목에서 키워드 추출
        keywords = self._extract_keywords_from_title(title)
        
        # 스타일별 프롬프트 생성
        style_prompts = {
            'blog-thumbnail': f"Professional blog thumbnail image featuring {keywords}, clean modern design, high quality, 16:9 aspect ratio",
            'infographic': f"Colorful infographic style illustration about {keywords}, informative and engaging",
            'minimalist': f"Minimalist clean design representing {keywords}, simple and elegant",
            'vibrant': f"Vibrant and eye-catching image about {keywords}, bright colors, engaging"
        }
        
        prompt = style_prompts.get(style, style_prompts['blog-thumbnail'])
        
        try:
            # OpenAI DALL-E API 호출 (실제 구현에서는 API 키 필요)
            response = await self._call_dalle_api(prompt)
            
            if response and response.get('data'):
                image_url = response['data'][0]['url']
                
                # 이미지 다운로드 및 처리
                image_data = await self._download_and_process_image(image_url)
                
                return {
                    'url': image_url,
                    'data': image_data,
                    'prompt': prompt,
                    'generator': 'dall-e'
                }
            
        except Exception as e:
            app_logger.error(f"DALL-E image generation failed", error=e)
            
        return None
    
    async def _process_user_image(self, image_path: str) -> Dict[str, Any]:
        """사용자 업로드 이미지 처리"""
        
        try:
            # 이미지 파일 읽기 및 최적화
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # PIL로 이미지 최적화
            image = Image.open(io.BytesIO(image_data))
            
            # 크기 조정 (최대 1920x1080)
            if image.width > 1920 or image.height > 1080:
                image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            
            # 최적화된 이미지를 bytes로 변환
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            optimized_data = output.getvalue()
            
            return {
                'data': optimized_data,
                'format': 'JPEG',
                'size': len(optimized_data),
                'dimensions': image.size,
                'source': 'user_upload'
            }
            
        except Exception as e:
            app_logger.error(f"Error processing user image", error=e, image_path=image_path)
            return None
    
    async def _post_immediately(
        self, 
        title: str, 
        content: str, 
        platform_config: Dict[str, Any], 
        image_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """즉시 포스팅"""
        
        platform = platform_config['platform']
        
        if platform == 'wordpress':
            return await self._post_to_wordpress(title, content, platform_config, image_data)
        elif platform == 'blogspot':
            return await self._post_to_blogspot(title, content, platform_config, image_data)
        elif platform == 'tistory':
            return await self._post_to_tistory(title, content, platform_config, image_data)
        else:
            return {
                'success': False,
                'error': f'Unsupported platform: {platform}',
                'title': title,
                'platform': platform
            }
    
    async def _post_to_wordpress(
        self, 
        title: str, 
        content: str, 
        platform_config: Dict[str, Any], 
        image_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """WordPress 포스팅"""
        
        try:
            base_url = platform_config['url'].rstrip('/')
            username = platform_config.get('username')
            password = platform_config.get('password')
            api_key = platform_config.get('api_key')  # Application Password
            
            # WordPress REST API 엔드포인트
            api_url = f"{base_url}/wp-json/wp/v2/posts"
            
            # 인증 헤더
            if api_key:
                auth = base64.b64encode(f"{username}:{api_key}".encode()).decode()
                headers = {
                    'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/json'
                }
            else:
                return {
                    'success': False,
                    'error': 'WordPress API key required',
                    'title': title,
                    'platform': 'wordpress'
                }
            
            # 이미지 업로드 (있는 경우)
            featured_media_id = None
            if image_data:
                featured_media_id = await self._upload_wordpress_image(
                    base_url, headers, image_data, title
                )
            
            # 포스트 데이터
            post_data = {
                'title': title,
                'content': content,
                'status': 'publish',
                'categories': [1],  # 기본 카테고리
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
            # API 호출
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=post_data) as response:
                    if response.status == 201:
                        result = await response.json()
                        return {
                            'success': True,
                            'post_id': result['id'],
                            'url': result['link'],
                            'title': title,
                            'platform': 'wordpress'
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'WordPress API error: {response.status} - {error_text}',
                            'title': title,
                            'platform': 'wordpress'
                        }
            
        except Exception as e:
            app_logger.error(f"WordPress posting failed", error=e, title=title)
            return {
                'success': False,
                'error': str(e),
                'title': title,
                'platform': 'wordpress'
            }
    
    async def _post_to_blogspot(
        self, 
        title: str, 
        content: str, 
        platform_config: Dict[str, Any], 
        image_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """BlogSpot 포스팅"""
        
        try:
            blog_id = platform_config.get('blog_id')
            api_key = platform_config.get('api_key')
            
            if not blog_id or not api_key:
                return {
                    'success': False,
                    'error': 'BlogSpot blog_id and api_key required',
                    'title': title,
                    'platform': 'blogspot'
                }
            
            # BlogSpot API 엔드포인트
            api_url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts"
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # 이미지 처리 (BlogSpot은 HTML 콘텐츠에 이미지 임베드)
            if image_data:
                # 이미지를 base64로 인코딩하여 HTML에 포함
                image_base64 = base64.b64encode(image_data['data']).decode()
                image_html = f'<img src="data:image/jpeg;base64,{image_base64}" alt="{title}" style="max-width:100%;">'
                content = image_html + '<br><br>' + content
            
            # 포스트 데이터
            post_data = {
                'title': title,
                'content': content
            }
            
            # API 호출
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=post_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'post_id': result['id'],
                            'url': result['url'],
                            'title': title,
                            'platform': 'blogspot'
                        }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'BlogSpot API error: {response.status} - {error_text}',
                            'title': title,
                            'platform': 'blogspot'
                        }
            
        except Exception as e:
            app_logger.error(f"BlogSpot posting failed", error=e, title=title)
            return {
                'success': False,
                'error': str(e),
                'title': title,
                'platform': 'blogspot'
            }
    
    async def _post_to_tistory(
        self, 
        title: str, 
        content: str, 
        platform_config: Dict[str, Any], 
        image_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Tistory 포스팅"""
        
        try:
            blog_name = platform_config.get('blog_name')
            access_token = platform_config.get('access_token')
            
            if not blog_name or not access_token:
                return {
                    'success': False,
                    'error': 'Tistory blog_name and access_token required',
                    'title': title,
                    'platform': 'tistory'
                }
            
            # 이미지 업로드 (있는 경우)
            if image_data:
                image_url = await self._upload_tistory_image(
                    blog_name, access_token, image_data, title
                )
                if image_url:
                    content = f'<img src="{image_url}" alt="{title}" style="max-width:100%;"><br><br>' + content
            
            # Tistory API 엔드포인트
            api_url = "https://www.tistory.com/apis/post/write"
            
            # 포스트 데이터
            post_data = {
                'access_token': access_token,
                'blogName': blog_name,
                'title': title,
                'content': content,
                'visibility': '3',  # 공개
                'category': '0',  # 기본 카테고리
                'output': 'json'
            }
            
            # API 호출
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, data=post_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('tistory', {}).get('status') == '200':
                            return {
                                'success': True,
                                'post_id': result['tistory']['postId'],
                                'url': result['tistory']['url'],
                                'title': title,
                                'platform': 'tistory'
                            }
                        else:
                            return {
                                'success': False,
                                'error': f"Tistory API error: {result}",
                                'title': title,
                                'platform': 'tistory'
                            }
                    else:
                        error_text = await response.text()
                        return {
                            'success': False,
                            'error': f'Tistory API error: {response.status} - {error_text}',
                            'title': title,
                            'platform': 'tistory'
                        }
            
        except Exception as e:
            app_logger.error(f"Tistory posting failed", error=e, title=title)
            return {
                'success': False,
                'error': str(e),
                'title': title,
                'platform': 'tistory'
            }
    
    async def _schedule_post(
        self, 
        title: str, 
        content: str, 
        platform_config: Dict[str, Any], 
        image_data: Optional[Dict[str, Any]], 
        post_time: datetime
    ) -> Dict[str, Any]:
        """예약 포스팅 (데이터베이스에 저장)"""
        
        # 실제 구현에서는 데이터베이스에 저장하고 스케줄러로 처리
        return {
            'success': True,
            'scheduled_time': post_time.isoformat(),
            'title': title,
            'platform': platform_config['platform'],
            'status': 'scheduled'
        }
    
    def _calculate_post_time(
        self, 
        schedule_settings: Dict[str, Any], 
        title_index: int, 
        platform_count: int, 
        platform_index: int
    ) -> datetime:
        """포스팅 시간 계산"""
        
        base_time = datetime.now()
        
        if schedule_settings.get('immediate', False):
            return base_time
        
        # 간격 설정
        interval_minutes = schedule_settings.get('interval_minutes', 30)
        start_delay_minutes = schedule_settings.get('start_delay_minutes', 0)
        
        # 플랫폼별 추가 지연
        platform_delay = platform_index * schedule_settings.get('platform_delay_minutes', 5)
        
        # 전체 지연 시간 계산
        total_delay = (
            start_delay_minutes + 
            (title_index * interval_minutes) + 
            platform_delay
        )
        
        return base_time + timedelta(minutes=total_delay)
    
    def _extract_keywords_from_title(self, title: str) -> str:
        """제목에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        stop_words = {'의', '를', '을', '이', '가', '에', '에서', '로', '으로', '와', '과', '하는', '되는', '있는', '없는'}
        words = title.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        return ' '.join(keywords[:3])  # 상위 3개 키워드
    
    async def _call_dalle_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """DALL-E API 호출 (모의)"""
        # 실제 구현에서는 OpenAI API 사용
        await asyncio.sleep(0.1)  # 시뮬레이션
        return {
            'data': [{
                'url': 'https://example.com/generated-image.jpg'
            }]
        }
    
    async def _download_and_process_image(self, image_url: str) -> bytes:
        """이미지 다운로드 및 처리"""
        # 실제 구현에서는 이미지 다운로드 및 최적화
        return b'fake_image_data'
    
    async def _upload_wordpress_image(
        self, 
        base_url: str, 
        headers: Dict[str, str], 
        image_data: Dict[str, Any], 
        title: str
    ) -> Optional[int]:
        """WordPress 이미지 업로드"""
        try:
            media_url = f"{base_url}/wp-json/wp/v2/media"
            
            # 파일 업로드 준비
            files = {
                'file': ('image.jpg', image_data['data'], 'image/jpeg')
            }
            
            # 헤더에서 Content-Type 제거 (multipart로 자동 설정됨)
            upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(media_url, headers=upload_headers, data=files) as response:
                    if response.status == 201:
                        result = await response.json()
                        return result['id']
            
            return None
            
        except Exception as e:
            app_logger.error(f"WordPress image upload failed", error=e)
            return None
    
    async def _upload_tistory_image(
        self, 
        blog_name: str, 
        access_token: str, 
        image_data: Dict[str, Any], 
        title: str
    ) -> Optional[str]:
        """Tistory 이미지 업로드"""
        try:
            upload_url = "https://www.tistory.com/apis/post/attach"
            
            files = {
                'uploadedfile': ('image.jpg', image_data['data'], 'image/jpeg')
            }
            
            data = {
                'access_token': access_token,
                'blogName': blog_name,
                'output': 'json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(upload_url, data=data, files=files) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('tistory', {}).get('status') == '200':
                            return result['tistory']['url']
            
            return None
            
        except Exception as e:
            app_logger.error(f"Tistory image upload failed", error=e)
            return None


# Export for main.py
__all__ = ['AutoPostingService']