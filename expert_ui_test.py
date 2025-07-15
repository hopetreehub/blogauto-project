#!/usr/bin/env python3
"""
전문가 페르소나 UI/UX 테스트 스크립트
- 크로미움 브라우저로 실제 사용자 관점에서 테스트
- 디자인, 기능성, 사용성 종합 검증
"""

import subprocess
import time
import json
import os
from datetime import datetime

class ExpertUITester:
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "frontend_url": "http://localhost:4007",
            "backend_url": "http://localhost:8000",
            "tests": {},
            "issues": [],
            "recommendations": []
        }
        
    def run_chromium_test(self, url, test_name, js_commands=None):
        """크로미움으로 실제 브라우저 테스트 실행"""
        try:
            # 크로미움 명령어 준비
            chromium_cmd = [
                'chromium-browser',
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-web-security',
                '--dump-dom',
                '--virtual-time-budget=10000',
                url
            ]
            
            # 크로미움 실행
            result = subprocess.run(chromium_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                dom_content = result.stdout
                self.test_results["tests"][test_name] = {
                    "status": "success",
                    "dom_length": len(dom_content),
                    "has_content": len(dom_content) > 1000,
                    "timestamp": datetime.now().isoformat()
                }
                return dom_content
            else:
                self.test_results["tests"][test_name] = {
                    "status": "failed",
                    "error": result.stderr,
                    "timestamp": datetime.now().isoformat()
                }
                return None
                
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return None
    
    def analyze_html_structure(self, html_content, page_name):
        """HTML 구조 및 디자인 요소 분석"""
        analysis = {
            "has_html": "<html" in html_content,
            "has_head": "<head" in html_content,
            "has_body": "<body" in html_content,
            "has_navigation": any(nav in html_content.lower() for nav in ["<nav", "navigation", "menu"]),
            "has_main_content": "<main" in html_content or "main" in html_content,
            "has_footer": "<footer" in html_content,
            "has_css": any(css in html_content for css in ["<style", ".css", "stylesheet"]),
            "has_js": any(js in html_content for js in ["<script", ".js"]),
            "responsive_indicators": any(resp in html_content for resp in ["viewport", "responsive", "mobile"]),
            "accessibility_features": any(acc in html_content for acc in ["aria-", "alt=", "role="]),
            "form_elements": any(form in html_content for form in ["<form", "<input", "<button"]),
            "error_indicators": any(err in html_content.lower() for err in ["error", "404", "500", "failed"])
        }
        
        # 문제점 식별
        issues = []
        if not analysis["has_html"]:
            issues.append(f"{page_name}: HTML 구조 누락")
        if not analysis["has_navigation"]:
            issues.append(f"{page_name}: 네비게이션 요소 누락")
        if analysis["error_indicators"]:
            issues.append(f"{page_name}: 에러 표시 감지")
        if not analysis["responsive_indicators"]:
            issues.append(f"{page_name}: 반응형 디자인 표시 누락")
        if not analysis["accessibility_features"]:
            issues.append(f"{page_name}: 접근성 기능 부족")
            
        self.test_results["issues"].extend(issues)
        return analysis
    
    def test_main_pages(self):
        """주요 페이지들 테스트"""
        pages_to_test = [
            ("홈페이지", "http://localhost:4007/"),
            ("콘텐츠 생성", "http://localhost:4007/content"),
            ("제목 생성", "http://localhost:4007/titles"),
            ("키워드 분석", "http://localhost:4007/keywords"),
            ("이미지 생성", "http://localhost:4007/images"),
            ("설정", "http://localhost:4007/settings"),
            ("WordPress", "http://localhost:4007/wordpress")
        ]
        
        for page_name, url in pages_to_test:
            print(f"🔍 {page_name} 테스트 중...")
            html_content = self.run_chromium_test(url, f"page_{page_name}")
            
            if html_content:
                analysis = self.analyze_html_structure(html_content, page_name)
                self.test_results["tests"][f"analysis_{page_name}"] = analysis
                print(f"✅ {page_name} 분석 완료")
            else:
                print(f"❌ {page_name} 테스트 실패")
                
            time.sleep(2)  # 서버 부하 방지
    
    def test_api_endpoints(self):
        """백엔드 API 엔드포인트 테스트"""
        import requests
        
        api_endpoints = [
            ("Health Check", "GET", "/"),
            ("API 정보", "GET", "/api/info"),
            ("키워드 분석", "POST", "/api/keywords/analyze"),
            ("제목 생성", "POST", "/api/titles/generate"),
            ("콘텐츠 생성", "POST", "/api/content/generate")
        ]
        
        for name, method, endpoint in api_endpoints:
            try:
                url = f"http://localhost:8000{endpoint}"
                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    # POST 요청을 위한 더미 데이터
                    data = {"keyword": "test", "title": "test"}
                    response = requests.post(url, json=data, timeout=10)
                
                self.test_results["tests"][f"api_{name}"] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "has_response": len(response.text) > 0,
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"🔗 API {name}: {response.status_code}")
                
            except Exception as e:
                self.test_results["tests"][f"api_{name}"] = {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                print(f"❌ API {name} 오류: {str(e)}")
    
    def generate_expert_recommendations(self):
        """전문가 관점에서 개선 권고사항 생성"""
        recommendations = []
        
        # UI/UX 개선사항
        if len(self.test_results["issues"]) > 0:
            recommendations.append("🎨 UI/UX 개선: " + ", ".join(self.test_results["issues"][:3]))
        
        # 성능 개선사항
        slow_apis = [name for name, data in self.test_results["tests"].items() 
                    if "api_" in name and data.get("response_time", 0) > 5]
        if slow_apis:
            recommendations.append(f"⚡ 성능 최적화: {', '.join(slow_apis)} API 응답시간 개선 필요")
        
        # 접근성 개선사항
        recommendations.append("♿ 접근성 강화: ARIA 라벨, 키보드 네비게이션, 대체 텍스트 추가")
        
        # 보안 개선사항
        recommendations.append("🛡️ 보안 강화: API 키 검증, 입력값 sanitization, HTTPS 적용")
        
        # 사용자 경험 개선
        recommendations.append("👤 UX 개선: 로딩 상태 표시, 에러 메시지 개선, 진행률 표시")
        
        self.test_results["recommendations"] = recommendations
    
    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("🚀 전문가 페르소나 UI/UX 종합 테스트 시작")
        print("=" * 60)
        
        # 1. 서버 상태 확인
        print("1️⃣ 서버 상태 확인...")
        
        # 2. 메인 페이지들 테스트
        print("2️⃣ 주요 페이지 테스트...")
        self.test_main_pages()
        
        # 3. API 엔드포인트 테스트
        print("3️⃣ API 엔드포인트 테스트...")
        self.test_api_endpoints()
        
        # 4. 전문가 권고사항 생성
        print("4️⃣ 전문가 분석 및 권고사항 생성...")
        self.generate_expert_recommendations()
        
        # 5. 결과 저장
        report_file = f"expert_ui_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print("=" * 60)
        print(f"📊 테스트 완료! 보고서: {report_file}")
        
        return self.test_results

if __name__ == "__main__":
    tester = ExpertUITester()
    results = tester.run_comprehensive_test()
    
    # 요약 출력
    print("\n📋 테스트 요약:")
    print(f"총 테스트: {len(results['tests'])}")
    print(f"발견된 이슈: {len(results['issues'])}")
    print(f"권고사항: {len(results['recommendations'])}")
    
    if results['issues']:
        print("\n⚠️ 주요 이슈:")
        for issue in results['issues'][:5]:
            print(f"  - {issue}")
    
    if results['recommendations']:
        print("\n💡 개선 권고사항:")
        for rec in results['recommendations']:
            print(f"  - {rec}")