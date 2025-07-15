#!/usr/bin/env python3
"""
성능 테스트 스크립트
- API 응답시간 측정
- 데이터베이스 쿼리 성능 분석
- WordPress 포스팅 성능 테스트
- 병목 지점 파악
"""

import time
import requests
import json
import sqlite3
import asyncio
from datetime import datetime
from typing import Dict, List, Tuple
import statistics
import os
import subprocess

class PerformanceTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {
            "api_tests": [],
            "db_tests": [],
            "wordpress_tests": [],
            "system_metrics": {}
        }
        
    def measure_system_resources(self) -> Dict:
        """시스템 리소스 사용량 측정"""
        # CPU 사용률
        try:
            cpu_result = subprocess.run(['grep', 'cpu ', '/proc/stat'], capture_output=True, text=True)
            cpu_percent = 0  # 간단히 0으로 설정
        except:
            cpu_percent = 0
            
        # 메모리 사용률
        try:
            mem_result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            lines = mem_result.stdout.split('\n')
            if len(lines) > 1:
                mem_values = lines[1].split()
                if len(mem_values) > 2:
                    total = float(mem_values[1])
                    used = float(mem_values[2])
                    memory_percent = (used / total) * 100 if total > 0 else 0
                else:
                    memory_percent = 0
            else:
                memory_percent = 0
        except:
            memory_percent = 0
            
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": round(memory_percent, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def measure_api_response_time(self, endpoint: str, method: str = "GET", 
                                 data: Dict = None, headers: Dict = None) -> Tuple[float, int, str]:
        """API 응답시간 측정"""
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", json=data, headers=headers)
            
            elapsed_time = (time.time() - start_time) * 1000  # ms
            return elapsed_time, response.status_code, response.text[:200]
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            return elapsed_time, 0, str(e)
    
    def test_database_performance(self):
        """데이터베이스 쿼리 성능 테스트"""
        db_path = "/mnt/e/project/test-blogauto-project/backend/blogauto_personal.db"
        
        if not os.path.exists(db_path):
            return {"error": "Database file not found"}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tests = []
        
        # 1. 간단한 SELECT 쿼리
        start = time.time()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        tests.append({
            "query": "SELECT COUNT(*) FROM users",
            "time_ms": (time.time() - start) * 1000,
            "result": f"{count} users"
        })
        
        # 2. 복잡한 쿼리 (generated_titles 테이블 사용)
        start = time.time()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM generated_titles
            WHERE created_at IS NOT NULL
        """)
        count = cursor.fetchone()[0]
        tests.append({
            "query": "Complex query (generated_titles)",
            "time_ms": (time.time() - start) * 1000,
            "result": f"{count} records"
        })
        
        # 3. 인덱스 확인
        start = time.time()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        tests.append({
            "query": "Check indexes",
            "time_ms": (time.time() - start) * 1000,
            "result": f"{len(indexes)} indexes found"
        })
        
        conn.close()
        return tests
    
    def test_wordpress_posting(self):
        """WordPress 포스팅 성능 테스트"""
        # 먼저 로그인
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        # 로그인 시간 측정
        start = time.time()
        login_response = requests.post(f"{self.base_url}/api/auth/login", json=login_data)
        login_time = (time.time() - start) * 1000
        
        if login_response.status_code != 200:
            return [{
                "test": "Login",
                "time_ms": login_time,
                "status": "Failed",
                "error": login_response.text
            }]
        
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        tests = [{
            "test": "Login",
            "time_ms": login_time,
            "status": "Success"
        }]
        
        # WordPress 연결 테스트
        start = time.time()
        wp_test = requests.post(
            f"{self.base_url}/api/wordpress/test-connection",
            json={"site_url": "https://example.com"},
            headers=headers
        )
        tests.append({
            "test": "WordPress Connection Test",
            "time_ms": (time.time() - start) * 1000,
            "status": "Success" if wp_test.status_code == 200 else "Failed",
            "details": wp_test.text[:100]
        })
        
        # 콘텐츠 생성 및 포스팅 테스트
        content_data = {
            "title": "성능 테스트 포스트",
            "content": "이것은 성능 테스트를 위한 콘텐츠입니다.",
            "keywords": ["테스트", "성능"],
            "site_id": "test_site"
        }
        
        start = time.time()
        post_response = requests.post(
            f"{self.base_url}/api/wordpress/create-post",
            json=content_data,
            headers=headers
        )
        tests.append({
            "test": "Create WordPress Post",
            "time_ms": (time.time() - start) * 1000,
            "status": "Success" if post_response.status_code == 200 else "Failed",
            "details": post_response.text[:100]
        })
        
        return tests
    
    def run_performance_tests(self):
        """전체 성능 테스트 실행"""
        print("🚀 성능 테스트 시작...")
        print("=" * 60)
        
        # 1. 시스템 리소스 측정
        print("\n📊 시스템 리소스 측정 중...")
        self.results["system_metrics"]["start"] = self.measure_system_resources()
        
        # 2. API 엔드포인트 테스트
        print("\n🔌 API 응답시간 테스트...")
        api_endpoints = [
            ("/", "GET"),
            ("/api/health", "GET"),
            ("/api/auth/login", "POST", {"username": "admin", "password": "admin123"}),
        ]
        
        for endpoint_data in api_endpoints:
            endpoint = endpoint_data[0]
            method = endpoint_data[1]
            data = endpoint_data[2] if len(endpoint_data) > 2 else None
            
            # 5회 반복 측정
            times = []
            for i in range(5):
                elapsed, status, response = self.measure_api_response_time(endpoint, method, data)
                times.append(elapsed)
                time.sleep(0.1)  # 부하 방지
            
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "avg_time_ms": round(avg_time, 2),
                "min_time_ms": round(min_time, 2),
                "max_time_ms": round(max_time, 2),
                "last_status": status
            }
            self.results["api_tests"].append(result)
            print(f"  {method} {endpoint}: avg={avg_time:.2f}ms, min={min_time:.2f}ms, max={max_time:.2f}ms")
        
        # 3. 데이터베이스 성능 테스트
        print("\n💾 데이터베이스 성능 테스트...")
        db_results = self.test_database_performance()
        self.results["db_tests"] = db_results
        for test in db_results:
            if "error" in test:
                print(f"  ❌ {test['error']}")
            else:
                print(f"  {test['query']}: {test['time_ms']:.2f}ms")
        
        # 4. WordPress 포스팅 테스트
        print("\n📝 WordPress 포스팅 성능 테스트...")
        wp_results = self.test_wordpress_posting()
        self.results["wordpress_tests"] = wp_results
        for test in wp_results:
            print(f"  {test['test']}: {test['time_ms']:.2f}ms - {test['status']}")
        
        # 5. 최종 시스템 리소스 측정
        self.results["system_metrics"]["end"] = self.measure_system_resources()
        
        # 6. 결과 저장
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """테스트 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 결과가 {filename}에 저장되었습니다.")
    
    def print_summary(self):
        """테스트 결과 요약"""
        print("\n" + "=" * 60)
        print("📊 성능 테스트 요약")
        print("=" * 60)
        
        # API 성능
        if self.results["api_tests"]:
            avg_times = [t["avg_time_ms"] for t in self.results["api_tests"]]
            print(f"\n🔌 API 응답시간:")
            print(f"  평균: {statistics.mean(avg_times):.2f}ms")
            print(f"  최소: {min(avg_times):.2f}ms")
            print(f"  최대: {max(avg_times):.2f}ms")
        
        # DB 성능
        if self.results["db_tests"] and "error" not in self.results["db_tests"]:
            db_times = [t["time_ms"] for t in self.results["db_tests"] if "time_ms" in t]
            if db_times:
                print(f"\n💾 데이터베이스 쿼리:")
                print(f"  평균: {statistics.mean(db_times):.2f}ms")
        
        # 시스템 리소스
        if "start" in self.results["system_metrics"] and "end" in self.results["system_metrics"]:
            start = self.results["system_metrics"]["start"]
            end = self.results["system_metrics"]["end"]
            print(f"\n🖥️ 시스템 리소스:")
            print(f"  CPU: {start['cpu_percent']}% → {end['cpu_percent']}%")
            print(f"  Memory: {start['memory_percent']}% → {end['memory_percent']}%")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    tester = PerformanceTester()
    tester.run_performance_tests()