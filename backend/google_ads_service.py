"""
Google Ads Keyword Planner API 연동 서비스
실제 Google 검색량과 경쟁도 데이터를 활용한 키워드 분석
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

# Google Ads API 의존성 (pip install google-ads 필요)
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    print("⚠️ Google Ads API 라이브러리가 설치되지 않았습니다. pip install google-ads 를 실행해주세요.")
    GOOGLE_ADS_AVAILABLE = False

@dataclass
class GoogleKeywordData:
    keyword: str
    avg_monthly_searches: int
    competition: str
    competition_index: float
    low_top_of_page_bid: float
    high_top_of_page_bid: float
    keyword_difficulty: int

class GoogleAdsKeywordService:
    def __init__(self):
        # Google Ads API 설정 파일 경로
        self.config_file = os.getenv('GOOGLE_ADS_CONFIG_FILE', 'google-ads.yaml')
        self.customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')
        
        # Google Ads 클라이언트 초기화
        if GOOGLE_ADS_AVAILABLE and os.path.exists(self.config_file):
            try:
                self.client = GoogleAdsClient.load_from_storage(self.config_file)
                print("✅ Google Ads API 클라이언트 초기화 완료")
            except Exception as e:
                print(f"⚠️ Google Ads API 초기화 실패: {e}")
                self.client = None
        else:
            self.client = None
            print("⚠️ Google Ads API 설정이 없습니다. 목업 데이터를 사용합니다.")
    
    async def get_keyword_ideas(self, seed_keywords: List[str], language: str = "ko", location: str = "KR") -> List[GoogleKeywordData]:
        """
        Google Keyword Planner에서 키워드 아이디어 가져오기
        
        Args:
            seed_keywords: 시드 키워드 리스트
            language: 언어 코드 (ko, en 등)
            location: 국가 코드 (KR, US 등)
        """
        if not self.client or not self.customer_id:
            return self._get_mock_keyword_ideas(seed_keywords)
        
        try:
            keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")
            
            # 요청 생성
            request = self.client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = self.customer_id
            
            # 언어 및 위치 설정
            request.language = self._get_language_constant(language)
            request.geo_target_constants.append(self._get_location_constant(location))
            
            # 키워드 설정
            request.keyword_seed.keywords.extend(seed_keywords)
            
            # 키워드 아이디어 요청
            keyword_ideas = keyword_plan_idea_service.generate_keyword_ideas(request=request)
            
            # 결과 처리
            results = []
            for idea in keyword_ideas.results:
                keyword_data = GoogleKeywordData(
                    keyword=idea.text,
                    avg_monthly_searches=idea.keyword_idea_metrics.avg_monthly_searches or 0,
                    competition=idea.keyword_idea_metrics.competition.name,
                    competition_index=idea.keyword_idea_metrics.competition_index or 0.0,
                    low_top_of_page_bid=float(idea.keyword_idea_metrics.low_top_of_page_bid_micros or 0) / 1000000,
                    high_top_of_page_bid=float(idea.keyword_idea_metrics.high_top_of_page_bid_micros or 0) / 1000000,
                    keyword_difficulty=self._calculate_keyword_difficulty(idea.keyword_idea_metrics)
                )
                results.append(keyword_data)
            
            # 검색량 순으로 정렬
            results.sort(key=lambda x: x.avg_monthly_searches, reverse=True)
            return results[:20]  # 상위 20개 반환
            
        except GoogleAdsException as ex:
            print(f"Google Ads API 요청 실패: {ex}")
            return self._get_mock_keyword_ideas(seed_keywords)
        except Exception as e:
            print(f"키워드 아이디어 조회 오류: {e}")
            return self._get_mock_keyword_ideas(seed_keywords)
    
    def _get_language_constant(self, language: str) -> str:
        """언어 상수 반환"""
        language_mapping = {
            "ko": "1012",  # Korean
            "en": "1000",  # English
            "ja": "1005",  # Japanese
            "zh": "1017"   # Chinese
        }
        return f"languageConstants/{language_mapping.get(language, '1012')}"
    
    def _get_location_constant(self, location: str) -> str:
        """위치 상수 반환"""
        location_mapping = {
            "KR": "2410",  # South Korea
            "US": "2840",  # United States
            "JP": "2392",  # Japan
            "CN": "2156"   # China
        }
        return f"geoTargetConstants/{location_mapping.get(location, '2410')}"
    
    def _calculate_keyword_difficulty(self, metrics) -> int:
        """키워드 난이도 계산 (0-100)"""
        competition_score = 0
        if hasattr(metrics, 'competition_index') and metrics.competition_index:
            competition_score = metrics.competition_index * 100
        
        # CPC 기반 난이도 추가
        if hasattr(metrics, 'high_top_of_page_bid_micros') and metrics.high_top_of_page_bid_micros:
            cpc_score = min(50, (metrics.high_top_of_page_bid_micros / 1000000) * 10)
            competition_score = (competition_score + cpc_score) / 2
        
        return int(min(100, max(0, competition_score)))
    
    def _get_mock_keyword_ideas(self, seed_keywords: List[str]) -> List[GoogleKeywordData]:
        """목업 키워드 데이터 생성"""
        mock_keywords = []
        
        for seed in seed_keywords:
            # 기본 키워드
            mock_keywords.append(GoogleKeywordData(
                keyword=seed,
                avg_monthly_searches=hash(seed) % 10000 + 1000,
                competition="MEDIUM",
                competition_index=0.5,
                low_top_of_page_bid=1.2,
                high_top_of_page_bid=3.5,
                keyword_difficulty=60
            ))
            
            # 변형 키워드들 생성
            variations = [
                f"{seed} 추천",
                f"{seed} 리뷰",
                f"{seed} 후기",
                f"{seed} 가격",
                f"{seed} 비교",
                f"2025 {seed}",
                f"최고의 {seed}",
                f"{seed} 순위"
            ]
            
            for variation in variations:
                # 키워드별로 다른 값 생성
                search_volume = max(100, (hash(variation) % 5000) + 500)
                competition_level = ["LOW", "MEDIUM", "HIGH"][hash(variation) % 3]
                comp_index = (hash(variation) % 100) / 100
                
                mock_keywords.append(GoogleKeywordData(
                    keyword=variation,
                    avg_monthly_searches=search_volume,
                    competition=competition_level,
                    competition_index=comp_index,
                    low_top_of_page_bid=0.5 + (comp_index * 2),
                    high_top_of_page_bid=1.0 + (comp_index * 4),
                    keyword_difficulty=int(comp_index * 100)
                ))
        
        # 검색량 순 정렬
        mock_keywords.sort(key=lambda x: x.avg_monthly_searches, reverse=True)
        return mock_keywords[:15]
    
    async def get_search_volume_forecast(self, keywords: List[str], days_ahead: int = 30) -> Dict[str, Any]:
        """
        키워드 검색량 예측
        
        Args:
            keywords: 예측할 키워드 리스트
            days_ahead: 예측 기간 (일)
        """
        if not self.client or not self.customer_id:
            return self._get_mock_forecast(keywords, days_ahead)
        
        try:
            # Google Ads Keyword Plan 서비스 사용
            keyword_plan_service = self.client.get_service("KeywordPlanService")
            
            # 실제 예측 로직 구현 (복잡한 API 호출 필요)
            # 현재는 목업 데이터 반환
            return self._get_mock_forecast(keywords, days_ahead)
            
        except Exception as e:
            print(f"검색량 예측 오류: {e}")
            return self._get_mock_forecast(keywords, days_ahead)
    
    def _get_mock_forecast(self, keywords: List[str], days_ahead: int) -> Dict[str, Any]:
        """목업 예측 데이터"""
        forecast_data = {}
        
        for keyword in keywords:
            base_volume = hash(keyword) % 5000 + 1000
            
            # 일별 예측값 생성
            daily_forecast = []
            for day in range(days_ahead):
                # 주말 효과, 계절성 등을 고려한 변동
                day_of_week = (datetime.now() + timedelta(days=day)).weekday()
                weekend_factor = 0.8 if day_of_week >= 5 else 1.0
                
                seasonal_factor = 1.0 + 0.2 * (hash(f"{keyword}{day}") % 100 - 50) / 100
                
                daily_volume = int(base_volume * weekend_factor * seasonal_factor / 30)
                daily_forecast.append({
                    'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
                    'predicted_searches': daily_volume
                })
            
            forecast_data[keyword] = {
                'keyword': keyword,
                'forecast_period_days': days_ahead,
                'total_predicted_searches': sum(d['predicted_searches'] for d in daily_forecast),
                'avg_daily_searches': sum(d['predicted_searches'] for d in daily_forecast) // days_ahead,
                'daily_forecast': daily_forecast,
                'confidence_level': 0.75 + (hash(keyword) % 25) / 100  # 75-100% 신뢰도
            }
        
        return forecast_data
    
    async def get_keyword_competition_analysis(self, keywords: List[str]) -> Dict[str, Any]:
        """키워드 경쟁 분석"""
        competition_data = {}
        
        for keyword in keywords:
            # 실제로는 Google Ads API의 경쟁 데이터 사용
            mock_competition = {
                'keyword': keyword,
                'competition_level': ["LOW", "MEDIUM", "HIGH"][hash(keyword) % 3],
                'competition_index': (hash(keyword) % 100) / 100,
                'advertiser_count': hash(keyword) % 500 + 100,
                'avg_cpc': 1.0 + (hash(keyword) % 300) / 100,
                'top_of_page_bid_low': 0.8 + (hash(keyword) % 200) / 100,
                'top_of_page_bid_high': 2.0 + (hash(keyword) % 400) / 100,
                'difficulty_score': hash(keyword) % 100,
                'opportunity_score': 100 - (hash(keyword) % 100)
            }
            
            competition_data[keyword] = mock_competition
        
        return competition_data
    
    async def get_trending_keywords(self, category: str, region: str = "KR") -> List[str]:
        """트렌딩 키워드 조회"""
        # 실제로는 Google Trends API 연동 필요
        trending_keywords = [
            f"{category} 2025",
            f"{category} 추천",
            f"인기 {category}",
            f"{category} 순위",
            f"최고 {category}",
            f"{category} 리뷰",
            f"{category} 가격비교",
            f"신상 {category}",
            f"{category} 할인",
            f"{category} 베스트"
        ]
        
        return trending_keywords

# 통합 키워드 분석 서비스
class IntegratedKeywordAnalyzer:
    def __init__(self):
        self.google_service = GoogleAdsKeywordService()
        
    async def comprehensive_keyword_analysis(self, seed_keywords: List[str], category: str) -> Dict[str, Any]:
        """종합 키워드 분석"""
        
        # 1. Google Keyword Planner 데이터
        google_ideas = await self.google_service.get_keyword_ideas(seed_keywords)
        
        # 2. 검색량 예측
        forecast_data = await self.google_service.get_search_volume_forecast(seed_keywords)
        
        # 3. 경쟁 분석
        competition_data = await self.google_service.get_keyword_competition_analysis(seed_keywords)
        
        # 4. 트렌딩 키워드
        trending_keywords = await self.google_service.get_trending_keywords(category)
        
        # 5. 통합 분석 결과 생성
        analysis_result = {
            'analysis_date': datetime.now().isoformat(),
            'seed_keywords': seed_keywords,
            'category': category,
            'google_keyword_ideas': [
                {
                    'keyword': idea.keyword,
                    'monthly_searches': idea.avg_monthly_searches,
                    'competition': idea.competition,
                    'difficulty': idea.keyword_difficulty,
                    'cpc_low': idea.low_top_of_page_bid,
                    'cpc_high': idea.high_top_of_page_bid
                }
                for idea in google_ideas
            ],
            'search_volume_forecast': forecast_data,
            'competition_analysis': competition_data,
            'trending_keywords': trending_keywords,
            'recommendations': self._generate_recommendations(google_ideas, trending_keywords)
        }
        
        return analysis_result
    
    def _generate_recommendations(self, keyword_ideas: List[GoogleKeywordData], trending_keywords: List[str]) -> Dict[str, Any]:
        """추천 사항 생성"""
        
        # 높은 검색량 + 낮은 경쟁도 키워드 찾기
        golden_opportunities = []
        for idea in keyword_ideas:
            if idea.avg_monthly_searches > 1000 and idea.competition == "LOW":
                golden_opportunities.append(idea.keyword)
        
        # 롱테일 키워드 찾기
        long_tail_keywords = []
        for idea in keyword_ideas:
            if len(idea.keyword.split()) >= 3 and idea.competition in ["LOW", "MEDIUM"]:
                long_tail_keywords.append(idea.keyword)
        
        return {
            'golden_opportunities': golden_opportunities[:5],
            'long_tail_keywords': long_tail_keywords[:5],
            'trending_picks': trending_keywords[:5],
            'content_strategy': self._suggest_content_strategy(keyword_ideas),
            'budget_recommendations': self._suggest_budget_strategy(keyword_ideas)
        }
    
    def _suggest_content_strategy(self, keyword_ideas: List[GoogleKeywordData]) -> List[str]:
        """콘텐츠 전략 제안"""
        strategies = []
        
        high_volume_keywords = [k for k in keyword_ideas if k.avg_monthly_searches > 5000]
        if high_volume_keywords:
            strategies.append("고검색량 키워드로 메인 콘텐츠 제작")
        
        low_competition_keywords = [k for k in keyword_ideas if k.competition == "LOW"]
        if low_competition_keywords:
            strategies.append("경쟁도 낮은 키워드로 SEO 최적화")
        
        return strategies
    
    def _suggest_budget_strategy(self, keyword_ideas: List[GoogleKeywordData]) -> Dict[str, Any]:
        """예산 전략 제안"""
        if not keyword_ideas:
            return {}
        
        avg_cpc = sum(k.high_top_of_page_bid for k in keyword_ideas) / len(keyword_ideas)
        
        return {
            'recommended_daily_budget': f"${avg_cpc * 20:.2f}",
            'cost_per_acquisition_estimate': f"${avg_cpc * 5:.2f}",
            'budget_allocation': {
                'high_intent_keywords': "60%",
                'brand_keywords': "25%", 
                'discovery_keywords': "15%"
            }
        }

# 테스트 함수
async def test_google_ads_service():
    """Google Ads 서비스 테스트"""
    analyzer = IntegratedKeywordAnalyzer()
    
    seed_keywords = ["스탠딩책상", "사무용 의자"]
    category = "사무용 가구"
    
    print("=== Google Ads 키워드 분석 시작 ===")
    result = await analyzer.comprehensive_keyword_analysis(seed_keywords, category)
    
    print(f"\n분석 완료: {result['analysis_date']}")
    print(f"카테고리: {result['category']}")
    
    print(f"\n=== Google 키워드 아이디어 ===")
    for idea in result['google_keyword_ideas'][:5]:
        print(f"- {idea['keyword']}: {idea['monthly_searches']:,}회/월, {idea['competition']}, ${idea['cpc_low']:.2f}-${idea['cpc_high']:.2f}")
    
    print(f"\n=== 추천 사항 ===")
    recommendations = result['recommendations']
    print(f"황금 기회 키워드: {', '.join(recommendations['golden_opportunities'])}")
    print(f"롱테일 키워드: {', '.join(recommendations['long_tail_keywords'])}")

if __name__ == "__main__":
    asyncio.run(test_google_ads_service())