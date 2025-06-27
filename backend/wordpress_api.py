"""
WordPress REST API 연동 모듈
자동 포스팅 및 WordPress 관리 기능
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from logger import app_logger

class WordPressAPI:
    def __init__(self):
        self.wp_url = None
        self.username = None
        self.password = None
        self.auth = None
        self.api_base = None
    
    def setup(self, wp_url: str, username: str, password: str):
        """WordPress 연결 설정"""
        self.wp_url = wp_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth = aiohttp.BasicAuth(username, password)
        self.api_base = f"{self.wp_url}/wp-json/wp/v2"
        
        app_logger.info(f"WordPress API 설정 완료: {self.wp_url}")
    
    async def test_connection(self) -> Dict[str, Any]:
        """WordPress 연결 테스트"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/users/me",
                    auth=self.auth,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        user_data = await response.json()
                        return {
                            "success": True,
                            "user_info": user_data
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            app_logger.error(f"WordPress 연결 테스트 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """WordPress 카테고리 목록 조회"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/categories",
                    auth=self.auth,
                    params={"per_page": 100}
                ) as response:
                    
                    if response.status == 200:
                        categories = await response.json()
                        return [
                            {
                                "id": cat["id"],
                                "name": cat["name"],
                                "slug": cat["slug"],
                                "count": cat["count"]
                            }
                            for cat in categories
                        ]
                    else:
                        app_logger.warning(f"카테고리 조회 실패: HTTP {response.status}")
                        return []
                        
        except Exception as e:
            app_logger.error(f"카테고리 조회 오류: {e}")
            return []
    
    async def create_category(self, name: str, description: str = "") -> Optional[Dict[str, Any]]:
        """새 카테고리 생성"""
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "name": name,
                    "description": description
                }
                
                async with session.post(
                    f"{self.api_base}/categories",
                    auth=self.auth,
                    json=data
                ) as response:
                    
                    if response.status == 201:
                        category = await response.json()
                        app_logger.info(f"카테고리 생성 완료: {name}")
                        return {
                            "id": category["id"],
                            "name": category["name"],
                            "slug": category["slug"]
                        }
                    else:
                        error_text = await response.text()
                        app_logger.warning(f"카테고리 생성 실패: {error_text}")
                        return None
                        
        except Exception as e:
            app_logger.error(f"카테고리 생성 오류: {e}")
            return None
    
    async def upload_media(self, image_url: str, title: str) -> Optional[Dict[str, Any]]:
        """이미지 업로드 (URL에서)"""
        try:
            # 외부 이미지 다운로드
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as img_response:
                    if img_response.status != 200:
                        return None
                    
                    image_data = await img_response.read()
                    content_type = img_response.headers.get('content-type', 'image/jpeg')
                
                # WordPress에 업로드
                headers = {
                    'Content-Type': content_type,
                    'Content-Disposition': f'attachment; filename="{title}.jpg"'
                }
                
                async with session.post(
                    f"{self.api_base}/media",
                    auth=self.auth,
                    data=image_data,
                    headers=headers
                ) as response:
                    
                    if response.status == 201:
                        media = await response.json()
                        return {
                            "id": media["id"],
                            "url": media["source_url"],
                            "title": media["title"]["rendered"]
                        }
                    else:
                        app_logger.warning(f"이미지 업로드 실패: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            app_logger.error(f"이미지 업로드 오류: {e}")
            return None
    
    async def publish_post(
        self,
        title: str,
        content: str,
        status: str = "publish",
        categories: List[int] = None,
        tags: List[str] = None,
        featured_image_id: Optional[int] = None,
        scheduled_time: Optional[datetime] = None,
        excerpt: str = ""
    ) -> Dict[str, Any]:
        """블로그 글 발행"""
        
        app_logger.info(f"WordPress 포스팅 시작: {title}")
        
        try:
            # 포스팅 데이터 준비
            post_data = {
                "title": title,
                "content": content,
                "status": status,
                "excerpt": excerpt[:150] if excerpt else content[:150].replace('\n', ' ')
            }
            
            # 카테고리 설정
            if categories:
                post_data["categories"] = categories
            
            # 태그 설정
            if tags:
                # 태그 이름을 ID로 변환 (필요시)
                post_data["tags"] = await self._get_or_create_tags(tags)
            
            # 썸네일 이미지 설정
            if featured_image_id:
                post_data["featured_media"] = featured_image_id
            
            # 예약 포스팅 설정
            if scheduled_time:
                post_data["date"] = scheduled_time.isoformat()
                post_data["status"] = "future"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/posts",
                    auth=self.auth,
                    json=post_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status in [200, 201]:
                        post = await response.json()
                        
                        result = {
                            "success": True,
                            "post_id": str(post["id"]),
                            "post_url": post["link"],
                            "status": post["status"],
                            "published_date": post.get("date"),
                            "title": post["title"]["rendered"]
                        }
                        
                        app_logger.info(f"WordPress 포스팅 완료: {title} (ID: {post['id']})")
                        return result
                        
                    else:
                        error_text = await response.text()
                        app_logger.error(f"WordPress 포스팅 실패: HTTP {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            app_logger.error(f"WordPress 포스팅 오류: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_or_create_tags(self, tag_names: List[str]) -> List[int]:
        """태그 ID 조회 또는 생성"""
        tag_ids = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # 기존 태그 조회
                async with session.get(
                    f"{self.api_base}/tags",
                    auth=self.auth,
                    params={"per_page": 100}
                ) as response:
                    
                    existing_tags = {}
                    if response.status == 200:
                        tags = await response.json()
                        existing_tags = {tag["name"]: tag["id"] for tag in tags}
                
                # 각 태그 처리
                for tag_name in tag_names:
                    if tag_name in existing_tags:
                        tag_ids.append(existing_tags[tag_name])
                    else:
                        # 새 태그 생성
                        async with session.post(
                            f"{self.api_base}/tags",
                            auth=self.auth,
                            json={"name": tag_name}
                        ) as tag_response:
                            
                            if tag_response.status == 201:
                                new_tag = await tag_response.json()
                                tag_ids.append(new_tag["id"])
                                app_logger.info(f"새 태그 생성: {tag_name}")
                            else:
                                app_logger.warning(f"태그 생성 실패: {tag_name}")
        
        except Exception as e:
            app_logger.error(f"태그 처리 오류: {e}")
        
        return tag_ids
    
    async def get_posts(self, per_page: int = 10, page: int = 1) -> List[Dict[str, Any]]:
        """발행된 글 목록 조회"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "per_page": per_page,
                    "page": page,
                    "status": "publish"
                }
                
                async with session.get(
                    f"{self.api_base}/posts",
                    auth=self.auth,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        posts = await response.json()
                        return [
                            {
                                "id": post["id"],
                                "title": post["title"]["rendered"],
                                "link": post["link"],
                                "date": post["date"],
                                "excerpt": post["excerpt"]["rendered"],
                                "status": post["status"]
                            }
                            for post in posts
                        ]
                    else:
                        app_logger.warning(f"글 목록 조회 실패: HTTP {response.status}")
                        return []
                        
        except Exception as e:
            app_logger.error(f"글 목록 조회 오류: {e}")
            return []
    
    async def update_post(
        self,
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """글 수정"""
        try:
            update_data = {}
            if title:
                update_data["title"] = title
            if content:
                update_data["content"] = content
            if status:
                update_data["status"] = status
            
            if not update_data:
                return {"success": False, "error": "수정할 데이터가 없습니다"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/posts/{post_id}",
                    auth=self.auth,
                    json=update_data
                ) as response:
                    
                    if response.status == 200:
                        post = await response.json()
                        app_logger.info(f"글 수정 완료: {post_id}")
                        return {
                            "success": True,
                            "post_id": post["id"],
                            "title": post["title"]["rendered"],
                            "link": post["link"]
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            app_logger.error(f"글 수정 오류: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_post(self, post_id: int, force: bool = False) -> Dict[str, Any]:
        """글 삭제"""
        try:
            params = {"force": "true"} if force else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.api_base}/posts/{post_id}",
                    auth=self.auth,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        app_logger.info(f"글 삭제 완료: {post_id}")
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            app_logger.error(f"글 삭제 오류: {e}")
            return {
                "success": False,
                "error": str(e)
            }