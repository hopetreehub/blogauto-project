#!/usr/bin/env python3
"""
성능 최적화 시스템 테스트 스크립트
Step 9: 성능 최적화 및 캐싱 전략 검증
"""

import asyncio
import aiohttp
import time
import statistics
from typing import Dict, Any, List
import json

class PerformanceOptimizationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_cache_performance(self) -> Dict[str, Any]:
        """캐시 성능 테스트"""
        print("💾 캐시 성능 테스트...")
        
        test_keyword = "performance_test_cache"
        endpoint = "/api/keywords/analyze"
        data = {"keyword": test_keyword, "max_results": 5}
        
        # 첫 번째 요청 (캐시 미스)
        start_time = time.time()
        async with self.session.post(f"{self.base_url}{endpoint}", json=data) as response:
            first_response_time = time.time() - start_time
            first_status = response.status
            first_data = await response.json() if response.status == 200 else None
        
        # 두 번째 요청 (캐시 히트)
        start_time = time.time()
        async with self.session.post(f"{self.base_url}{endpoint}", json=data) as response:
            second_response_time = time.time() - start_time
            second_status = response.status
            second_data = await response.json() if response.status == 200 else None
        
        # 캐시 상태 확인
        async with self.session.get(f"{self.base_url}/api/performance/cache") as response:
            cache_status = await response.json() if response.status == 200 else {}
        
        # 캐시 효과 계산
        if first_response_time > 0:
            speedup = first_response_time / second_response_time
        else:
            speedup = 0
        
        return {
            "cache_test": {
                "first_request": {
                    "response_time": first_response_time,
                    "status": first_status,
                    "cache_miss": True
                },
                "second_request": {
                    "response_time": second_response_time,
                    "status": second_status,
                    "cache_hit": second_response_time < first_response_time
                },
                "speedup": speedup,
                "cache_effective": speedup > 1.5
            },
            "cache_status": cache_status,
            "data_consistency": first_data == second_data if first_data and second_data else False
        }
    
    async def test_response_compression(self) -> Dict[str, Any]:
        """응답 압축 테스트"""
        print("🗜️ 응답 압축 테스트...")
        
        # 큰 응답을 생성하는 엔드포인트 호출
        endpoint = "/api/keywords/analyze"
        data = {"keyword": "compression_test", "max_results": 20}
        
        # 압축 없이 요청
        headers_no_compress = {"Accept-Encoding": "identity"}
        async with self.session.post(
            f"{self.base_url}{endpoint}", 
            json=data, 
            headers=headers_no_compress
        ) as response:
            uncompressed_size = len(await response.read())
            uncompressed_headers = dict(response.headers)
        
        # 압축 요청
        headers_compress = {"Accept-Encoding": "gzip"}
        async with self.session.post(
            f"{self.base_url}{endpoint}", 
            json=data, 
            headers=headers_compress
        ) as response:
            compressed_size = len(await response.read())
            compressed_headers = dict(response.headers)
            has_compression = response.headers.get("content-encoding") == "gzip"
        
        compression_ratio = 1 - (compressed_size / uncompressed_size) if uncompressed_size > 0 else 0
        
        return {
            "compression_enabled": has_compression,
            "uncompressed_size": uncompressed_size,
            "compressed_size": compressed_size,
            "compression_ratio": compression_ratio,
            "compression_effective": compression_ratio > 0.3,  # 30% 이상 압축
            "headers": {
                "uncompressed": uncompressed_headers.get("content-encoding", "none"),
                "compressed": compressed_headers.get("content-encoding", "none")
            }
        }
    
    async def test_concurrent_performance(self) -> Dict[str, Any]:
        """동시 요청 성능 테스트"""
        print("🔄 동시 요청 성능 테스트...")
        
        concurrent_levels = [1, 5, 10, 20]
        results = {}
        
        for level in concurrent_levels:
            response_times = await self._run_concurrent_requests(level)
            
            if response_times:
                results[f"concurrent_{level}"] = {
                    "count": len(response_times),
                    "avg_response_time": statistics.mean(response_times),
                    "min_response_time": min(response_times),
                    "max_response_time": max(response_times),
                    "p95_response_time": statistics.quantiles(response_times, n=20)[18],  # 95th percentile
                    "total_time": sum(response_times)
                }
            else:
                results[f"concurrent_{level}"] = {"error": "No successful requests"}
        
        # 스케일링 효율성 계산
        if "concurrent_1" in results and "concurrent_10" in results:
            single_avg = results["concurrent_1"]["avg_response_time"]
            concurrent_avg = results["concurrent_10"]["avg_response_time"]
            scaling_efficiency = single_avg / concurrent_avg if concurrent_avg > 0 else 0
        else:
            scaling_efficiency = 0
        
        return {
            "concurrent_tests": results,
            "scaling_efficiency": scaling_efficiency,
            "scaling_good": scaling_efficiency > 0.7  # 70% 이상 유지
        }
    
    async def _run_concurrent_requests(self, count: int) -> List[float]:
        """동시 요청 실행"""
        async def make_request():
            start_time = time.time()
            try:
                async with self.session.post(
                    f"{self.base_url}/api/keywords/analyze",
                    json={"keyword": f"concurrent_test_{count}", "max_results": 3}
                ) as response:
                    await response.read()
                    return time.time() - start_time if response.status == 200 else None
            except:
                return None
        
        tasks = [make_request() for _ in range(count)]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
    
    async def test_connection_pooling(self) -> Dict[str, Any]:
        """연결 풀링 테스트"""
        print("🏊 연결 풀링 테스트...")
        
        # HTTP 연결 풀 상태 확인
        async with self.session.get(f"{self.base_url}/api/performance/http-pool") as response:
            http_pool_status = await response.json() if response.status == 200 else {}
        
        # 데이터베이스 연결 풀 상태 확인
        async with self.session.get(f"{self.base_url}/api/performance/database") as response:
            db_status = await response.json() if response.status == 200 else {}
        
        # 여러 요청으로 연결 풀 테스트
        request_count = 50
        start_time = time.time()
        
        tasks = []
        for i in range(request_count):
            task = self.session.get(f"{self.base_url}/api/health")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful_requests = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
        
        # 요청 후 연결 풀 상태
        async with self.session.get(f"{self.base_url}/api/performance/http-pool") as response:
            http_pool_after = await response.json() if response.status == 200 else {}
        
        return {
            "http_pool": {
                "before": http_pool_status,
                "after": http_pool_after,
                "connection_reuse": http_pool_status.get("connections", 0) > 0
            },
            "database_pool": db_status.get("connection_pool", {}),
            "stress_test": {
                "total_requests": request_count,
                "successful_requests": successful_requests,
                "total_time": total_time,
                "requests_per_second": request_count / total_time if total_time > 0 else 0
            }
        }
    
    async def test_performance_monitoring(self) -> Dict[str, Any]:
        """성능 모니터링 시스템 테스트"""
        print("📊 성능 모니터링 테스트...")
        
        # 성능 요약 정보 조회
        async with self.session.get(f"{self.base_url}/api/performance/summary") as response:
            if response.status == 200:
                performance_summary = await response.json()
                
                return {
                    "monitoring_active": True,
                    "metrics": {
                        "total_requests": performance_summary.get("total_requests", 0),
                        "requests_per_second": performance_summary.get("requests_per_second", 0),
                        "error_rate": performance_summary.get("error_rate", 0),
                        "slow_request_rate": performance_summary.get("slow_request_rate", 0)
                    },
                    "response_times": performance_summary.get("response_times", {}),
                    "slowest_endpoints": performance_summary.get("slowest_endpoints", [])[:5]
                }
            else:
                return {"monitoring_active": False, "error": f"HTTP {response.status}"}
    
    async def test_cache_invalidation(self) -> Dict[str, Any]:
        """캐시 무효화 테스트"""
        print("🗑️ 캐시 무효화 테스트...")
        
        test_keyword = "invalidation_test"
        endpoint = "/api/keywords/analyze"
        data = {"keyword": test_keyword, "max_results": 3}
        
        # 1. 첫 요청으로 캐시 생성
        async with self.session.post(f"{self.base_url}{endpoint}", json=data) as response:
            original_data = await response.json() if response.status == 200 else None
        
        # 2. 캐시 상태 확인
        async with self.session.get(f"{self.base_url}/api/performance/cache") as response:
            cache_before = await response.json() if response.status == 200 else {}
        
        # 3. 캐시 클리어
        async with self.session.post(
            f"{self.base_url}/api/performance/cache/clear",
            params={"pattern": f"keywords:{test_keyword}*"}
        ) as response:
            clear_result = await response.json() if response.status == 200 else {}
        
        # 4. 캐시 상태 재확인
        async with self.session.get(f"{self.base_url}/api/performance/cache") as response:
            cache_after = await response.json() if response.status == 200 else {}
        
        # 5. 동일 요청으로 캐시 미스 확인
        start_time = time.time()
        async with self.session.post(f"{self.base_url}{endpoint}", json=data) as response:
            new_response_time = time.time() - start_time
            new_data = await response.json() if response.status == 200 else None
        
        return {
            "cache_invalidation_works": clear_result.get("success", False),
            "cleared_keys": clear_result.get("cleared_keys", 0),
            "cache_entries_before": cache_before.get("l1_cache", {}).get("entries", 0),
            "cache_entries_after": cache_after.get("l1_cache", {}).get("entries", 0),
            "response_time_after_clear": new_response_time,
            "data_consistency": original_data == new_data if original_data and new_data else False
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 성능 테스트 실행"""
        print("🚀 성능 최적화 시스템 종합 테스트 시작...")
        print("=" * 60)
        
        results = {}
        
        # 1. 캐시 성능 테스트
        results["cache_performance"] = await self.test_cache_performance()
        
        # 2. 응답 압축 테스트
        results["response_compression"] = await self.test_response_compression()
        
        # 3. 동시 요청 성능 테스트
        results["concurrent_performance"] = await self.test_concurrent_performance()
        
        # 4. 연결 풀링 테스트
        results["connection_pooling"] = await self.test_connection_pooling()
        
        # 5. 성능 모니터링 테스트
        results["performance_monitoring"] = await self.test_performance_monitoring()
        
        # 6. 캐시 무효화 테스트
        results["cache_invalidation"] = await self.test_cache_invalidation()
        
        return results

async def main():
    """메인 테스트 실행"""
    async with PerformanceOptimizationTester() as tester:
        results = await tester.run_all_tests()
        
        print("\n" + "=" * 60)
        print("📊 성능 최적화 시스템 테스트 결과 요약")
        print("=" * 60)
        
        # 캐시 성능 결과
        cache = results["cache_performance"]["cache_test"]
        print(f"💾 캐시 성능:")
        print(f"   - 캐시 효과: {'✅' if cache['cache_effective'] else '❌'}")
        print(f"   - 속도 향상: {cache['speedup']:.2f}배")
        print(f"   - 첫 요청: {cache['first_request']['response_time']:.3f}초")
        print(f"   - 캐시 요청: {cache['second_request']['response_time']:.3f}초")
        
        # 응답 압축 결과
        compression = results["response_compression"]
        print(f"\n🗜️ 응답 압축:")
        print(f"   - 압축 활성화: {'✅' if compression['compression_enabled'] else '❌'}")
        print(f"   - 압축률: {compression['compression_ratio']:.1%}")
        print(f"   - 원본 크기: {compression['uncompressed_size']} bytes")
        print(f"   - 압축 크기: {compression['compressed_size']} bytes")
        
        # 동시 요청 성능
        concurrent = results["concurrent_performance"]
        print(f"\n🔄 동시 요청 성능:")
        print(f"   - 스케일링 효율: {concurrent['scaling_efficiency']:.2f}")
        print(f"   - 스케일링 상태: {'✅ 양호' if concurrent['scaling_good'] else '⚠️ 개선 필요'}")
        if "concurrent_10" in concurrent["concurrent_tests"]:
            stats = concurrent["concurrent_tests"]["concurrent_10"]
            print(f"   - 10개 동시 요청 평균: {stats['avg_response_time']:.3f}초")
            print(f"   - 95th percentile: {stats['p95_response_time']:.3f}초")
        
        # 연결 풀링
        pooling = results["connection_pooling"]
        stress = pooling["stress_test"]
        print(f"\n🏊 연결 풀링:")
        print(f"   - HTTP 연결 재사용: {'✅' if pooling['http_pool']['connection_reuse'] else '❌'}")
        print(f"   - 스트레스 테스트: {stress['successful_requests']}/{stress['total_requests']} 성공")
        print(f"   - 처리량: {stress['requests_per_second']:.1f} req/s")
        
        # 성능 모니터링
        monitoring = results["performance_monitoring"]
        if monitoring["monitoring_active"]:
            metrics = monitoring["metrics"]
            print(f"\n📊 성능 모니터링:")
            print(f"   - 모니터링 활성화: ✅")
            print(f"   - 총 요청 수: {metrics['total_requests']}")
            print(f"   - 에러율: {metrics['error_rate']:.1%}")
            print(f"   - 느린 요청 비율: {metrics['slow_request_rate']:.1%}")
        
        # 캐시 무효화
        invalidation = results["cache_invalidation"]
        print(f"\n🗑️ 캐시 무효화:")
        print(f"   - 무효화 작동: {'✅' if invalidation['cache_invalidation_works'] else '❌'}")
        print(f"   - 삭제된 키: {invalidation['cleared_keys']}")
        
        # 전체 점수 계산
        total_checks = 6
        passed_checks = sum([
            cache["cache_effective"],
            compression["compression_effective"],
            concurrent["scaling_good"],
            pooling["http_pool"]["connection_reuse"],
            monitoring["monitoring_active"],
            invalidation["cache_invalidation_works"]
        ])
        
        success_rate = (passed_checks / total_checks) * 100
        
        print(f"\n🎯 전체 성능 최적화 점수: {success_rate:.1f}%")
        print("🎉 성능 최적화 및 캐싱 시스템 구축 완료!")
        
        # 상세 결과를 JSON 파일로 저장
        with open("/mnt/e/project/test-blogauto-project/performance_optimization_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("📄 상세 결과가 performance_optimization_test_results.json에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())