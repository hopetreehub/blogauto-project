"""
최적화된 제목 생성 서비스
- 클릭률(CTR) 최적화
- 감정 유발 알고리즘
- SEO 최적화
- 플랫폼별 맞춤화
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
from logger import ai_logger


class OptimizedTitleService:
    """사람들이 찾아올 수 있는 최적의 제목을 생성하는 고급 알고리즘"""
    
    def __init__(self):
        # CTR이 높은 단어들
        self.high_ctr_words = [
            # 감정 유발
            '놀라운', '충격적인', '믿을 수 없는', '신기한', '대박',
            '완전', '진짜', '실제', '정말', '엄청',
            
            # 호기심 유발
            '비밀', '숨겨진', '몰랐던', '의외의', '특별한',
            '신박한', '독특한', '색다른', '새로운', '최신',
            
            # 긴급성
            '지금', '당장', '오늘', '즉시', '빨리',
            '마지막', '마감', '한정', '제한', '기회',
            
            # 이익/혜택
            '무료', '공짜', '할인', '절약', '이득',
            '꿀팁', '꿀정보', '득템', '혜택', '특가',
            
            # 사회적 증명
            '인기', '화제', '바이럴', '핫한', '트렌드',
            '베스트', '1위', '추천', '인정', '검증',
            
            # 개인화
            '나만의', '당신의', '우리', '내', '여러분'
        ]
        
        # 플랫폼별 최적화 패턴
        self.platform_patterns = {
            'wordpress': {
                'optimal_length': (40, 60),  # 글자 수
                'preferred_structure': 'keyword + benefit + emotion'
            },
            'blogspot': {
                'optimal_length': (35, 55),
                'preferred_structure': 'emotion + keyword + action'
            },
            'tistory': {
                'optimal_length': (30, 50),
                'preferred_structure': 'curiosity + keyword + result'
            }
        }
    
    async def generate_optimized_titles(
        self,
        keyword: str,
        category: str,
        platform: str = 'wordpress',
        count: int = 15,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """최적화된 제목 생성 메인 함수"""
        
        try:
            ai_logger.log_generation(
                service="OptimizedTitleService",
                operation="generate_optimized_titles",
                user_id="system",
                success=True,
                keyword=keyword,
                category=category,
                platform=platform,
                count=count
            )
            
            # 1. 다양한 제목 패턴 생성
            titles = []
            
            # 감정 유발 제목
            emotional_titles = await self._generate_emotional_titles(keyword, category)
            titles.extend(emotional_titles)
            
            # 호기심 유발 제목  
            curiosity_titles = await self._generate_curiosity_titles(keyword, category)
            titles.extend(curiosity_titles)
            
            # 혜택/이익 강조 제목
            benefit_titles = await self._generate_benefit_titles(keyword, category)
            titles.extend(benefit_titles)
            
            # 사회적 증명 제목
            social_proof_titles = await self._generate_social_proof_titles(keyword, category)
            titles.extend(social_proof_titles)
            
            # 문제 해결 제목
            problem_solving_titles = await self._generate_problem_solving_titles(keyword, category)
            titles.extend(problem_solving_titles)
            
            # 리스트형 제목
            list_titles = await self._generate_list_titles(keyword, category)
            titles.extend(list_titles)
            
            # How-to 제목
            howto_titles = await self._generate_howto_titles(keyword, category)
            titles.extend(howto_titles)
            
            # 2. 각 제목에 대해 CTR 점수 계산
            scored_titles = []
            for title in titles:
                ctr_score = self._calculate_ctr_score(title, keyword, category, platform)
                seo_score = self._calculate_seo_score(title, keyword)
                engagement_score = self._calculate_engagement_score(title, category)
                
                final_score = (ctr_score * 0.4 + seo_score * 0.3 + engagement_score * 0.3)
                
                scored_titles.append({
                    'title': title,
                    'ctr_score': round(ctr_score, 2),
                    'seo_score': round(seo_score, 2),
                    'engagement_score': round(engagement_score, 2),
                    'final_score': round(final_score, 2),
                    'duplicate_rate': self._estimate_duplicate_rate(title, keyword),
                    'platform_optimized': self._is_platform_optimized(title, platform)
                })
            
            # 3. 점수 순으로 정렬하여 상위 결과 반환
            scored_titles.sort(key=lambda x: x['final_score'], reverse=True)
            
            # 중복 제거 및 다양성 확보
            final_titles = self._ensure_diversity(scored_titles[:count * 2])
            
            ai_logger.log_generation(
                service="OptimizedTitleService",
                operation="generate_optimized_titles_completed",
                user_id="system",
                success=True,
                keyword=keyword,
                generated_count=len(final_titles),
                avg_score=sum(t['final_score'] for t in final_titles) / len(final_titles) if final_titles else 0
            )
            
            return final_titles[:count]
            
        except Exception as e:
            ai_logger.log_generation(
                service="OptimizedTitleService",
                operation="generate_optimized_titles",
                user_id="system",
                success=False,
                keyword=keyword,
                error=str(e)
            )
            return await self._fallback_titles(keyword, category, count)
    
    async def _generate_emotional_titles(self, keyword: str, category: str) -> List[str]:
        """감정을 유발하는 제목 생성"""
        emotional_patterns = [
            f"놀라운 {keyword}의 비밀",
            f"충격적인 {keyword} 사실들",
            f"믿을 수 없는 {keyword} 이야기",
            f"당신이 몰랐던 {keyword}의 진실",
            f"완전 대박인 {keyword} 꿀팁",
            f"진짜 효과있는 {keyword} 방법",
            f"실제로 해본 {keyword} 후기",
            f"정말 신기한 {keyword} 현상",
            f"엄청난 {keyword}의 힘",
            f"감동적인 {keyword} 스토리"
        ]
        
        return emotional_patterns
    
    async def _generate_curiosity_titles(self, keyword: str, category: str) -> List[str]:
        """호기심을 유발하는 제목 생성"""
        curiosity_patterns = [
            f"{keyword}에 숨겨진 비밀",
            f"아무도 모르는 {keyword} 팁",
            f"의외의 {keyword} 활용법",
            f"특별한 {keyword} 이야기",
            f"신박한 {keyword} 아이디어",
            f"독특한 {keyword} 경험",
            f"색다른 {keyword} 접근법",
            f"새로운 {keyword} 트렌드",
            f"최신 {keyword} 소식",
            f"다른 사람들은 모르는 {keyword}"
        ]
        
        return curiosity_patterns
    
    async def _generate_benefit_titles(self, keyword: str, category: str) -> List[str]:
        """혜택과 이익을 강조하는 제목 생성"""
        benefit_patterns = [
            f"무료로 배우는 {keyword}",
            f"공짜 {keyword} 정보",
            f"{keyword}로 돈 절약하는 법",
            f"{keyword} 이득 보는 방법",
            f"꿀팁! {keyword} 활용법",
            f"꿀정보 {keyword} 가이드",
            f"{keyword}로 득템하기",
            f"혜택 많은 {keyword} 추천",
            f"특가 {keyword} 정보",
            f"{keyword} 할인 받는 법"
        ]
        
        return benefit_patterns
    
    async def _generate_social_proof_titles(self, keyword: str, category: str) -> List[str]:
        """사회적 증명을 활용한 제목 생성"""
        social_patterns = [
            f"인기 폭발 {keyword} 추천",
            f"화제의 {keyword} 소개",
            f"바이럴 {keyword} 정보",
            f"핫한 {keyword} 트렌드",
            f"베스트 {keyword} 순위",
            f"1위 {keyword} 리뷰",
            f"추천받은 {keyword} 리스트",
            f"인정받은 {keyword} 방법",
            f"검증된 {keyword} 팁",
            f"모든 사람이 찾는 {keyword}"
        ]
        
        return social_patterns
    
    async def _generate_problem_solving_titles(self, keyword: str, category: str) -> List[str]:
        """문제 해결형 제목 생성"""
        problem_patterns = [
            f"{keyword} 문제 해결법",
            f"{keyword} 고민 상담",
            f"{keyword} 실패 원인과 해답",
            f"{keyword} 성공하는 법",
            f"{keyword} 비법 공개",
            f"{keyword} 못할 때 해결책",
            f"{keyword} 어려울 때 팁",
            f"{keyword} 쉽게 하는 방법",
            f"{keyword} 완벽 가이드",
            f"{keyword} 마스터하기"
        ]
        
        return problem_patterns
    
    async def _generate_list_titles(self, keyword: str, category: str) -> List[str]:
        """리스트형 제목 생성 (숫자 포함)"""
        numbers = [3, 5, 7, 10, 15, 20]
        list_patterns = []
        
        for num in numbers:
            list_patterns.extend([
                f"{num}가지 {keyword} 방법",
                f"{num}개의 {keyword} 팁",
                f"{num}선! {keyword} 추천",
                f"TOP {num} {keyword} 리스트"
            ])
        
        return list_patterns
    
    async def _generate_howto_titles(self, keyword: str, category: str) -> List[str]:
        """How-to 형태의 제목 생성"""
        howto_patterns = [
            f"{keyword} 하는 방법",
            f"{keyword} 시작하는 법",
            f"초보자를 위한 {keyword}",
            f"전문가의 {keyword} 가이드",
            f"완벽한 {keyword} 매뉴얼",
            f"{keyword} 단계별 설명",
            f"{keyword} 쉽게 배우기",
            f"{keyword} 기초부터 고급까지",
            f"{keyword} A to Z",
            f"{keyword} 완전 정복"
        ]
        
        return howto_patterns
    
    def _calculate_ctr_score(self, title: str, keyword: str, category: str, platform: str) -> float:
        """클릭률(CTR) 점수 계산"""
        score = 50.0  # 기본 점수
        
        # 고CTR 단어 포함 점수
        high_ctr_count = sum(1 for word in self.high_ctr_words if word in title)
        score += high_ctr_count * 5
        
        # 감정적 단어 보너스
        emotional_words = ['놀라운', '충격적인', '대박', '완전', '진짜', '실제']
        if any(word in title for word in emotional_words):
            score += 10
        
        # 숫자 포함 보너스
        if re.search(r'\d+', title):
            score += 8
        
        # 길이 최적화 (플랫폼별)
        platform_config = self.platform_patterns.get(platform, {'optimal_length': (40, 60)})
        optimal_min, optimal_max = platform_config['optimal_length']
        title_length = len(title)
        
        if optimal_min <= title_length <= optimal_max:
            score += 10
        elif title_length < optimal_min:
            score -= (optimal_min - title_length) * 0.5
        else:
            score -= (title_length - optimal_max) * 0.3
        
        # 키워드 포함 여부
        if keyword.lower() in title.lower():
            score += 15
        
        # 호기심 유발 요소
        curiosity_indicators = ['비밀', '숨겨진', '몰랐던', '의외의', '특별한']
        if any(indicator in title for indicator in curiosity_indicators):
            score += 12
        
        return min(score, 100)  # 최대 100점
    
    def _calculate_seo_score(self, title: str, keyword: str) -> float:
        """SEO 점수 계산"""
        score = 50.0
        
        # 키워드 위치 (앞쪽에 있을수록 좋음)
        keyword_position = title.lower().find(keyword.lower())
        if keyword_position == 0:
            score += 15
        elif keyword_position <= 10:
            score += 10
        elif keyword_position <= 20:
            score += 5
        
        # 키워드 밀도 (적당해야 함)
        keyword_count = title.lower().count(keyword.lower())
        if keyword_count == 1:
            score += 10
        elif keyword_count == 2:
            score += 5
        elif keyword_count > 2:
            score -= 5
        
        # 제목 길이 (SEO 관점)
        title_length = len(title)
        if 30 <= title_length <= 60:
            score += 10
        elif title_length < 30 or title_length > 70:
            score -= 5
        
        # 특수문자 사용 (적당히)
        special_chars = ['!', '?', ':', '-']
        special_count = sum(title.count(char) for char in special_chars)
        if 1 <= special_count <= 2:
            score += 5
        elif special_count > 3:
            score -= 3
        
        return min(score, 100)
    
    def _calculate_engagement_score(self, title: str, category: str) -> float:
        """참여도 점수 계산"""
        score = 50.0
        
        # 액션 단어 포함
        action_words = ['하는법', '방법', '팁', '가이드', '추천', '리뷰', '비교']
        if any(word in title for word in action_words):
            score += 12
        
        # 개인화 요소
        personal_words = ['나만의', '당신의', '우리', '내', '여러분']
        if any(word in title for word in personal_words):
            score += 8
        
        # 긴급성 표현
        urgency_words = ['지금', '당장', '오늘', '즉시', '빨리', '마지막']
        if any(word in title for word in urgency_words):
            score += 10
        
        # 질문 형태
        if title.endswith('?'):
            score += 6
        
        # 감탄사 사용
        if '!' in title:
            score += 4
        
        return min(score, 100)
    
    def _estimate_duplicate_rate(self, title: str, keyword: str) -> int:
        """중복률 추정 (단순 알고리즘)"""
        # 일반적인 단어가 많을수록 중복률 높음
        common_words = ['방법', '팁', '추천', '리뷰', '가이드', '정보']
        common_count = sum(1 for word in common_words if word in title)
        
        # 길이가 짧을수록 중복 가능성 높음
        length_factor = max(0, 20 - len(title)) * 2
        
        # 특별한 단어가 적을수록 중복률 높음
        unique_words = ['신박한', '독특한', '의외의', '숨겨진', '특별한']
        unique_count = sum(1 for word in unique_words if word in title)
        
        duplicate_rate = (common_count * 15 + length_factor - unique_count * 10)
        return max(5, min(85, duplicate_rate))  # 5-85% 범위
    
    def _is_platform_optimized(self, title: str, platform: str) -> bool:
        """플랫폼 최적화 여부 확인"""
        platform_config = self.platform_patterns.get(platform, {'optimal_length': (40, 60)})
        optimal_min, optimal_max = platform_config['optimal_length']
        
        return optimal_min <= len(title) <= optimal_max
    
    def _ensure_diversity(self, titles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """제목 다양성 확보"""
        diverse_titles = []
        used_patterns = set()
        
        for title_info in titles:
            title = title_info['title']
            
            # 패턴 추출 (첫 2-3 단어)
            pattern = ' '.join(title.split()[:3])
            
            if pattern not in used_patterns:
                diverse_titles.append(title_info)
                used_patterns.add(pattern)
                
                if len(diverse_titles) >= 15:  # 최대 15개까지
                    break
        
        return diverse_titles
    
    async def _fallback_titles(self, keyword: str, category: str, count: int) -> List[Dict[str, Any]]:
        """폴백 제목 (AI 실패 시)"""
        fallback_titles = [
            f"{keyword} 완벽 가이드",
            f"놀라운 {keyword}의 비밀",
            f"{keyword} 추천 베스트",
            f"{keyword} 꿀팁 대공개",
            f"초보자를 위한 {keyword}",
            f"{keyword} 하는 방법",
            f"인기 {keyword} 정보",
            f"{keyword} 완전 정복",
            f"실제 {keyword} 후기",
            f"{keyword} 트렌드"
        ]
        
        result = []
        for i, title in enumerate(fallback_titles[:count]):
            result.append({
                'title': title,
                'ctr_score': 65.0,
                'seo_score': 70.0,
                'engagement_score': 60.0,
                'final_score': 65.0,
                'duplicate_rate': 30,
                'platform_optimized': True
            })
        
        return result


# Export for main.py
__all__ = ['OptimizedTitleService']