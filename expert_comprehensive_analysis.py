#!/usr/bin/env python3
"""
전문가 페르소나 종합 시스템 분석 보고서
- 실제 프로덕션 환경 관점에서 분석
- UI/UX, 기능성, 보안, 성능 종합 평가
"""

import json
import re
import time
from datetime import datetime
import requests
import subprocess

class ExpertSystemAnalyzer:
    def __init__(self):
        self.analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_version": "Expert Level 2.0",
            "system_status": {},
            "ui_ux_analysis": {},
            "backend_analysis": {},
            "security_analysis": {},
            "performance_analysis": {},
            "critical_issues": [],
            "recommendations": {},
            "scores": {}
        }
    
    def analyze_html_structure(self, html_content):
        """HTML 구조 상세 분석"""
        analysis = {
            "structure_quality": 0,
            "design_elements": {},
            "accessibility": {},
            "responsive_design": {},
            "issues": []
        }
        
        # 기본 HTML 구조 확인
        if all(tag in html_content for tag in ["<html", "<head", "<body"]):
            analysis["structure_quality"] += 20
        else:
            analysis["issues"].append("기본 HTML 구조 불완전")
        
        # 메타데이터 분석
        meta_tags = len(re.findall(r'<meta[^>]*>', html_content))
        if meta_tags >= 3:
            analysis["structure_quality"] += 15
        
        # CSS 프레임워크 감지
        if "tailwind" in html_content.lower():
            analysis["design_elements"]["css_framework"] = "Tailwind CSS"
            analysis["structure_quality"] += 20
        
        # 반응형 디자인 요소
        responsive_classes = ["sm:", "md:", "lg:", "xl:", "responsive"]
        responsive_count = sum(1 for cls in responsive_classes if cls in html_content)
        if responsive_count > 5:
            analysis["responsive_design"]["quality"] = "Good"
            analysis["structure_quality"] += 15
        
        # 접근성 기능
        accessibility_features = ["aria-", "alt=", "role=", "tabindex"]
        accessibility_count = sum(1 for feature in accessibility_features if feature in html_content)
        analysis["accessibility"]["features_count"] = accessibility_count
        if accessibility_count > 0:
            analysis["structure_quality"] += 10
        
        # 네비게이션 구조
        if any(nav in html_content.lower() for nav in ["<nav", "navigation", "sidebar"]):
            analysis["design_elements"]["navigation"] = "Present"
            analysis["structure_quality"] += 10
        else:
            analysis["issues"].append("명확한 네비게이션 구조 부족")
        
        # 시맨틱 HTML
        semantic_tags = ["<main", "<header", "<footer", "<section", "<article"]
        semantic_count = sum(1 for tag in semantic_tags if tag in html_content)
        analysis["design_elements"]["semantic_score"] = semantic_count
        if semantic_count >= 2:
            analysis["structure_quality"] += 10
        
        return analysis
    
    def analyze_ui_components(self, html_content):
        """UI 컴포넌트 및 디자인 패턴 분석"""
        components = {
            "buttons": len(re.findall(r'<button[^>]*>', html_content)),
            "forms": len(re.findall(r'<form[^>]*>', html_content)),
            "inputs": len(re.findall(r'<input[^>]*>', html_content)),
            "modals": len(re.findall(r'modal', html_content, re.IGNORECASE)),
            "cards": len(re.findall(r'card', html_content, re.IGNORECASE)),
            "icons": len(re.findall(r'[🔍✍️📝🎨🚀📊💾📈⚡📡📋🤖⚙️]', html_content))
        }
        
        design_patterns = {
            "grid_layout": "grid" in html_content,
            "flexbox": "flex" in html_content,
            "animations": "animate" in html_content or "transition" in html_content,
            "hover_effects": "hover:" in html_content,
            "responsive_text": any(size in html_content for size in ["text-sm", "text-lg", "text-xl"])
        }
        
        return {
            "components": components,
            "design_patterns": design_patterns,
            "ui_complexity": "High" if sum(components.values()) > 10 else "Medium"
        }
    
    def test_backend_apis(self):
        """백엔드 API 종합 테스트"""
        api_tests = {
            "health_check": {"url": "/", "method": "GET"},
            "swagger_docs": {"url": "/docs", "method": "GET"},
            "api_info": {"url": "/api/info", "method": "GET"},
            "keywords_analyze": {"url": "/api/keywords/analyze", "method": "POST"},
            "titles_generate": {"url": "/api/titles/generate", "method": "POST"},
            "content_generate": {"url": "/api/content/generate", "method": "POST"}
        }
        
        results = {}
        base_url = "http://localhost:8000"
        
        for test_name, config in api_tests.items():
            try:
                url = base_url + config["url"]
                
                if config["method"] == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    headers = {"Content-Type": "application/json", "X-API-Key": "test"}
                    data = {"keyword": "test", "title": "test content"}
                    response = requests.post(url, json=data, headers=headers, timeout=10)
                
                results[test_name] = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "response_size": len(response.text),
                    "success": response.status_code < 400,
                    "error_message": response.text if response.status_code >= 400 else None
                }
                
            except Exception as e:
                results[test_name] = {
                    "status_code": 0,
                    "error": str(e),
                    "success": False
                }
        
        return results
    
    def analyze_security_aspects(self, html_content, api_results):
        """보안 측면 분석"""
        security_issues = []
        security_score = 100
        
        # HTTPS 확인
        if "http://" in html_content and "https://" not in html_content:
            security_issues.append("HTTPS 미사용 - 프로덕션에서 필수")
            security_score -= 20
        
        # API 키 노출 확인
        if any(keyword in html_content.lower() for keyword in ["api_key", "secret", "token"]):
            security_issues.append("잠재적 API 키 노출 위험")
            security_score -= 30
        
        # CSP (Content Security Policy) 확인
        if "content-security-policy" not in html_content.lower():
            security_issues.append("Content Security Policy 헤더 누락")
            security_score -= 15
        
        # API 인증 확인
        auth_required_apis = [name for name, result in api_results.items() 
                            if result.get("status_code") == 401]
        if len(auth_required_apis) > 0:
            security_score += 20  # 인증이 요구되는 것은 좋음
        
        # CORS 확인
        if any("cors" in str(result.get("error", "")).lower() for result in api_results.values()):
            security_issues.append("CORS 설정 문제 가능성")
            security_score -= 10
        
        return {
            "security_score": max(0, security_score),
            "issues": security_issues,
            "recommendations": [
                "HTTPS 강제 적용",
                "API 키 환경변수 관리",
                "CSP 헤더 설정",
                "Rate Limiting 구현",
                "입력값 Sanitization 강화"
            ]
        }
    
    def analyze_performance(self, api_results):
        """성능 분석"""
        response_times = [result.get("response_time", 0) for result in api_results.values() 
                         if result.get("response_time")]
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = 0
            max_response_time = 0
        
        performance_score = 100
        issues = []
        
        if avg_response_time > 2:
            performance_score -= 30
            issues.append(f"평균 응답시간 느림: {avg_response_time:.2f}초")
        
        if max_response_time > 5:
            performance_score -= 20
            issues.append(f"최대 응답시간 과도: {max_response_time:.2f}초")
        
        return {
            "performance_score": max(0, performance_score),
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "issues": issues,
            "recommendations": [
                "API 응답시간 최적화",
                "캐싱 시스템 구현",
                "데이터베이스 쿼리 최적화",
                "CDN 적용 고려",
                "이미지 최적화"
            ]
        }
    
    def calculate_overall_scores(self):
        """전체 점수 계산"""
        # UI/UX 점수
        ui_structure_score = self.analysis_report["ui_ux_analysis"].get("structure_analysis", {}).get("structure_quality", 0)
        ui_score = min(100, ui_structure_score)
        
        # 기능성 점수
        api_success_rate = len([r for r in self.analysis_report["backend_analysis"].values() 
                              if r.get("success", False)]) / len(self.analysis_report["backend_analysis"]) * 100
        
        # 전체 점수
        security_score = self.analysis_report["security_analysis"]["security_score"]
        performance_score = self.analysis_report["performance_analysis"]["performance_score"]
        
        overall_score = (ui_score * 0.25 + api_success_rate * 0.25 + 
                        security_score * 0.25 + performance_score * 0.25)
        
        return {
            "ui_ux_score": ui_score,
            "functionality_score": api_success_rate,
            "security_score": security_score,
            "performance_score": performance_score,
            "overall_score": overall_score
        }
    
    def generate_expert_recommendations(self):
        """전문가 권고사항 생성"""
        recommendations = {
            "immediate_fixes": [],
            "short_term_improvements": [],
            "long_term_enhancements": []
        }
        
        # 즉시 수정 필요
        if self.analysis_report["scores"]["security_score"] < 70:
            recommendations["immediate_fixes"].append("🔒 보안 취약점 즉시 해결")
        
        if self.analysis_report["scores"]["performance_score"] < 60:
            recommendations["immediate_fixes"].append("⚡ 성능 최적화 urgent")
        
        # 단기 개선사항
        recommendations["short_term_improvements"].extend([
            "🎨 UI/UX 일관성 개선",
            "♿ 접근성 기능 강화", 
            "📱 모바일 최적화",
            "🔄 에러 핸들링 개선"
        ])
        
        # 장기 발전 방향
        recommendations["long_term_enhancements"].extend([
            "🚀 PWA (Progressive Web App) 적용",
            "📊 사용자 분석 도구 도입",
            "🤖 AI 기능 확장",
            "🔧 DevOps 파이프라인 구축"
        ])
        
        return recommendations
    
    def run_comprehensive_analysis(self):
        """종합 분석 실행"""
        print("🔬 전문가 페르소나 종합 시스템 분석 시작")
        print("=" * 60)
        
        # 1. 프론트엔드 HTML 분석
        print("1️⃣ 프론트엔드 UI/UX 분석...")
        try:
            response = requests.get("http://localhost:4007/", timeout=10)
            html_content = response.text
            
            self.analysis_report["ui_ux_analysis"] = {
                "structure_analysis": self.analyze_html_structure(html_content),
                "component_analysis": self.analyze_ui_components(html_content),
                "page_size": len(html_content),
                "load_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            self.analysis_report["ui_ux_analysis"] = {"error": str(e)}
        
        # 2. 백엔드 API 분석
        print("2️⃣ 백엔드 API 기능 분석...")
        self.analysis_report["backend_analysis"] = self.test_backend_apis()
        
        # 3. 보안 분석
        print("3️⃣ 보안 취약점 분석...")
        self.analysis_report["security_analysis"] = self.analyze_security_aspects(
            html_content if 'html_content' in locals() else "",
            self.analysis_report["backend_analysis"]
        )
        
        # 4. 성능 분석
        print("4️⃣ 성능 최적화 분석...")
        self.analysis_report["performance_analysis"] = self.analyze_performance(
            self.analysis_report["backend_analysis"]
        )
        
        # 5. 종합 점수 계산
        print("5️⃣ 종합 점수 계산...")
        self.analysis_report["scores"] = self.calculate_overall_scores()
        
        # 6. 전문가 권고사항
        print("6️⃣ 전문가 권고사항 생성...")
        self.analysis_report["recommendations"] = self.generate_expert_recommendations()
        
        # 7. 보고서 저장
        report_filename = f"expert_comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_report, f, ensure_ascii=False, indent=2)
        
        print("=" * 60)
        print(f"📋 분석 완료! 상세 보고서: {report_filename}")
        
        return self.analysis_report

def main():
    analyzer = ExpertSystemAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    # 요약 출력
    print("\n" + "="*60)
    print("📊 전문가 분석 결과 요약")
    print("="*60)
    
    scores = results.get("scores", {})
    print(f"🎨 UI/UX 점수:      {scores.get('ui_ux_score', 0):.1f}/100")
    print(f"⚙️  기능성 점수:     {scores.get('functionality_score', 0):.1f}/100") 
    print(f"🔒 보안 점수:       {scores.get('security_score', 0):.1f}/100")
    print(f"⚡ 성능 점수:       {scores.get('performance_score', 0):.1f}/100")
    print(f"🏆 종합 점수:       {scores.get('overall_score', 0):.1f}/100")
    
    # 등급 산정
    overall_score = scores.get('overall_score', 0)
    if overall_score >= 90:
        grade = "🥇 우수 (A)"
    elif overall_score >= 80:
        grade = "🥈 양호 (B)"
    elif overall_score >= 70:
        grade = "🥉 보통 (C)"
    elif overall_score >= 60:
        grade = "⚠️  개선필요 (D)"
    else:
        grade = "🚨 심각 (F)"
    
    print(f"\n📈 시스템 등급: {grade}")
    
    # 주요 권고사항
    recommendations = results.get("recommendations", {})
    if recommendations.get("immediate_fixes"):
        print("\n🚨 즉시 수정 필요:")
        for fix in recommendations["immediate_fixes"]:
            print(f"  • {fix}")
    
    if recommendations.get("short_term_improvements"):
        print("\n💡 단기 개선사항:")
        for improvement in recommendations["short_term_improvements"][:3]:
            print(f"  • {improvement}")

if __name__ == "__main__":
    main()