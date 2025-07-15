#!/usr/bin/env python3
"""
Playwright를 사용한 전체 성능 검증
- 실제 브라우저에서 사용자 시나리오 테스트
- 페이지 로딩 시간 측정
- WordPress 포스팅 워크플로우 테스트
"""

import asyncio
import time
import json
from datetime import datetime
from playwright.async_api import async_playwright
import statistics

class PlaywrightPerformanceTester:
    def __init__(self):
        self.base_url = "http://localhost:5002"  # 프론트엔드 URL
        self.api_url = "http://localhost:8000"   # 백엔드 API URL
        self.results = {
            "page_load_times": [],
            "api_response_times": [],
            "workflow_times": {},
            "errors": []
        }
        
    async def measure_page_load(self, page, url, name):
        """페이지 로딩 시간 측정"""
        start_time = time.time()
        
        try:
            await page.goto(url, wait_until='networkidle')
            load_time = (time.time() - start_time) * 1000
            
            # JavaScript 실행 시간 측정
            js_metrics = await page.evaluate("""() => {
                const perfData = window.performance.timing;
                return {
                    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart,
                    loadComplete: perfData.loadEventEnd - perfData.navigationStart,
                    firstPaint: perfData.responseEnd - perfData.navigationStart
                };
            }""")
            
            result = {
                "name": name,
                "url": url,
                "total_load_time_ms": round(load_time, 2),
                "dom_content_loaded_ms": js_metrics.get('domContentLoaded', 0),
                "load_complete_ms": js_metrics.get('loadComplete', 0),
                "first_paint_ms": js_metrics.get('firstPaint', 0),
                "timestamp": datetime.now().isoformat()
            }
            
            self.results["page_load_times"].append(result)
            return result
            
        except Exception as e:
            error = {
                "name": name,
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["errors"].append(error)
            return None
    
    async def test_wordpress_posting_workflow(self, page):
        """WordPress 포스팅 전체 워크플로우 테스트"""
        workflow_start = time.time()
        steps = {}
        
        try:
            # 1. 로그인 페이지 이동
            step_start = time.time()
            await page.goto(f"{self.base_url}/login", wait_until='networkidle')
            steps["navigate_to_login"] = (time.time() - step_start) * 1000
            
            # 2. 로그인 수행
            step_start = time.time()
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin123')
            await page.click('button[type="submit"]')
            await page.wait_for_navigation()
            steps["login"] = (time.time() - step_start) * 1000
            
            # 3. 콘텐츠 생성 페이지로 이동
            step_start = time.time()
            await page.goto(f"{self.base_url}/content", wait_until='networkidle')
            steps["navigate_to_content"] = (time.time() - step_start) * 1000
            
            # 4. 키워드 입력 및 제목 생성
            step_start = time.time()
            await page.fill('input[placeholder*="키워드"]', '성능 테스트')
            await page.click('button:has-text("제목 생성")')
            await page.wait_for_selector('.title-suggestions', timeout=30000)
            steps["generate_titles"] = (time.time() - step_start) * 1000
            
            # 5. 제목 선택 및 콘텐츠 생성
            step_start = time.time()
            await page.click('.title-suggestions li:first-child')
            await page.click('button:has-text("콘텐츠 생성")')
            await page.wait_for_selector('.generated-content', timeout=60000)
            steps["generate_content"] = (time.time() - step_start) * 1000
            
            # 6. WordPress 발행
            step_start = time.time()
            await page.click('button:has-text("WordPress 발행")')
            await page.wait_for_selector('.publish-success', timeout=30000)
            steps["publish_to_wordpress"] = (time.time() - step_start) * 1000
            
            total_time = (time.time() - workflow_start) * 1000
            
            self.results["workflow_times"] = {
                "steps": steps,
                "total_time_ms": round(total_time, 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.results["errors"].append({
                "workflow": "wordpress_posting",
                "error": str(e),
                "completed_steps": list(steps.keys()),
                "timestamp": datetime.now().isoformat()
            })
    
    async def test_api_performance(self, page):
        """API 직접 호출 성능 테스트"""
        api_tests = []
        
        # API 호출 테스트
        endpoints = [
            ("/api/health", "GET"),
            ("/api/keywords/analyze", "POST", {"keyword": "테스트", "country": "KR"}),
            ("/api/titles/generate", "POST", {"keyword": "테스트", "count": 5}),
        ]
        
        for endpoint_data in endpoints:
            endpoint = endpoint_data[0]
            method = endpoint_data[1]
            data = endpoint_data[2] if len(endpoint_data) > 2 else None
            
            # JavaScript에서 fetch 호출
            start_time = time.time()
            
            js_code = f"""
                async () => {{
                    const start = performance.now();
                    try {{
                        const response = await fetch('{self.api_url}{endpoint}', {{
                            method: '{method}',
                            headers: {{'Content-Type': 'application/json'}},
                            body: {json.dumps(data) if data else 'null'}
                        }});
                        const end = performance.now();
                        return {{
                            status: response.status,
                            time: end - start,
                            ok: response.ok
                        }};
                    }} catch (error) {{
                        return {{
                            error: error.message,
                            time: performance.now() - start
                        }};
                    }}
                }}
            """
            
            result = await page.evaluate(js_code)
            
            api_tests.append({
                "endpoint": endpoint,
                "method": method,
                "response_time_ms": round(result.get('time', 0), 2),
                "status": result.get('status', 'error'),
                "timestamp": datetime.now().isoformat()
            })
        
        self.results["api_response_times"] = api_tests
    
    async def run_tests(self):
        """전체 테스트 실행"""
        print("🎭 Playwright 성능 테스트 시작...")
        print("=" * 60)
        
        async with async_playwright() as p:
            # 브라우저 시작 (headless 모드)
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            
            try:
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    locale='ko-KR'
                )
                
                page = await context.new_page()
                
                # 네트워크 모니터링 활성화
                await page.route('**/*', lambda route: route.continue_())
                
                # 1. 페이지 로딩 성능 테스트
                print("\n📄 페이지 로딩 성능 테스트...")
                pages_to_test = [
                    (f"{self.base_url}/", "홈페이지"),
                    (f"{self.base_url}/login", "로그인 페이지"),
                    (f"{self.base_url}/dashboard", "대시보드"),
                    (f"{self.base_url}/content", "콘텐츠 생성"),
                    (f"{self.base_url}/wordpress", "WordPress 관리")
                ]
                
                for url, name in pages_to_test:
                    result = await self.measure_page_load(page, url, name)
                    if result:
                        print(f"  {name}: {result['total_load_time_ms']}ms")
                
                # 2. API 성능 테스트
                print("\n🔌 API 성능 테스트...")
                await self.test_api_performance(page)
                for api_test in self.results["api_response_times"]:
                    print(f"  {api_test['method']} {api_test['endpoint']}: {api_test['response_time_ms']}ms")
                
                # 3. WordPress 포스팅 워크플로우 테스트
                print("\n📝 WordPress 포스팅 워크플로우 테스트...")
                await self.test_wordpress_posting_workflow(page)
                if "steps" in self.results["workflow_times"]:
                    for step, time_ms in self.results["workflow_times"]["steps"].items():
                        print(f"  {step}: {time_ms:.2f}ms")
                
            finally:
                await browser.close()
        
        # 결과 저장
        self.save_results()
        self.print_summary()
    
    def save_results(self):
        """테스트 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"playwright_performance_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 결과가 {filename}에 저장되었습니다.")
    
    def print_summary(self):
        """테스트 결과 요약"""
        print("\n" + "=" * 60)
        print("📊 성능 테스트 요약")
        print("=" * 60)
        
        # 페이지 로딩 성능
        if self.results["page_load_times"]:
            load_times = [p["total_load_time_ms"] for p in self.results["page_load_times"]]
            print(f"\n📄 페이지 로딩 시간:")
            print(f"  평균: {statistics.mean(load_times):.2f}ms")
            print(f"  최소: {min(load_times):.2f}ms")
            print(f"  최대: {max(load_times):.2f}ms")
            
            # 가장 느린 페이지
            slowest = max(self.results["page_load_times"], key=lambda x: x["total_load_time_ms"])
            print(f"  가장 느린 페이지: {slowest['name']} ({slowest['total_load_time_ms']}ms)")
        
        # API 응답 시간
        if self.results["api_response_times"]:
            api_times = [a["response_time_ms"] for a in self.results["api_response_times"]]
            print(f"\n🔌 API 응답 시간:")
            print(f"  평균: {statistics.mean(api_times):.2f}ms")
            print(f"  최소: {min(api_times):.2f}ms")
            print(f"  최대: {max(api_times):.2f}ms")
        
        # 워크플로우 성능
        if "total_time_ms" in self.results["workflow_times"]:
            print(f"\n📝 WordPress 포스팅 워크플로우:")
            print(f"  전체 시간: {self.results['workflow_times']['total_time_ms']:.2f}ms")
            
            if "steps" in self.results["workflow_times"]:
                slowest_step = max(
                    self.results["workflow_times"]["steps"].items(),
                    key=lambda x: x[1]
                )
                print(f"  가장 느린 단계: {slowest_step[0]} ({slowest_step[1]:.2f}ms)")
        
        # 에러 요약
        if self.results["errors"]:
            print(f"\n❌ 에러 발생: {len(self.results['errors'])}건")
            for error in self.results["errors"]:
                print(f"  - {error.get('name', error.get('workflow', 'Unknown'))}: {error.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)


async def main():
    tester = PlaywrightPerformanceTester()
    await tester.run_tests()


if __name__ == "__main__":
    asyncio.run(main())