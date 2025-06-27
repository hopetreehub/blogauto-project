"""
통합 키워드 분석 서비스
네이버 DataLab + Google Ads + 기존 SEO 분석을 통합한 종합 키워드 분석
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from naver_datalab_service import NaverDataLabService
from google_ads_service import GoogleAdsKeywordService, IntegratedKeywordAnalyzer
from seo_keyword_analyzer import SEOKeywordAnalyzer, SEOKeyword

@dataclass
class IntegratedKeywordResult:
    keyword: str
    
    # 네이버 데이터
    naver_trend_ratio: float
    naver_trend_direction: str
    naver_seasonal: bool
    naver_competition: str
    
    # Google 데이터
    google_monthly_searches: int
    google_competition: str
    google_cpc_low: float
    google_cpc_high: float
    google_difficulty: int
    
    # SEO 분석 데이터
    seo_score: float
    seo_reason: str
    
    # 통합 점수
    integrated_score: float
    recommended_priority: str
    content_opportunity: str

class IntegratedKeywordService:
    def __init__(self):
        self.naver_service = NaverDataLabService()
        self.google_service = GoogleAdsKeywordService()
        self.seo_analyzer = SEOKeywordAnalyzer()
        self.integrated_analyzer = IntegratedKeywordAnalyzer()
    
    async def comprehensive_analysis(self, item_name: str, category: str, include_variations: bool = True) -> Dict[str, Any]:
        """
        종합 키워드 분석 수행
        
        Args:
            item_name: 분석할 아이템 이름
            category: 카테고리
            include_variations: 변형 키워드 포함 여부
        """
        print(f"🔍 종합 키워드 분석 시작: {item_name} ({category})")
        
        # 1. 기본 시드 키워드 생성
        seed_keywords = self._generate_seed_keywords(item_name, category)
        
        # 2. 각 서비스별 분석 병렬 실행
        tasks = [
            self._analyze_with_naver(seed_keywords),
            self._analyze_with_google(seed_keywords, category),
            self._analyze_with_seo(item_name, category)
        ]
        
        naver_results, google_results, seo_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. 에러 처리
        if isinstance(naver_results, Exception):
            print(f"⚠️ 네이버 분석 오류: {naver_results}")
            naver_results = {}
        
        if isinstance(google_results, Exception):
            print(f"⚠️ Google 분석 오류: {google_results}")
            google_results = {'google_keyword_ideas': []}
        
        if isinstance(seo_results, Exception):
            print(f"⚠️ SEO 분석 오류: {seo_results}")
            seo_results = []
        
        # 4. 결과 통합
        integrated_results = self._integrate_results(
            seed_keywords, naver_results, google_results, seo_results
        )
        
        # 5. 최종 분석 리포트 생성
        analysis_report = {
            'analysis_metadata': {
                'item_name': item_name,
                'category': category,
                'analysis_date': datetime.now().isoformat(),
                'data_sources': ['naver_datalab', 'google_ads', 'seo_analyzer']
            },
            'keyword_analysis': integrated_results,
            'strategic_insights': self._generate_strategic_insights(integrated_results),
            'content_recommendations': self._generate_content_recommendations(integrated_results),
            'ranking_opportunities': self._identify_ranking_opportunities(integrated_results),
            'competitive_analysis': self._analyze_competition_landscape(integrated_results)
        }
        
        print(f"✅ 종합 분석 완료: {len(integrated_results)}개 키워드 분석")
        return analysis_report
    
    def _generate_seed_keywords(self, item_name: str, category: str) -> List[str]:
        """시드 키워드 생성"""
        seed_keywords = [
            item_name,
            f"{item_name} 추천",
            f"{item_name} 리뷰",
            f"{item_name} 후기",
            f"{category} {item_name}",
            f"2025 {item_name}",
            f"최고의 {item_name}",
            f"{item_name} 가격",
            f"{item_name} 비교",
            f"인기 {item_name}"
        ]
        return list(set(seed_keywords))  # 중복 제거
    
    async def _analyze_with_naver(self, keywords: List[str]) -> Dict[str, Any]:
        """네이버 DataLab 분석"""
        try:
            # 네이버는 최대 5개 키워드만 처리 가능
            naver_keywords = keywords[:5]
            trend_data = await self.naver_service.get_search_trend(naver_keywords)
            competition_data = await self.naver_service.analyze_keyword_competition(naver_keywords)
            
            return {
                'trend_data': trend_data,
                'competition_data': competition_data
            }
        except Exception as e:
            print(f"네이버 분석 중 오류: {e}")
            return {}
    
    async def _analyze_with_google(self, keywords: List[str], category: str) -> Dict[str, Any]:
        """Google Ads 분석"""
        try:
            return await self.integrated_analyzer.comprehensive_keyword_analysis(keywords, category)
        except Exception as e:
            print(f"Google 분석 중 오류: {e}")
            return {'google_keyword_ideas': []}
    
    async def _analyze_with_seo(self, item_name: str, category: str) -> List[SEOKeyword]:
        """SEO 분석"""
        try:
            return await self.seo_analyzer.analyze_seo_keywords(item_name, category)
        except Exception as e:
            print(f"SEO 분석 중 오류: {e}")
            return []
    
    def _integrate_results(self, seed_keywords: List[str], naver_data: Dict, google_data: Dict, seo_data: List[SEOKeyword]) -> List[IntegratedKeywordResult]:
        """각 서비스 결과를 통합"""
        integrated_results = []
        
        # 모든 키워드를 수집
        all_keywords = set(seed_keywords)
        
        # Google 키워드 추가
        for google_idea in google_data.get('google_keyword_ideas', []):
            all_keywords.add(google_idea['keyword'])
        
        # SEO 키워드 추가
        for seo_keyword in seo_data:
            all_keywords.add(seo_keyword.keyword)
        
        # 각 키워드에 대해 통합 분석 수행
        for keyword in all_keywords:
            # 네이버 데이터 찾기
            naver_info = naver_data.get('trend_data', {}).get(keyword, {})
            naver_comp = naver_data.get('competition_data', {}).get(keyword, {})
            
            # Google 데이터 찾기
            google_info = None
            for g_idea in google_data.get('google_keyword_ideas', []):
                if g_idea['keyword'] == keyword:
                    google_info = g_idea
                    break
            
            # SEO 데이터 찾기
            seo_info = None
            for seo_kw in seo_data:
                if seo_kw.keyword == keyword:
                    seo_info = seo_kw
                    break
            
            # 통합 결과 생성
            integrated_result = self._create_integrated_result(keyword, naver_info, naver_comp, google_info, seo_info)
            integrated_results.append(integrated_result)
        
        # 통합 점수 순으로 정렬
        integrated_results.sort(key=lambda x: x.integrated_score, reverse=True)
        return integrated_results[:15]  # 상위 15개만 반환
    
    def _create_integrated_result(self, keyword: str, naver_trend: Dict, naver_comp: Dict, google_info: Dict, seo_info: SEOKeyword) -> IntegratedKeywordResult:
        """개별 키워드의 통합 결과 생성"""
        
        # 네이버 데이터 추출
        naver_trend_ratio = naver_trend.get('avg_ratio', 0)
        naver_trend_direction = naver_trend.get('trend_direction', 'unknown')
        naver_seasonal = naver_trend.get('seasonal_pattern', False)
        naver_competition = naver_comp.get('competition_level', '알 수 없음')
        
        # Google 데이터 추출
        google_monthly_searches = google_info.get('monthly_searches', 0) if google_info else 0
        google_competition = google_info.get('competition', 'UNKNOWN') if google_info else 'UNKNOWN'
        google_cpc_low = google_info.get('cpc_low', 0.0) if google_info else 0.0
        google_cpc_high = google_info.get('cpc_high', 0.0) if google_info else 0.0
        google_difficulty = google_info.get('difficulty', 50) if google_info else 50
        
        # SEO 데이터 추출
        seo_score = seo_info.score if seo_info else 50.0
        seo_reason = seo_info.reason if seo_info else "기본 SEO 분석"
        
        # 통합 점수 계산
        integrated_score = self._calculate_integrated_score(
            naver_trend_ratio, google_monthly_searches, google_difficulty, seo_score
        )
        
        # 우선순위 결정
        recommended_priority = self._determine_priority(integrated_score, google_monthly_searches, google_competition)
        
        # 콘텐츠 기회 분석
        content_opportunity = self._analyze_content_opportunity(keyword, naver_seasonal, google_competition, seo_score)
        
        return IntegratedKeywordResult(
            keyword=keyword,
            naver_trend_ratio=naver_trend_ratio,
            naver_trend_direction=naver_trend_direction,
            naver_seasonal=naver_seasonal,
            naver_competition=naver_competition,
            google_monthly_searches=google_monthly_searches,
            google_competition=google_competition,
            google_cpc_low=google_cpc_low,
            google_cpc_high=google_cpc_high,
            google_difficulty=google_difficulty,
            seo_score=seo_score,
            seo_reason=seo_reason,
            integrated_score=integrated_score,
            recommended_priority=recommended_priority,
            content_opportunity=content_opportunity
        )
    
    def _calculate_integrated_score(self, naver_ratio: float, google_searches: int, google_difficulty: int, seo_score: float) -> float:
        """통합 점수 계산"""
        # 각 지표를 0-100 스케일로 정규화
        naver_score = min(100, naver_ratio * 2)  # 네이버 트렌드 비율
        google_score = min(100, google_searches / 100)  # Google 검색량
        difficulty_score = 100 - google_difficulty  # 난이도 반전 (낮을수록 좋음)
        
        # 가중 평균 계산
        weights = {
            'naver': 0.25,
            'google': 0.35,
            'difficulty': 0.20,
            'seo': 0.20
        }
        
        integrated_score = (
            naver_score * weights['naver'] +
            google_score * weights['google'] +
            difficulty_score * weights['difficulty'] +
            seo_score * weights['seo']
        )
        
        return round(integrated_score, 1)
    
    def _determine_priority(self, integrated_score: float, google_searches: int, google_competition: str) -> str:
        """우선순위 결정"""
        if integrated_score >= 80:
            return "매우 높음"
        elif integrated_score >= 70:
            return "높음"
        elif integrated_score >= 60:
            return "보통"
        elif integrated_score >= 50:
            return "낮음"
        else:
            return "매우 낮음"
    
    def _analyze_content_opportunity(self, keyword: str, seasonal: bool, competition: str, seo_score: float) -> str:
        """콘텐츠 기회 분석"""
        opportunities = []
        
        if competition in ["LOW", "낮음"]:
            opportunities.append("경쟁도 낮음")
        
        if seasonal:
            opportunities.append("계절성 트렌드")
        
        if seo_score > 70:
            opportunities.append("SEO 최적화 가능")
        
        if "리뷰" in keyword or "후기" in keyword:
            opportunities.append("구매 의도 높음")
        
        if "2025" in keyword or "최신" in keyword:
            opportunities.append("트렌드 키워드")
        
        return ", ".join(opportunities) if opportunities else "일반적 기회"
    
    def _generate_strategic_insights(self, results: List[IntegratedKeywordResult]) -> Dict[str, Any]:
        """전략적 인사이트 생성"""
        high_priority_keywords = [r for r in results if r.recommended_priority in ["매우 높음", "높음"]]
        seasonal_keywords = [r for r in results if r.naver_seasonal]
        low_competition_keywords = [r for r in results if r.google_competition in ["LOW", "낮음"]]
        
        return {
            'total_keywords_analyzed': len(results),
            'high_priority_count': len(high_priority_keywords),
            'seasonal_opportunities': len(seasonal_keywords),
            'low_competition_opportunities': len(low_competition_keywords),
            'avg_integrated_score': sum(r.integrated_score for r in results) / len(results) if results else 0,
            'top_performing_keywords': [r.keyword for r in results[:5]],
            'quick_wins': [r.keyword for r in low_competition_keywords[:3]],
            'seasonal_picks': [r.keyword for r in seasonal_keywords[:3]]
        }
    
    def _generate_content_recommendations(self, results: List[IntegratedKeywordResult]) -> List[Dict[str, str]]:
        """콘텐츠 추천 생성"""
        recommendations = []
        
        # 상위 키워드별 콘텐츠 전략 제안
        for result in results[:8]:
            content_type = "리뷰/후기" if any(word in result.keyword for word in ["리뷰", "후기"]) else \
                          "가이드/방법" if any(word in result.keyword for word in ["방법", "가이드"]) else \
                          "비교/추천" if any(word in result.keyword for word in ["비교", "추천"]) else \
                          "정보성 콘텐츠"
            
            recommendations.append({
                'keyword': result.keyword,
                'content_type': content_type,
                'priority': result.recommended_priority,
                'opportunity': result.content_opportunity,
                'target_length': "2000-3000자" if result.google_competition != "HIGH" else "3000-5000자"
            })
        
        return recommendations
    
    def _identify_ranking_opportunities(self, results: List[IntegratedKeywordResult]) -> Dict[str, List[str]]:
        """랭킹 기회 식별"""
        return {
            'immediate_opportunities': [
                r.keyword for r in results 
                if r.google_competition in ["LOW", "낮음"] and r.integrated_score > 60
            ][:5],
            'medium_term_targets': [
                r.keyword for r in results 
                if r.google_competition == "MEDIUM" and r.integrated_score > 70
            ][:5],
            'long_term_goals': [
                r.keyword for r in results 
                if r.google_monthly_searches > 5000 and r.integrated_score > 50
            ][:3]
        }
    
    def _analyze_competition_landscape(self, results: List[IntegratedKeywordResult]) -> Dict[str, Any]:
        """경쟁 환경 분석"""
        competition_distribution = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, '낮음': 0, '보통': 0, '높음': 0}
        
        for result in results:
            comp = result.google_competition
            if comp in competition_distribution:
                competition_distribution[comp] += 1
        
        avg_cpc = sum(r.google_cpc_high for r in results) / len(results) if results else 0
        
        return {
            'competition_distribution': competition_distribution,
            'avg_cpc': round(avg_cpc, 2),
            'market_competitiveness': 'high' if avg_cpc > 2.0 else 'medium' if avg_cpc > 1.0 else 'low',
            'entry_barriers': 'low' if competition_distribution.get('LOW', 0) + competition_distribution.get('낮음', 0) > len(results) * 0.3 else 'high'
        }

# 사용 예시
async def test_integrated_service():
    """통합 키워드 서비스 테스트"""
    service = IntegratedKeywordService()
    
    result = await service.comprehensive_analysis("스탠딩책상", "사무용 가구")
    
    print("=== 통합 키워드 분석 결과 ===")
    print(f"분석일시: {result['analysis_metadata']['analysis_date']}")
    print(f"아이템: {result['analysis_metadata']['item_name']}")
    print(f"카테고리: {result['analysis_metadata']['category']}")
    
    print(f"\n=== 전략적 인사이트 ===")
    insights = result['strategic_insights']
    print(f"총 분석 키워드: {insights['total_keywords_analyzed']}개")
    print(f"고우선순위 키워드: {insights['high_priority_count']}개")
    print(f"평균 통합점수: {insights['avg_integrated_score']:.1f}")
    
    print(f"\n=== 상위 키워드 ===")
    for i, keyword_result in enumerate(result['keyword_analysis'][:5], 1):
        print(f"{i}. {keyword_result.keyword}")
        print(f"   통합점수: {keyword_result.integrated_score}")
        print(f"   Google 검색량: {keyword_result.google_monthly_searches:,}/월")
        print(f"   우선순위: {keyword_result.recommended_priority}")
        print(f"   기회요소: {keyword_result.content_opportunity}")
        print()

if __name__ == "__main__":
    asyncio.run(test_integrated_service())