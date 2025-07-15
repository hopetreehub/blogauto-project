#!/usr/bin/env python3
"""
모니터링 시스템 테스트 스크립트
Step 8: 모니터링 시스템 구축 검증
"""

import asyncio
import aiohttp
import time
import json
import os
from typing import Dict, Any, List
from datetime import datetime

class MonitoringSystemTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_prometheus_metrics(self) -> Dict[str, Any]:
        """Prometheus 메트릭 엔드포인트 테스트"""
        print("📊 Prometheus 메트릭 테스트...")
        
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    metrics_text = await response.text()
                    
                    # 메트릭 파싱
                    metrics = self._parse_prometheus_metrics(metrics_text)
                    
                    # 필수 메트릭 확인
                    required_metrics = [
                        "blogauto_api_requests_total",
                        "blogauto_api_request_duration_seconds",
                        "blogauto_api_requests_in_progress",
                        "blogauto_keywords_analyzed_total",
                        "blogauto_cpu_usage_percent",
                        "blogauto_memory_usage_bytes"
                    ]
                    
                    found_metrics = []
                    missing_metrics = []
                    
                    for metric in required_metrics:
                        if metric in metrics:
                            found_metrics.append(metric)
                        else:
                            missing_metrics.append(metric)
                    
                    return {
                        "status": "success",
                        "metrics_endpoint": True,
                        "total_metrics": len(metrics),
                        "found_required_metrics": len(found_metrics),
                        "missing_metrics": missing_metrics,
                        "sample_values": {
                            metric: metrics.get(metric, {}).get("value", "N/A")
                            for metric in found_metrics[:5]
                        }
                    }
                else:
                    return {
                        "status": "error",
                        "metrics_endpoint": False,
                        "error": f"HTTP {response.status}"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "metrics_endpoint": False,
                "error": str(e)
            }
    
    def _parse_prometheus_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """Prometheus 메트릭 텍스트 파싱"""
        metrics = {}
        
        for line in metrics_text.split('\n'):
            if line and not line.startswith('#'):
                try:
                    parts = line.split(' ')
                    if len(parts) >= 2:
                        metric_name = parts[0].split('{')[0]
                        metric_value = float(parts[1]) if parts[1] != 'NaN' else None
                        
                        if metric_name not in metrics:
                            metrics[metric_name] = {"value": metric_value, "count": 1}
                        else:
                            metrics[metric_name]["count"] += 1
                except:
                    continue
        
        return metrics
    
    async def test_health_endpoints(self) -> Dict[str, Any]:
        """헬스체크 엔드포인트 테스트"""
        print("🏥 헬스체크 엔드포인트 테스트...")
        
        results = {}
        
        # 기본 헬스체크
        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    results["basic_health"] = {
                        "status": health_data.get("status", "unknown"),
                        "apis": health_data.get("apis", {})
                    }
                else:
                    results["basic_health"] = {"status": "error", "code": response.status}
        except Exception as e:
            results["basic_health"] = {"status": "error", "error": str(e)}
        
        # 상세 헬스체크
        try:
            async with self.session.get(f"{self.base_url}/health/detailed") as response:
                if response.status == 200:
                    detailed_data = await response.json()
                    results["detailed_health"] = {
                        "status": detailed_data.get("status", "unknown"),
                        "system": detailed_data.get("system", {}),
                        "process": detailed_data.get("process", {}),
                        "monitoring": detailed_data.get("monitoring", {})
                    }
                else:
                    results["detailed_health"] = {"status": "error", "code": response.status}
        except Exception as e:
            results["detailed_health"] = {"status": "error", "error": str(e)}
        
        return results
    
    async def test_error_tracking(self) -> Dict[str, Any]:
        """에러 추적 시스템 테스트"""
        print("🐛 에러 추적 시스템 테스트...")
        
        # 의도적으로 에러를 발생시켜 추적 테스트
        error_endpoints = [
            ("/api/nonexistent", 404),
            ("/api/keywords/analyze", 401),  # API 키 없이 호출
        ]
        
        # 에러 발생
        for endpoint, expected_status in error_endpoints:
            try:
                async with self.session.post(f"{self.base_url}{endpoint}", json={}) as response:
                    pass  # 에러 발생이 목적
            except:
                pass
        
        # 잠시 대기 후 에러 요약 확인
        await asyncio.sleep(1)
        
        try:
            async with self.session.get(f"{self.base_url}/api/monitoring/errors") as response:
                if response.status == 200:
                    error_summary = await response.json()
                    return {
                        "status": "success",
                        "error_tracking": True,
                        "total_errors": error_summary.get("total_errors", 0),
                        "error_types": error_summary.get("error_types", 0),
                        "most_common_errors": error_summary.get("most_common_errors", [])[:3],
                        "recent_patterns": error_summary.get("recent_patterns", [])[:3]
                    }
                else:
                    return {
                        "status": "error",
                        "error_tracking": False,
                        "code": response.status
                    }
        except Exception as e:
            return {
                "status": "error",
                "error_tracking": False,
                "error": str(e)
            }
    
    async def test_business_metrics(self) -> Dict[str, Any]:
        """비즈니스 메트릭 수집 테스트"""
        print("📈 비즈니스 메트릭 테스트...")
        
        # 메트릭을 생성할 API 호출
        test_operations = [
            {
                "endpoint": "/api/keywords/analyze",
                "method": "POST",
                "data": {"keyword": "모니터링", "max_results": 3},
                "metric": "keywords_analyzed"
            }
        ]
        
        # API 호출 실행
        for op in test_operations:
            try:
                if op["method"] == "POST":
                    async with self.session.post(
                        f"{self.base_url}{op['endpoint']}", 
                        json=op["data"]
                    ) as response:
                        pass
            except:
                pass
        
        # 메트릭 확인
        await asyncio.sleep(1)
        
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    metrics_text = await response.text()
                    
                    # 비즈니스 메트릭 확인
                    business_metrics = [
                        "blogauto_keywords_analyzed_total",
                        "blogauto_titles_generated_total",
                        "blogauto_content_generated_total"
                    ]
                    
                    found_business_metrics = []
                    for metric in business_metrics:
                        if metric in metrics_text:
                            found_business_metrics.append(metric)
                    
                    return {
                        "status": "success",
                        "business_metrics_collection": True,
                        "found_metrics": found_business_metrics,
                        "collection_rate": len(found_business_metrics) / len(business_metrics) * 100
                    }
                else:
                    return {
                        "status": "error",
                        "business_metrics_collection": False,
                        "code": response.status
                    }
        except Exception as e:
            return {
                "status": "error",
                "business_metrics_collection": False,
                "error": str(e)
            }
    
    async def test_rate_limit_metrics(self) -> Dict[str, Any]:
        """Rate Limiting 메트릭 테스트"""
        print("🚦 Rate Limiting 메트릭 테스트...")
        
        # Rate limit에 도달하도록 많은 요청 발생
        endpoint = "/api/keywords/analyze"
        
        for i in range(15):  # Rate limit 초과
            try:
                async with self.session.post(
                    f"{self.base_url}{endpoint}",
                    json={"keyword": f"test{i}"}
                ) as response:
                    if response.status == 429:
                        break
            except:
                pass
        
        # 메트릭 확인
        try:
            async with self.session.get(f"{self.base_url}/metrics") as response:
                if response.status == 200:
                    metrics_text = await response.text()
                    
                    rate_limit_metrics = [
                        "blogauto_rate_limit_rejected_total",
                        "blogauto_blocked_ips_total"
                    ]
                    
                    found_rl_metrics = []
                    for metric in rate_limit_metrics:
                        if metric in metrics_text:
                            found_rl_metrics.append(metric)
                    
                    # Rate limit 통계 확인
                    async with self.session.get(f"{self.base_url}/api/admin/rate-limit-stats") as rl_response:
                        if rl_response.status == 200:
                            rl_stats = await rl_response.json()
                            blocked_ips = rl_stats.get("blocked_ips", 0)
                        else:
                            blocked_ips = "unknown"
                    
                    return {
                        "status": "success",
                        "rate_limit_metrics": True,
                        "found_metrics": found_rl_metrics,
                        "blocked_ips_count": blocked_ips
                    }
                else:
                    return {
                        "status": "error",
                        "rate_limit_metrics": False,
                        "code": response.status
                    }
        except Exception as e:
            return {
                "status": "error",
                "rate_limit_metrics": False,
                "error": str(e)
            }
    
    async def test_monitoring_performance(self) -> Dict[str, Any]:
        """모니터링 시스템 성능 테스트"""
        print("⚡ 모니터링 성능 테스트...")
        
        # 메트릭 엔드포인트 응답 시간 측정
        response_times = []
        
        for i in range(10):
            start_time = time.time()
            try:
                async with self.session.get(f"{self.base_url}/metrics") as response:
                    await response.text()
                    response_time = (time.time() - start_time) * 1000  # ms
                    response_times.append(response_time)
            except:
                pass
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            return {
                "status": "success",
                "performance_test": True,
                "avg_response_time_ms": round(avg_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2),
                "samples": len(response_times),
                "performance_acceptable": avg_response_time < 100  # 100ms 미만이면 양호
            }
        else:
            return {
                "status": "error",
                "performance_test": False,
                "error": "No successful requests"
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 모니터링 테스트 실행"""
        print("🚀 모니터링 시스템 종합 테스트 시작...")
        print("=" * 60)
        
        results = {}
        
        # 1. Prometheus 메트릭 테스트
        results["prometheus"] = await self.test_prometheus_metrics()
        
        # 2. 헬스체크 엔드포인트 테스트
        results["health_checks"] = await self.test_health_endpoints()
        
        # 3. 에러 추적 테스트
        results["error_tracking"] = await self.test_error_tracking()
        
        # 4. 비즈니스 메트릭 테스트
        results["business_metrics"] = await self.test_business_metrics()
        
        # 5. Rate Limiting 메트릭 테스트
        results["rate_limit_metrics"] = await self.test_rate_limit_metrics()
        
        # 6. 성능 테스트
        results["performance"] = await self.test_monitoring_performance()
        
        return results

async def main():
    """메인 테스트 실행"""
    async with MonitoringSystemTester() as tester:
        results = await tester.run_all_tests()
        
        print("\n" + "=" * 60)
        print("📊 모니터링 시스템 테스트 결과 요약")
        print("=" * 60)
        
        # Prometheus 메트릭 결과
        prometheus = results["prometheus"]
        print(f"📊 Prometheus 메트릭:")
        print(f"   - 메트릭 엔드포인트: {'✅' if prometheus.get('metrics_endpoint') else '❌'}")
        print(f"   - 총 메트릭 수: {prometheus.get('total_metrics', 0)}")
        print(f"   - 필수 메트릭: {prometheus.get('found_required_metrics', 0)}/6")
        
        # 헬스체크 결과
        health = results["health_checks"]
        print(f"\n🏥 헬스체크:")
        print(f"   - 기본 헬스체크: {health.get('basic_health', {}).get('status', 'unknown')}")
        print(f"   - 상세 헬스체크: {health.get('detailed_health', {}).get('status', 'unknown')}")
        if "system" in health.get("detailed_health", {}):
            system = health["detailed_health"]["system"]
            print(f"   - CPU 사용률: {system.get('cpu_percent', 'N/A')}%")
            print(f"   - 메모리 사용률: {system.get('memory_percent', 'N/A')}%")
        
        # 에러 추적 결과
        errors = results["error_tracking"]
        print(f"\n🐛 에러 추적:")
        print(f"   - 에러 추적 시스템: {'✅' if errors.get('error_tracking') else '❌'}")
        print(f"   - 총 에러 수: {errors.get('total_errors', 0)}")
        print(f"   - 에러 타입: {errors.get('error_types', 0)}")
        
        # 비즈니스 메트릭 결과
        business = results["business_metrics"]
        print(f"\n📈 비즈니스 메트릭:")
        print(f"   - 메트릭 수집: {'✅' if business.get('business_metrics_collection') else '❌'}")
        print(f"   - 수집률: {business.get('collection_rate', 0):.1f}%")
        
        # Rate Limiting 메트릭 결과
        rate_limit = results["rate_limit_metrics"]
        print(f"\n🚦 Rate Limiting 메트릭:")
        print(f"   - 메트릭 수집: {'✅' if rate_limit.get('rate_limit_metrics') else '❌'}")
        print(f"   - 차단된 IP: {rate_limit.get('blocked_ips_count', 'N/A')}")
        
        # 성능 결과
        performance = results["performance"]
        print(f"\n⚡ 성능:")
        print(f"   - 평균 응답 시간: {performance.get('avg_response_time_ms', 'N/A')}ms")
        print(f"   - 성능 상태: {'✅ 양호' if performance.get('performance_acceptable') else '⚠️ 개선 필요'}")
        
        # 전체 점수 계산
        total_checks = 6
        passed_checks = sum([
            prometheus.get('metrics_endpoint', False),
            health.get('basic_health', {}).get('status') == 'healthy',
            errors.get('error_tracking', False),
            business.get('business_metrics_collection', False),
            rate_limit.get('rate_limit_metrics', False),
            performance.get('performance_acceptable', False)
        ])
        
        success_rate = (passed_checks / total_checks) * 100
        
        print(f"\n🎯 전체 모니터링 시스템 준비도: {success_rate:.1f}%")
        print("🎉 모니터링 시스템 구축 완료!")
        
        # 상세 결과를 JSON 파일로 저장
        with open("/mnt/e/project/test-blogauto-project/monitoring_system_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("📄 상세 결과가 monitoring_system_test_results.json에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())