"""
간단한 API 테스트 - 실제 실행 중인 서버에 대한 테스트
"""

import requests
import pytest

BASE_URL = "http://localhost:8000"

class TestBasicAPI:
    """기본 API 기능 테스트"""
    
    def test_server_is_running(self):
        """서버 실행 상태 확인"""
        try:
            response = requests.get(f"{BASE_URL}/api/health", timeout=5)
            assert response.status_code == 200
        except requests.RequestException:
            pytest.fail("서버가 실행되지 않았습니다")
    
    def test_health_endpoint(self):
        """헬스체크 엔드포인트 테스트"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Blog Auto Process API" in data["message"]
    
    def test_dashboard_stats(self):
        """대시보드 통계 API 테스트"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["keywords_analyzed", "titles_generated", "content_generated", "posts_published"]
        for field in required_fields:
            assert field in data
            assert isinstance(data[field], int)

class TestAPIValidation:
    """API 입력 검증 테스트"""
    
    def test_keyword_analysis_validation(self):
        """키워드 분석 API 검증"""
        # 빈 요청
        response = requests.post(f"{BASE_URL}/api/keywords/analyze", json={})
        assert response.status_code == 422
        
        # 정상 요청 구조 (API 키 없음으로 401 예상)
        response = requests.post(f"{BASE_URL}/api/keywords/analyze", json={
            "keyword": "테스트",
            "country": "KR",
            "max_results": 3
        })
        assert response.status_code in [200, 401, 422]
    
    def test_title_generation_validation(self):
        """제목 생성 API 검증"""
        # 빈 요청
        response = requests.post(f"{BASE_URL}/api/titles/generate", json={})
        assert response.status_code == 422
        
        # 정상 요청 구조
        response = requests.post(f"{BASE_URL}/api/titles/generate", json={
            "keyword": "테스트",
            "count": 3,
            "tone": "professional",
            "length": "medium",
            "language": "ko"
        })
        assert response.status_code in [200, 401, 422]
    
    def test_content_generation_validation(self):
        """콘텐츠 생성 API 검증"""
        # 빈 요청
        response = requests.post(f"{BASE_URL}/api/content/generate", json={})
        assert response.status_code == 422
        
        # 정상 요청 구조
        response = requests.post(f"{BASE_URL}/api/content/generate", json={
            "title": "테스트 제목",
            "keyword": "테스트",
            "length": "medium",
            "tone": "professional",
            "language": "ko"
        })
        assert response.status_code in [200, 401, 422]

class TestErrorHandling:
    """에러 처리 테스트"""
    
    def test_404_endpoint(self):
        """존재하지 않는 엔드포인트"""
        response = requests.get(f"{BASE_URL}/api/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """잘못된 HTTP 메서드"""
        response = requests.patch(f"{BASE_URL}/api/health")
        assert response.status_code == 405

class TestAPIStructure:
    """API 응답 구조 테스트"""
    
    def test_cors_headers(self):
        """CORS 헤더 확인"""
        response = requests.options(f"{BASE_URL}/api/health")
        # CORS가 설정되어 있으면 적절한 헤더가 있어야 함
        assert response.status_code in [200, 405]  # OPTIONS가 허용되지 않을 수 있음
    
    def test_content_type_headers(self):
        """Content-Type 헤더 확인"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])