#!/usr/bin/env python3
"""
WordPress 직접 포스팅 성능 테스트
- 실제 WordPress API 호출 테스트
- 포스팅 성능 측정
- 병목 지점 파악
"""

import time
import requests
import json
from datetime import datetime
import statistics
from typing import Dict, List, Tuple

class WordPressPerformanceTester:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.results = {
            "auth_tests": [],
            "wordpress_tests": [],
            "optimization_suggestions": [],
            "timestamp": datetime.now().isoformat()
        }
        self.headers = {}
        
    def test_real_api_endpoints(self):
        """real_api_simple.py의 실제 엔드포인트 테스트"""
        print("🔍 실제 API 엔드포인트 테스트 시작...")
        
        # 1. 헬스 체크
        response = requests.get(f"{self.api_url}/api/health")
        print(f"  Health Check: {response.status_code}")
        
        # 2. 키워드 분석 테스트
        print("\n📊 키워드 분석 테스트...")
        keyword_data = {
            "keyword": "블로그 성능 최적화",
            "country": "KR",
            "max_results": 5
        }
        
        start = time.time()
        response = requests.post(
            f"{self.api_url}/api/keywords/analyze",
            json=keyword_data,
            headers={"X-API-Key": "test-key"}  # API 키 헤더 추가
        )
        elapsed = (time.time() - start) * 1000
        
        self.results["wordpress_tests"].append({
            "test": "Keyword Analysis",
            "endpoint": "/api/keywords/analyze",
            "time_ms": round(elapsed, 2),
            "status": response.status_code,
            "response_size": len(response.content) if response.status_code == 200 else 0
        })
        print(f"  Status: {response.status_code}, Time: {elapsed:.2f}ms")
        
        # 3. 제목 생성 테스트
        print("\n🎯 제목 생성 테스트...")
        title_data = {
            "keyword": "성능 최적화",
            "count": 3,
            "tone": "professional",
            "language": "ko"
        }
        
        start = time.time()
        response = requests.post(
            f"{self.api_url}/api/titles/generate",
            json=title_data,
            headers={"X-OpenAI-API-Key": "test-key"}
        )
        elapsed = (time.time() - start) * 1000
        
        self.results["wordpress_tests"].append({
            "test": "Title Generation",
            "endpoint": "/api/titles/generate",
            "time_ms": round(elapsed, 2),
            "status": response.status_code,
            "response_size": len(response.content) if response.status_code == 200 else 0
        })
        print(f"  Status: {response.status_code}, Time: {elapsed:.2f}ms")
        
        # 4. 콘텐츠 생성 테스트
        print("\n📝 콘텐츠 생성 테스트...")
        content_data = {
            "title": "블로그 성능 최적화의 모든 것",
            "keyword": "성능 최적화",
            "length": "short",  # 빠른 테스트를 위해 짧게
            "tone": "professional",
            "language": "ko"
        }
        
        start = time.time()
        response = requests.post(
            f"{self.api_url}/api/content/generate",
            json=content_data,
            headers={"X-OpenAI-API-Key": "test-key"}
        )
        elapsed = (time.time() - start) * 1000
        
        self.results["wordpress_tests"].append({
            "test": "Content Generation",
            "endpoint": "/api/content/generate",
            "time_ms": round(elapsed, 2),
            "status": response.status_code,
            "response_size": len(response.content) if response.status_code == 200 else 0
        })
        print(f"  Status: {response.status_code}, Time: {elapsed:.2f}ms")
        
        # 5. WordPress 연결 테스트
        print("\n🔌 WordPress 연결 테스트...")
        wp_config = {
            "site_url": "https://example.wordpress.com",
            "username": "admin",
            "password": "password"
        }
        
        start = time.time()
        response = requests.post(
            f"{self.api_url}/api/wordpress/test-connection",
            json=wp_config
        )
        elapsed = (time.time() - start) * 1000
        
        self.results["wordpress_tests"].append({
            "test": "WordPress Connection",
            "endpoint": "/api/wordpress/test-connection",
            "time_ms": round(elapsed, 2),
            "status": response.status_code,
            "details": response.json() if response.status_code == 200 else response.text[:100]
        })
        print(f"  Status: {response.status_code}, Time: {elapsed:.2f}ms")
        
        # 6. WordPress 포스팅 테스트
        print("\n📤 WordPress 포스팅 테스트...")
        post_data = {
            "site_url": "https://example.wordpress.com",
            "username": "admin",
            "password": "password",
            "title": "성능 테스트 포스트",
            "content": "이것은 성능 테스트를 위한 콘텐츠입니다.",
            "status": "draft",
            "categories": ["테스트"],
            "tags": ["성능", "최적화"]
        }
        
        start = time.time()
        response = requests.post(
            f"{self.api_url}/api/wordpress/publish",
            json=post_data
        )
        elapsed = (time.time() - start) * 1000
        
        self.results["wordpress_tests"].append({
            "test": "WordPress Publishing",
            "endpoint": "/api/wordpress/publish",
            "time_ms": round(elapsed, 2),
            "status": response.status_code,
            "details": response.json() if response.status_code == 200 else response.text[:100]
        })
        print(f"  Status: {response.status_code}, Time: {elapsed:.2f}ms")
    
    def analyze_performance(self):
        """성능 분석 및 최적화 제안"""
        print("\n🔍 성능 분석 중...")
        
        # API 응답 시간 분석
        api_times = [t["time_ms"] for t in self.results["wordpress_tests"] if "time_ms" in t]
        if api_times:
            avg_time = statistics.mean(api_times)
            max_time = max(api_times)
            min_time = min(api_times)
            
            # 병목 지점 찾기
            slowest = max(self.results["wordpress_tests"], key=lambda x: x.get("time_ms", 0))
            
            # 최적화 제안
            if avg_time > 1000:  # 1초 이상
                self.results["optimization_suggestions"].append({
                    "issue": "높은 평균 응답 시간",
                    "current": f"{avg_time:.2f}ms",
                    "suggestion": "캐싱 전략 구현, 데이터베이스 쿼리 최적화"
                })
            
            if slowest["time_ms"] > 3000:  # 3초 이상
                self.results["optimization_suggestions"].append({
                    "issue": f"느린 엔드포인트: {slowest['endpoint']}",
                    "current": f"{slowest['time_ms']:.2f}ms",
                    "suggestion": "비동기 처리, 백그라운드 작업 고려"
                })
            
            # 콘텐츠 생성 최적화
            content_test = next((t for t in self.results["wordpress_tests"] if t["test"] == "Content Generation"), None)
            if content_test and content_test["time_ms"] > 5000:
                self.results["optimization_suggestions"].append({
                    "issue": "콘텐츠 생성 시간 과다",
                    "current": f"{content_test['time_ms']:.2f}ms",
                    "suggestion": "스트리밍 응답, 청크 단위 생성 구현"
                })
    
    def print_report(self):
        """성능 테스트 보고서 출력"""
        print("\n" + "=" * 60)
        print("📊 WordPress 성능 테스트 보고서")
        print("=" * 60)
        
        # API 테스트 결과
        print("\n🔌 API 엔드포인트 성능:")
        for test in self.results["wordpress_tests"]:
            status_emoji = "✅" if test.get("status") == 200 else "❌"
            print(f"  {status_emoji} {test['test']}: {test.get('time_ms', 'N/A')}ms (Status: {test.get('status', 'N/A')})")
        
        # 통계
        api_times = [t["time_ms"] for t in self.results["wordpress_tests"] if "time_ms" in t]
        if api_times:
            print(f"\n📈 성능 통계:")
            print(f"  평균 응답 시간: {statistics.mean(api_times):.2f}ms")
            print(f"  최소 응답 시간: {min(api_times):.2f}ms")
            print(f"  최대 응답 시간: {max(api_times):.2f}ms")
            
            # 가장 느린 엔드포인트
            slowest = max(self.results["wordpress_tests"], key=lambda x: x.get("time_ms", 0))
            print(f"  가장 느린 엔드포인트: {slowest['endpoint']} ({slowest['time_ms']:.2f}ms)")
        
        # 최적화 제안
        if self.results["optimization_suggestions"]:
            print("\n💡 최적화 제안:")
            for suggestion in self.results["optimization_suggestions"]:
                print(f"  • {suggestion['issue']}")
                print(f"    현재: {suggestion['current']}")
                print(f"    제안: {suggestion['suggestion']}")
        
        print("\n" + "=" * 60)
    
    def save_results(self):
        """결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wordpress_performance_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 결과가 {filename}에 저장되었습니다.")
    
    def run_tests(self):
        """전체 테스트 실행"""
        print("🚀 WordPress 성능 테스트 시작...")
        print("=" * 60)
        
        # 실제 API 테스트
        self.test_real_api_endpoints()
        
        # 성능 분석
        self.analyze_performance()
        
        # 보고서 출력
        self.print_report()
        
        # 결과 저장
        self.save_results()


if __name__ == "__main__":
    tester = WordPressPerformanceTester()
    tester.run_tests()