"""
API 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient

class TestHealthEndpoints:
    """헬스체크 엔드포인트 테스트"""
    
    def test_health_check(self, client: TestClient):
        """기본 헬스체크 테스트"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client: TestClient):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Blog Auto Process API" in data["message"]

class TestKeywordEndpoints:
    """키워드 분석 엔드포인트 테스트"""
    
    def test_keyword_analysis_structure(self, client: TestClient, sample_keyword_data):
        """키워드 분석 API 구조 테스트"""
        response = client.post("/api/keywords/analyze", json=sample_keyword_data)
        
        # 성공하거나 API 키 에러가 예상됨
        assert response.status_code in [200, 401, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                keyword_item = data[0]
                required_fields = ["keyword", "search_volume", "competition", "cpc", "opportunity_score"]
                for field in required_fields:
                    assert field in keyword_item
    
    def test_keyword_analysis_validation(self, client: TestClient):
        """키워드 분석 입력 검증 테스트"""
        # 빈 키워드
        response = client.post("/api/keywords/analyze", json={})
        assert response.status_code == 422
        
        # 잘못된 국가 코드는 허용되어야 함 (기본값 사용)
        response = client.post("/api/keywords/analyze", json={
            "keyword": "테스트",
            "country": "INVALID",
            "max_results": 3
        })
        assert response.status_code in [200, 401, 422]

class TestTitleEndpoints:
    """제목 생성 엔드포인트 테스트"""
    
    def test_title_generation_structure(self, client: TestClient, sample_title_data):
        """제목 생성 API 구조 테스트"""
        response = client.post("/api/titles/generate", json=sample_title_data)
        
        # 성공하거나 API 키 에러가 예상됨
        assert response.status_code in [200, 401, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            if len(data) > 0:
                title_item = data[0]
                assert "title" in title_item
                assert "duplicate_rate" in title_item
    
    def test_title_generation_validation(self, client: TestClient):
        """제목 생성 입력 검증 테스트"""
        # 빈 키워드
        response = client.post("/api/titles/generate", json={})
        assert response.status_code == 422
        
        # 잘못된 개수
        response = client.post("/api/titles/generate", json={
            "keyword": "테스트",
            "count": -1
        })
        assert response.status_code == 422

class TestContentEndpoints:
    """콘텐츠 생성 엔드포인트 테스트"""
    
    def test_content_generation_structure(self, client: TestClient, sample_content_data):
        """콘텐츠 생성 API 구조 테스트"""
        response = client.post("/api/content/generate", json=sample_content_data)
        
        # 성공하거나 API 키 에러가 예상됨
        assert response.status_code in [200, 401, 422]
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["content", "seo_score", "geo_score", "copyscape_result"]
            for field in required_fields:
                assert field in data
    
    def test_content_generation_validation(self, client: TestClient):
        """콘텐츠 생성 입력 검증 테스트"""
        # 빈 제목
        response = client.post("/api/content/generate", json={})
        assert response.status_code == 422

class TestDashboardEndpoints:
    """대시보드 엔드포인트 테스트"""
    
    def test_dashboard_stats(self, client: TestClient):
        """대시보드 통계 테스트"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["keywords_analyzed", "titles_generated", "content_generated", "posts_published"]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], int)

class TestErrorHandling:
    """에러 처리 테스트"""
    
    def test_404_error(self, client: TestClient):
        """존재하지 않는 엔드포인트 테스트"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client: TestClient):
        """허용되지 않는 HTTP 메서드 테스트"""
        response = client.patch("/api/health")
        assert response.status_code == 405
    
    def test_invalid_json(self, client: TestClient):
        """잘못된 JSON 형식 테스트"""
        response = client.post(
            "/api/keywords/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422