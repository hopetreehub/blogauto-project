"""
SEO 키워드 분석 시스템
최신 트렌드와 검색량, 경쟁도를 분석하여 최적화된 키워드를 생성합니다.
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random
from dataclasses import dataclass

@dataclass
class SEOKeyword:
    keyword: str
    search_volume: str  # 예상 검색량
    competition: str    # 경쟁도
    seasonal: bool      # 계절성 요인
    reason: str         # 추천 이유
    score: float        # SEO 점수

class SEOKeywordAnalyzer:
    def __init__(self):
        # 계절성 키워드 매핑
        self.seasonal_keywords = {
            "spring": ["봄", "신상", "새학기", "이사", "미세먼지", "알레르기", "꽃가루"],
            "summer": ["여름", "휴가", "방학", "에어컨", "선풍기", "시원한", "더위", "자외선"],
            "autumn": ["가을", "신학기", "환절기", "단풍", "독감", "건조", "추위준비"],
            "winter": ["겨울", "크리스마스", "신년", "난방", "히터", "건조", "감기", "연말"]
        }
        
        # 트렌드 증폭 키워드
        self.trend_amplifiers = [
            "2025", "최신", "신상", "추천", "베스트", "인기", "핫한", "트렌드",
            "리뷰", "후기", "비교", "순위", "랭킹", "가성비", "꿀템", "필수템"
        ]
        
        # 검색 의도별 키워드
        self.search_intents = {
            "정보": ["방법", "하는법", "가이드", "팁", "노하우", "정보", "알아보기"],
            "구매": ["추천", "리뷰", "후기", "비교", "가격", "할인", "세일", "구매"],
            "문제해결": ["해결", "문제", "고장", "오류", "수리", "개선", "최적화"]
        }
    
    def get_active_guideline(self, db_session):
        """활성화된 키워드 분석 지침 가져오기"""
        try:
            from models import SystemPrompt
            from sqlalchemy import and_
            
            guideline = db_session.query(SystemPrompt).filter(
                and_(
                    SystemPrompt.prompt_type == 'KEYWORD_ANALYSIS',
                    SystemPrompt.is_active == True
                )
            ).first()
            
            if guideline:
                return guideline.prompt_content
            else:
                return None
        except Exception as e:
            print(f"지침 로드 오류: {e}")
            return None

    def get_current_season(self) -> str:
        """현재 계절 반환"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        elif month in [9, 10, 11]:
            return "autumn"
        else:
            return "winter"

    def analyze_seasonality(self, item_name: str, category: str) -> bool:
        """계절성 분석"""
        current_season = self.get_current_season()
        seasonal_terms = self.seasonal_keywords[current_season]
        
        # 아이템이나 카테고리에 계절성 키워드가 포함되어 있는지 확인
        text = f"{item_name} {category}".lower()
        return any(term in text for term in seasonal_terms)

    def calculate_competition_score(self, keyword: str) -> Tuple[str, float]:
        """경쟁도 계산 (실제로는 API 연동이 필요하지만, 현재는 휴리스틱 방식)"""
        # 키워드 길이가 길수록 경쟁도 낮음
        length_factor = max(0.1, 1.0 - (len(keyword) / 20))
        
        # 특수 문자나 숫자가 포함되면 경쟁도 낮음
        special_factor = 0.8 if re.search(r'[0-9]', keyword) else 1.0
        
        # 브랜드명이나 구체적인 모델명이 포함되면 경쟁도 낮음
        specific_terms = ["리뷰", "후기", "사용법", "설치", "조립", "2025"]
        specific_factor = 0.7 if any(term in keyword for term in specific_terms) else 1.0
        
        competition_score = length_factor * special_factor * specific_factor
        
        if competition_score > 0.8:
            return "높음", competition_score
        elif competition_score > 0.5:
            return "보통", competition_score
        else:
            return "낮음", competition_score

    def estimate_search_volume(self, keyword: str, category: str) -> str:
        """검색량 추정 (실제로는 Google Keyword Planner API 등 사용)"""
        # 일반적인 카테고리의 기본 검색량
        base_volumes = {
            "사무용 가구": 5000,
            "전자제품": 8000,
            "의류": 12000,
            "식품": 10000,
            "화장품": 15000,
            "운동용품": 6000,
            "생활용품": 7000
        }
        
        base_volume = base_volumes.get(category, 5000)
        
        # 키워드 특성에 따른 조정
        if any(word in keyword for word in ["추천", "리뷰", "후기"]):
            base_volume *= 1.5
        if any(word in keyword for word in ["2025", "최신", "신상"]):
            base_volume *= 1.3
        if len(keyword) > 15:  # 롱테일 키워드
            base_volume *= 0.6
            
        volume = int(base_volume * random.uniform(0.7, 1.3))
        
        if volume > 10000:
            return f"{volume//1000}K+"
        elif volume > 1000:
            return f"{volume//100}00+"
        else:
            return f"{volume}+"

    def generate_keyword_variations(self, item_name: str, category: str) -> List[str]:
        """키워드 변형 생성"""
        variations = []
        
        # 기본 조합
        variations.extend([
            f"{item_name}",
            f"{item_name} 추천",
            f"{item_name} 리뷰",
            f"{item_name} 후기",
            f"{item_name} 가격",
            f"{item_name} 비교"
        ])
        
        # 카테고리 조합
        variations.extend([
            f"{category} {item_name}",
            f"{category} 추천",
            f"최고의 {item_name}",
            f"인기 {item_name}"
        ])
        
        # 현재 연도 추가
        current_year = datetime.now().year
        variations.extend([
            f"{current_year} {item_name}",
            f"{current_year} {item_name} 추천",
            f"{current_year} 최신 {item_name}"
        ])
        
        # 검색 의도별 키워드 생성
        for intent, intent_words in self.search_intents.items():
            for word in intent_words[:2]:  # 각 의도별로 2개씩만
                variations.append(f"{item_name} {word}")
        
        # 계절성 키워드 추가
        current_season = self.get_current_season()
        seasonal_terms = self.seasonal_keywords[current_season][:3]
        for term in seasonal_terms:
            if term in ["봄", "여름", "가을", "겨울"]:
                variations.append(f"{term} {item_name}")
        
        # 트렌드 키워드 추가
        for amplifier in self.trend_amplifiers[:5]:
            variations.append(f"{amplifier} {item_name}")
        
        return list(set(variations))  # 중복 제거

    def score_keyword(self, keyword: str, item_name: str, category: str) -> float:
        """키워드 점수 계산"""
        score = 50.0  # 기본 점수
        
        # 길이 점수 (10-20자가 최적)
        length = len(keyword)
        if 10 <= length <= 20:
            score += 10
        elif length < 10:
            score += 5
        else:
            score -= 5
        
        # 검색 의도 점수
        intent_words = ["추천", "리뷰", "후기", "비교", "방법", "가격"]
        if any(word in keyword for word in intent_words):
            score += 15
        
        # 트렌드 점수
        if any(word in keyword for word in self.trend_amplifiers):
            score += 10
        
        # 구체성 점수
        if item_name in keyword and any(word in keyword for word in ["최고", "베스트", "인기"]):
            score += 8
        
        # 계절성 보너스
        if self.analyze_seasonality(keyword, category):
            score += 12
        
        # 중복 키워드 페널티
        words = keyword.split()
        if len(words) != len(set(words)):
            score -= 10
        
        return min(score, 100.0)

    async def analyze_seo_keywords(self, item_name: str, category: str, db_session=None) -> List[SEOKeyword]:
        """SEO 키워드 분석 메인 함수"""
        print(f"SEO 키워드 분석 시작: {item_name} ({category})")
        
        # 지침 로드 (있으면 사용, 없으면 기본 알고리즘)
        guideline = None
        if db_session:
            try:
                guideline = self.get_active_guideline(db_session)
                print(f"지침 로드됨: {len(guideline) if guideline else 0}자")
            except Exception as e:
                print(f"지침 로드 실패, 기본 알고리즘 사용: {e}")
        
        # 키워드 변형 생성
        keyword_variations = self.generate_keyword_variations(item_name, category)
        
        seo_keywords = []
        
        for keyword in keyword_variations:
            # 경쟁도 분석
            competition, comp_score = self.calculate_competition_score(keyword)
            
            # 검색량 추정
            search_volume = self.estimate_search_volume(keyword, category)
            
            # 계절성 분석
            seasonal = self.analyze_seasonality(keyword, category)
            
            # SEO 점수 계산
            seo_score = self.score_keyword(keyword, item_name, category)
            
            # 추천 이유 생성
            reason = self.generate_recommendation_reason(keyword, competition, seasonal, seo_score)
            
            seo_keyword = SEOKeyword(
                keyword=keyword,
                search_volume=search_volume,
                competition=competition,
                seasonal=seasonal,
                reason=reason,
                score=seo_score
            )
            
            seo_keywords.append(seo_keyword)
        
        # 점수순으로 정렬하여 상위 10개 반환
        seo_keywords.sort(key=lambda x: x.score, reverse=True)
        return seo_keywords[:10]

    def generate_recommendation_reason(self, keyword: str, competition: str, seasonal: bool, score: float) -> str:
        """추천 이유 생성"""
        reasons = []
        
        if competition == "낮음":
            reasons.append("경쟁도가 낮아 상위노출 가능성 높음")
        elif competition == "보통":
            reasons.append("적절한 경쟁도로 SEO 효과 기대")
        
        if seasonal:
            season_name = {
                "spring": "봄철", "summer": "여름철", 
                "autumn": "가을철", "winter": "겨울철"
            }[self.get_current_season()]
            reasons.append(f"{season_name} 트렌드 키워드")
        
        if any(word in keyword for word in ["추천", "리뷰", "후기"]):
            reasons.append("구매 의도 높은 검색어")
        
        if any(word in keyword for word in ["2025", "최신"]):
            reasons.append("최신 트렌드 반영")
        
        if score > 80:
            reasons.append("높은 SEO 점수")
        elif score > 60:
            reasons.append("양호한 SEO 점수")
        
        if len(keyword) > 15:
            reasons.append("롱테일 키워드로 타겟팅 용이")
        
        return ", ".join(reasons) if reasons else "기본 SEO 키워드"

# 사용 예시
async def main():
    analyzer = SEOKeywordAnalyzer()
    results = await analyzer.analyze_seo_keywords("스탠딩책상", "사무용 가구")
    
    print("\n=== SEO 키워드 분석 결과 ===")
    for i, keyword in enumerate(results, 1):
        print(f"{i}. {keyword.keyword}")
        print(f"   검색량: {keyword.search_volume}")
        print(f"   경쟁도: {keyword.competition}")
        print(f"   계절성: {'있음' if keyword.seasonal else '없음'}")
        print(f"   SEO점수: {keyword.score:.1f}")
        print(f"   추천이유: {keyword.reason}")
        print()

if __name__ == "__main__":
    asyncio.run(main())