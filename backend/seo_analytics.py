from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import Keyword, GeneratedTitle, GeneratedContent, User
import statistics

class SEOAnalytics:
    """SEO 분석 및 리포팅 클래스"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_keyword_performance(self, user_id: str, days: int = 30) -> Dict:
        """키워드 성과 분석"""
        since_date = datetime.now() - timedelta(days=days)
        
        # 키워드 분석 통계
        keywords = self.db.query(Keyword).filter(
            Keyword.created_by == user_id,
            Keyword.created_at >= since_date
        ).all()
        
        if not keywords:
            return {
                "total_keywords": 0,
                "avg_search_volume": 0,
                "avg_opportunity_score": 0,
                "competition_distribution": {},
                "top_keywords": []
            }
        
        # 통계 계산
        search_volumes = [k.search_volume for k in keywords]
        opportunity_scores = [k.opportunity_score for k in keywords if k.opportunity_score]
        
        # 경쟁도 분포
        competition_dist = {}
        for keyword in keywords:
            comp = keyword.competition or "Unknown"
            competition_dist[comp] = competition_dist.get(comp, 0) + 1
        
        # 상위 키워드 (기회점수 기준)
        top_keywords = sorted(
            keywords, 
            key=lambda x: x.opportunity_score or 0, 
            reverse=True
        )[:10]
        
        return {
            "total_keywords": len(keywords),
            "avg_search_volume": statistics.mean(search_volumes) if search_volumes else 0,
            "avg_opportunity_score": statistics.mean(opportunity_scores) if opportunity_scores else 0,
            "competition_distribution": competition_dist,
            "top_keywords": [
                {
                    "keyword": k.keyword,
                    "search_volume": k.search_volume,
                    "opportunity_score": k.opportunity_score,
                    "competition": k.competition
                }
                for k in top_keywords
            ]
        }
    
    def get_content_analytics(self, user_id: str, days: int = 30) -> Dict:
        """콘텐츠 분석 데이터"""
        since_date = datetime.now() - timedelta(days=days)
        
        contents = self.db.query(GeneratedContent).filter(
            GeneratedContent.created_by == user_id,
            GeneratedContent.created_at >= since_date
        ).all()
        
        if not contents:
            return {
                "total_content": 0,
                "avg_seo_score": 0,
                "avg_geo_score": 0,
                "content_by_day": [],
                "seo_score_distribution": {}
            }
        
        # SEO 점수 통계
        seo_scores = [c.seo_score for c in contents if c.seo_score]
        geo_scores = [c.geo_score for c in contents if c.geo_score]
        
        # 일별 콘텐츠 생성량
        content_by_day = self._get_daily_counts(contents, days)
        
        # SEO 점수 분포
        seo_distribution = {}
        for content in contents:
            if content.seo_score:
                score_range = self._get_score_range(content.seo_score)
                seo_distribution[score_range] = seo_distribution.get(score_range, 0) + 1
        
        return {
            "total_content": len(contents),
            "avg_seo_score": statistics.mean(seo_scores) if seo_scores else 0,
            "avg_geo_score": statistics.mean(geo_scores) if geo_scores else 0,
            "content_by_day": content_by_day,
            "seo_score_distribution": seo_distribution
        }
    
    def get_title_analytics(self, user_id: str, days: int = 30) -> Dict:
        """제목 분석 데이터"""
        since_date = datetime.now() - timedelta(days=days)
        
        titles = self.db.query(GeneratedTitle).filter(
            GeneratedTitle.created_by == user_id,
            GeneratedTitle.created_at >= since_date
        ).all()
        
        if not titles:
            return {
                "total_titles": 0,
                "avg_duplicate_rate": 0,
                "language_distribution": {},
                "tone_distribution": {},
                "titles_by_day": []
            }
        
        # 중복률 통계
        duplicate_rates = [t.duplicate_rate for t in titles if t.duplicate_rate]
        
        # 언어 분포
        lang_dist = {}
        for title in titles:
            lang = title.language or "unknown"
            lang_dist[lang] = lang_dist.get(lang, 0) + 1
        
        # 톤 분포
        tone_dist = {}
        for title in titles:
            tone = title.tone or "unknown"
            tone_dist[tone] = tone_dist.get(tone, 0) + 1
        
        # 일별 제목 생성량
        titles_by_day = self._get_daily_counts(titles, days)
        
        return {
            "total_titles": len(titles),
            "avg_duplicate_rate": statistics.mean(duplicate_rates) if duplicate_rates else 0,
            "language_distribution": lang_dist,
            "tone_distribution": tone_dist,
            "titles_by_day": titles_by_day
        }
    
    def get_productivity_metrics(self, user_id: str, days: int = 30) -> Dict:
        """생산성 지표"""
        since_date = datetime.now() - timedelta(days=days)
        
        # 각 활동별 카운트
        keywords_count = self.db.query(func.count(Keyword.id)).filter(
            Keyword.created_by == user_id,
            Keyword.created_at >= since_date
        ).scalar()
        
        titles_count = self.db.query(func.count(GeneratedTitle.id)).filter(
            GeneratedTitle.created_by == user_id,
            GeneratedTitle.created_at >= since_date
        ).scalar()
        
        content_count = self.db.query(func.count(GeneratedContent.id)).filter(
            GeneratedContent.created_by == user_id,
            GeneratedContent.created_at >= since_date
        ).scalar()
        
        # 일평균 계산
        daily_avg = {
            "keywords_per_day": keywords_count / days if days > 0 else 0,
            "titles_per_day": titles_count / days if days > 0 else 0,
            "content_per_day": content_count / days if days > 0 else 0
        }
        
        # 완성률 (키워드 -> 제목 -> 콘텐츠)
        completion_rate = {
            "keyword_to_title": (titles_count / keywords_count * 100) if keywords_count > 0 else 0,
            "title_to_content": (content_count / titles_count * 100) if titles_count > 0 else 0,
            "overall_completion": (content_count / keywords_count * 100) if keywords_count > 0 else 0
        }
        
        return {
            "period_stats": {
                "keywords": keywords_count,
                "titles": titles_count,
                "content": content_count
            },
            "daily_averages": daily_avg,
            "completion_rates": completion_rate
        }
    
    def get_comprehensive_dashboard(self, user_id: str, days: int = 30) -> Dict:
        """종합 대시보드 데이터"""
        return {
            "keyword_performance": self.get_keyword_performance(user_id, days),
            "content_analytics": self.get_content_analytics(user_id, days),
            "title_analytics": self.get_title_analytics(user_id, days),
            "productivity_metrics": self.get_productivity_metrics(user_id, days),
            "period": {
                "days": days,
                "start_date": (datetime.now() - timedelta(days=days)).isoformat(),
                "end_date": datetime.now().isoformat()
            }
        }
    
    def _get_daily_counts(self, items: List, days: int) -> List[Dict]:
        """일별 카운트 데이터 생성"""
        daily_counts = {}
        
        # 지난 N일 동안의 날짜 초기화
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            daily_counts[date_str] = 0
        
        # 실제 데이터 카운트
        for item in items:
            if item.created_at:
                date_str = item.created_at.strftime("%Y-%m-%d")
                if date_str in daily_counts:
                    daily_counts[date_str] += 1
        
        # 날짜순 정렬
        return [
            {"date": date, "count": count}
            for date, count in sorted(daily_counts.items())
        ]
    
    def _get_score_range(self, score: int) -> str:
        """점수를 범위로 분류"""
        if score >= 90:
            return "90-100 (Excellent)"
        elif score >= 80:
            return "80-89 (Good)"
        elif score >= 70:
            return "70-79 (Average)"
        elif score >= 60:
            return "60-69 (Poor)"
        else:
            return "0-59 (Very Poor)"