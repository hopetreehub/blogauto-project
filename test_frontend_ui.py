#!/usr/bin/env python3
"""
프론트엔드 UI 테스트 - Playwright 기반
전체 사용자 워크플로우 테스트
"""

import asyncio
from playwright.async_api import async_playwright
import json
import time

class FrontendUITester:
    def __init__(self, base_url="http://localhost:6001", api_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_url = api_url
        self.test_results = []
    
    async def run_all_tests(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                print("🎭 Playwright UI 테스트 시작...")
                
                # 1. 메인 페이지 테스트
                await self.test_main_page(page)
                
                # 2. 대시보드 테스트
                await self.test_dashboard(page)
                
                # 3. 키워드 분석 페이지 테스트
                await self.test_keywords_page(page)
                
                # 4. 제목 생성 페이지 테스트
                await self.test_titles_page(page)
                
                # 5. 콘텐츠 생성 페이지 테스트
                await self.test_content_page(page)
                
                # 6. 설정 페이지 테스트
                await self.test_settings_page(page)
                
                # 7. 지침 관리 페이지 테스트
                await self.test_guidelines_page(page)
                
                # 8. SEO 분석 페이지 테스트
                await self.test_seo_page(page)
                
                print("\n📊 UI 테스트 결과 요약:")
                self.print_results()
                
            except Exception as e:
                print(f"❌ 테스트 실행 중 오류: {e}")
                
            finally:
                await browser.close()
    
    async def test_main_page(self, page):
        """메인 페이지 테스트"""
        try:
            print("🏠 메인 페이지 테스트 중...")
            await page.goto(self.base_url, wait_until="networkidle")
            
            # 페이지 타이틀 확인
            title = await page.title()
            assert "블로그 자동화" in title
            
            # 주요 텍스트 확인
            main_heading = await page.locator('h1').first.text_content()
            assert "블로그 자동화" in main_heading
            
            # 시작하기 버튼 확인
            start_button = page.locator('a[href="/dashboard"]')
            assert await start_button.is_visible()
            
            # 기능 카드들 확인
            feature_cards = page.locator('[class*="grid"] > div')
            count = await feature_cards.count()
            assert count >= 4  # 키워드분석, 제목생성, 콘텐츠생성, 자동포스팅
            
            self.test_results.append({
                "test": "메인 페이지",
                "status": "✅ 통과",
                "details": f"타이틀: {title}, 기능 카드: {count}개"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "메인 페이지",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    async def test_dashboard(self, page):
        """대시보드 테스트"""
        try:
            print("📊 대시보드 테스트 중...")
            await page.goto(f"{self.base_url}/dashboard", wait_until="networkidle")
            
            # 네비게이션 메뉴 확인
            nav_links = page.locator('nav a')
            nav_count = await nav_links.count()
            assert nav_count >= 6  # 주요 메뉴들
            
            # 통계 카드들 확인
            stats_cards = page.locator('[class*="bg-white"][class*="shadow"]')
            stats_count = await stats_cards.count()
            
            self.test_results.append({
                "test": "대시보드",
                "status": "✅ 통과",
                "details": f"네비게이션 메뉴: {nav_count}개, 통계 카드: {stats_count}개"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "대시보드",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    async def test_keywords_page(self, page):
        """키워드 분석 페이지 테스트"""
        try:
            print("🔍 키워드 분석 페이지 테스트 중...")
            await page.goto(f"{self.base_url}/keywords", wait_until="networkidle")
            
            # 키워드 입력 필드 확인
            keyword_input = page.locator('input[placeholder*="키워드"]')
            assert await keyword_input.is_visible()
            
            # 국가 선택 드롭다운 확인
            country_select = page.locator('select')
            assert await country_select.is_visible()
            
            # 분석 버튼 확인
            analyze_button = page.locator('button:has-text("분석")')
            assert await analyze_button.is_visible()
            
            # 테스트 키워드로 분석 시도
            await keyword_input.fill("블로그 글쓰기")
            await analyze_button.click()
            
            # 결과 로딩 기다리기
            await page.wait_for_timeout(3000)
            
            self.test_results.append({
                "test": "키워드 분석",
                "status": "✅ 통과",
                "details": "입력 필드, 선택박스, 버튼 정상 동작"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "키워드 분석",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    async def test_titles_page(self, page):
        """제목 생성 페이지 테스트"""
        try:
            print("✍️ 제목 생성 페이지 테스트 중...")
            await page.goto(f"{self.base_url}/titles", wait_until="networkidle")
            
            # 키워드 입력 필드 확인
            keyword_input = page.locator('input[placeholder*="키워드"]')
            assert await keyword_input.is_visible()
            
            # 생성 개수 설정 확인
            count_input = page.locator('input[type="number"]')
            assert await count_input.is_visible()
            
            # 생성 버튼 확인
            generate_button = page.locator('button:has-text("생성")')
            assert await generate_button.is_visible()
            
            # 테스트 제목 생성
            await keyword_input.fill("AI 블로그 작성법")
            await generate_button.click()
            
            # 결과 로딩 기다리기
            await page.wait_for_timeout(3000)
            
            self.test_results.append({
                "test": "제목 생성",
                "status": "✅ 통과",
                "details": "입력 필드, 설정 옵션, 생성 버튼 정상 동작"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "제목 생성",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    async def test_content_page(self, page):
        """콘텐츠 생성 페이지 테스트"""
        try:
            print("📝 콘텐츠 생성 페이지 테스트 중...")
            await page.goto(f"{self.base_url}/content", wait_until="networkidle")
            
            # 제목 입력 필드 확인
            title_input = page.locator('input[placeholder*="제목"]')
            assert await title_input.is_visible()
            
            # 지침 보기 버튼 확인
            guidelines_button = page.locator('button:has-text("지침")')
            if await guidelines_button.is_visible():
                await guidelines_button.click()
                await page.wait_for_timeout(1000)
            
            # 생성 버튼 확인
            generate_button = page.locator('button:has-text("생성")')
            assert await generate_button.is_visible()
            
            self.test_results.append({
                "test": "콘텐츠 생성",
                "status": "✅ 통과",
                "details": "제목 입력, 지침 확인, 생성 기능 접근 가능"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "콘텐츠 생성",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    async def test_settings_page(self, page):
        """설정 페이지 테스트"""
        try:
            print("⚙️ 설정 페이지 테스트 중...")
            await page.goto(f"{self.base_url}/settings", wait_until="networkidle")
            
            # API 키 입력 필드들 확인
            api_inputs = page.locator('input[type="password"], input[placeholder*="API"]')
            input_count = await api_inputs.count()
            assert input_count >= 1  # 최소 OpenAI API 키 입력
            
            # 저장 버튼 확인
            save_button = page.locator('button:has-text("저장")')
            assert await save_button.is_visible()
            
            self.test_results.append({
                "test": "설정 페이지",
                "status": "✅ 통과",
                "details": f"API 키 입력 필드 {input_count}개, 저장 기능 확인"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "설정 페이지",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    async def test_guidelines_page(self, page):
        """지침 관리 페이지 테스트"""
        try:
            print("📋 지침 관리 페이지 테스트 중...")
            await page.goto(f"{self.base_url}/guidelines", wait_until="networkidle")
            
            # 지침 카테고리 확인
            guideline_sections = page.locator('h3, h2')
            section_count = await guideline_sections.count()
            
            # 텍스트 영역 확인
            textareas = page.locator('textarea')
            textarea_count = await textareas.count()
            assert textarea_count >= 3  # 키워드, 제목, 콘텐츠 지침
            
            self.test_results.append({
                "test": "지침 관리",
                "status": "✅ 통과",
                "details": f"지침 섹션 {section_count}개, 텍스트 영역 {textarea_count}개"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "지침 관리",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    async def test_seo_page(self, page):
        """SEO 분석 페이지 테스트"""
        try:
            print("📈 SEO 분석 페이지 테스트 중...")
            await page.goto(f"{self.base_url}/seo", wait_until="networkidle")
            
            # 페이지 로딩 확인
            page_content = await page.content()
            assert len(page_content) > 1000  # 기본적인 컨텐츠 존재
            
            self.test_results.append({
                "test": "SEO 분석",
                "status": "✅ 통과",
                "details": "페이지 로딩 및 컨텐츠 확인"
            })
            
        except Exception as e:
            self.test_results.append({
                "test": "SEO 분석",
                "status": "❌ 실패",
                "details": str(e)
            })
    
    def print_results(self):
        """테스트 결과 출력"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if "✅" in result["status"])
        
        print(f"\n{'='*60}")
        print(f"📊 UI 테스트 결과: {passed_tests}/{total_tests} 통과")
        print(f"{'='*60}")
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            print(f"   세부사항: {result['details']}")
            print()
        
        print(f"✨ 전체 성공률: {passed_tests/total_tests*100:.1f}%")

async def main():
    """메인 실행 함수"""
    print("🚀 BlogAuto 프론트엔드 UI 테스트 시작")
    print("=" * 60)
    
    # 서버 상태 확인
    import requests
    try:
        response = requests.get("http://localhost:6001", timeout=5)
        print(f"✅ 프론트엔드 서버 응답: {response.status_code}")
    except:
        print("❌ 프론트엔드 서버에 연결할 수 없습니다. 서버를 먼저 시작해주세요.")
        return
    
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"✅ 백엔드 API 응답: {response.status_code}")
    except:
        print("❌ 백엔드 API에 연결할 수 없습니다.")
        return
    
    print()
    
    # UI 테스트 실행
    tester = FrontendUITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())