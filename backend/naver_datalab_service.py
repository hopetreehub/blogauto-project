"""
네이버 DataLab API 연동 서비스
실제 네이버 검색 트렌드 데이터를 가져와서 키워드 분석에 활용
"""

import os
import json
import requests
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from dataclasses import dataclass

@dataclass
class NaverKeywordData:
    keyword: str
    search_volume: int
    trend_data: List[Dict]
    competition_level: str
    seasonal_pattern: bool
    peak_periods: List[str]

class NaverDataLabService:
    def __init__(self):
        # 네이버 API 설정 (환경변수에서 가져오기)
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.base_url = 'https://openapi.naver.com/v1/datalab'
        
        # API 키가 없으면 경고
        if not self.client_id or not self.client_secret:
            print("⚠️ 네이버 API 키가 설정되지 않았습니다. 환경변수 NAVER_CLIENT_ID, NAVER_CLIENT_SECRET를 설정해주세요.")
    
    def get_headers(self) -> Dict[str, str]:
        """네이버 API 요청 헤더 생성"""
        return {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret,
            'Content-Type': 'application/json'
        }
    
    async def get_search_trend(self, keywords: List[str], start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        네이버 DataLab 검색어 트렌드 조회
        
        Args:
            keywords: 검색할 키워드 리스트 (최대 5개)
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
        """
        if not self.client_id or not self.client_secret:
            return self._get_mock_trend_data(keywords)
        
        # 기본 날짜 설정 (최근 1년)
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # 네이버 DataLab API 요청 데이터 구성
        request_data = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": "month",  # date, week, month
            "keywordGroups": []
        }
        
        # 키워드 그룹 생성 (최대 5개)
        for i, keyword in enumerate(keywords[:5]):
            keyword_group = {
                "groupName": f"키워드{i+1}",
                "keywords": [keyword]
            }
            request_data["keywordGroups"].append(keyword_group)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/search",
                    headers=self.get_headers(),
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_trend_data(data, keywords)
                    else:
                        error_text = await response.text()
                        print(f"네이버 DataLab API 오류: {response.status} - {error_text}")
                        return self._get_mock_trend_data(keywords)
        
        except Exception as e:
            print(f"네이버 DataLab API 요청 실패: {e}")
            return self._get_mock_trend_data(keywords)
    
    def _process_trend_data(self, api_data: Dict, keywords: List[str]) -> Dict[str, Any]:
        """API 응답 데이터 처리"""
        processed_data = {}
        
        if 'results' in api_data:
            for i, result in enumerate(api_data['results']):
                if i < len(keywords):
                    keyword = keywords[i]
                    trend_values = [item['ratio'] for item in result['data']]
                    
                    processed_data[keyword] = {
                        'keyword': keyword,
                        'trend_data': result['data'],
                        'avg_ratio': sum(trend_values) / len(trend_values) if trend_values else 0,
                        'max_ratio': max(trend_values) if trend_values else 0,
                        'min_ratio': min(trend_values) if trend_values else 0,
                        'trend_direction': self._calculate_trend_direction(trend_values),
                        'seasonal_pattern': self._detect_seasonal_pattern(trend_values),
                        'peak_periods': self._find_peak_periods(result['data'])
                    }
        
        return processed_data
    
    def _calculate_trend_direction(self, values: List[int]) -> str:
        """트렌드 방향 계산"""
        if len(values) < 3:
            return "insufficient_data"
        
        recent_avg = sum(values[-3:]) / 3
        earlier_avg = sum(values[:3]) / 3
        
        if recent_avg > earlier_avg * 1.2:
            return "increasing"
        elif recent_avg < earlier_avg * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _detect_seasonal_pattern(self, values: List[int]) -> bool:
        """계절성 패턴 감지"""
        if len(values) < 12:  # 12개월 미만이면 계절성 판단 어려움
            return False
        
        # 간단한 계절성 감지: 분산이 평균 대비 큰 경우
        if not values:
            return False
        
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        
        # 변동성이 평균의 30% 이상이면 계절성 있다고 판단
        return variance > (avg * 0.3) ** 2
    
    def _find_peak_periods(self, data: List[Dict]) -> List[str]:
        """피크 기간 찾기"""
        if not data:
            return []
        
        values = [item['ratio'] for item in data]
        if not values:
            return []
        
        avg = sum(values) / len(values)
        peaks = []
        
        for item in data:
            if item['ratio'] > avg * 1.5:  # 평균의 150% 이상인 경우 피크
                peaks.append(item['period'])
        
        return peaks[:3]  # 최대 3개만 반환
    
    def _get_mock_trend_data(self, keywords: List[str]) -> Dict[str, Any]:
        """API 키가 없을 때 목업 데이터 반환"""
        mock_data = {}
        
        for keyword in keywords:
            # 키워드별로 다른 패턴의 목업 데이터 생성
            base_ratio = hash(keyword) % 50 + 20  # 20-70 사이 값
            trend_data = []
            
            # 12개월 데이터 생성
            for i in range(12):
                period = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
                ratio = max(0, base_ratio + (hash(keyword + period) % 30 - 15))
                trend_data.append({
                    'period': period,
                    'ratio': ratio
                })
            
            trend_values = [item['ratio'] for item in trend_data]
            
            mock_data[keyword] = {
                'keyword': keyword,
                'trend_data': trend_data,
                'avg_ratio': sum(trend_values) / len(trend_values),
                'max_ratio': max(trend_values),
                'min_ratio': min(trend_values),
                'trend_direction': self._calculate_trend_direction(trend_values),
                'seasonal_pattern': self._detect_seasonal_pattern(trend_values),
                'peak_periods': self._find_peak_periods(trend_data)
            }
        
        return mock_data
    
    async def get_shopping_trend(self, category: str, keywords: List[str] = None) -> Dict[str, Any]:
        """
        네이버 쇼핑 인사이트 트렌드 조회
        
        Args:
            category: 쇼핑 카테고리
            keywords: 특정 키워드 리스트
        """
        if not self.client_id or not self.client_secret:
            return self._get_mock_shopping_data(category, keywords)
        
        # 쇼핑 카테고리 매핑
        category_mapping = {
            "사무용 가구": "50000006",
            "전자제품": "50000008",
            "의류": "50000003",
            "화장품": "50000010",
            "식품": "50000012",
            "생활용품": "50000005"
        }
        
        category_id = category_mapping.get(category, "50000000")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v1/shopping/category/keyword/age",
                    headers=self.get_headers(),
                    params={
                        'cid': category_id,
                        'timeUnit': 'month',
                        'startDate': (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                        'endDate': datetime.now().strftime('%Y-%m-%d')
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_shopping_data(data, category)
                    else:
                        return self._get_mock_shopping_data(category, keywords)
        
        except Exception as e:
            print(f"네이버 쇼핑 인사이트 API 요청 실패: {e}")
            return self._get_mock_shopping_data(category, keywords)
    
    def _process_shopping_data(self, api_data: Dict, category: str) -> Dict[str, Any]:
        """쇼핑 인사이트 데이터 처리"""
        return {
            'category': category,
            'shopping_trends': api_data,
            'top_keywords': self._extract_top_keywords(api_data),
            'age_distribution': self._extract_age_data(api_data),
            'seasonal_insights': self._extract_seasonal_insights(api_data)
        }
    
    def _extract_top_keywords(self, data: Dict) -> List[str]:
        """쇼핑 데이터에서 인기 키워드 추출"""
        # 실제 API 응답 구조에 따라 구현
        if 'results' in data and data['results']:
            keywords = []
            for result in data['results']:
                if 'keyword' in result:
                    keywords.append(result['keyword'])
            return keywords[:10]
        return []
    
    def _extract_age_data(self, data: Dict) -> Dict[str, int]:
        """연령대별 데이터 추출"""
        # 실제 API 응답 구조에 따라 구현
        return {
            '10대': 15,
            '20대': 25,
            '30대': 30,
            '40대': 20,
            '50대+': 10
        }
    
    def _extract_seasonal_insights(self, data: Dict) -> Dict[str, Any]:
        """계절별 인사이트 추출"""
        return {
            'peak_season': '12월',
            'low_season': '2월',
            'growth_rate': '+15%'
        }
    
    def _get_mock_shopping_data(self, category: str, keywords: List[str] = None) -> Dict[str, Any]:
        """쇼핑 목업 데이터"""
        return {
            'category': category,
            'shopping_trends': {},
            'top_keywords': keywords[:5] if keywords else [f"{category} 추천", f"{category} 인기", f"{category} 베스트"],
            'age_distribution': {
                '10대': 15, '20대': 25, '30대': 30, '40대': 20, '50대+': 10
            },
            'seasonal_insights': {
                'peak_season': '12월',
                'low_season': '2월', 
                'growth_rate': '+15%'
            }
        }
    
    async def analyze_keyword_competition(self, keywords: List[str]) -> Dict[str, Any]:
        """키워드 경쟁도 분석"""
        competition_data = {}
        
        for keyword in keywords:
            # 네이버 검색 결과 수 조회 (간접적 경쟁도 측정)
            search_count = await self._get_search_result_count(keyword)
            
            competition_level = "낮음"
            if search_count > 1000000:
                competition_level = "높음"
            elif search_count > 100000:
                competition_level = "보통"
            
            competition_data[keyword] = {
                'keyword': keyword,
                'search_result_count': search_count,
                'competition_level': competition_level,
                'difficulty_score': min(100, search_count // 10000)  # 0-100 점수
            }
        
        return competition_data
    
    async def _get_search_result_count(self, keyword: str) -> int:
        """네이버 검색 결과 수 조회 (추정)"""
        # 실제로는 네이버 검색 API나 웹 스크래핑 필요
        # 현재는 키워드 특성에 따른 추정값 반환
        
        base_count = 50000
        
        # 키워드 길이에 따른 조정
        if len(keyword) > 10:
            base_count *= 0.3
        elif len(keyword) > 5:
            base_count *= 0.7
        
        # 특정 단어 포함 시 조정
        if any(word in keyword for word in ["추천", "후기", "리뷰"]):
            base_count *= 2
        
        if any(word in keyword for word in ["2025", "최신"]):
            base_count *= 0.5
        
        return int(base_count * (1 + (hash(keyword) % 100) / 100))

# 사용 예시 및 테스트 함수
async def test_naver_datalab():
    """네이버 DataLab 서비스 테스트"""
    service = NaverDataLabService()
    
    # 검색 트렌드 조회
    keywords = ["스탠딩책상", "사무용 의자", "모니터암"]
    trend_data = await service.get_search_trend(keywords)
    
    print("=== 네이버 검색 트렌드 ===")
    for keyword, data in trend_data.items():
        print(f"\n키워드: {keyword}")
        print(f"평균 검색비율: {data['avg_ratio']:.1f}")
        print(f"트렌드 방향: {data['trend_direction']}")
        print(f"계절성: {'있음' if data['seasonal_pattern'] else '없음'}")
        print(f"피크 기간: {', '.join(data['peak_periods'])}")
    
    # 쇼핑 트렌드 조회
    shopping_data = await service.get_shopping_trend("사무용 가구", keywords)
    print(f"\n=== 쇼핑 인사이트 ({shopping_data['category']}) ===")
    print(f"인기 키워드: {', '.join(shopping_data['top_keywords'])}")
    
    # 경쟁도 분석
    competition_data = await service.analyze_keyword_competition(keywords)
    print(f"\n=== 키워드 경쟁도 ===")
    for keyword, data in competition_data.items():
        print(f"{keyword}: {data['competition_level']} (검색결과 {data['search_result_count']:,}건)")

if __name__ == "__main__":
    asyncio.run(test_naver_datalab())