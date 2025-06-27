"""
자동화 워크플로우 엔진
카테고리 → 키워드 → 제목 → 블로그 글 → 포스팅까지 완전 자동화
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from models import (
    Site, AutomationSession, GeneratedKeywordBatch, 
    GeneratedTitleBatch, PostingResult, SystemPrompt
)
from seo_keyword_analyzer import SEOKeywordAnalyzer
from advanced_title_generator import AdvancedTitleGenerator
from advanced_blog_writer import AdvancedBlogWriter
from logger import app_logger, ai_logger
from wordpress_api import WordPressAPI

class AutomationEngine:
    def __init__(self):
        self.keyword_analyzer = SEOKeywordAnalyzer()
        self.title_generator = AdvancedTitleGenerator()
        self.blog_writer = AdvancedBlogWriter()
        self.wordpress_api = WordPressAPI()
        
        # 카테고리별 시드 키워드 맵핑
        self.category_seeds = {
            "여행": ["국내여행", "해외여행", "제주도", "부산", "강릉", "경주", "여행코스", "맛집", "숙박", "관광명소"],
            "맛집": ["맛집추천", "카페", "레스토랑", "디저트", "브런치", "야식", "배달음식", "홈카페", "요리", "레시피"],
            "패션": ["패션", "코디", "스타일링", "옷", "신발", "가방", "액세서리", "뷰티", "화장품", "네일"],
            "IT": ["프로그래밍", "개발", "앱", "소프트웨어", "하드웨어", "스마트폰", "노트북", "게임", "AI", "블록체인"],
            "건강": ["건강", "운동", "다이어트", "요가", "헬스", "영양", "의학", "병원", "약", "건강관리"],
            "라이프스타일": ["인테리어", "취미", "독서", "영화", "음악", "반려동물", "육아", "결혼", "데이트", "선물"],
            "금융": ["투자", "재테크", "주식", "부동산", "보험", "대출", "펀드", "가상화폐", "경제", "금융상품"],
            "교육": ["공부", "학습", "시험", "자격증", "영어", "온라인강의", "책", "교육", "진로", "취업"]
        }
    
    async def start_automation_session(
        self, 
        db: Session, 
        site_id: str, 
        user_id: str, 
        category: str,
        auto_posting: bool = False
    ) -> AutomationSession:
        """자동화 세션 시작"""
        
        app_logger.info(f"자동화 세션 시작: site={site_id}, category={category}")
        
        try:
            # 새 세션 생성
            session = AutomationSession(
                site_id=site_id,
                category=category,
                step_status="started",
                auto_posting_enabled=auto_posting,
                created_by=user_id
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            app_logger.info(f"자동화 세션 생성 완료: {session.id}")
            return session
            
        except Exception as e:
            db.rollback()
            app_logger.error(f"자동화 세션 시작 실패: {e}")
            raise
    
    async def generate_category_keywords(
        self,
        db: Session,
        session_id: str,
        category: str,
        count: int = 20,
        use_trends: bool = True
    ) -> Dict[str, Any]:
        """카테고리 기반 키워드 자동 생성"""
        
        ai_logger.info(f"카테고리 키워드 생성 시작: {category}, 개수: {count}")
        
        try:
            # 세션 조회
            session = db.query(AutomationSession).filter(
                AutomationSession.id == session_id
            ).first()
            
            if not session:
                raise ValueError("세션을 찾을 수 없습니다")
            
            # 사이트 정보 조회
            site = db.query(Site).filter(Site.id == session.site_id).first()
            if not site:
                raise ValueError("사이트를 찾을 수 없습니다")
            
            # 지침 로드
            guideline = None
            if site.keyword_guideline_id:
                guideline_obj = db.query(SystemPrompt).filter(
                    SystemPrompt.id == site.keyword_guideline_id
                ).first()
                if guideline_obj:
                    guideline = guideline_obj.prompt_content
            
            # 카테고리 시드 키워드 가져오기
            seed_keywords = self.category_seeds.get(category, [category])
            
            # 키워드 생성 결과 저장
            all_keywords = []
            
            # 각 시드 키워드에 대해 키워드 분석 수행
            for seed in seed_keywords[:5]:  # 상위 5개 시드만 사용
                try:
                    keywords = await self.keyword_analyzer.analyze_seo_keywords(
                        seed, category, db_session=db
                    )
                    
                    for kw in keywords:
                        keyword_data = {
                            "keyword": kw.keyword,
                            "search_volume": kw.search_volume,
                            "competition": kw.competition,
                            "seasonal": kw.seasonal,
                            "reason": kw.reason,
                            "seo_score": kw.score,
                            "trend_score": random.uniform(70, 95),  # 트렌드 점수 (실제로는 API 연동)
                            "category": category,
                            "seed_keyword": seed
                        }
                        all_keywords.append(keyword_data)
                        
                except Exception as e:
                    ai_logger.warning(f"시드 키워드 '{seed}' 분석 실패: {e}")
                    continue
            
            # 점수 기반 정렬 및 상위 N개 선택
            all_keywords.sort(key=lambda x: x["seo_score"] + x["trend_score"], reverse=True)
            selected_keywords = all_keywords[:count]
            
            # 통계 계산
            avg_seo_score = sum(kw["seo_score"] for kw in selected_keywords) / len(selected_keywords) if selected_keywords else 0
            avg_trend_score = sum(kw["trend_score"] for kw in selected_keywords) / len(selected_keywords) if selected_keywords else 0
            
            # 배치 결과 저장
            keyword_batch = GeneratedKeywordBatch(
                session_id=session_id,
                category=category,
                keywords_data=json.dumps(selected_keywords, ensure_ascii=False),
                total_count=len(selected_keywords),
                average_seo_score=avg_seo_score,
                average_trend_score=avg_trend_score,
                generation_params=json.dumps({
                    "count": count,
                    "use_trends": use_trends,
                    "seed_keywords": seed_keywords[:5]
                }, ensure_ascii=False),
                guideline_used=site.keyword_guideline_id
            )
            
            db.add(keyword_batch)
            
            # 세션 업데이트
            session.generated_keywords = json.dumps(selected_keywords, ensure_ascii=False)
            session.keywords_count = len(selected_keywords)
            session.step_status = "keywords_generated"
            session.updated_at = datetime.utcnow()
            
            # 사이트 통계 업데이트
            site.total_keywords_generated += len(selected_keywords)
            
            db.commit()
            
            ai_logger.info(f"카테고리 키워드 생성 완료: {len(selected_keywords)}개")
            
            return {
                "session_id": session_id,
                "category": category,
                "keywords": selected_keywords,
                "total_count": len(selected_keywords),
                "average_seo_score": avg_seo_score,
                "average_trend_score": avg_trend_score,
                "status": "success"
            }
            
        except Exception as e:
            db.rollback()
            ai_logger.error(f"카테고리 키워드 생성 실패: {e}")
            raise
    
    async def generate_keyword_titles(
        self,
        db: Session,
        session_id: str,
        selected_keywords: List[str],
        titles_per_keyword: int = 10
    ) -> Dict[str, Any]:
        """선택된 키워드들로 제목 자동 생성"""
        
        ai_logger.info(f"키워드 제목 생성 시작: {len(selected_keywords)}개 키워드")
        
        try:
            # 세션 조회
            session = db.query(AutomationSession).filter(
                AutomationSession.id == session_id
            ).first()
            
            if not session:
                raise ValueError("세션을 찾을 수 없습니다")
            
            # 사이트 정보 조회
            site = db.query(Site).filter(Site.id == session.site_id).first()
            
            # 지침 로드
            guideline = None
            if site.title_guideline_id:
                guideline_obj = db.query(SystemPrompt).filter(
                    SystemPrompt.id == site.title_guideline_id
                ).first()
                if guideline_obj:
                    guideline = guideline_obj.prompt_content
            
            all_titles = []
            title_batches = []
            
            # 각 키워드에 대해 제목 생성
            for keyword in selected_keywords:
                try:
                    # 제목 생성
                    titles = await self.title_generator.generate_advanced_titles(
                        keyword=keyword,
                        count=titles_per_keyword,
                        guidelines=guideline
                    )
                    
                    # 제목 데이터 변환
                    title_data = []
                    for title in titles:
                        title_info = {
                            "title": title.title,
                            "seo_score": title.seo_score,
                            "viral_score": title.viral_potential,
                            "geo_score": title.geo_score,
                            "click_potential": title.total_score,
                            "length": len(title.title),
                            "format_type": title.format_type,
                            "keyword": keyword
                        }
                        title_data.append(title_info)
                        all_titles.append(title_info)
                    
                    # 배치별 통계 계산
                    avg_viral = sum(t["viral_score"] for t in title_data) / len(title_data) if title_data else 0
                    avg_seo = sum(t["seo_score"] for t in title_data) / len(title_data) if title_data else 0
                    avg_click = sum(t["click_potential"] for t in title_data) / len(title_data) if title_data else 0
                    
                    # 배치 결과 저장
                    title_batch = GeneratedTitleBatch(
                        session_id=session_id,
                        keyword=keyword,
                        titles_data=json.dumps(title_data, ensure_ascii=False),
                        total_count=len(title_data),
                        average_viral_score=avg_viral,
                        average_seo_score=avg_seo,
                        average_click_potential=avg_click,
                        generation_params=json.dumps({
                            "titles_per_keyword": titles_per_keyword,
                            "guideline_used": bool(guideline)
                        }, ensure_ascii=False),
                        guideline_used=site.title_guideline_id
                    )
                    
                    title_batches.append(title_batch)
                    
                except Exception as e:
                    ai_logger.warning(f"키워드 '{keyword}' 제목 생성 실패: {e}")
                    continue
            
            # 모든 배치 저장
            for batch in title_batches:
                db.add(batch)
            
            # 세션 업데이트
            session.generated_titles = json.dumps(all_titles, ensure_ascii=False)
            session.selected_keywords = json.dumps(selected_keywords, ensure_ascii=False)
            session.titles_count = len(all_titles)
            session.step_status = "titles_generated"
            session.updated_at = datetime.utcnow()
            
            # 사이트 통계 업데이트
            site.total_titles_generated += len(all_titles)
            
            db.commit()
            
            ai_logger.info(f"키워드 제목 생성 완료: {len(all_titles)}개")
            
            return {
                "session_id": session_id,
                "keywords": selected_keywords,
                "titles": all_titles,
                "total_count": len(all_titles),
                "titles_per_keyword": titles_per_keyword,
                "status": "success"
            }
            
        except Exception as e:
            db.rollback()
            ai_logger.error(f"키워드 제목 생성 실패: {e}")
            raise
    
    async def generate_title_contents(
        self,
        db: Session,
        session_id: str,
        selected_titles: List[str]
    ) -> Dict[str, Any]:
        """선택된 제목들로 블로그 글 자동 생성"""
        
        ai_logger.info(f"제목 블로그 글 생성 시작: {len(selected_titles)}개 제목")
        
        try:
            # 세션 조회
            session = db.query(AutomationSession).filter(
                AutomationSession.id == session_id
            ).first()
            
            if not session:
                raise ValueError("세션을 찾을 수 없습니다")
            
            # 사이트 정보 조회
            site = db.query(Site).filter(Site.id == session.site_id).first()
            
            # 지침 로드
            guideline = None
            if site.blog_guideline_id:
                guideline_obj = db.query(SystemPrompt).filter(
                    SystemPrompt.id == site.blog_guideline_id
                ).first()
                if guideline_obj:
                    guideline = guideline_obj.prompt_content
            
            generated_contents = []
            
            # 각 제목에 대해 블로그 글 생성
            for title in selected_titles:
                try:
                    # 블로그 글 생성
                    content_result = await self.blog_writer.generate_blog_content(
                        title=title,
                        guidelines=guideline
                    )
                    
                    # 콘텐츠 데이터 변환
                    content_data = {
                        "title": title,
                        "content": content_result.content,
                        "seo_keywords": content_result.seo_keywords,
                        "lsi_keywords": content_result.lsi_keywords,
                        "word_count": content_result.word_count,
                        "seo_score": content_result.seo_score,
                        "geo_score": content_result.geo_optimization_score,
                        "readability_score": content_result.readability_score,
                        "subtopics": content_result.subtopics,
                        "generated_at": datetime.utcnow().isoformat()
                    }
                    
                    generated_contents.append(content_data)
                    
                except Exception as e:
                    ai_logger.warning(f"제목 '{title}' 블로그 글 생성 실패: {e}")
                    continue
            
            # 세션 업데이트
            session.generated_contents = json.dumps(generated_contents, ensure_ascii=False)
            session.selected_titles = json.dumps(selected_titles, ensure_ascii=False)
            session.contents_count = len(generated_contents)
            session.step_status = "content_generated"
            session.updated_at = datetime.utcnow()
            
            # 사이트 통계 업데이트
            site.total_posts_generated += len(generated_contents)
            
            db.commit()
            
            ai_logger.info(f"제목 블로그 글 생성 완료: {len(generated_contents)}개")
            
            return {
                "session_id": session_id,
                "titles": selected_titles,
                "contents": generated_contents,
                "total_count": len(generated_contents),
                "status": "success"
            }
            
        except Exception as e:
            db.rollback()
            ai_logger.error(f"제목 블로그 글 생성 실패: {e}")
            raise
    
    async def publish_contents(
        self,
        db: Session,
        session_id: str,
        selected_content_titles: List[str],
        schedule_settings: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """생성된 블로그 글들을 WordPress에 자동 포스팅"""
        
        app_logger.info(f"자동 포스팅 시작: {len(selected_content_titles)}개 글")
        
        try:
            # 세션 조회
            session = db.query(AutomationSession).filter(
                AutomationSession.id == session_id
            ).first()
            
            if not session:
                raise ValueError("세션을 찾을 수 없습니다")
            
            # 사이트 정보 조회
            site = db.query(Site).filter(Site.id == session.site_id).first()
            if not site or not site.wordpress_url:
                raise ValueError("WordPress 연동 정보가 없습니다")
            
            # 생성된 콘텐츠 로드
            if not session.generated_contents:
                raise ValueError("생성된 콘텐츠가 없습니다")
            
            contents = json.loads(session.generated_contents)
            selected_contents = [
                content for content in contents 
                if content["title"] in selected_content_titles
            ]
            
            if not selected_contents:
                raise ValueError("선택된 콘텐츠가 없습니다")
            
            # WordPress API 초기화
            from site_manager import site_manager
            wp_password = site_manager.decrypt_password(site.wordpress_password_encrypted)
            
            self.wordpress_api.setup(
                site.wordpress_url,
                site.wordpress_username,
                wp_password
            )
            
            posting_results = []
            successful_posts = 0
            
            # 각 콘텐츠 포스팅
            for i, content in enumerate(selected_contents):
                try:
                    # 스케줄 설정 처리
                    post_time = None
                    if schedule_settings and not schedule_settings.get("immediate", True):
                        delay_minutes = schedule_settings.get("start_delay_minutes", 0)
                        interval_minutes = schedule_settings.get("interval_minutes", 30)
                        post_time = datetime.utcnow() + timedelta(
                            minutes=delay_minutes + (i * interval_minutes)
                        )
                    
                    # WordPress 포스팅
                    post_result = await self.wordpress_api.publish_post(
                        title=content["title"],
                        content=content["content"],
                        scheduled_time=post_time
                    )
                    
                    # 포스팅 결과 저장
                    posting_result = PostingResult(
                        session_id=session_id,
                        site_id=session.site_id,
                        title=content["title"],
                        content=content["content"],
                        wordpress_post_id=post_result.get("post_id"),
                        post_url=post_result.get("post_url"),
                        post_status=post_result.get("status", "published"),
                        scheduled_time=post_time,
                        posted_time=datetime.utcnow() if not post_time else None,
                        posting_params=json.dumps(schedule_settings or {}, ensure_ascii=False)
                    )
                    
                    db.add(posting_result)
                    
                    posting_results.append({
                        "title": content["title"],
                        "status": "success",
                        "post_id": post_result.get("post_id"),
                        "post_url": post_result.get("post_url"),
                        "scheduled_time": post_time.isoformat() if post_time else None
                    })
                    
                    successful_posts += 1
                    
                except Exception as e:
                    app_logger.error(f"포스팅 실패 - 제목: {content['title']}, 오류: {e}")
                    
                    # 실패 결과 저장
                    posting_result = PostingResult(
                        session_id=session_id,
                        site_id=session.site_id,
                        title=content["title"],
                        content=content["content"],
                        post_status="failed",
                        error_message=str(e),
                        posting_params=json.dumps(schedule_settings or {}, ensure_ascii=False)
                    )
                    
                    db.add(posting_result)
                    
                    posting_results.append({
                        "title": content["title"],
                        "status": "failed",
                        "error": str(e)
                    })
            
            # 세션 업데이트
            session.posted_contents = json.dumps(posting_results, ensure_ascii=False)
            session.published_count = successful_posts
            session.step_status = "published" if successful_posts > 0 else "failed"
            if successful_posts == len(selected_contents):
                session.step_status = "completed"
                session.completed_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            
            # 사이트 통계 업데이트
            site.total_posts_published += successful_posts
            
            db.commit()
            
            app_logger.info(f"자동 포스팅 완료: 성공 {successful_posts}/{len(selected_contents)}개")
            
            return {
                "session_id": session_id,
                "total_requested": len(selected_contents),
                "successful": successful_posts,
                "failed": len(selected_contents) - successful_posts,
                "results": posting_results,
                "status": "completed" if successful_posts > 0 else "failed"
            }
            
        except Exception as e:
            db.rollback()
            app_logger.error(f"자동 포스팅 실패: {e}")
            raise
    
    async def get_session_status(self, db: Session, session_id: str) -> Dict[str, Any]:
        """자동화 세션 상태 조회"""
        try:
            session = db.query(AutomationSession).filter(
                AutomationSession.id == session_id
            ).first()
            
            if not session:
                return {"error": "세션을 찾을 수 없습니다"}
            
            result = {
                "session_id": session_id,
                "site_id": session.site_id,
                "category": session.category,
                "step_status": session.step_status,
                "keywords_count": session.keywords_count,
                "titles_count": session.titles_count,
                "contents_count": session.contents_count,
                "published_count": session.published_count,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat() if session.updated_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            }
            
            # 생성된 데이터 포함 (필요한 경우)
            if session.generated_keywords:
                result["keywords"] = json.loads(session.generated_keywords)
            if session.generated_titles:
                result["titles"] = json.loads(session.generated_titles)
            if session.generated_contents:
                result["contents"] = json.loads(session.generated_contents)
            if session.posted_contents:
                result["posting_results"] = json.loads(session.posted_contents)
            
            return result
            
        except Exception as e:
            app_logger.error(f"세션 상태 조회 실패: {e}")
            raise

# 싱글톤 인스턴스
automation_engine = AutomationEngine()