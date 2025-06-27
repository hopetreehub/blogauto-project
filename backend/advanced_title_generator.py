"""
시의성과 검색 전략 기반 고급 블로그 제목 생성 시스템
SEO, 바이럴성, 시의성, 클릭 유도 요소를 모두 반영한 전문적인 제목 생성
"""

import re
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass
import asyncio

@dataclass
class TitleTemplate:
    format_type: str  # 질문형, 리스트형, How-to형, 비교형, 공감형
    template: str
    emotion_trigger: str  # 감정 유발 요소
    urgency_level: int  # 긴급성 수준 (1-5)
    seo_power: int  # SEO 효과 (1-5)

class AdvancedTitleGenerator:
    def __init__(self):
        # 계절/시기별 키워드
        self.seasonal_keywords = self._get_seasonal_keywords()
        
        # 트렌드 키워드 (2025년 기준)
        self.trend_keywords = [
            "2025", "최신", "신상", "요즘", "지금", "올해", "이번", "핫한", "인기",
            "MZ세대", "GenZ", "바이럴", "틱톡", "인스타", "유튜브", "AI", "챗GPT"
        ]
        
        # 감정 유발 키워드
        self.emotion_triggers = {
            "호기심": ["궁금한", "신기한", "놀라운", "충격적인", "몰랐던", "숨겨진", "비밀"],
            "공감": ["나만 그런가", "혹시 나도", "모든 사람이", "누구나", "우리 모두"],
            "긴급성": ["지금", "오늘", "당장", "즉시", "빨리", "놓치면 후회"],
            "독점성": ["단독", "최초", "오직", "혼자만", "특별한", "독점 공개"],
            "이익": ["무료", "할인", "혜택", "득템", "꿀팁", "이득"]
        }
        
        # 클릭 유도 키워드
        self.click_baits = [
            "이유", "방법", "비법", "꿀팁", "노하우", "비결", "해법", "솔루션",
            "총정리", "완벽 가이드", "실전 팁", "현실적인", "검증된", "과학적인"
        ]
        
        # 제목 템플릿 정의
        self.title_templates = self._initialize_templates()
        
        # 부정적 키워드 (필터링용)
        self.negative_words = [
            "실패", "포기", "불가능", "어려운", "복잡한", "귀찮은", "힘든"
        ]
    
    def _get_seasonal_keywords(self) -> Dict[str, List[str]]:
        """현재 계절에 맞는 키워드 반환"""
        month = datetime.now().month
        
        seasonal_map = {
            "겨울": ["겨울", "연말", "신년", "크리스마스", "새해", "추위", "난방", "따뜻한"],
            "봄": ["봄", "신학기", "새 시작", "꽃", "미세먼지", "환절기", "알레르기"],
            "여름": ["여름", "휴가", "더위", "시원한", "에어컨", "자외선", "피서", "휴양"],
            "가을": ["가을", "단풍", "환절기", "건조", "독감", "면역", "건강관리"]
        }
        
        if month in [12, 1, 2]:
            current_season = "겨울"
        elif month in [3, 4, 5]:
            current_season = "봄"
        elif month in [6, 7, 8]:
            current_season = "여름"
        else:
            current_season = "가을"
        
        return {
            "current": seasonal_map[current_season],
            "all": seasonal_map
        }
    
    def _initialize_templates(self) -> List[TitleTemplate]:
        """다양한 제목 템플릿 초기화"""
        return [
            # 질문형 템플릿
            TitleTemplate("질문형", "{keyword}하는 이유가 뭘까?", "호기심", 4, 4),
            TitleTemplate("질문형", "{keyword} 효과 있을까? 실제 후기", "의구심", 3, 5),
            TitleTemplate("질문형", "혹시 나도 {keyword} 해야 할까?", "공감", 4, 4),
            TitleTemplate("질문형", "{keyword} vs {alternative}, 어떤 게 좋을까?", "비교", 3, 4),
            TitleTemplate("질문형", "왜 요즘 모두 {keyword}에 열광할까?", "트렌드", 5, 4),
            
            # 리스트형 템플릿
            TitleTemplate("리스트형", "{keyword} 핵심 포인트 5가지", "정리", 3, 5),
            TitleTemplate("리스트형", "{keyword} 실패하는 3가지 이유", "경고", 4, 4),
            TitleTemplate("리스트형", "{keyword} 꿀팁 7선, 이것만 알면 OK", "실용", 4, 5),
            TitleTemplate("리스트형", "{keyword} 단계별 가이드 10분 완성", "간편", 4, 4),
            TitleTemplate("리스트형", "전문가가 추천하는 {keyword} TOP5", "권위", 3, 5),
            
            # How-to형 템플릿
            TitleTemplate("How-to형", "{keyword} 완벽 마스터하는 법", "성취", 3, 5),
            TitleTemplate("How-to형", "초보자도 쉬운 {keyword} 시작하기", "접근성", 3, 4),
            TitleTemplate("How-to형", "{keyword} 제대로 하는 방법은?", "정확성", 3, 4),
            TitleTemplate("How-to형", "하루 10분으로 {keyword} 마스터", "효율", 5, 4),
            TitleTemplate("How-to형", "{keyword} 고수들만 아는 비법", "독점", 4, 4),
            
            # 비교형 템플릿  
            TitleTemplate("비교형", "{keyword} VS {alternative} 완벽 비교", "객관", 3, 5),
            TitleTemplate("비교형", "{keyword} 브랜드별 장단점 분석", "분석", 3, 4),
            TitleTemplate("비교형", "가성비 {keyword} 추천, 이것만 보세요", "경제", 4, 5),
            TitleTemplate("비교형", "{keyword} 진짜 vs 가짜 구별법", "진실", 4, 4),
            
            # 공감형 템플릿
            TitleTemplate("공감형", "나만 {keyword} 어려워하나 싶었는데", "공감", 5, 3),
            TitleTemplate("공감형", "{keyword} 고민, 이제 그만!", "해결", 4, 4),
            TitleTemplate("공감형", "모든 사람이 {keyword}하는 이유", "보편성", 4, 4),
            TitleTemplate("공감형", "{keyword} 스트레스 이겨내는 법", "위로", 4, 3),
            
            # 트렌드형 템플릿
            TitleTemplate("트렌드형", "2025년 {keyword} 트렌드 전망", "미래", 5, 5),
            TitleTemplate("트렌드형", "요즘 핫한 {keyword}, 나도 해볼까?", "유행", 5, 4),
            TitleTemplate("트렌드형", "MZ세대가 선택한 {keyword} 베스트", "세대", 4, 4),
            TitleTemplate("트렌드형", "올해 꼭 해야 할 {keyword} 정리", "연간", 4, 4),
            
            # 긴급형 템플릿
            TitleTemplate("긴급형", "지금 당장 {keyword} 해야 하는 이유", "긴급", 5, 4),
            TitleTemplate("긴급형", "{keyword} 놓치면 후회하는 기회", "기회", 5, 3),
            TitleTemplate("긴급형", "오늘부터 {keyword} 시작해야 하는 이유", "즉시", 5, 4),
            
            # 결과/성과형 템플릿
            TitleTemplate("결과형", "{keyword}으로 인생이 바뀐 후기", "변화", 4, 3),
            TitleTemplate("결과형", "{keyword} 한 달 후 놀라운 변화", "성과", 4, 4),
            TitleTemplate("결과형", "{keyword} 성공 사례와 노하우", "성공", 3, 4),
            
            # 경험형 템플릿
            TitleTemplate("경험형", "실제로 {keyword} 해봤더니...", "경험", 4, 3),
            TitleTemplate("경험형", "{keyword} 직접 체험 솔직 후기", "솔직", 4, 4),
            TitleTemplate("경험형", "{keyword} 3개월 도전기 공개", "도전", 3, 3)
        ]
    
    async def generate_optimized_titles(self, keyword: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        키워드를 기반으로 최적화된 블로그 제목 생성
        
        Args:
            keyword: 기본 키워드
            count: 생성할 제목 개수
        """
        
        # 키워드 분석 및 확장
        analyzed_keyword = self._analyze_keyword(keyword)
        expanded_keywords = self._expand_keyword(keyword)
        
        # 시의성 키워드 추가
        timely_keywords = self._get_timely_keywords()
        
        # 다양한 템플릿으로 제목 생성
        generated_titles = []
        
        # 템플릿 타입별로 균등하게 분배
        template_types = list(set(t.format_type for t in self.title_templates))
        templates_per_type = max(1, count // len(template_types))
        
        for template_type in template_types:
            type_templates = [t for t in self.title_templates if t.format_type == template_type]
            selected_templates = random.sample(type_templates, min(templates_per_type, len(type_templates)))
            
            for template in selected_templates:
                if len(generated_titles) >= count:
                    break
                
                title_data = self._generate_single_title(keyword, template, timely_keywords, expanded_keywords)
                if title_data:
                    generated_titles.append(title_data)
        
        # 부족한 개수만큼 추가 생성
        while len(generated_titles) < count:
            random_template = random.choice(self.title_templates)
            title_data = self._generate_single_title(keyword, random_template, timely_keywords, expanded_keywords)
            if title_data and title_data not in generated_titles:
                generated_titles.append(title_data)
        
        # 점수순으로 정렬하여 상위 항목 반환
        generated_titles.sort(key=lambda x: x['total_score'], reverse=True)
        return generated_titles[:count]
    
    def _analyze_keyword(self, keyword: str) -> Dict[str, Any]:
        """키워드 분석"""
        return {
            "length": len(keyword),
            "word_count": len(keyword.split()),
            "has_brand": self._detect_brand(keyword),
            "category": self._categorize_keyword(keyword),
            "sentiment": self._analyze_sentiment(keyword)
        }
    
    def _expand_keyword(self, keyword: str) -> List[str]:
        """키워드 확장"""
        expansions = [keyword]
        
        # 관련 키워드 추가
        related_terms = {
            "운동": ["헬스", "피트니스", "다이어트", "건강"],
            "음식": ["요리", "레시피", "맛집", "식당"],
            "여행": ["관광", "휴가", "여행지", "숙박"],
            "패션": ["스타일", "코디", "옷", "브랜드"],
            "뷰티": ["화장품", "스킨케어", "메이크업", "관리"],
            "재테크": ["투자", "금융", "돈", "경제"],
            "자기계발": ["성장", "학습", "스킬", "능력"]
        }
        
        for category, terms in related_terms.items():
            if any(term in keyword for term in terms):
                expansions.extend(terms[:2])
        
        return list(set(expansions))
    
    def _get_timely_keywords(self) -> List[str]:
        """시의성 있는 키워드 반환"""
        current_date = datetime.now()
        timely = []
        
        # 현재 계절 키워드
        timely.extend(self.seasonal_keywords["current"])
        
        # 요일별 키워드
        if current_date.weekday() >= 5:  # 주말
            timely.extend(["주말", "휴일", "여가"])
        else:  # 평일
            timely.extend(["월요일", "평일", "직장인"])
        
        # 월별 특성
        month_keywords = {
            1: ["신년", "새해", "다이어트", "결심"],
            2: ["발렌타인", "겨울"],
            3: ["봄", "새학기", "졸업"],
            4: ["벚꽃", "봄나들이"],
            5: ["어린이날", "가정의달"],
            6: ["여름준비", "휴가계획"],
            7: ["여름휴가", "장마"],
            8: ["휴가", "무더위"],
            9: ["가을", "신학기"],
            10: ["단풍", "가을여행"],
            11: ["겨울준비", "추위"],
            12: ["연말", "크리스마스", "정산"]
        }
        
        timely.extend(month_keywords.get(current_date.month, []))
        
        return timely[:5]  # 최대 5개
    
    def _generate_single_title(self, keyword: str, template: TitleTemplate, timely_keywords: List[str], expanded_keywords: List[str]) -> Dict[str, Any]:
        """단일 제목 생성"""
        try:
            # 기본 제목 생성
            title = template.template.format(keyword=keyword, alternative=self._get_alternative_keyword(keyword))
            
            # 시의성 키워드 추가 (30% 확률)
            if random.random() < 0.3 and timely_keywords:
                timely_word = random.choice(timely_keywords)
                title = f"{timely_word} {title}"
            
            # 트렌드 키워드 추가 (20% 확률)
            if random.random() < 0.2:
                trend_word = random.choice(self.trend_keywords)
                title = title.replace(keyword, f"{trend_word} {keyword}")
            
            # 감정 유발 키워드 추가 (40% 확률)
            if random.random() < 0.4:
                emotion_category = random.choice(list(self.emotion_triggers.keys()))
                emotion_word = random.choice(self.emotion_triggers[emotion_category])
                title = f"{emotion_word} {title}"
            
            # 길이 조정 (35자 이내)
            if len(title) > 35:
                title = title[:32] + "..."
            
            # 점수 계산
            scores = self._calculate_title_score(title, keyword, template)
            
            return {
                "title": title,
                "format_type": template.format_type,
                "emotion_trigger": template.emotion_trigger,
                "seo_score": scores["seo"],
                "click_score": scores["click"],
                "viral_score": scores["viral"],
                "timely_score": scores["timely"],
                "total_score": scores["total"],
                "length": len(title),
                "reason": self._generate_title_reason(title, scores)
            }
        
        except Exception as e:
            print(f"제목 생성 오류: {e}")
            return None
    
    def _get_alternative_keyword(self, keyword: str) -> str:
        """대체 키워드 생성"""
        alternatives = {
            "운동": "다이어트",
            "음식": "요리", 
            "여행": "휴가",
            "공부": "학습",
            "일": "업무",
            "돈": "재테크"
        }
        
        for key, alt in alternatives.items():
            if key in keyword:
                return alt
        
        return "다른 방법"
    
    def _calculate_title_score(self, title: str, keyword: str, template: TitleTemplate) -> Dict[str, float]:
        """제목 점수 계산"""
        scores = {
            "seo": 0.0,
            "click": 0.0, 
            "viral": 0.0,
            "timely": 0.0
        }
        
        # SEO 점수
        scores["seo"] = template.seo_power * 20  # 기본 점수
        if keyword in title:
            scores["seo"] += 10
        if any(word in title for word in self.click_baits):
            scores["seo"] += 15
        if len(title) <= 35:
            scores["seo"] += 10
        
        # 클릭 유도 점수
        scores["click"] = template.urgency_level * 15
        if any(word in title for word in ["?", "!", "이유", "방법", "비법"]):
            scores["click"] += 20
        if any(word in title for word in self.emotion_triggers["호기심"]):
            scores["click"] += 15
        
        # 바이럴 점수
        viral_words = ["놀라운", "충격", "대박", "꿀팁", "비밀", "독점"]
        scores["viral"] = sum(10 for word in viral_words if word in title)
        if any(word in title for word in self.trend_keywords):
            scores["viral"] += 25
        
        # 시의성 점수
        timely_words = self.seasonal_keywords["current"] + ["2025", "요즘", "지금", "올해"]
        scores["timely"] = sum(15 for word in timely_words if word in title)
        
        # 총점 계산 (가중 평균)
        weights = {"seo": 0.3, "click": 0.3, "viral": 0.2, "timely": 0.2}
        scores["total"] = sum(scores[key] * weights[key] for key in weights)
        
        return scores
    
    def _generate_title_reason(self, title: str, scores: Dict[str, float]) -> str:
        """제목 추천 이유 생성"""
        reasons = []
        
        if scores["seo"] > 70:
            reasons.append("SEO 최적화")
        if scores["click"] > 60:
            reasons.append("클릭 유도력 높음")
        if scores["viral"] > 50:
            reasons.append("바이럴 가능성")
        if scores["timely"] > 40:
            reasons.append("시의성 반영")
        if len(title) <= 30:
            reasons.append("적절한 길이")
        
        return ", ".join(reasons) if reasons else "균형잡힌 제목"
    
    def _detect_brand(self, keyword: str) -> bool:
        """브랜드명 감지"""
        brands = ["삼성", "애플", "구글", "네이버", "카카오", "LG", "현대"]
        return any(brand in keyword for brand in brands)
    
    def _categorize_keyword(self, keyword: str) -> str:
        """키워드 카테고리 분류"""
        categories = {
            "건강": ["운동", "다이어트", "헬스", "건강", "의료"],
            "음식": ["음식", "요리", "맛집", "레시피", "식당"],
            "여행": ["여행", "관광", "휴가", "호텔", "항공"],
            "기술": ["AI", "프로그래밍", "앱", "소프트웨어", "IT"],
            "라이프스타일": ["인테리어", "패션", "뷰티", "생활"]
        }
        
        for category, words in categories.items():
            if any(word in keyword for word in words):
                return category
        
        return "일반"
    
    def _analyze_sentiment(self, keyword: str) -> str:
        """키워드 감정 분석"""
        positive_words = ["좋은", "최고", "완벽", "성공", "행복"]
        negative_words = ["나쁜", "실패", "문제", "고민", "스트레스"]
        
        if any(word in keyword for word in positive_words):
            return "긍정"
        elif any(word in keyword for word in negative_words):
            return "부정"
        else:
            return "중립"

# 사용 예시 및 테스트
async def test_advanced_title_generator():
    """고급 제목 생성기 테스트"""
    generator = AdvancedTitleGenerator()
    
    test_keywords = ["장마철 건강관리", "스탠딩책상", "재택근무", "다이어트"]
    
    for keyword in test_keywords:
        print(f"\n=== '{keyword}' 키워드 제목 생성 ===")
        titles = await generator.generate_optimized_titles(keyword, 5)
        
        for i, title_data in enumerate(titles, 1):
            print(f"{i}. {title_data['title']}")
            print(f"   타입: {title_data['format_type']}")
            print(f"   총점: {title_data['total_score']:.1f}")
            print(f"   추천이유: {title_data['reason']}")
            print()

if __name__ == "__main__":
    asyncio.run(test_advanced_title_generator())