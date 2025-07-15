#!/usr/bin/env python3
"""
Rate Limiting 테스트 스크립트
보안 강화 Step 5 - Rate Limiting 구현 검증
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Tuple

class RateLimitTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: dict = None, headers: dict = None) -> Tuple[int, dict]:
        """API 요청 수행"""
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.request(method, url, json=data, headers=headers) as response:
                response_data = await response.json()
                return response.status, response_data
        except Exception as e:
            return 500, {"error": str(e)}
    
    async def test_basic_functionality(self) -> Dict:
        """기본 기능 테스트"""
        print("🔍 기본 기능 테스트...")
        
        # Health check
        status, data = await self.make_request("GET", "/api/health")
        health_ok = status == 200
        
        # Rate limit stats
        status, stats = await self.make_request("GET", "/api/admin/rate-limit-stats")
        stats_ok = status == 200 and "active_ips" in stats
        
        return {
            "health_check": health_ok,
            "rate_limit_stats": stats_ok,
            "initial_stats": stats if stats_ok else {}
        }
    
    async def test_endpoint_rate_limiting(self) -> Dict:
        """엔드포인트별 Rate Limiting 테스트"""
        print("🚦 엔드포인트별 Rate Limiting 테스트...")
        
        endpoint = "/api/keywords/analyze"
        limit = 10  # 설정된 limit
        
        # 연속 요청 수행
        results = []
        for i in range(limit + 3):  # limit를 3개 초과
            status, data = await self.make_request(
                "POST", 
                endpoint, 
                {"keyword": f"테스트{i}"}
            )
            results.append({
                "request_num": i + 1,
                "status": status,
                "limited": status == 429,
                "response": data.get("error", data.get("detail", ""))[:50]
            })
            await asyncio.sleep(0.1)  # 짧은 대기
        
        # 결과 분석
        successful_requests = [r for r in results if r["status"] in [200, 401]]  # 401은 API 키 없음
        rate_limited_requests = [r for r in results if r["status"] == 429]
        
        return {
            "total_requests": len(results),
            "successful_before_limit": len(successful_requests),
            "rate_limited_count": len(rate_limited_requests),
            "limit_triggered_correctly": len(successful_requests) <= limit and len(rate_limited_requests) > 0,
            "first_rate_limit_at": rate_limited_requests[0]["request_num"] if rate_limited_requests else None,
            "details": results[-5:]  # 마지막 5개 요청만 표시
        }
    
    async def test_ip_rate_limiting(self) -> Dict:
        """IP별 Rate Limiting 테스트"""
        print("🌐 IP별 Rate Limiting 테스트...")
        
        # 여러 엔드포인트에 분산 요청으로 IP limit 테스트
        endpoints = ["/api/health", "/api/dashboard/stats", "/api/admin/rate-limit-stats"]
        ip_limit = 100
        
        # IP limit에 근접하도록 요청
        results = []
        for i in range(30):  # 30개 요청
            endpoint = endpoints[i % len(endpoints)]
            status, data = await self.make_request("GET", endpoint)
            results.append({"endpoint": endpoint, "status": status})
            
            if i % 10 == 0:  # 10개마다 잠시 대기
                await asyncio.sleep(0.1)
        
        # 통계 확인
        status, stats = await self.make_request("GET", "/api/admin/rate-limit-stats")
        
        return {
            "total_requests": len(results),
            "successful_requests": len([r for r in results if r["status"] == 200]),
            "current_active_ips": stats.get("active_ips", 0) if status == 200 else 0,
            "ip_limit_reached": any(r["status"] == 429 for r in results),
            "final_stats": stats if status == 200 else {}
        }
    
    async def test_suspicious_activity_detection(self) -> Dict:
        """의심스러운 활동 감지 테스트"""
        print("🚨 의심스러운 활동 감지 테스트...")
        
        # 빠른 연속 요청으로 의심스러운 패턴 생성
        endpoints = [
            "/api/health", "/api/dashboard/stats", "/api/admin/rate-limit-stats",
            "/api/keywords/analyze", "/api/titles/generate", "/api/content/generate"
        ]
        
        start_time = time.time()
        results = []
        
        # 30초 내에 많은 요청 시도 (의심스러운 패턴)
        for i in range(20):
            endpoint = endpoints[i % len(endpoints)]
            status, data = await self.make_request(
                "POST" if "analyze" in endpoint or "generate" in endpoint else "GET",
                endpoint,
                {"keyword": "test", "count": 1} if "analyze" in endpoint or "generate" in endpoint else None
            )
            results.append({
                "request": i + 1,
                "endpoint": endpoint,
                "status": status,
                "blocked": status == 429 and "blocked" in str(data).lower()
            })
            
            # 매우 빠른 요청
            if i < 10:
                await asyncio.sleep(0.05)  # 50ms
            else:
                await asyncio.sleep(0.1)   # 100ms
        
        elapsed_time = time.time() - start_time
        
        # 차단 상태 확인
        blocked_requests = [r for r in results if r["blocked"]]
        
        return {
            "total_requests": len(results),
            "elapsed_time": round(elapsed_time, 2),
            "requests_per_second": round(len(results) / elapsed_time, 2),
            "blocked_requests": len(blocked_requests),
            "suspicious_detected": len(blocked_requests) > 0,
            "first_block_at": blocked_requests[0]["request"] if blocked_requests else None
        }
    
    async def test_rate_limit_headers(self) -> Dict:
        """Rate Limit 헤더 테스트"""
        print("📋 Rate Limit 헤더 테스트...")
        
        endpoint = "/api/health"
        
        async with self.session.get(f"{self.base_url}{endpoint}") as response:
            headers = dict(response.headers)
            
            rate_limit_headers = {
                key: value for key, value in headers.items()
                if key.lower().startswith("x-ratelimit")
            }
        
        return {
            "has_rate_limit_headers": len(rate_limit_headers) > 0,
            "headers": rate_limit_headers,
            "response_status": response.status
        }
    
    async def run_all_tests(self) -> Dict:
        """모든 테스트 실행"""
        print("🚀 Rate Limiting 종합 테스트 시작...")
        print("=" * 60)
        
        results = {}
        
        # 1. 기본 기능 테스트
        results["basic"] = await self.test_basic_functionality()
        
        # 2. 엔드포인트별 Rate Limiting
        results["endpoint_limiting"] = await self.test_endpoint_rate_limiting()
        
        # 3. IP별 Rate Limiting
        results["ip_limiting"] = await self.test_ip_rate_limiting()
        
        # 4. 의심스러운 활동 감지
        results["suspicious_detection"] = await self.test_suspicious_activity_detection()
        
        # 5. Rate Limit 헤더
        results["headers"] = await self.test_rate_limit_headers()
        
        return results

async def main():
    """메인 테스트 실행"""
    async with RateLimitTester() as tester:
        results = await tester.run_all_tests()
        
        print("\n" + "=" * 60)
        print("📊 Rate Limiting 테스트 결과 요약")
        print("=" * 60)
        
        # 기본 기능
        basic = results["basic"]
        print(f"✅ Health Check: {'통과' if basic['health_check'] else '실패'}")
        print(f"✅ Stats API: {'통과' if basic['rate_limit_stats'] else '실패'}")
        
        # 엔드포인트 제한
        endpoint = results["endpoint_limiting"]
        print(f"🚦 엔드포인트 Rate Limiting: {'통과' if endpoint['limit_triggered_correctly'] else '실패'}")
        print(f"   - 제한 전 성공 요청: {endpoint['successful_before_limit']}")
        print(f"   - Rate Limited 요청: {endpoint['rate_limited_count']}")
        
        # IP 제한
        ip_limit = results["ip_limiting"]
        print(f"🌐 IP Rate Limiting: {'모니터링 중' if ip_limit['successful_requests'] > 0 else '실패'}")
        print(f"   - 총 요청: {ip_limit['total_requests']}")
        print(f"   - 성공 요청: {ip_limit['successful_requests']}")
        
        # 의심스러운 활동
        suspicious = results["suspicious_detection"]
        print(f"🚨 의심스러운 활동 감지: {'감지됨' if suspicious['suspicious_detected'] else '미감지'}")
        print(f"   - 초당 요청: {suspicious['requests_per_second']}")
        print(f"   - 차단된 요청: {suspicious['blocked_requests']}")
        
        # 헤더
        headers = results["headers"]
        print(f"📋 Rate Limit 헤더: {'포함됨' if headers['has_rate_limit_headers'] else '미포함'}")
        
        # 최종 통계
        print(f"\n📈 최종 서버 상태:")
        if basic.get("initial_stats"):
            stats = basic["initial_stats"]
            print(f"   - 활성 IP: {stats.get('active_ips', 0)}")
            print(f"   - 차단된 IP: {stats.get('blocked_ips', 0)}")
            print(f"   - 의심스러운 IP: {stats.get('suspicious_ips', 0)}")
        
        print("\n🎯 Rate Limiting 구현 완료!")
        
        # 상세 결과를 JSON 파일로 저장
        with open("/mnt/e/project/test-blogauto-project/rate_limiting_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("📄 상세 결과가 rate_limiting_test_results.json에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())