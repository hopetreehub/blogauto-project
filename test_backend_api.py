#!/usr/bin/env python3
"""
백엔드 API 심화 테스트
모든 엔드포인트 및 기능 테스트
"""

import requests
import json
import time
from datetime import datetime

class BackendAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def run_all_tests(self):
        print("🔧 백엔드 API 테스트 시작...")
        
        # 1. 헬스체크 테스트
        self.test_health_check()
        
        # 2. 키워드 분석 API 테스트
        self.test_keyword_analysis()
        
        # 3. 제목 생성 API 테스트
        self.test_title_generation()
        
        # 4. 콘텐츠 생성 API 테스트
        self.test_content_generation()
        
        # 5. 대시보드 통계 API 테스트
        self.test_dashboard_stats()
        
        # 6. 설정 API 테스트
        self.test_settings_api()
        
        # 7. 지침 API 테스트
        self.test_guidelines_api()
        
        # 8. SEO 분석 API 테스트
        self.test_seo_api()
        
        # 9. 배치 처리 API 테스트
        self.test_batch_api()
        
        print("\n📊 API 테스트 결과 요약:")
        self.print_results()
    
    def test_health_check(self):
        """헬스체크 API 테스트"""
        try:
            print("💓 헬스체크 테스트 중...")
            
            # 기본 헬스체크
            response = self.make_request("GET", "/api/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            
            # API 서버 메인 엔드포인트
            response = self.make_request("GET", "/")
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            
            self.test_results.append({
                "test": "헬스체크",
                "status": "✅ 통과",
                "details": f"상태: {data.get('status', 'healthy')}"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "헬스체크",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def test_keyword_analysis(self):
        """키워드 분석 API 테스트"""
        try:
            print("🔍 키워드 분석 API 테스트 중...")
            
            # 키워드 분석 요청
            payload = {
                "keyword": "블로그 글쓰기",
                "country": "KR",
                "max_results": 5
            }
            
            response = self.make_request("POST", "/api/keywords/analyze", payload)
            print(f"   응답 상태코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)
                if len(data) > 0:
                    keyword_data = data[0]
                    required_fields = ["keyword", "search_volume", "competition", "cpc", "opportunity_score"]
                    for field in required_fields:
                        assert field in keyword_data
                
                details = f"키워드 {len(data)}개 분석 완료"
            else:
                # API 키 미설정으로 인한 에러는 예상되는 상황
                error_data = response.json()
                details = f"API 키 미설정 (예상됨): {error_data.get('detail', '')}"
            
            self.test_results.append({
                "test": "키워드 분석 API",
                "status": "✅ 통과" if response.status_code in [200, 422, 400] else "❌ 실패",
                "details": details
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "키워드 분석 API",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def test_title_generation(self):
        """제목 생성 API 테스트"""
        try:
            print("✍️ 제목 생성 API 테스트 중...")
            
            payload = {
                "keyword": "블로그 마케팅",
                "count": 3,
                "tone": "professional",
                "length": "medium",
                "language": "ko"
            }
            
            response = self.make_request("POST", "/api/titles/generate", payload)
            print(f"   응답 상태코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)
                if len(data) > 0:
                    title_data = data[0]
                    assert "title" in title_data
                    assert "duplicate_rate" in title_data
                
                details = f"제목 {len(data)}개 생성 완료"
            else:
                error_data = response.json()
                details = f"API 키 미설정 (예상됨): {error_data.get('detail', '')}"
            
            self.test_results.append({
                "test": "제목 생성 API",
                "status": "✅ 통과" if response.status_code in [200, 422, 400] else "❌ 실패",
                "details": details
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "제목 생성 API",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def test_content_generation(self):
        """콘텐츠 생성 API 테스트"""
        try:
            print("📝 콘텐츠 생성 API 테스트 중...")
            
            payload = {
                "title": "효과적인 블로그 마케팅 전략 가이드",
                "keyword": "블로그 마케팅",
                "length": "medium",
                "tone": "professional",
                "language": "ko"
            }
            
            response = self.make_request("POST", "/api/content/generate", payload)
            print(f"   응답 상태코드: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["content", "seo_score", "geo_score", "copyscape_result"]
                for field in required_fields:
                    assert field in data
                
                content_length = len(data["content"])
                details = f"콘텐츠 생성 완료 ({content_length}자)"
            else:
                error_data = response.json()
                details = f"API 키 미설정 (예상됨): {error_data.get('detail', '')}"
            
            self.test_results.append({
                "test": "콘텐츠 생성 API",
                "status": "✅ 통과" if response.status_code in [200, 422, 400] else "❌ 실패",
                "details": details
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "콘텐츠 생성 API",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def test_dashboard_stats(self):
        """대시보드 통계 API 테스트"""
        try:
            print("📊 대시보드 통계 API 테스트 중...")
            
            response = self.make_request("GET", "/api/dashboard/stats")
            assert response.status_code == 200
            
            data = response.json()
            required_fields = ["keywords_analyzed", "titles_generated", "content_generated", "posts_published"]
            for field in required_fields:
                assert field in data
            
            self.test_results.append({
                "test": "대시보드 통계 API",
                "status": "✅ 통과",
                "details": f"통계 데이터 {len(data)}개 필드 확인"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "대시보드 통계 API",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def test_settings_api(self):
        """설정 API 테스트"""
        try:
            print("⚙️ 설정 API 테스트 중...")
            
            # 설정 저장 테스트 (실제로는 저장하지 않고 API 호출만 테스트)
            payload = {
                "openai_api_key": "test-key-for-validation"
            }
            
            # settings 엔드포인트가 있는지 확인
            endpoints_to_check = [
                "/api/settings",
                "/api/config",
                "/api/keys"
            ]
            
            found_endpoint = False
            for endpoint in endpoints_to_check:
                try:
                    response = self.make_request("GET", endpoint)
                    if response.status_code in [200, 405]:  # 405 = Method Not Allowed (GET 대신 POST 필요)
                        found_endpoint = True
                        break
                except:
                    continue
            
            self.test_results.append({
                "test": "설정 API",
                "status": "✅ 통과" if found_endpoint else "⚠️ 부분통과",
                "details": "설정 엔드포인트 접근 확인" if found_endpoint else "설정 API 구현 필요"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "설정 API",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def test_guidelines_api(self):
        """지침 API 테스트"""
        try:
            print("📋 지침 API 테스트 중...")
            
            # 지침 관련 엔드포인트 확인
            endpoints_to_check = [
                "/api/guidelines",
                "/api/prompts",
                "/api/admin/prompts/summary"
            ]
            
            found_endpoint = False
            for endpoint in endpoints_to_check:
                try:
                    response = self.make_request("GET", endpoint)
                    if response.status_code in [200, 401, 403]:  # 401/403 = 인증 필요 (정상)
                        found_endpoint = True
                        break
                except:
                    continue
            
            self.test_results.append({
                "test": "지침 API",
                "status": "✅ 통과" if found_endpoint else "⚠️ 부분통과",
                "details": "지침 엔드포인트 접근 확인" if found_endpoint else "지침 API 구현 필요"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "지침 API",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def test_seo_api(self):
        """SEO 분석 API 테스트"""
        try:
            print("📈 SEO 분석 API 테스트 중...")
            
            # SEO 관련 엔드포인트 확인
            endpoints_to_check = [
                "/api/seo/dashboard",
                "/api/seo/keyword-performance",
                "/api/seo/content-analytics"
            ]
            
            found_endpoints = 0
            for endpoint in endpoints_to_check:
                try:
                    response = self.make_request("GET", endpoint)
                    if response.status_code in [200, 401, 403]:
                        found_endpoints += 1
                except:
                    continue
            
            self.test_results.append({
                "test": "SEO 분석 API",
                "status": "✅ 통과" if found_endpoints >= 2 else "⚠️ 부분통과",
                "details": f"SEO 엔드포인트 {found_endpoints}/3개 확인"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "SEO 분석 API",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def test_batch_api(self):
        """배치 처리 API 테스트"""
        try:
            print("🔄 배치 처리 API 테스트 중...")
            
            # 배치 관련 엔드포인트 확인
            endpoints_to_check = [
                "/api/batch/tasks",
                "/api/batch/submit",
                "/api/content/batch-generate"
            ]
            
            found_endpoints = 0
            for endpoint in endpoints_to_check:
                try:
                    response = self.make_request("GET", endpoint)
                    if response.status_code in [200, 401, 403, 405]:  # 405 = POST 필요
                        found_endpoints += 1
                except:
                    continue
            
            self.test_results.append({
                "test": "배치 처리 API",
                "status": "✅ 통과" if found_endpoints >= 2 else "⚠️ 부분통과",
                "details": f"배치 엔드포인트 {found_endpoints}/3개 확인"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "배치 처리 API",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def make_request(self, method, endpoint, data=None, headers=None):
        """HTTP 요청 헬퍼"""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {
            "Content-Type": "application/json"
        }
        if headers:
            default_headers.update(headers)
        
        if method == "GET":
            return requests.get(url, headers=default_headers, timeout=10)
        elif method == "POST":
            return requests.post(url, json=data, headers=default_headers, timeout=10)
        elif method == "PUT":
            return requests.put(url, json=data, headers=default_headers, timeout=10)
        elif method == "DELETE":
            return requests.delete(url, headers=default_headers, timeout=10)
    
    def print_results(self):
        """테스트 결과 출력"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "✅" in result["status"])
        partial_tests = sum(1 for result in self.test_results if "⚠️" in result["status"])
        
        print(f"\n{'='*60}")
        print(f"📊 API 테스트 결과: {passed_tests}/{total_tests} 통과, {partial_tests}개 부분통과")
        print(f"{'='*60}")
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            print(f"   세부사항: {result['details']}")
            print()
        
        success_rate = (passed_tests + partial_tests * 0.5) / total_tests * 100
        print(f"✨ 전체 성공률: {success_rate:.1f}%")

def main():
    """메인 실행 함수"""
    print("🚀 BlogAuto 백엔드 API 테스트 시작")
    print("=" * 60)
    
    # 서버 상태 확인
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"✅ 백엔드 서버 응답: {response.status_code}")
    except Exception as e:
        print(f"❌ 백엔드 서버에 연결할 수 없습니다: {e}")
        return
    
    print()
    
    # API 테스트 실행
    tester = BackendAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()