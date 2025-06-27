"""
황금 키워드 생성 서비스
- 수익성, 창의성, 유입량을 고려한 최적의 키워드 발굴
- 실시간 트렌드 분석 및 경쟁 분석
- 플랫폼별 최적화된 키워드 추천
"""

import asyncio
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import openai
from logger import ai_logger
import requests
from collections import defaultdict
import re


class GoldenKeywordService:
    """황금 키워드 생성을 위한 고급 알고리즘 서비스"""
    
    def __init__(self):
        self.trend_keywords = {}
        self.profit_multipliers = {
            '재테크': 2.5, '투자': 2.3, '부동산': 2.1, '부업': 1.9,
            '다이어트': 1.8, '뷰티': 1.7, '패션': 1.6, '여행': 1.5,
            '음식': 1.4, '건강': 1.6, '운동': 1.5, '육아': 1.7,
            '반려동물': 1.4, '자동차': 1.8, '게임': 1.3, '영화': 1.2,
            '음악': 1.1, '책': 1.2, '교육': 1.6, '프로그래밍': 1.9,
            '창업': 2.2, '온라인쇼핑': 1.8, '리뷰': 1.5, '라이프스타일': 1.4
        }
    
    async def generate_golden_keywords(
        self, 
        category: str, 
        domain: str = "", 
        platform: str = "wordpress"
    ) -> Dict[str, List[str]]:
        """메인 황금 키워드 생성 함수"""
        
        try:
            # 1. 기본 카테고리 키워드 생성
            base_keywords = await self._generate_base_keywords(category)
            
            # 2. 수익성 키워드 생성 (돈이 되는 키워드)
            profitable_keywords = await self._generate_profitable_keywords(category, base_keywords)
            
            # 3. 트렌딩 키워드 생성 (현재 핫한 키워드)
            trending_keywords = await self._generate_trending_keywords(category, base_keywords)
            
            # 4. 황금 키워드 생성 (창의적이고 유입량 높은 키워드)
            golden_keywords = await self._generate_creative_golden_keywords(
                category, base_keywords, profitable_keywords, trending_keywords
            )
            
            ai_logger.info(
                f"Golden keywords generated successfully",
                category=category,
                golden_count=len(golden_keywords),
                profitable_count=len(profitable_keywords),
                trending_count=len(trending_keywords)
            )
            
            return {
                "golden_keywords": golden_keywords,
                "profitable_keywords": profitable_keywords,
                "trending_keywords": trending_keywords
            }
            
        except Exception as e:
            ai_logger.error(f"Error in golden keyword generation", error=e, category=category)
            return await self._fallback_keywords(category)
    
    async def _generate_base_keywords(self, category: str) -> List[str]:
        """카테고리별 기본 키워드 생성"""
        
        category_seeds = {
            '여행': [
                '여행지', '여행코스', '숙소', '맛집', '관광명소', '여행팁', 
                '여행준비', '여행용품', '항공권', '렌터카', '패키지여행', '자유여행',
                '해외여행', '국내여행', '가족여행', '커플여행', '혼여행', '배낭여행'
            ],
            '음식': [
                '레시피', '맛집', '요리법', '간단요리', '다이어트요리', '디저트',
                '한식', '양식', '중식', '일식', '분식', '술안주', '도시락', '브런치',
                '홈쿡', '쿠킹클래스', '요리재료', '조미료', '키친용품'
            ],
            '재테크': [
                '투자', '주식', '부동산', '적금', '예금', '펀드', '채권', '금융',
                '세금', '연금', '보험', '대출', '신용', '부업', '사업', '창업',
                '경제', '금리', '환율', '인플레이션', '포트폴리오', '자산관리'
            ],
            '뷰티': [
                '화장품', '스킨케어', '메이크업', '미용', '성형', '다이어트',
                '헤어', '네일', '향수', '코스메틱', '팩', '클렌징', '선크림',
                '립스틱', '아이섀도', '파운데이션', '컨실러', '마스카라'
            ],
            '건강': [
                '운동', '다이어트', '영양', '의학', '병원', '약품', '건강식품',
                '요가', '필라테스', '헬스', '러닝', '수영', '등산', '자전거',
                '스트레칭', '마사지', '명상', '수면', '스트레스', '면역력'
            ]
        }
        
        # 기본 시드 키워드 가져오기
        seeds = category_seeds.get(category, [category])
        
        # AI를 통한 확장 키워드 생성
        expanded_keywords = await self._ai_expand_keywords(category, seeds[:5])
        
        return seeds + expanded_keywords
    
    async def _generate_profitable_keywords(self, category: str, base_keywords: List[str]) -> List[str]:
        """수익성이 높은 키워드 생성 (구매 의도가 높은 키워드)"""
        
        profit_indicators = [
            '추천', '후기', '리뷰', '비교', '순위', '가격', '할인', '쿠폰',
            '구매', '주문', '배송', '무료', '이벤트', '세일', '특가', '브랜드',
            '인기', '베스트', '신상', '출시', '론칭', '예약', '구독', '멤버십'
        ]
        
        profitable_keywords = []
        
        # 기본 키워드와 수익 지시어 조합
        for keyword in base_keywords[:8]:
            for indicator in profit_indicators[:6]:
                profitable_keywords.append(f"{keyword} {indicator}")
        
        # AI를 통한 수익성 키워드 생성
        ai_profitable = await self._ai_generate_profitable_keywords(category)
        profitable_keywords.extend(ai_profitable)
        
        # 수익성 점수로 정렬
        scored_keywords = []
        profit_multiplier = self.profit_multipliers.get(category, 1.0)
        
        for kw in profitable_keywords:
            score = self._calculate_profit_score(kw, profit_multiplier)
            scored_keywords.append((kw, score))
        
        # 상위 15개 선택
        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        return [kw for kw, score in scored_keywords[:15]]
    
    async def _generate_trending_keywords(self, category: str, base_keywords: List[str]) -> List[str]:
        """현재 트렌딩인 키워드 생성"""
        
        trending_keywords = []
        
        # 시기별 트렌드 키워드
        current_month = datetime.now().month
        seasonal_keywords = self._get_seasonal_keywords(category, current_month)
        trending_keywords.extend(seasonal_keywords)
        
        # 최신 트렌드 키워드 (AI 생성)
        ai_trending = await self._ai_generate_trending_keywords(category)
        trending_keywords.extend(ai_trending)
        
        # 소셜 미디어 트렌드 키워드
        social_trending = self._get_social_trending_keywords(category)
        trending_keywords.extend(social_trending)
        
        return trending_keywords[:15]
    
    async def _generate_creative_golden_keywords(
        self, 
        category: str, 
        base_keywords: List[str], 
        profitable_keywords: List[str], 
        trending_keywords: List[str]
    ) -> List[str]:
        """창의적이고 유입량이 높은 황금 키워드 생성"""
        
        golden_keywords = []
        
        # 1. 롱테일 키워드 생성 (3-5단어 조합)
        longtail_keywords = await self._generate_longtail_keywords(category, base_keywords)
        golden_keywords.extend(longtail_keywords)
        
        # 2. 의외의 조합 키워드 (창의적 접근)
        creative_combinations = await self._generate_creative_combinations(category, base_keywords)
        golden_keywords.extend(creative_combinations)
        
        # 3. 문제 해결형 키워드
        problem_solving_keywords = await self._generate_problem_solving_keywords(category)
        golden_keywords.extend(problem_solving_keywords)
        
        # 4. 감정 유발 키워드
        emotional_keywords = await self._generate_emotional_keywords(category, base_keywords)
        golden_keywords.extend(emotional_keywords)
        
        # 유입량 점수로 정렬
        scored_keywords = []
        for kw in golden_keywords:
            traffic_score = self._calculate_traffic_potential(kw, category)
            scored_keywords.append((kw, traffic_score))
        
        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        return [kw for kw, score in scored_keywords[:15]]
    
    async def _ai_expand_keywords(self, category: str, seeds: List[str]) -> List[str]:
        """AI를 사용한 키워드 확장"""
        try:
            prompt = f"""
            다음 {category} 카테고리의 시드 키워드들을 분석해서, 
            검색량이 높고 경쟁이 적은 새로운 키워드 10개를 생성해주세요.
            
            시드 키워드: {', '.join(seeds)}
            
            조건:
            1. 한국인들이 실제로 검색할 만한 키워드
            2. 너무 경쟁이 치열하지 않은 키워드
            3. 검색 의도가 명확한 키워드
            4. 2-4단어로 구성된 키워드
            
            결과를 JSON 배열 형태로만 반환: ["키워드1", "키워드2", ...]
            """
            
            # OpenAI API 호출 (실제 구현에서는 설정된 AI 서비스 사용)
            response = await self._call_ai_service(prompt)
            
            # JSON 파싱
            import json
            try:
                keywords = json.loads(response)
                return keywords if isinstance(keywords, list) else []
            except:
                return []
                
        except Exception as e:
            ai_logger.error(f"AI keyword expansion failed", error=e)
            return []
    
    async def _ai_generate_profitable_keywords(self, category: str) -> List[str]:
        """AI를 사용한 수익성 키워드 생성"""
        try:
            prompt = f"""
            {category} 카테고리에서 구매 전환율이 높고 수익성이 좋은 키워드 10개를 생성해주세요.
            
            조건:
            1. 구매 의도가 높은 키워드
            2. 광고 수익을 낼 수 있는 키워드  
            3. 제품/서비스 구매로 연결되는 키워드
            4. 브랜드, 리뷰, 비교 관련 키워드 포함
            
            JSON 배열로만 반환: ["키워드1", "키워드2", ...]
            """
            
            response = await self._call_ai_service(prompt)
            
            try:
                keywords = json.loads(response)
                return keywords if isinstance(keywords, list) else []
            except:
                return []
                
        except Exception as e:
            ai_logger.error(f"AI profitable keyword generation failed", error=e)
            return []
    
    async def _ai_generate_trending_keywords(self, category: str) -> List[str]:
        """AI를 사용한 트렌딩 키워드 생성"""
        try:
            current_date = datetime.now().strftime("%Y년 %m월")
            
            prompt = f"""
            {current_date} 현재 {category} 카테고리에서 트렌딩인 키워드 10개를 생성해주세요.
            
            조건:
            1. 최근 3개월 내 인기 상승한 키워드
            2. 소셜미디어에서 화제가 되는 키워드
            3. 시즌/이벤트와 관련된 키워드
            4. 새로운 트렌드나 유행을 반영한 키워드
            
            JSON 배열로만 반환: ["키워드1", "키워드2", ...]
            """
            
            response = await self._call_ai_service(prompt)
            
            try:
                keywords = json.loads(response)
                return keywords if isinstance(keywords, list) else []
            except:
                return []
                
        except Exception as e:
            ai_logger.error(f"AI trending keyword generation failed", error=e)
            return []
    
    async def _generate_longtail_keywords(self, category: str, base_keywords: List[str]) -> List[str]:
        """롱테일 키워드 생성"""
        modifiers = [
            '방법', '팁', '가이드', '추천', '비교', '순위', '리스트', '정보',
            '초보자', '전문가', '완벽한', '최고의', '인기', '유명한', '숨겨진',
            '2024년', '최신', '트렌드', '핫한', '화제의', '베스트', '실제',
            '무료', '유료', '저렴한', '고급', '프리미엄', '할인', '이벤트'
        ]
        
        longtail_keywords = []
        
        for keyword in base_keywords[:8]:
            for modifier in modifiers[:10]:
                longtail_keywords.append(f"{modifier} {keyword}")
                longtail_keywords.append(f"{keyword} {modifier}")
        
        return longtail_keywords
    
    async def _generate_creative_combinations(self, category: str, base_keywords: List[str]) -> List[str]:
        """창의적 키워드 조합 생성"""
        unexpected_modifiers = [
            '혼자서', '집에서', '5분만에', '간단하게', '쉽게', '빠르게',
            '숨겨진', '의외의', '신박한', '독특한', '특별한', '색다른',
            '요즘', '인싸', '핫한', '유행하는', '화제의', '바이럴',
            '절약', '돈안드는', '무료', '공짜', '저비용', '합리적'
        ]
        
        creative_keywords = []
        
        for keyword in base_keywords[:6]:
            for modifier in unexpected_modifiers[:8]:
                creative_keywords.append(f"{modifier} {keyword}")
        
        return creative_keywords
    
    async def _generate_problem_solving_keywords(self, category: str) -> List[str]:
        """문제 해결형 키워드 생성"""
        problem_patterns = [
            f"{category} 문제", f"{category} 고민", f"{category} 해결",
            f"{category} 실패", f"{category} 성공", f"{category} 비법",
            f"{category} 못할때", f"{category} 어려울때", f"{category} 쉽게하는법"
        ]
        
        return problem_patterns
    
    async def _generate_emotional_keywords(self, category: str, base_keywords: List[str]) -> List[str]:
        """감정 유발 키워드 생성"""
        emotional_modifiers = [
            '놀라운', '충격적인', '감동적인', '웃긴', '재밌는', '신기한',
            '무서운', '슬픈', '행복한', '뿌듯한', '만족한', '후회없는'
        ]
        
        emotional_keywords = []
        
        for keyword in base_keywords[:5]:
            for emotion in emotional_modifiers[:6]:
                emotional_keywords.append(f"{emotion} {keyword}")
        
        return emotional_keywords
    
    def _get_seasonal_keywords(self, category: str, month: int) -> List[str]:
        """시기별 키워드 생성"""
        seasonal_map = {
            1: ['신년', '새해', '다짐', '계획'],
            2: ['겨울', '추위', '따뜻한'],
            3: ['봄', '벚꽃', '새학기', '졸업'],
            4: ['봄나들이', '꽃구경', '소풍'],
            5: ['어린이날', '가정의달', '가족여행'],
            6: ['여름준비', '다이어트', '휴가'],
            7: ['여름휴가', '바다', '피서지'],
            8: ['휴가', '피서', '여름'],
            9: ['가을', '단풍', '새학기'],
            10: ['가을여행', '단풍구경', '독서'],
            11: ['가을패션', '겨울준비'],
            12: ['연말', '크리스마스', '선물', '파티']
        }
        
        seasonal_words = seasonal_map.get(month, [])
        return [f"{category} {word}" for word in seasonal_words]
    
    def _get_social_trending_keywords(self, category: str) -> List[str]:
        """소셜 미디어 트렌드 키워드"""
        social_trends = [
            '인스타', '틱톡', '유튜브', '릴스', '스토리', '라이브',
            '챌린지', '바이럴', '핫플', '맛집투어', '일상',
            'OOTD', 'GRWM', '브이로그', '먹방', '리뷰'
        ]
        
        return [f"{category} {trend}" for trend in social_trends[:8]]
    
    def _calculate_profit_score(self, keyword: str, category_multiplier: float) -> float:
        """수익성 점수 계산"""
        profit_words = [
            '추천', '후기', '리뷰', '비교', '순위', '가격', '할인', '쿠폰',
            '구매', '브랜드', '인기', '베스트', '신상', '예약'
        ]
        
        score = 1.0
        for word in profit_words:
            if word in keyword:
                score += 0.3
        
        # 길이 보정 (너무 긴 키워드는 감점)
        if len(keyword) > 20:
            score *= 0.8
        elif len(keyword) < 5:
            score *= 0.9
        
        return score * category_multiplier
    
    def _calculate_traffic_potential(self, keyword: str, category: str) -> float:
        """유입량 잠재력 계산"""
        traffic_words = [
            '방법', '팁', '가이드', '추천', '리스트', '정보', '완벽한',
            '최고의', '인기', '트렌드', '핫한', '무료', '쉽게', '간단하게'
        ]
        
        score = 1.0
        
        # 트래픽 유발 단어 가점
        for word in traffic_words:
            if word in keyword:
                score += 0.25
        
        # 감정적 단어 가점
        emotional_words = ['놀라운', '충격적인', '신기한', '재밌는']
        for word in emotional_words:
            if word in keyword:
                score += 0.4
        
        # 롱테일 키워드 가점 (적당한 길이)
        if 6 <= len(keyword) <= 15:
            score += 0.3
        
        return score
    
    async def _call_ai_service(self, prompt: str) -> str:
        """AI 서비스 호출 (실제 구현에서는 설정된 서비스 사용)"""
        try:
            # 실제 구현에서는 OpenAI API 또는 다른 AI 서비스 사용
            # 여기서는 임시 응답
            await asyncio.sleep(0.1)  # 시뮬레이션
            return '["임시 키워드1", "임시 키워드2", "임시 키워드3"]'
        except Exception as e:
            ai_logger.error(f"AI service call failed", error=e)
            return '[]'
    
    async def _fallback_keywords(self, category: str) -> Dict[str, List[str]]:
        """폴백 키워드 (AI 서비스 실패 시)"""
        fallback_data = {
            '여행': {
                'golden_keywords': [
                    '혼자 여행 코스', '가족 여행지 추천', '당일치기 여행',
                    '숨겨진 맛집', '인스타 핫플', '저렴한 숙소'
                ],
                'profitable_keywords': [
                    '여행용품 추천', '항공권 할인', '호텔 예약',
                    '여행보험 비교', '렌터카 후기', '패키지여행 가격'
                ],
                'trending_keywords': [
                    '2024 여행지', '워케이션', '글램핑',
                    '펜션 추천', '캠핑카 여행', '드라이브 코스'
                ]
            }
        }
        
        return fallback_data.get(category, {
            'golden_keywords': [f'{category} 추천', f'{category} 팁', f'{category} 가이드'],
            'profitable_keywords': [f'{category} 후기', f'{category} 비교', f'{category} 할인'],
            'trending_keywords': [f'2024 {category}', f'{category} 트렌드', f'핫한 {category}']
        })


# main.py에서 import할 수 있도록 클래스 export
__all__ = ['GoldenKeywordService']