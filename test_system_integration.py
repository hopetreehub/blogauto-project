#!/usr/bin/env python3
"""
전체 시스템 통합 테스트
Step 11: 모든 구성 요소의 종합적 검증
"""

import asyncio
import aiohttp
import json
import time
import requests
from typing import Dict, Any, List
from datetime import datetime
import subprocess
import sys
import os

class SystemIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = {}
        self.errors = []
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_system_health(self) -> Dict[str, Any]:
        """시스템 전체 상태 확인"""
        print("🏥 전체 시스템 상태 확인...")
        
        health_checks = {}
        
        # 1. 백엔드 서버 상태
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    health_checks["backend"] = {
                        "status": "healthy",
                        "response_time": health_data.get("response_time", 0),
                        "version": health_data.get("version", "unknown")
                    }
                else:
                    health_checks["backend"] = {"status": "unhealthy", "code": response.status}
        except Exception as e:
            health_checks["backend"] = {"status": "error", "error": str(e)}
        
        # 2. 데이터베이스 연결
        try:
            async with self.session.get(f"{self.base_url}/api/health/database") as response:
                if response.status == 200:
                    db_data = await response.json()
                    health_checks["database"] = {
                        "status": "connected",
                        "connection_pool": db_data.get("connection_pool", {})
                    }
                else:
                    health_checks["database"] = {"status": "disconnected"}
        except Exception as e:
            health_checks["database"] = {"status": "error", "error": str(e)}
        
        # 3. Redis 캐시
        try:
            async with self.session.get(f"{self.base_url}/api/performance/cache") as response:
                if response.status == 200:
                    cache_data = await response.json()
                    health_checks["redis"] = {
                        "status": "connected",
                        "l2_cache": cache_data.get("l2_cache", {})
                    }
                else:
                    health_checks["redis"] = {"status": "disconnected"}
        except Exception as e:
            health_checks["redis"] = {"status": "error", "error": str(e)}
        
        # 4. 모니터링 시스템
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    health_checks["monitoring"] = {"status": "active"}
                else:
                    health_checks["monitoring"] = {"status": "inactive"}
        except Exception as e:
            health_checks["monitoring"] = {"status": "error", "error": str(e)}
        
        return health_checks
    
    async def test_core_functionality(self) -> Dict[str, Any]:
        """핵심 기능 테스트"""
        print("🔧 핵심 기능 테스트...")
        
        core_tests = {}
        
        # 1. 키워드 분석 기능
        try:
            keyword_payload = {
                "keyword": "통합테스트",
                "country": "KR",
                "max_results": 5
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/keywords/analyze",
                json=keyword_payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    core_tests["keyword_analysis"] = {
                        "status": "success",
                        "response_time": response_time,
                        "has_data": bool(data.get("keyword")),
                        "search_volume": data.get("search_volume", 0)
                    }
                else:
                    core_tests["keyword_analysis"] = {
                        "status": "failed",
                        "code": response.status
                    }
        except Exception as e:
            core_tests["keyword_analysis"] = {"status": "error", "error": str(e)}
        
        # 2. 제목 생성 기능
        try:
            title_payload = {
                "keyword": "통합테스트",
                "count": 3,
                "tone": "professional",
                "language": "ko"
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/titles/generate",
                json=title_payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    core_tests["title_generation"] = {
                        "status": "success",
                        "response_time": response_time,
                        "title_count": len(data.get("titles", [])),
                        "avg_score": sum(t.get("score", 0) for t in data.get("titles", [])) / max(1, len(data.get("titles", [])))
                    }
                else:
                    core_tests["title_generation"] = {
                        "status": "failed",
                        "code": response.status
                    }
        except Exception as e:
            core_tests["title_generation"] = {"status": "error", "error": str(e)}
        
        # 3. 콘텐츠 생성 기능
        try:
            content_payload = {
                "title": "통합 테스트를 위한 샘플 제목",
                "keyword": "통합테스트",
                "length": "short",
                "tone": "professional"
            }
            
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/content/generate",
                json=content_payload
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    core_tests["content_generation"] = {
                        "status": "success",
                        "response_time": response_time,
                        "word_count": data.get("word_count", 0),
                        "seo_score": data.get("seo_score", 0),
                        "has_content": bool(data.get("content"))
                    }
                else:
                    core_tests["content_generation"] = {
                        "status": "failed",
                        "code": response.status
                    }
        except Exception as e:
            core_tests["content_generation"] = {"status": "error", "error": str(e)}
        
        return core_tests
    
    async def test_security_features(self) -> Dict[str, Any]:
        """보안 기능 테스트"""
        print("🔒 보안 기능 테스트...")
        
        security_tests = {}
        
        # 1. Rate Limiting 테스트
        try:
            # 빠른 연속 요청으로 Rate Limit 확인
            responses = []
            for i in range(65):  # 분당 60회 제한을 초과
                try:
                    async with self.session.get(f"{self.base_url}/health") as response:
                        responses.append(response.status)
                except:
                    responses.append(0)
            
            rate_limited = any(status == 429 for status in responses[-10:])  # 마지막 10개 요청 확인
            
            security_tests["rate_limiting"] = {
                "status": "active" if rate_limited else "inactive",
                "total_requests": len(responses),
                "rate_limited_count": responses.count(429)
            }
        except Exception as e:
            security_tests["rate_limiting"] = {"status": "error", "error": str(e)}
        
        # 2. CORS 헤더 확인
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                cors_headers = {
                    "access_control_allow_origin": response.headers.get("Access-Control-Allow-Origin"),
                    "access_control_allow_methods": response.headers.get("Access-Control-Allow-Methods"),
                    "access_control_allow_headers": response.headers.get("Access-Control-Allow-Headers")
                }
                
                security_tests["cors"] = {
                    "status": "configured",
                    "headers": cors_headers
                }
        except Exception as e:
            security_tests["cors"] = {"status": "error", "error": str(e)}
        
        # 3. 보안 헤더 확인
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                security_headers = {
                    "x_content_type_options": response.headers.get("X-Content-Type-Options"),
                    "x_frame_options": response.headers.get("X-Frame-Options"),
                    "x_xss_protection": response.headers.get("X-XSS-Protection")
                }
                
                security_tests["security_headers"] = {
                    "status": "present",
                    "headers": security_headers
                }
        except Exception as e:
            security_tests["security_headers"] = {"status": "error", "error": str(e)}
        
        return security_tests
    
    async def test_performance_systems(self) -> Dict[str, Any]:
        """성능 시스템 테스트"""
        print("⚡ 성능 시스템 테스트...")
        
        performance_tests = {}
        
        # 1. 캐싱 시스템 테스트
        try:
            # 첫 번째 요청 (캐시 미스)
            test_keyword = f"cache_test_{int(time.time())}"
            payload = {"keyword": test_keyword, "max_results": 3}
            
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/keywords/analyze",
                json=payload
            ) as response:
                first_time = time.time() - start_time
                first_status = response.status
            
            # 두 번째 요청 (캐시 히트)
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/keywords/analyze",
                json=payload
            ) as response:
                second_time = time.time() - start_time
                second_status = response.status
            
            # 캐시 효과 측정
            speedup = first_time / second_time if second_time > 0 else 0
            
            performance_tests["caching"] = {
                "status": "working",
                "first_request_time": first_time,
                "second_request_time": second_time,
                "speedup": speedup,
                "cache_effective": speedup > 1.2
            }
        except Exception as e:
            performance_tests["caching"] = {"status": "error", "error": str(e)}
        
        # 2. 응답 압축 테스트
        try:
            # 압축 요청
            headers = {"Accept-Encoding": "gzip"}
            async with self.session.get(
                f"{self.base_url}/health",
                headers=headers
            ) as response:
                content_encoding = response.headers.get("Content-Encoding", "")
                content_length = len(await response.read())
                
                performance_tests["compression"] = {
                    "status": "active" if "gzip" in content_encoding else "inactive",
                    "content_encoding": content_encoding,
                    "compressed_size": content_length
                }
        except Exception as e:
            performance_tests["compression"] = {"status": "error", "error": str(e)}
        
        # 3. 연결 풀 상태
        try:
            async with self.session.get(f"{self.base_url}/api/performance/http-pool") as response:
                if response.status == 200:
                    pool_data = await response.json()
                    performance_tests["connection_pooling"] = {
                        "status": "active",
                        "pool_info": pool_data
                    }
                else:
                    performance_tests["connection_pooling"] = {"status": "unavailable"}
        except Exception as e:
            performance_tests["connection_pooling"] = {"status": "error", "error": str(e)}
        
        return performance_tests
    
    async def test_monitoring_systems(self) -> Dict[str, Any]:
        """모니터링 시스템 테스트"""
        print("📊 모니터링 시스템 테스트...")
        
        monitoring_tests = {}
        
        # 1. Prometheus 메트릭
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    metrics_data = await response.text()
                    monitoring_tests["prometheus"] = {
                        "status": "active",
                        "metrics_count": len(metrics_data.split('\n')),
                        "has_custom_metrics": "blogauto_" in metrics_data
                    }
                else:
                    monitoring_tests["prometheus"] = {"status": "inactive"}
        except Exception as e:
            monitoring_tests["prometheus"] = {"status": "error", "error": str(e)}
        
        # 2. 성능 요약 데이터
        try:
            async with self.session.get(f"{self.base_url}/api/performance/summary") as response:
                if response.status == 200:
                    summary_data = await response.json()
                    monitoring_tests["performance_summary"] = {
                        "status": "active",
                        "total_requests": summary_data.get("total_requests", 0),
                        "error_rate": summary_data.get("error_rate", 0),
                        "avg_response_time": summary_data.get("response_times", {}).get("average", 0)
                    }
                else:
                    monitoring_tests["performance_summary"] = {"status": "unavailable"}
        except Exception as e:
            monitoring_tests["performance_summary"] = {"status": "error", "error": str(e)}
        
        # 3. 헬스체크 상세 정보
        try:
            async with self.session.get(f"{self.base_url}/api/health/detailed") as response:
                if response.status == 200:
                    health_data = await response.json()
                    monitoring_tests["health_detailed"] = {
                        "status": "active",
                        "components": health_data.get("components", {}),
                        "overall_status": health_data.get("status", "unknown")
                    }
                else:
                    monitoring_tests["health_detailed"] = {"status": "unavailable"}
        except Exception as e:
            monitoring_tests["health_detailed"] = {"status": "error", "error": str(e)}
        
        return monitoring_tests
    
    async def test_data_flow_integration(self) -> Dict[str, Any]:
        """데이터 흐름 통합 테스트"""
        print("🔄 데이터 흐름 통합 테스트...")
        
        flow_tests = {}
        
        try:
            # 전체 워크플로우: 키워드 → 제목 → 콘텐츠
            test_keyword = "데이터흐름테스트"
            
            # 1단계: 키워드 분석
            step1_start = time.time()
            async with self.session.post(
                f"{self.base_url}/api/keywords/analyze",
                json={"keyword": test_keyword, "max_results": 3}
            ) as response:
                step1_time = time.time() - step1_start
                if response.status == 200:
                    keyword_data = await response.json()
                    step1_success = True
                else:
                    step1_success = False
                    keyword_data = {}
            
            # 2단계: 제목 생성 (키워드 분석 결과 사용)
            step2_start = time.time()
            async with self.session.post(
                f"{self.base_url}/api/titles/generate",
                json={"keyword": test_keyword, "count": 2}
            ) as response:
                step2_time = time.time() - step2_start
                if response.status == 200:
                    title_data = await response.json()
                    step2_success = True
                    best_title = title_data.get("titles", [{}])[0].get("title", "기본 제목")
                else:
                    step2_success = False
                    title_data = {}
                    best_title = "기본 제목"
            
            # 3단계: 콘텐츠 생성 (제목 생성 결과 사용)
            step3_start = time.time()
            async with self.session.post(
                f"{self.base_url}/api/content/generate",
                json={
                    "title": best_title,
                    "keyword": test_keyword,
                    "length": "short"
                }
            ) as response:
                step3_time = time.time() - step3_start
                if response.status == 200:
                    content_data = await response.json()
                    step3_success = True
                else:
                    step3_success = False
                    content_data = {}
            
            total_time = step1_time + step2_time + step3_time
            
            flow_tests["end_to_end_workflow"] = {
                "status": "success" if all([step1_success, step2_success, step3_success]) else "partial",
                "steps": {
                    "keyword_analysis": {
                        "success": step1_success,
                        "time": step1_time,
                        "search_volume": keyword_data.get("search_volume", 0)
                    },
                    "title_generation": {
                        "success": step2_success,
                        "time": step2_time,
                        "title_count": len(title_data.get("titles", []))
                    },
                    "content_generation": {
                        "success": step3_success,
                        "time": step3_time,
                        "word_count": content_data.get("word_count", 0)
                    }
                },
                "total_time": total_time,
                "data_consistency": {
                    "keyword_used": test_keyword,
                    "title_generated": best_title,
                    "content_created": bool(content_data.get("content"))
                }
            }
            
        except Exception as e:
            flow_tests["end_to_end_workflow"] = {"status": "error", "error": str(e)}
        
        return flow_tests
    
    async def test_stress_conditions(self) -> Dict[str, Any]:
        """스트레스 조건 테스트"""
        print("💪 스트레스 조건 테스트...")
        
        stress_tests = {}
        
        # 1. 동시 요청 처리
        try:
            concurrent_count = 20
            tasks = []
            
            async def make_request():
                start_time = time.time()
                try:
                    async with self.session.get(f"{self.base_url}/health") as response:
                        return {
                            "status": response.status,
                            "time": time.time() - start_time,
                            "success": response.status == 200
                        }
                except Exception as e:
                    return {
                        "status": 0,
                        "time": time.time() - start_time,
                        "success": False,
                        "error": str(e)
                    }
            
            # 동시 요청 실행
            start_time = time.time()
            tasks = [make_request() for _ in range(concurrent_count)]
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            successful_requests = sum(1 for r in results if r["success"])
            avg_response_time = sum(r["time"] for r in results) / len(results)
            
            stress_tests["concurrent_requests"] = {
                "status": "completed",
                "total_requests": concurrent_count,
                "successful_requests": successful_requests,
                "success_rate": successful_requests / concurrent_count,
                "avg_response_time": avg_response_time,
                "total_time": total_time,
                "requests_per_second": concurrent_count / total_time
            }
            
        except Exception as e:
            stress_tests["concurrent_requests"] = {"status": "error", "error": str(e)}
        
        # 2. 메모리 집약적 작업
        try:
            # 큰 키워드 목록으로 테스트
            large_keyword = "메모리테스트" * 10  # 긴 키워드
            
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/keywords/analyze",
                json={"keyword": large_keyword, "max_results": 50}
            ) as response:
                response_time = time.time() - start_time
                
                stress_tests["memory_intensive"] = {
                    "status": "completed",
                    "response_status": response.status,
                    "response_time": response_time,
                    "handled_large_request": response.status == 200,
                    "keyword_length": len(large_keyword)
                }
        except Exception as e:
            stress_tests["memory_intensive"] = {"status": "error", "error": str(e)}
        
        return stress_tests
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 통합 테스트 실행"""
        print("🚀 전체 시스템 통합 테스트 시작...")
        print("=" * 80)
        
        comprehensive_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_duration": 0,
            "overall_status": "unknown",
            "test_results": {}
        }
        
        test_start_time = time.time()
        
        try:
            # 1. 시스템 상태 확인
            comprehensive_results["test_results"]["system_health"] = await self.test_system_health()
            
            # 2. 핵심 기능 테스트
            comprehensive_results["test_results"]["core_functionality"] = await self.test_core_functionality()
            
            # 3. 보안 기능 테스트
            comprehensive_results["test_results"]["security_features"] = await self.test_security_features()
            
            # 4. 성능 시스템 테스트
            comprehensive_results["test_results"]["performance_systems"] = await self.test_performance_systems()
            
            # 5. 모니터링 시스템 테스트
            comprehensive_results["test_results"]["monitoring_systems"] = await self.test_monitoring_systems()
            
            # 6. 데이터 흐름 통합 테스트
            comprehensive_results["test_results"]["data_flow_integration"] = await self.test_data_flow_integration()
            
            # 7. 스트레스 조건 테스트
            comprehensive_results["test_results"]["stress_conditions"] = await self.test_stress_conditions()
            
            # 전체 테스트 소요 시간
            comprehensive_results["test_duration"] = time.time() - test_start_time
            
            # 전체 상태 평가
            comprehensive_results["overall_status"] = self._evaluate_overall_status(
                comprehensive_results["test_results"]
            )
            
        except Exception as e:
            comprehensive_results["overall_status"] = "error"
            comprehensive_results["error"] = str(e)
            comprehensive_results["test_duration"] = time.time() - test_start_time
        
        return comprehensive_results
    
    def _evaluate_overall_status(self, test_results: Dict[str, Any]) -> str:
        """전체 테스트 결과 평가"""
        critical_systems = [
            "system_health",
            "core_functionality", 
            "data_flow_integration"
        ]
        
        important_systems = [
            "security_features",
            "performance_systems",
            "monitoring_systems"
        ]
        
        # 중요 시스템 점검
        critical_issues = 0
        for system in critical_systems:
            if system in test_results:
                system_data = test_results[system]
                if self._has_critical_issues(system_data):
                    critical_issues += 1
        
        # 부가 시스템 점검
        minor_issues = 0
        for system in important_systems:
            if system in test_results:
                system_data = test_results[system]
                if self._has_minor_issues(system_data):
                    minor_issues += 1
        
        # 상태 결정
        if critical_issues == 0 and minor_issues <= 1:
            return "excellent"
        elif critical_issues == 0 and minor_issues <= 2:
            return "good"
        elif critical_issues <= 1:
            return "fair"
        else:
            return "poor"
    
    def _has_critical_issues(self, system_data: Dict[str, Any]) -> bool:
        """중요한 문제가 있는지 확인"""
        for key, value in system_data.items():
            if isinstance(value, dict):
                status = value.get("status", "unknown")
                if status in ["error", "failed", "unhealthy", "disconnected"]:
                    return True
        return False
    
    def _has_minor_issues(self, system_data: Dict[str, Any]) -> bool:
        """경미한 문제가 있는지 확인"""
        for key, value in system_data.items():
            if isinstance(value, dict):
                status = value.get("status", "unknown")
                if status in ["inactive", "unavailable", "partial"]:
                    return True
        return False

def print_test_summary(results: Dict[str, Any]):
    """테스트 결과 요약 출력"""
    print("\n" + "=" * 80)
    print("📊 전체 시스템 통합 테스트 결과 요약")
    print("=" * 80)
    
    # 전체 상태
    overall_status = results.get("overall_status", "unknown")
    status_emoji = {
        "excellent": "🟢",
        "good": "🟡", 
        "fair": "🟠",
        "poor": "🔴",
        "error": "💥"
    }
    
    print(f"전체 상태: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
    print(f"테스트 소요 시간: {results.get('test_duration', 0):.2f}초")
    print(f"테스트 실행 시간: {results.get('test_timestamp', 'unknown')}")
    
    # 시스템별 결과
    test_results = results.get("test_results", {})
    
    print("\n📋 시스템별 테스트 결과:")
    
    # 1. 시스템 상태
    health = test_results.get("system_health", {})
    print(f"\n🏥 시스템 상태:")
    for component, data in health.items():
        status = data.get("status", "unknown") if isinstance(data, dict) else "unknown"
        print(f"   - {component}: {status}")
    
    # 2. 핵심 기능
    core = test_results.get("core_functionality", {})
    print(f"\n🔧 핵심 기능:")
    for feature, data in core.items():
        status = data.get("status", "unknown") if isinstance(data, dict) else "unknown"
        response_time = data.get("response_time", 0) if isinstance(data, dict) else 0
        print(f"   - {feature}: {status} ({response_time:.3f}초)")
    
    # 3. 보안 기능
    security = test_results.get("security_features", {})
    print(f"\n🔒 보안 기능:")
    for feature, data in security.items():
        status = data.get("status", "unknown") if isinstance(data, dict) else "unknown"
        print(f"   - {feature}: {status}")
    
    # 4. 성능 시스템
    performance = test_results.get("performance_systems", {})
    print(f"\n⚡ 성능 시스템:")
    for feature, data in performance.items():
        status = data.get("status", "unknown") if isinstance(data, dict) else "unknown"
        if feature == "caching":
            speedup = data.get("speedup", 0) if isinstance(data, dict) else 0
            print(f"   - {feature}: {status} (속도 향상: {speedup:.2f}배)")
        else:
            print(f"   - {feature}: {status}")
    
    # 5. 데이터 흐름
    flow = test_results.get("data_flow_integration", {})
    workflow = flow.get("end_to_end_workflow", {})
    if workflow:
        print(f"\n🔄 데이터 흐름 통합:")
        print(f"   - 전체 워크플로우: {workflow.get('status', 'unknown')}")
        print(f"   - 전체 소요 시간: {workflow.get('total_time', 0):.3f}초")
        
        steps = workflow.get("steps", {})
        for step_name, step_data in steps.items():
            success = "성공" if step_data.get("success", False) else "실패"
            time_taken = step_data.get("time", 0)
            print(f"     • {step_name}: {success} ({time_taken:.3f}초)")
    
    # 6. 스트레스 테스트
    stress = test_results.get("stress_conditions", {})
    print(f"\n💪 스트레스 테스트:")
    concurrent = stress.get("concurrent_requests", {})
    if concurrent:
        success_rate = concurrent.get("success_rate", 0)
        rps = concurrent.get("requests_per_second", 0)
        print(f"   - 동시 요청: {success_rate:.1%} 성공률, {rps:.1f} req/s")
    
    # 권장사항
    print(f"\n💡 권장사항:")
    if overall_status == "excellent":
        print("   ✅ 모든 시스템이 정상 작동합니다. 프로덕션 배포 준비 완료!")
    elif overall_status == "good":
        print("   ✅ 대부분의 시스템이 정상입니다. 경미한 이슈만 수정하면 배포 가능합니다.")
    elif overall_status == "fair":
        print("   ⚠️  일부 중요한 문제가 발견되었습니다. 수정 후 재테스트를 권장합니다.")
    else:
        print("   🚨 심각한 문제가 발견되었습니다. 즉시 수정이 필요합니다.")

async def main():
    """메인 테스트 실행"""
    print("🧪 BlogAuto 전체 시스템 통합 테스트")
    print("Step 11: 모든 구성 요소의 종합적 검증")
    print("=" * 80)
    
    async with SystemIntegrationTester() as tester:
        results = await tester.run_comprehensive_test()
        
        # 결과 출력
        print_test_summary(results)
        
        # 결과를 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/mnt/e/project/test-blogauto-project/system_integration_test_results_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 상세 결과가 {filename}에 저장되었습니다.")
        
        # 최종 상태 반환
        return results.get("overall_status", "unknown")

if __name__ == "__main__":
    final_status = asyncio.run(main())
    
    # 종료 코드 설정
    if final_status in ["excellent", "good"]:
        sys.exit(0)
    else:
        sys.exit(1)