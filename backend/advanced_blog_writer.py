"""
SEO + GEO 최적화 고급 블로그 글쓰기 시스템
AI 세대를 선도하는 블로그 콘텐츠 자동 생성기
"""

import re
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class BlogTitle:
    title: str
    seo_score: int
    geo_score: int
    viral_potential: int
    total_score: float

@dataclass
class BlogContent:
    title: str
    content: str
    word_count: int
    seo_keywords: List[str]
    lsi_keywords: List[str]
    readability_score: int
    geo_optimization_score: int

class AdvancedBlogWriter:
    def __init__(self):
        # LSI 키워드 데이터베이스
        self.lsi_keywords_db = {
            "운동": ["헬스", "피트니스", "다이어트", "근육", "유산소", "무산소", "스트레칭", "웨이트"],
            "음식": ["요리", "레시피", "맛집", "식단", "영양", "건강식", "다이어트식", "조리법"],
            "여행": ["관광", "휴가", "여행지", "호텔", "항공", "패키지", "숙박", "관광명소"],
            "건강": ["웰빙", "영양", "질병", "예방", "치료", "면역", "의료", "건강관리"],
            "재테크": ["투자", "주식", "부동산", "금융", "경제", "수익", "자산", "포트폴리오"],
            "뷰티": ["화장품", "스킨케어", "메이크업", "미용", "관리", "제품", "브랜드", "루틴"],
            "패션": ["스타일", "코디", "브랜드", "트렌드", "의류", "액세서리", "쇼핑", "룩북"],
            "자기계발": ["성장", "학습", "스킬", "능력", "자기관리", "목표", "성취", "발전"]
        }
        
        # GEO 최적화용 인용 친화적 표현
        self.citation_phrases = [
            "최근 연구에 따르면",
            "한 보고서에 따르면", 
            "통계적으로 밝혀진 바에 의하면",
            "전문가들은 지적한다",
            "여러 연구결과가 보여주듯",
            "데이터 분석 결과",
            "실제 조사에서 나타난 바와 같이",
            "학계에서는 이를",
            "관련 업계 전문가들은",
            "국내외 사례를 살펴보면"
        ]
        
        # 감정 유발 키워드
        self.emotional_keywords = {
            "호기심": ["놀라운", "신기한", "충격적인", "혁신적인", "독특한"],
            "공감": ["우리 모두", "누구나", "많은 사람들이", "흔히", "대부분"],
            "긴급성": ["지금", "당장", "즉시", "빠르게", "신속하게"],
            "신뢰성": ["검증된", "입증된", "확실한", "믿을 수 있는", "과학적인"],
            "성취": ["성공", "달성", "완성", "마스터", "정복"]
        }
        
        # 현재 트렌드 키워드 (2025년 기준)
        self.trend_keywords = [
            "2025", "최신", "트렌드", "인기", "요즘", "올해", "이번", "신상", "핫한",
            "MZ세대", "GenZ", "AI", "디지털", "온라인", "스마트", "지속가능한"
        ]

    async def generate_blog_content(self, keyword: str) -> Dict[str, Any]:
        """키워드 기반 완전 자동 블로그 콘텐츠 생성"""
        
        # 1단계: SEO 검색 의도 + GEO 인용 가능성 기반 서브주제 추출
        subtopics = self._extract_subtopics(keyword)
        
        # 2단계: SEO + GEO 최적화 제목 3개 생성
        title_candidates = self._generate_optimized_titles(keyword, subtopics)
        
        # 3단계: 최고 점수 제목 선택
        best_title = max(title_candidates, key=lambda x: x.total_score)
        
        # 4단계: LSI 키워드 및 관련어 추출
        lsi_keywords = self._get_lsi_keywords(keyword)
        
        # 5단계: 블로그 본문 생성 (SEO + GEO 완전 최적화)
        blog_content = self._generate_full_content(
            best_title.title, 
            keyword, 
            subtopics, 
            lsi_keywords
        )
        
        return {
            "title_candidates": [
                {
                    "title": title.title,
                    "seo_score": title.seo_score,
                    "geo_score": title.geo_score,
                    "viral_potential": title.viral_potential,
                    "total_score": title.total_score
                }
                for title in title_candidates
            ],
            "selected_title": best_title.title,
            "content": blog_content.content,
            "word_count": blog_content.word_count,
            "seo_keywords": blog_content.seo_keywords,
            "lsi_keywords": blog_content.lsi_keywords,
            "readability_score": blog_content.readability_score,
            "geo_optimization_score": blog_content.geo_optimization_score,
            "subtopics": subtopics
        }

    def _extract_subtopics(self, keyword: str) -> List[str]:
        """SEO 검색 의도 + GEO 인용 가능성 기반 서브주제 추출"""
        
        # 기본 서브주제 템플릿
        subtopic_templates = {
            "정의형": f"{keyword}란 무엇인가",
            "방법형": f"{keyword} 하는 방법",
            "이유형": f"{keyword}하는 이유",
            "효과형": f"{keyword}의 효과",
            "비교형": f"{keyword} 종류별 비교",
            "팁형": f"{keyword} 꿀팁",
            "주의형": f"{keyword} 주의사항",
            "트렌드형": f"2025년 {keyword} 트렌드",
            "성공형": f"{keyword} 성공 사례",
            "미래형": f"{keyword}의 미래 전망"
        }
        
        # 키워드 카테고리에 따른 맞춤형 서브주제 생성
        category = self._categorize_keyword(keyword)
        
        if category == "건강":
            specific_subtopics = [
                f"{keyword}의 건강상 이점",
                f"{keyword} 시작하는 올바른 방법", 
                f"{keyword} 관련 주의사항과 부작용"
            ]
        elif category == "음식":
            specific_subtopics = [
                f"{keyword}의 영양성분과 효능",
                f"{keyword} 맛있게 만드는 레시피",
                f"{keyword} 보관법과 선택 요령"
            ]
        elif category == "여행":
            specific_subtopics = [
                f"{keyword} 여행 계획 세우기",
                f"{keyword} 필수 준비물과 팁",
                f"{keyword} 예산 절약 방법"
            ]
        elif category == "기술":
            specific_subtopics = [
                f"{keyword}의 작동 원리와 특징",
                f"{keyword} 활용법과 실제 사례",
                f"{keyword}의 장단점 분석"
            ]
        else:
            # 일반적인 서브주제
            specific_subtopics = [
                f"{keyword}의 핵심 포인트",
                f"{keyword} 실전 활용법",
                f"{keyword} 관련 최신 동향"
            ]
        
        return specific_subtopics

    def _generate_optimized_titles(self, keyword: str, subtopics: List[str]) -> List[BlogTitle]:
        """SEO + GEO 최적화 제목 3개 생성"""
        
        title_templates = [
            # SEO 강화형
            f"{keyword} 완벽 가이드: 2025년 최신 정보 총정리",
            f"{keyword} 제대로 알고 시작하기 - 초보자도 쉬운 방법",
            f"{keyword} 꿀팁 5가지, 이것만 알면 전문가급!",
            
            # GEO 최적화형 (AI 인용 친화적)
            f"전문가가 밝히는 {keyword}의 모든 것",
            f"연구로 입증된 {keyword}의 놀라운 효과",
            f"데이터로 보는 {keyword} 완벽 분석",
            
            # 바이럴형
            f"요즘 핫한 {keyword}, 나도 해볼까?",
            f"{keyword} 3개월 후기, 인생이 바뀌었다",
            f"모든 사람이 {keyword}하는 진짜 이유",
            
            # 트렌드형
            f"2025년 {keyword} 트렌드 예측",
            f"MZ세대가 선택한 {keyword} 베스트",
            f"올해 꼭 해야 할 {keyword} 정리"
        ]
        
        titles = []
        selected_templates = random.sample(title_templates, 3)
        
        for template in selected_templates:
            title_obj = BlogTitle(
                title=template,
                seo_score=self._calculate_seo_score(template, keyword),
                geo_score=self._calculate_geo_score(template),
                viral_potential=self._calculate_viral_score(template),
                total_score=0
            )
            # 총점 계산 (가중평균)
            title_obj.total_score = (
                title_obj.seo_score * 0.4 + 
                title_obj.geo_score * 0.3 + 
                title_obj.viral_potential * 0.3
            )
            titles.append(title_obj)
        
        return titles

    def _get_lsi_keywords(self, keyword: str) -> List[str]:
        """LSI 키워드 자동 탐색"""
        lsi_keywords = []
        
        # 직접 매칭
        for category, keywords in self.lsi_keywords_db.items():
            if any(word in keyword for word in keywords) or category in keyword:
                lsi_keywords.extend(keywords[:4])  # 상위 4개만
                break
        
        # 일반적인 LSI 키워드 추가
        general_lsi = [
            f"{keyword} 방법", f"{keyword} 효과", f"{keyword} 팁", 
            f"{keyword} 가이드", f"{keyword} 정보", f"{keyword} 추천"
        ]
        
        lsi_keywords.extend(general_lsi[:3])
        
        return list(set(lsi_keywords))[:10]  # 중복 제거 후 최대 10개

    def _generate_full_content(self, title: str, keyword: str, subtopics: List[str], lsi_keywords: List[str]) -> BlogContent:
        """SEO + GEO 완전 최적화 블로그 본문 생성"""
        
        # 인용 구문 선택
        citation = random.choice(self.citation_phrases)
        secondary_citation = random.choice(self.citation_phrases)
        
        # 감정 키워드 선택
        emotional_word = random.choice(self.emotional_keywords["호기심"])
        trust_word = random.choice(self.emotional_keywords["신뢰성"])
        
        # 트렌드 키워드 선택
        trend_word = random.choice(self.trend_keywords)
        
        # 본문 구성
        content_sections = []
        
        # 1. 도입부 (호기심 유발 + GEO 최적화)
        intro = f"""
{title}

{emotional_word} {keyword}에 대해 궁금해하시는 분들이 정말 많습니다. {citation}, {keyword}는 우리 일상에서 점점 더 중요한 역할을 하고 있는 것으로 나타났습니다.

이 글에서는 {keyword}에 대한 모든 것을 {trust_word} 정보와 실제 경험을 바탕으로 상세히 알려드리겠습니다. 특히 {trend_word} 트렌드에 맞춘 최신 정보까지 포함했으니 끝까지 읽어보시기 바랍니다.
        """
        content_sections.append(intro.strip())
        
        # 2. 본론 섹션들 (서브주제 기반)
        for i, subtopic in enumerate(subtopics, 1):
            
            # LSI 키워드 자연스럽게 삽입
            section_lsi = random.choice(lsi_keywords) if lsi_keywords else keyword
            section_citation = random.choice(self.citation_phrases)
            
            section_content = f"""
## {i}. {subtopic}

{section_citation}, {keyword}와 관련하여 {section_lsi}는 매우 중요한 요소로 분석되었습니다. 실제로 많은 사람들이 {keyword}를 시작할 때 가장 먼저 고려해야 할 부분이기도 합니다.

{keyword}의 경우 개인차가 있을 수 있지만, 일반적으로 다음과 같은 특징을 보입니다:

• **첫 번째 포인트**: {keyword}를 처음 접하는 분들도 쉽게 이해할 수 있도록 단계별로 설명드리겠습니다.
• **두 번째 포인트**: {section_lsi}와의 연관성을 고려하면 더욱 효과적인 결과를 얻을 수 있습니다.
• **세 번째 포인트**: 전문가들이 추천하는 방법을 실제로 적용해보시면 확실한 변화를 경험하실 것입니다.

특히 주목할 점은 {keyword}의 활용도가 {trend_word}에 들어 크게 높아지고 있다는 것입니다.
            """
            content_sections.append(section_content.strip())
        
        # 3. 결론 (CTA 포함)
        conclusion = f"""
## 마무리

지금까지 {keyword}에 대해 자세히 알아보았습니다. {secondary_citation}, 꾸준히 실천하는 것이 가장 중요한 성공 요인으로 밝혀졌습니다.

{keyword}는 단순히 일시적인 유행이 아닌, 앞으로도 계속 주목받을 중요한 주제입니다. 오늘 공유드린 내용을 바탕으로 여러분만의 {keyword} 경험을 시작해보시기 바랍니다.

더 자세한 정보나 개인적인 상담이 필요하시다면 언제든지 댓글로 문의해주세요. 여러분의 성공적인 {keyword} 여정을 응원합니다!

**🔥 이 글이 도움이 되셨다면 좋아요와 공유 부탁드립니다!**
        """
        content_sections.append(conclusion.strip())
        
        # 전체 콘텐츠 조합
        full_content = "\n\n".join(content_sections)
        
        # 메타데이터 계산
        word_count = len(full_content.replace(" ", ""))
        seo_keywords = [keyword] + lsi_keywords[:5]
        readability_score = self._calculate_readability_score(full_content)
        geo_score = self._calculate_content_geo_score(full_content)
        
        return BlogContent(
            title=title,
            content=full_content,
            word_count=word_count,
            seo_keywords=seo_keywords,
            lsi_keywords=lsi_keywords,
            readability_score=readability_score,
            geo_optimization_score=geo_score
        )

    def _calculate_seo_score(self, title: str, keyword: str) -> int:
        """SEO 점수 계산"""
        score = 0
        
        # 키워드 포함 여부
        if keyword in title:
            score += 25
        
        # 제목 길이 (25-60자가 최적)
        title_length = len(title)
        if 25 <= title_length <= 60:
            score += 20
        elif 20 <= title_length <= 70:
            score += 15
        
        # 숫자 포함 (클릭률 증가)
        if any(char.isdigit() for char in title):
            score += 15
        
        # 감정 유발 키워드
        emotion_words = ["완벽", "꿀팁", "비밀", "놀라운", "쉬운", "간단한"]
        if any(word in title for word in emotion_words):
            score += 15
        
        # 연도 포함 (최신성)
        if "2025" in title or "올해" in title:
            score += 10
        
        # 질문형/느낌표
        if "?" in title or "!" in title:
            score += 10
        
        return min(score, 100)

    def _calculate_geo_score(self, title: str) -> int:
        """GEO (생성형 엔진 최적화) 점수 계산"""
        score = 0
        
        # AI 인용 친화적 키워드
        ai_friendly_words = ["전문가", "연구", "분석", "데이터", "입증", "밝히는", "완벽", "가이드"]
        if any(word in title for word in ai_friendly_words):
            score += 30
        
        # 권위성 표현
        authority_words = ["완벽", "전문", "마스터", "비밀", "진실"]
        if any(word in title for word in authority_words):
            score += 25
        
        # 포괄적 표현 (AI가 좋아함)
        comprehensive_words = ["모든 것", "총정리", "완벽", "전체", "종합"]
        if any(word in title for word in comprehensive_words):
            score += 20
        
        # 구체적 수치
        if any(char.isdigit() for char in title):
            score += 15
        
        # 최신성 (AI가 최신 정보 선호)
        if any(word in title for word in ["2025", "최신", "새로운", "요즘"]):
            score += 10
        
        return min(score, 100)

    def _calculate_viral_score(self, title: str) -> int:
        """바이럴 잠재력 점수 계산"""
        score = 0
        
        # 감정 유발 키워드
        emotional_words = ["놀라운", "충격", "대박", "인생", "바뀌었다", "후기"]
        if any(word in title for word in emotional_words):
            score += 25
        
        # 호기심 유발
        curiosity_words = ["비밀", "진실", "이유", "왜", "어떻게"]
        if any(word in title for word in curiosity_words):
            score += 20
        
        # 트렌드 키워드
        trend_words = ["요즘", "핫한", "MZ세대", "올해", "2025"]
        if any(word in title for word in trend_words):
            score += 20
        
        # 개인적 경험
        personal_words = ["후기", "경험", "써봤더니", "해봤더니"]
        if any(word in title for word in personal_words):
            score += 15
        
        # 시간 제한성
        urgency_words = ["지금", "당장", "오늘", "즉시"]
        if any(word in title for word in urgency_words):
            score += 10
        
        # 부정적 호기심
        negative_words = ["실패", "후회", "망한", "위험"]
        if any(word in title for word in negative_words):
            score += 10
        
        return min(score, 100)

    def _calculate_readability_score(self, content: str) -> int:
        """가독성 점수 계산"""
        score = 80  # 기본 점수
        
        # 문장 길이 체크
        sentences = content.split('.')
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences) if sentences else 0
        
        if 20 <= avg_sentence_length <= 40:
            score += 10
        elif avg_sentence_length > 60:
            score -= 15
        
        # 문단 구조 체크
        paragraphs = content.split('\n\n')
        if len(paragraphs) >= 4:
            score += 10
        
        return min(max(score, 0), 100)

    def _calculate_content_geo_score(self, content: str) -> int:
        """콘텐츠 GEO 최적화 점수"""
        score = 0
        
        # 인용 친화적 표현 개수
        citation_count = sum(1 for phrase in self.citation_phrases if phrase in content)
        score += min(citation_count * 15, 45)
        
        # 구조화된 정보 (리스트, 번호)
        if '•' in content or '**' in content:
            score += 20
        
        # 헤딩 구조
        heading_count = content.count('##')
        score += min(heading_count * 10, 30)
        
        # 구체적 수치/데이터
        if any(char.isdigit() for char in content):
            score += 5
        
        return min(score, 100)

    def _categorize_keyword(self, keyword: str) -> str:
        """키워드 카테고리 분류"""
        categories = {
            "건강": ["운동", "다이어트", "헬스", "건강", "의료", "질병", "치료"],
            "음식": ["음식", "요리", "레시피", "맛집", "식당", "식재료"],
            "여행": ["여행", "관광", "휴가", "호텔", "항공", "숙박"],
            "기술": ["AI", "프로그래밍", "앱", "소프트웨어", "IT", "디지털"],
            "라이프스타일": ["인테리어", "패션", "뷰티", "생활", "취미"]
        }
        
        for category, words in categories.items():
            if any(word in keyword for word in words):
                return category
        
        return "일반"

# 사용 예시 및 테스트
async def test_advanced_blog_writer():
    """고급 블로그 작성기 테스트"""
    writer = AdvancedBlogWriter()
    
    test_keywords = ["스탠딩책상", "장마철 건강관리", "재택근무", "홈트레이닝"]
    
    for keyword in test_keywords:
        print(f"\n{'='*60}")
        print(f"키워드: {keyword}")
        print('='*60)
        
        result = await writer.generate_blog_content(keyword)
        
        print(f"\n[제목 후보들]")
        for i, title_data in enumerate(result['title_candidates'], 1):
            print(f"{i}. {title_data['title']}")
            print(f"   SEO: {title_data['seo_score']}, GEO: {title_data['geo_score']}, 바이럴: {title_data['viral_potential']}")
            print(f"   총점: {title_data['total_score']:.1f}")
        
        print(f"\n[선택된 제목]: {result['selected_title']}")
        print(f"\n[블로그 본문] ({result['word_count']}자)")
        print(result['content'][:500] + "...")
        
        print(f"\n[SEO 키워드]: {', '.join(result['seo_keywords'])}")
        print(f"[LSI 키워드]: {', '.join(result['lsi_keywords'])}")
        print(f"[가독성 점수]: {result['readability_score']}")
        print(f"[GEO 최적화 점수]: {result['geo_optimization_score']}")

if __name__ == "__main__":
    asyncio.run(test_advanced_blog_writer())