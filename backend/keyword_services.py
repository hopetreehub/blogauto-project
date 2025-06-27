import os
import requests
import random
from typing import List, Dict, Optional
import json

class KeywordService:
    """Base class for keyword analysis services"""
    
    def __init__(self):
        pass
    
    async def analyze_keywords(self, keyword: str, country: str = "KR", max_results: int = 10) -> List[Dict]:
        """Analyze keywords and return search volume, competition, CPC data"""
        raise NotImplementedError

class GoogleKeywordPlannerService(KeywordService):
    """Google Keyword Planner API service"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_ADS_API_KEY")
        self.customer_id = os.getenv("GOOGLE_ADS_CUSTOMER_ID")
        self.developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    
    async def analyze_keywords(self, keyword: str, country: str = "KR", max_results: int = 10) -> List[Dict]:
        """Analyze keywords using Google Keyword Planner"""
        # TODO: Implement actual Google Ads API integration
        # For now, return mock data with realistic variations
        
        base_volume = random.randint(500, 10000)
        base_cpc = round(random.uniform(0.5, 3.0), 2)
        
        keywords_data = []
        
        # Main keyword
        keywords_data.append({
            "keyword": keyword,
            "search_volume": base_volume,
            "competition": random.choice(["Low", "Medium", "High"]),
            "cpc": base_cpc,
            "opportunity_score": self._calculate_opportunity_score(base_volume, base_cpc, "Medium")
        })
        
        # Related keywords
        related_suffixes = [
            "방법", "가이드", "추천", "후기", "비교", "사용법", "팁", "종류", 
            "장점", "단점", "효과", "설정", "활용", "설명", "정보", "분석"
        ]
        
        for i, suffix in enumerate(related_suffixes[:max_results-1]):
            volume = int(base_volume * random.uniform(0.3, 0.8))
            cpc = round(base_cpc * random.uniform(0.6, 1.2), 2)
            competition = random.choice(["Low", "Medium", "High"])
            
            keywords_data.append({
                "keyword": f"{keyword} {suffix}",
                "search_volume": volume,
                "competition": competition,
                "cpc": cpc,
                "opportunity_score": self._calculate_opportunity_score(volume, cpc, competition)
            })
        
        return keywords_data[:max_results]
    
    def _calculate_opportunity_score(self, volume: int, cpc: float, competition: str) -> int:
        """Calculate opportunity score based on volume, CPC, and competition"""
        # High volume = good
        volume_score = min(volume / 1000 * 30, 40)
        
        # Lower CPC = better for opportunity
        cpc_score = max(30 - (cpc * 10), 10)
        
        # Lower competition = better
        competition_scores = {"Low": 30, "Medium": 20, "High": 10}
        competition_score = competition_scores.get(competition, 15)
        
        total_score = int(volume_score + cpc_score + competition_score)
        return min(max(total_score, 10), 100)

class SEMrushService(KeywordService):
    """SEMrush API service"""
    
    def __init__(self):
        self.api_key = os.getenv("SEMRUSH_API_KEY")
        self.base_url = "https://api.semrush.com/"
    
    async def analyze_keywords(self, keyword: str, country: str = "KR", max_results: int = 10) -> List[Dict]:
        """Analyze keywords using SEMrush API"""
        if not self.api_key:
            return self._get_mock_data(keyword, max_results)
        
        try:
            # SEMrush API call
            params = {
                "type": "phrase_this",
                "key": self.api_key,
                "phrase": keyword,
                "database": self._get_database_code(country),
                "export_columns": "Ph,Nq,Cp,Co",
                "export_format": "json"
            }
            
            response = requests.get(f"{self.base_url}reports/v1/projects/", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_semrush_data(data, max_results)
            else:
                print(f"SEMrush API error: {response.status_code}")
                return self._get_mock_data(keyword, max_results)
                
        except Exception as e:
            print(f"SEMrush API exception: {e}")
            return self._get_mock_data(keyword, max_results)
    
    def _get_database_code(self, country: str) -> str:
        """Get SEMrush database code for country"""
        country_codes = {
            "KR": "kr",
            "US": "us", 
            "JP": "jp",
            "GB": "uk",
            "DE": "de",
            "FR": "fr",
            "CA": "ca",
            "AU": "au"
        }
        return country_codes.get(country, "us")
    
    def _parse_semrush_data(self, data: Dict, max_results: int) -> List[Dict]:
        """Parse SEMrush API response"""
        keywords_data = []
        
        # Parse SEMrush response format
        # This would need to be adapted based on actual SEMrush API response format
        
        return keywords_data[:max_results]
    
    def _get_mock_data(self, keyword: str, max_results: int) -> List[Dict]:
        """Generate mock data when API is not available"""
        base_volume = random.randint(800, 12000)
        base_cpc = round(random.uniform(0.3, 2.5), 2)
        
        keywords_data = []
        
        # Main keyword
        keywords_data.append({
            "keyword": keyword,
            "search_volume": base_volume,
            "competition": random.choice(["Low", "Medium", "High"]),
            "cpc": base_cpc,
            "opportunity_score": self._calculate_opportunity_score(base_volume, base_cpc)
        })
        
        # Long-tail variations
        variations = [
            f"{keyword} 사용법", f"{keyword} 가격", f"{keyword} 리뷰", 
            f"{keyword} 비교", f"{keyword} 설치", f"{keyword} 추천",
            f"{keyword} 문제", f"{keyword} 해결", f"{keyword} 예제",
            f"최고의 {keyword}", f"{keyword} 무료", f"{keyword} 유료"
        ]
        
        for variation in variations[:max_results-1]:
            volume = int(base_volume * random.uniform(0.2, 0.7))
            cpc = round(base_cpc * random.uniform(0.5, 1.3), 2)
            
            keywords_data.append({
                "keyword": variation,
                "search_volume": volume,
                "competition": random.choice(["Low", "Medium", "High"]),
                "cpc": cpc,
                "opportunity_score": self._calculate_opportunity_score(volume, cpc)
            })
        
        return keywords_data[:max_results]
    
    def _calculate_opportunity_score(self, volume: int, cpc: float) -> int:
        """Calculate opportunity score"""
        # SEMrush-style scoring
        volume_score = min(volume / 1000 * 25, 35)
        cpc_score = max(25 - (cpc * 8), 5)
        trend_score = random.randint(15, 25)  # Mock trend score
        
        total_score = int(volume_score + cpc_score + trend_score)
        return min(max(total_score, 15), 95)

class AhrefsService(KeywordService):
    """Ahrefs API service"""
    
    def __init__(self):
        self.api_key = os.getenv("AHREFS_API_KEY")
        self.base_url = "https://apiv2.ahrefs.com"
    
    async def analyze_keywords(self, keyword: str, country: str = "KR", max_results: int = 10) -> List[Dict]:
        """Analyze keywords using Ahrefs API"""
        if not self.api_key:
            return self._get_mock_data(keyword, max_results)
        
        try:
            # Ahrefs API call
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }
            
            params = {
                "target": keyword,
                "country": country.lower(),
                "limit": max_results
            }
            
            response = requests.get(
                f"{self.base_url}/keywords-explorer/v3/keywords-volume", 
                headers=headers, 
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_ahrefs_data(data, max_results)
            else:
                print(f"Ahrefs API error: {response.status_code}")
                return self._get_mock_data(keyword, max_results)
                
        except Exception as e:
            print(f"Ahrefs API exception: {e}")
            return self._get_mock_data(keyword, max_results)
    
    def _parse_ahrefs_data(self, data: Dict, max_results: int) -> List[Dict]:
        """Parse Ahrefs API response"""
        keywords_data = []
        
        # Parse Ahrefs response format
        # This would need to be adapted based on actual Ahrefs API response format
        
        return keywords_data[:max_results]
    
    def _get_mock_data(self, keyword: str, max_results: int) -> List[Dict]:
        """Generate mock data when API is not available"""
        base_volume = random.randint(600, 8000)
        base_difficulty = random.randint(20, 80)
        
        keywords_data = []
        
        # Main keyword
        keywords_data.append({
            "keyword": keyword,
            "search_volume": base_volume,
            "competition": self._difficulty_to_competition(base_difficulty),
            "cpc": round(random.uniform(0.4, 2.8), 2),
            "opportunity_score": self._calculate_ahrefs_score(base_volume, base_difficulty)
        })
        
        # Related keywords
        related_keywords = [
            f"{keyword} 도구", f"{keyword} 소프트웨어", f"{keyword} 앱",
            f"{keyword} 온라인", f"{keyword} 무료", f"{keyword} 최고",
            f"{keyword} 2024", f"{keyword} 최신", f"{keyword} 인기",
            f"{keyword} 전문", f"{keyword} 쉬운", f"{keyword} 빠른"
        ]
        
        for related in related_keywords[:max_results-1]:
            volume = int(base_volume * random.uniform(0.25, 0.6))
            difficulty = random.randint(10, 70)
            
            keywords_data.append({
                "keyword": related,
                "search_volume": volume,
                "competition": self._difficulty_to_competition(difficulty),
                "cpc": round(random.uniform(0.2, 2.0), 2),
                "opportunity_score": self._calculate_ahrefs_score(volume, difficulty)
            })
        
        return keywords_data[:max_results]
    
    def _difficulty_to_competition(self, difficulty: int) -> str:
        """Convert Ahrefs difficulty score to competition level"""
        if difficulty < 30:
            return "Low"
        elif difficulty < 60:
            return "Medium"
        else:
            return "High"
    
    def _calculate_ahrefs_score(self, volume: int, difficulty: int) -> int:
        """Calculate opportunity score based on Ahrefs metrics"""
        volume_score = min(volume / 1000 * 30, 40)
        difficulty_score = max(40 - (difficulty * 0.5), 10)
        trend_score = random.randint(10, 20)
        
        total_score = int(volume_score + difficulty_score + trend_score)
        return min(max(total_score, 20), 90)

# Service factory
def get_keyword_service(service_name: str = "google") -> KeywordService:
    """Get keyword analysis service instance"""
    if service_name.lower() == "google":
        return GoogleKeywordPlannerService()
    elif service_name.lower() == "semrush":
        return SEMrushService()
    elif service_name.lower() == "ahrefs":
        return AhrefsService()
    else:
        # Default to Google
        return GoogleKeywordPlannerService()

# Aggregate service that combines multiple sources
class AggregateKeywordService:
    """Service that aggregates data from multiple keyword sources"""
    
    def __init__(self):
        self.services = [
            GoogleKeywordPlannerService(),
            SEMrushService(),
            AhrefsService()
        ]
    
    async def analyze_keywords(self, keyword: str, country: str = "KR", max_results: int = 10) -> List[Dict]:
        """Analyze keywords using multiple services and aggregate results"""
        all_keywords = {}
        
        # Collect data from all services
        for service in self.services:
            try:
                service_data = await service.analyze_keywords(keyword, country, max_results)
                for kw_data in service_data:
                    kw = kw_data["keyword"]
                    if kw not in all_keywords:
                        all_keywords[kw] = []
                    all_keywords[kw].append(kw_data)
            except Exception as e:
                print(f"Service error: {e}")
                continue
        
        # Aggregate and average the data
        aggregated_results = []
        for kw, data_list in all_keywords.items():
            if len(data_list) > 0:
                avg_volume = int(sum(d["search_volume"] for d in data_list) / len(data_list))
                avg_cpc = round(sum(d["cpc"] for d in data_list) / len(data_list), 2)
                avg_score = int(sum(d["opportunity_score"] for d in data_list) / len(data_list))
                
                # Most common competition level
                competitions = [d["competition"] for d in data_list]
                most_common_competition = max(set(competitions), key=competitions.count)
                
                aggregated_results.append({
                    "keyword": kw,
                    "search_volume": avg_volume,
                    "competition": most_common_competition,
                    "cpc": avg_cpc,
                    "opportunity_score": avg_score
                })
        
        # Sort by opportunity score and return top results
        aggregated_results.sort(key=lambda x: x["opportunity_score"], reverse=True)
        return aggregated_results[:max_results]