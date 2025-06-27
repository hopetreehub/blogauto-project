"""
사이트 관리 시스템
사용자의 블로그 사이트 등록, 수정, 삭제 및 WordPress 연동 관리
"""

import json
import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from cryptography.fernet import Fernet
import os
import base64
from datetime import datetime

from models import Site, SystemPrompt, User
from logger import app_logger

class SiteManager:
    def __init__(self):
        # 암호화 키 설정 (환경변수에서 가져오거나 생성)
        self.encryption_key = self._get_encryption_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """암호화 키 가져오기 또는 생성"""
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            # 새로운 키 생성 (실제 운영환경에서는 안전한 곳에 저장해야 함)
            key = Fernet.generate_key()
            app_logger.warning("새로운 암호화 키가 생성되었습니다. 환경변수 ENCRYPTION_KEY에 저장하세요.")
        else:
            key = key.encode() if isinstance(key, str) else key
        return key
    
    def encrypt_password(self, password: str) -> str:
        """비밀번호 암호화"""
        try:
            encrypted = self.cipher.encrypt(password.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            app_logger.error(f"비밀번호 암호화 실패: {e}")
            raise
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """비밀번호 복호화"""
        try:
            encrypted = base64.b64decode(encrypted_password.encode())
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            app_logger.error(f"비밀번호 복호화 실패: {e}")
            raise
    
    async def create_site(
        self, 
        db: Session, 
        user_id: str,
        name: str,
        url: str,
        description: str,
        category: str,
        wordpress_url: Optional[str] = None,
        wordpress_username: Optional[str] = None,
        wordpress_password: Optional[str] = None,
        keyword_guideline_id: Optional[str] = None,
        title_guideline_id: Optional[str] = None,
        blog_guideline_id: Optional[str] = None
    ) -> Site:
        """새 사이트 등록"""
        
        app_logger.info(f"새 사이트 등록 시작: {name} ({url})")
        
        try:
            # WordPress 비밀번호 암호화
            encrypted_password = None
            if wordpress_password:
                encrypted_password = self.encrypt_password(wordpress_password)
            
            # 사이트 생성
            site = Site(
                name=name,
                url=url,
                description=description,
                category=category,
                wordpress_url=wordpress_url,
                wordpress_username=wordpress_username,
                wordpress_password_encrypted=encrypted_password,
                keyword_guideline_id=keyword_guideline_id,
                title_guideline_id=title_guideline_id,
                blog_guideline_id=blog_guideline_id,
                created_by=user_id
            )
            
            db.add(site)
            db.commit()
            db.refresh(site)
            
            app_logger.info(f"사이트 등록 완료: {site.id}")
            return site
            
        except Exception as e:
            db.rollback()
            app_logger.error(f"사이트 등록 실패: {e}")
            raise
    
    async def get_user_sites(self, db: Session, user_id: str) -> List[Site]:
        """사용자의 사이트 목록 조회"""
        try:
            sites = db.query(Site).filter(
                and_(
                    Site.created_by == user_id,
                    Site.is_active == True
                )
            ).order_by(Site.created_at.desc()).all()
            
            return sites
        except Exception as e:
            app_logger.error(f"사이트 목록 조회 실패: {e}")
            raise
    
    async def get_site_by_id(self, db: Session, site_id: str, user_id: str) -> Optional[Site]:
        """사이트 상세 정보 조회"""
        try:
            site = db.query(Site).filter(
                and_(
                    Site.id == site_id,
                    Site.created_by == user_id,
                    Site.is_active == True
                )
            ).first()
            
            return site
        except Exception as e:
            app_logger.error(f"사이트 조회 실패: {e}")
            raise
    
    async def update_site(
        self,
        db: Session,
        site_id: str,
        user_id: str,
        **update_data
    ) -> Optional[Site]:
        """사이트 정보 수정"""
        
        app_logger.info(f"사이트 수정 시작: {site_id}")
        
        try:
            site = await self.get_site_by_id(db, site_id, user_id)
            if not site:
                return None
            
            # WordPress 비밀번호가 포함되어 있으면 암호화
            if 'wordpress_password' in update_data:
                password = update_data.pop('wordpress_password')
                if password:
                    update_data['wordpress_password_encrypted'] = self.encrypt_password(password)
                else:
                    update_data['wordpress_password_encrypted'] = None
            
            # 필드 업데이트
            for field, value in update_data.items():
                if hasattr(site, field):
                    setattr(site, field, value)
            
            site.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(site)
            
            app_logger.info(f"사이트 수정 완료: {site_id}")
            return site
            
        except Exception as e:
            db.rollback()
            app_logger.error(f"사이트 수정 실패: {e}")
            raise
    
    async def delete_site(self, db: Session, site_id: str, user_id: str) -> bool:
        """사이트 삭제 (소프트 삭제)"""
        
        app_logger.info(f"사이트 삭제 시작: {site_id}")
        
        try:
            site = await self.get_site_by_id(db, site_id, user_id)
            if not site:
                return False
            
            site.is_active = False
            site.updated_at = datetime.utcnow()
            db.commit()
            
            app_logger.info(f"사이트 삭제 완료: {site_id}")
            return True
            
        except Exception as e:
            db.rollback()
            app_logger.error(f"사이트 삭제 실패: {e}")
            raise
    
    async def test_wordpress_connection(
        self, 
        wordpress_url: str, 
        username: str, 
        password: str
    ) -> Dict[str, Any]:
        """WordPress 연결 테스트"""
        
        app_logger.info(f"WordPress 연결 테스트: {wordpress_url}")
        
        try:
            # WordPress REST API 엔드포인트 준비
            api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2"
            
            # 기본 인증 정보
            auth = aiohttp.BasicAuth(username, password)
            
            async with aiohttp.ClientSession() as session:
                # 사용자 정보 조회로 인증 테스트
                async with session.get(
                    f"{api_url}/users/me",
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        user_data = await response.json()
                        return {
                            "success": True,
                            "message": "WordPress 연결 성공",
                            "user_info": {
                                "id": user_data.get("id"),
                                "name": user_data.get("name"),
                                "email": user_data.get("email"),
                                "roles": user_data.get("roles", [])
                            }
                        }
                    elif response.status == 401:
                        return {
                            "success": False,
                            "message": "인증 실패: 사용자명 또는 비밀번호를 확인하세요"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"연결 실패 (HTTP {response.status}): {error_text[:200]}"
                        }
                        
        except aiohttp.ClientError as e:
            app_logger.error(f"WordPress 연결 테스트 실패: {e}")
            return {
                "success": False,
                "message": f"연결 오류: {str(e)}"
            }
        except Exception as e:
            app_logger.error(f"WordPress 연결 테스트 예외: {e}")
            return {
                "success": False,
                "message": f"예상치 못한 오류: {str(e)}"
            }
    
    async def get_available_guidelines(self, db: Session) -> Dict[str, List[Dict]]:
        """사용 가능한 지침 목록 조회"""
        try:
            # 활성화된 지침들 조회
            guidelines = db.query(SystemPrompt).filter(
                SystemPrompt.is_active == True
            ).order_by(SystemPrompt.prompt_type, SystemPrompt.created_at.desc()).all()
            
            # 타입별로 그룹화
            result = {
                "keyword_analysis": [],
                "title_generation": [],
                "blog_writing": []
            }
            
            for guideline in guidelines:
                guideline_data = {
                    "id": guideline.id,
                    "name": guideline.name,
                    "description": guideline.description,
                    "created_at": guideline.created_at.isoformat(),
                    "is_default": guideline.is_default
                }
                
                prompt_type = guideline.prompt_type.value
                if prompt_type in result:
                    result[prompt_type].append(guideline_data)
            
            return result
            
        except Exception as e:
            app_logger.error(f"지침 목록 조회 실패: {e}")
            raise
    
    async def get_site_statistics(self, db: Session, site_id: str, user_id: str) -> Dict[str, Any]:
        """사이트 통계 정보 조회"""
        try:
            site = await self.get_site_by_id(db, site_id, user_id)
            if not site:
                return {}
            
            return {
                "total_keywords_generated": site.total_keywords_generated,
                "total_titles_generated": site.total_titles_generated,
                "total_posts_generated": site.total_posts_generated,
                "total_posts_published": site.total_posts_published,
                "success_rate": (
                    site.total_posts_published / site.total_posts_generated * 100
                    if site.total_posts_generated > 0 else 0
                ),
                "last_activity": site.updated_at.isoformat() if site.updated_at else None
            }
            
        except Exception as e:
            app_logger.error(f"사이트 통계 조회 실패: {e}")
            raise

# 싱글톤 인스턴스
site_manager = SiteManager()