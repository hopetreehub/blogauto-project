#!/usr/bin/env python3
"""
스마트 제목 생성기
키워드 특성에 맞는 자연스럽고 매력적인 제목 생성
"""

import random
import re
from datetime import datetime
from typing import Dict, List, Tuple

class SmartTitleGenerator:
    
    def __init__(self):
        # 현재 연도
        self.current_year = datetime.now().year
        
        # 카테고리별 제목 템플릿
        self.category_templates = {
            "health": {
                "power_words": ["효과적인", "검증된", "과학적인", "안전한", "자연스러운", "건강한"],
                "action_words": ["개선하는", "높이는", "강화하는", "지키는", "관리하는", "유지하는"],
                "benefit_words": ["효능", "효과", "이점", "장점", "비법", "방법"],
                "title_patterns": [
                    "{power_word} {keyword}의 {benefit_word} {count}가지",
                    "{keyword}로 {action_word} 건강 관리법",
                    "의사가 추천하는 {keyword} 완벽 가이드",
                    "{keyword}의 놀라운 {benefit_word}과 실천법",
                    "매일 실천하는 {keyword} 건강 루틴",
                    "{keyword} 초보자를 위한 단계별 가이드",
                    "전문가가 알려주는 {keyword}의 모든 것",
                    "{keyword}와 건강: 알아야 할 핵심 정보"
                ]
            },
            "food": {
                "power_words": ["맛있는", "영양가 높은", "간단한", "특별한", "건강한", "신선한"],
                "action_words": ["요리하는", "만드는", "활용하는", "준비하는", "보관하는", "선택하는"],
                "benefit_words": ["레시피", "요리법", "활용법", "비법", "팁", "방법"],
                "title_patterns": [
                    "{power_word} {keyword} {benefit_word} {count}가지",
                    "{keyword}로 {action_word} 건강 요리",
                    "요리 초보도 성공하는 {keyword} 레시피",
                    "{keyword}의 영양과 맛을 살리는 조리법",
                    "매일 먹고 싶은 {keyword} 요리 아이디어",
                    "영양사가 추천하는 {keyword} 활용 가이드",
                    "{keyword} 고르는 법부터 요리까지",
                    "집에서 {action_word} {keyword} 완벽 레시피"
                ]
            },
            "business": {
                "power_words": ["성공하는", "효과적인", "검증된", "실용적인", "혁신적인", "전략적인"],
                "action_words": ["활용하는", "적용하는", "실행하는", "구축하는", "개선하는", "성장하는"],
                "benefit_words": ["전략", "방법", "노하우", "시스템", "프로세스", "솔루션"],
                "title_patterns": [
                    "{power_word} {keyword} {benefit_word} {count}단계",
                    "{keyword}로 {action_word} 비즈니스 성공법",
                    "전문가가 검증한 {keyword} 완벽 가이드",
                    "{keyword} 도입부터 성과까지",
                    "실무진이 말하는 {keyword}의 핵심",
                    "{keyword} 초보자를 위한 실전 매뉴얼",
                    "ROI를 높이는 {keyword} 활용 전략",
                    "{keyword} 성공 사례와 실행 방법"
                ]
            },
            "technology": {
                "power_words": ["최신", "실용적인", "효율적인", "혁신적인", "스마트한", "간편한"],
                "action_words": ["활용하는", "적용하는", "구현하는", "개발하는", "운영하는", "최적화하는"],
                "benefit_words": ["기술", "도구", "솔루션", "시스템", "플랫폼", "방법"],
                "title_patterns": [
                    "{power_word} {keyword} {benefit_word} {count}선",
                    "{keyword}로 {action_word} 디지털 혁신",
                    "개발자가 추천하는 {keyword} 완전정복",
                    "{keyword} 초보자도 이해하는 실무 가이드",
                    "실제 현장에서 사용하는 {keyword} 활용법",
                    "{keyword} 도입부터 운영까지",
                    "전문가가 알려주는 {keyword}의 모든 것",
                    "{keyword} 트렌드와 실무 적용 사례"
                ]
            },
            "lifestyle": {
                "power_words": ["행복한", "만족스러운", "의미 있는", "특별한", "소중한", "아름다운"],
                "action_words": ["만들어가는", "즐기는", "실천하는", "추구하는", "완성하는", "경험하는"],
                "benefit_words": ["라이프스타일", "일상", "습관", "방법", "비법", "팁"],
                "title_patterns": [
                    "{power_word} {keyword} {benefit_word} {count}가지",
                    "{keyword}로 {action_word} 일상의 변화",
                    "삶의 질을 높이는 {keyword} 가이드",
                    "{keyword} 초보자를 위한 실천 방법",
                    "매일이 특별해지는 {keyword} 루틴",
                    "전문가가 제안하는 {keyword} 라이프",
                    "{keyword}로 찾는 나만의 행복",
                    "{keyword}와 함께하는 의미 있는 일상"
                ]
            }
        }
        
        # 숫자 관련 패턴
        self.number_patterns = [
            "3가지", "5가지", "7가지", "10가지",
            "3단계", "5단계", "7단계",
            "3개월", "6개월", "1년",
            "30일", "100일"
        ]
        
        # 감정적 호소 단어들
        self.emotional_words = {
            "positive": ["놀라운", "효과적인", "완벽한", "최고의", "검증된", "강력한"],
            "urgency": ["놓치면 안 되는", "반드시 알아야 할", "지금 당장", "더 늦기 전에"],
            "curiosity": ["숨겨진", "의외의", "모르면 손해인", "전문가만 아는"],
            "achievement": ["성공하는", "달성하는", "완성하는", "마스터하는"]
        }

    def categorize_keyword(self, keyword: str) -> str:
        """키워드를 카테고리로 분류"""
        keyword_lower = keyword.lower()
        
        health_patterns = ["건강", "면역", "다이어트", "운동", "체중", "질병", "치료", "예방", "의학", "영양"]
        food_patterns = ["식단", "음식", "요리", "레시피", "식품", "채소", "과일", "고기", "생선", "조리"]
        business_patterns = ["비즈니스", "사업", "창업", "투자", "마케팅", "세일즈", "수익", "전략", "경영"]
        tech_patterns = ["기술", "IT", "프로그래밍", "앱", "소프트웨어", "AI", "블록체인", "클라우드"]
        
        if any(pattern in keyword_lower for pattern in health_patterns):
            return "health"
        elif any(pattern in keyword_lower for pattern in food_patterns):
            return "food" 
        elif any(pattern in keyword_lower for pattern in business_patterns):
            return "business"
        elif any(pattern in keyword_lower for pattern in tech_patterns):
            return "technology"
        else:
            return "lifestyle"

    def generate_number_variant(self) -> str:
        """적절한 숫자 표현 생성"""
        return random.choice(self.number_patterns)

    def add_emotional_appeal(self, title: str, category: str) -> str:
        """감정적 호소력 추가"""
        if random.random() < 0.3:  # 30% 확률로 감정적 단어 추가
            emotion_type = random.choice(list(self.emotional_words.keys()))
            emotion_word = random.choice(self.emotional_words[emotion_type])
            
            # 제목 앞에 추가하는 경우
            if emotion_type in ["urgency", "curiosity"]:
                return f"{emotion_word} {title}"
            # 형용사 교체하는 경우
            else:
                return title.replace("효과적인", emotion_word).replace("좋은", emotion_word)
        
        return title

    def make_title_natural(self, title: str, keyword: str) -> str:
        """제목을 더 자연스럽게 만들기"""
        # 부자연스러운 반복 제거
        words = title.split()
        cleaned_words = []
        prev_word = ""
        
        for word in words:
            # 연속된 같은 단어 제거
            if word != prev_word:
                cleaned_words.append(word)
            prev_word = word
        
        title = " ".join(cleaned_words)
        
        # 특정 패턴의 중복 제거 (예: "5가지가지" -> "5가지")
        title = re.sub(r'(\d+가지)가지', r'\1', title)
        title = re.sub(r'(\d+단계)단계', r'\1', title)
        title = re.sub(r'(\w+)(\1)', r'\1', title)  # 연속된 같은 단어 제거
        
        # 문법 검사 및 수정
        title = re.sub(r'\s+', ' ', title)  # 중복 공백 제거
        title = title.strip()
        
        # 자연스러운 조사 추가
        if not title.endswith(('다', '요', '법', '것', '기', '하기', '까지', '부터', '정복', '가이드')):
            if random.random() < 0.4:
                title += " 완전정복"
            elif random.random() < 0.3:
                title += " 가이드"
        
        return title

    def generate_seo_optimized_titles(self, keyword: str, count: int = 5, tone: str = "professional") -> List[Dict]:
        """SEO 최적화된 제목 생성"""
        category = self.categorize_keyword(keyword)
        template = self.category_templates.get(category, self.category_templates["lifestyle"])
        
        titles = []
        used_patterns = set()
        
        for i in range(count):
            # 중복 방지를 위해 사용되지 않은 패턴 선택
            available_patterns = [p for p in template["title_patterns"] if p not in used_patterns]
            if not available_patterns:
                available_patterns = template["title_patterns"]
                used_patterns.clear()
            
            pattern = random.choice(available_patterns)
            used_patterns.add(pattern)
            
            # 패턴에 맞는 단어들 선택
            power_word = random.choice(template["power_words"])
            action_word = random.choice(template["action_words"])
            benefit_word = random.choice(template["benefit_words"])
            count_num = self.generate_number_variant()
            
            # 제목 생성
            title = pattern.format(
                keyword=keyword,
                power_word=power_word,
                action_word=action_word,
                benefit_word=benefit_word,
                count=count_num
            )
            
            # 자연스럽게 만들기
            title = self.make_title_natural(title, keyword)
            
            # 감정적 호소력 추가 (선택적)
            if random.random() < 0.4:
                title = self.add_emotional_appeal(title, category)
            
            # 점수 계산
            score = self.calculate_title_score(title, keyword, category)
            seo_score = self.calculate_seo_score(title, keyword)
            click_potential = self.assess_click_potential(title)
            
            titles.append({
                "title": title,
                "score": round(score, 1),
                "seo_score": round(seo_score, 1),
                "click_potential": click_potential,
                "category": category,
                "reason": f"카테고리별 최적화 ({category}), {tone} 톤, 자연스러운 문법"
            })
        
        # 점수 순으로 정렬
        titles.sort(key=lambda x: x["score"], reverse=True)
        
        return titles

    def generate_with_guidelines(self, keyword: str, count: int = 5, tone: str = "professional", guidelines: str = "") -> List[Dict]:
        """사용자 지침을 완전히 적용한 제목 생성"""
        
        if not guidelines.strip():
            # 지침이 없으면 기본 생성
            return self.generate_seo_optimized_titles(keyword, count, tone)
        
        print(f"사용자 지침 완전 적용 모드: {guidelines[:100]}...")
        
        # 지침 분석
        guidelines_lower = guidelines.lower()
        style_analysis = self._analyze_title_style(guidelines_lower)
        
        # 지침 기반 제목 생성
        titles = []
        used_patterns = set()
        
        for i in range(count):
            # 지침에 맞는 제목 생성
            title = self._generate_guidelines_based_title(keyword, style_analysis, used_patterns)
            
            # 점수 계산
            score = self.calculate_title_score(title, keyword, "health")
            seo_score = self.calculate_seo_score(title, keyword)
            click_potential = self.assess_click_potential(title)
            
            titles.append({
                "title": title,
                "score": round(score, 1),
                "seo_score": round(seo_score, 1),
                "click_potential": click_potential,
                "category": "health",
                "reason": f"사용자 지침 완전 적용: {style_analysis['tone']} 톤, {style_analysis['formality']} 스타일",
                "guidelines_applied": True,
                "style_applied": style_analysis
            })
        
        # 점수 순으로 정렬
        titles.sort(key=lambda x: x["score"], reverse=True)
        
        return titles
    
    def _analyze_title_style(self, guidelines_lower: str) -> dict:
        """제목 스타일 분석"""
        style = {
            "formality": "formal",  # formal, casual
            "tone": "professional",  # professional, friendly, enthusiastic
            "length_preference": "medium",  # short, medium, long
            "use_numbers": False,
            "use_emojis": False,
            "include_benefit": True,
            "include_action": True
        }
        
        # 반말/존댓말 분석
        if any(word in guidelines_lower for word in ["반말", "친근", "편하게", "접근하기 쉬운"]):
            style["formality"] = "casual"
            style["tone"] = "friendly"
        
        # 톤 분석
        if any(word in guidelines_lower for word in ["열정적", "신나게", "활기차게"]):
            style["tone"] = "enthusiastic"
        elif any(word in guidelines_lower for word in ["친근", "따뜻", "편안"]):
            style["tone"] = "friendly"
        
        # 길이 분석
        if any(word in guidelines_lower for word in ["짧게", "간단", "임팩트"]):
            style["length_preference"] = "short"
        elif any(word in guidelines_lower for word in ["자세하게", "상세"]):
            style["length_preference"] = "long"
        
        # 숫자 포함
        if any(word in guidelines_lower for word in ["숫자", "가지", "단계", "방법"]):
            style["use_numbers"] = True
        
        # 이모티콘 사용
        if any(word in guidelines_lower for word in ["이모티콘", "이모지"]):
            style["use_emojis"] = True
        
        return style
    
    def _generate_guidelines_based_title(self, keyword: str, style: dict, used_patterns: set) -> str:
        """지침 기반 제목 생성"""
        
        # 기본 패턴들
        if style["formality"] == "casual":
            if style["use_numbers"]:
                patterns = [
                    f"{keyword} 쉽게 시작하는 방법 5가지",
                    f"{keyword} 초보자도 할 수 있는 팁 7가지",
                    f"{keyword} 바로 적용하는 실전 가이드 3단계",
                    f"{keyword} 성공하는 노하우 10가지",
                    f"{keyword} 완전정복 5가지 방법"
                ]
            else:
                patterns = [
                    f"{keyword} 쉽게 시작하는 방법",
                    f"{keyword} 초보자 완전 가이드",
                    f"{keyword} 바로 적용하는 실전 팁",
                    f"{keyword} 성공하는 노하우 공개",
                    f"{keyword} 완전정복 가이드"
                ]
        else:  # formal
            if style["use_numbers"]:
                patterns = [
                    f"전문가가 추천하는 {keyword} 5가지 방법",
                    f"{keyword} 완벽 가이드: 핵심 포인트 7가지",
                    f"검증된 {keyword} 실천법 3단계",
                    f"{keyword} 전문가 조언 10가지",
                    f"{keyword} 체계적 접근법 5단계"
                ]
            else:
                patterns = [
                    f"전문가가 추천하는 {keyword} 완벽 가이드",
                    f"{keyword} 전문가 조언과 실천법",
                    f"검증된 {keyword} 체계적 접근법",
                    f"{keyword} 성공을 위한 전문가 가이드",
                    f"{keyword} 올바른 이해와 실천"
                ]
        
        # 사용되지 않은 패턴 선택
        available_patterns = [p for p in patterns if p not in used_patterns]
        if not available_patterns:
            available_patterns = patterns
            used_patterns.clear()
        
        title = random.choice(available_patterns)
        used_patterns.add(title)
        
        # 길이 조정
        if style["length_preference"] == "short" and len(title) > 30:
            # 짧게 만들기
            if "방법" in title:
                title = title.replace(" 방법", "법")
            if "가이드" in title:
                title = title.replace(" 가이드", "")
            if "완벽한" in title:
                title = title.replace("완벽한 ", "")
        
        # 이모티콘 추가
        if style["use_emojis"]:
            emoji_map = {
                "방법": "💡",
                "가이드": "📚",
                "팁": "💪",
                "성공": "🎯",
                "완전정복": "🏆"
            }
            for word, emoji in emoji_map.items():
                if word in title:
                    title = f"{title} {emoji}"
                    break
        
        # 자연스러운 문법 수정
        title = self.make_title_natural(title, keyword)
        
        return title

    def calculate_title_score(self, title: str, keyword: str, category: str) -> float:
        """제목 품질 점수 계산"""
        score = 70.0  # 기본 점수
        
        # 키워드 포함 여부
        if keyword.lower() in title.lower():
            score += 15
        
        # 제목 길이 (SEO 최적화)
        title_length = len(title)
        if 30 <= title_length <= 60:
            score += 10
        elif 20 <= title_length <= 70:
            score += 5
        
        # 숫자 포함 (클릭률 향상)
        if any(num in title for num in ["3", "5", "7", "10", "30", "100"]):
            score += 8
        
        # 감정적 단어 포함
        emotional_words_flat = [word for words in self.emotional_words.values() for word in words]
        if any(word in title for word in emotional_words_flat):
            score += 5
        
        # 카테고리 관련성
        category_words = {
            "health": ["건강", "효과", "방법", "가이드", "비법"],
            "food": ["요리", "레시피", "맛", "영양", "조리"],
            "business": ["전략", "성공", "방법", "노하우", "시스템"],
            "technology": ["기술", "활용", "도구", "시스템", "솔루션"],
            "lifestyle": ["일상", "라이프", "방법", "습관", "팁"]
        }
        
        if category in category_words:
            if any(word in title for word in category_words[category]):
                score += 7
        
        return min(score, 100.0)

    def calculate_seo_score(self, title: str, keyword: str) -> float:
        """SEO 점수 계산"""
        score = 60.0  # 기본 점수
        
        # 키워드가 제목 앞쪽에 있는지
        if title.lower().startswith(keyword.lower()):
            score += 20
        elif keyword.lower() in title.lower()[:len(title)//2]:
            score += 15
        elif keyword.lower() in title.lower():
            score += 10
        
        # 제목 길이 SEO 최적화
        if 50 <= len(title) <= 60:
            score += 15
        elif 40 <= len(title) <= 70:
            score += 10
        
        # 특수문자 및 구조
        if ":" in title:
            score += 5
        if any(num in title for num in ["3", "5", "7", "10"]):
            score += 5
        
        return min(score, 100.0)

    def assess_click_potential(self, title: str) -> str:
        """클릭 잠재력 평가"""
        score = 0
        
        # 감정적 호소 단어
        emotional_words_flat = [word for words in self.emotional_words.values() for word in words]
        if any(word in title for word in emotional_words_flat):
            score += 2
        
        # 숫자 포함
        if any(num in title for num in ["3", "5", "7", "10"]):
            score += 2
        
        # 행동 유도 단어
        action_indicators = ["방법", "가이드", "비법", "팁", "전략", "노하우"]
        if any(word in title for word in action_indicators):
            score += 1
        
        # 전문성 표시
        expert_words = ["전문가", "의사", "영양사", "요리사", "개발자"]
        if any(word in title for word in expert_words):
            score += 1
        
        if score >= 5:
            return "very_high"
        elif score >= 3:
            return "high"
        elif score >= 1:
            return "medium"
        else:
            return "low"

# 인스턴스 생성
smart_title_generator = SmartTitleGenerator()