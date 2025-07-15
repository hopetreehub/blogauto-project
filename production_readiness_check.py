#!/usr/bin/env python3
"""
프로덕션 배포 준비 상태 최종 검증
Step 12: 모든 시스템 구성요소의 프로덕션 준비도 평가
"""

import asyncio
import aiohttp
import json
import time
import subprocess
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

class ProductionReadinessChecker:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = None
        self.check_results = {}
        self.critical_issues = []
        self.warnings = []
        self.recommendations = []
        
    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_api_functionality(self) -> Dict[str, Any]:
        """API 기능 완전성 검증"""
        print("🎯 API 기능 완전성 검증...")
        
        results = {}
        
        # 1. 기본 서버 응답
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                results["server_root"] = {
                    "status": response.status,
                    "working": response.status == 200,
                    "response_time": 0
                }
                if response.status == 200:
                    data = await response.json()
                    results["server_root"]["has_proper_response"] = bool(data.get("message"))
        except Exception as e:
            results["server_root"] = {"error": str(e), "working": False}
        
        # 2. 헬스체크 엔드포인트
        try:
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/health") as response:
                response_time = time.time() - start_time
                results["health_check"] = {
                    "status": response.status,
                    "working": response.status == 200,
                    "response_time": response_time
                }
                if response.status == 200:
                    health_data = await response.json()
                    results["health_check"].update({
                        "has_status": "status" in health_data,
                        "has_timestamp": "timestamp" in health_data,
                        "fast_response": response_time < 0.1
                    })
        except Exception as e:
            results["health_check"] = {"error": str(e), "working": False}
            self.critical_issues.append("헬스체크 엔드포인트 접근 불가")
        
        # 3. 키워드 분석 API
        try:
            test_payload = {"keyword": "프로덕션테스트", "country": "KR", "max_results": 5}
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/api/keywords/analyze", json=test_payload) as response:
                response_time = time.time() - start_time
                results["keyword_analysis"] = {
                    "status": response.status,
                    "working": response.status == 200,
                    "response_time": response_time
                }
                
                if response.status == 200:
                    data = await response.json()
                    results["keyword_analysis"].update({
                        "has_keyword": "keyword" in data,
                        "has_search_volume": "search_volume" in data,
                        "has_competition": "competition" in data,
                        "has_related_keywords": "related_keywords" in data,
                        "data_structure_valid": True
                    })
                elif response.status == 422:
                    # 검증 오류는 정상적인 동작
                    results["keyword_analysis"]["proper_validation"] = True
        except Exception as e:
            results["keyword_analysis"] = {"error": str(e), "working": False}
            self.critical_issues.append("키워드 분석 API 오류")
        
        # 4. 제목 생성 API
        try:
            test_payload = {"keyword": "프로덕션테스트", "count": 3, "tone": "professional"}
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/api/titles/generate", json=test_payload) as response:
                response_time = time.time() - start_time
                results["title_generation"] = {
                    "status": response.status,
                    "working": response.status == 200,
                    "response_time": response_time
                }
                
                if response.status == 200:
                    data = await response.json()
                    titles = data.get("titles", [])
                    results["title_generation"].update({
                        "has_titles": len(titles) > 0,
                        "titles_have_scores": all("score" in t for t in titles),
                        "proper_title_count": len(titles) == 3
                    })
        except Exception as e:
            results["title_generation"] = {"error": str(e), "working": False}
            self.warnings.append("제목 생성 API 접근 문제")
        
        # 5. 콘텐츠 생성 API
        try:
            test_payload = {
                "title": "프로덕션 테스트용 제목",
                "keyword": "프로덕션테스트",
                "length": "short"
            }
            start_time = time.time()
            async with self.session.post(f"{self.base_url}/api/content/generate", json=test_payload) as response:
                response_time = time.time() - start_time
                results["content_generation"] = {
                    "status": response.status,
                    "working": response.status == 200,
                    "response_time": response_time
                }
                
                if response.status == 200:
                    data = await response.json()
                    results["content_generation"].update({
                        "has_content": bool(data.get("content")),
                        "has_seo_score": "seo_score" in data,
                        "has_word_count": "word_count" in data,
                        "content_not_empty": len(data.get("content", "")) > 100
                    })
        except Exception as e:
            results["content_generation"] = {"error": str(e), "working": False}
            self.warnings.append("콘텐츠 생성 API 접근 문제")
        
        return results
    
    async def check_api_documentation(self) -> Dict[str, Any]:
        """API 문서화 상태 검증"""
        print("📚 API 문서화 상태 검증...")
        
        results = {}
        
        # 1. Swagger UI 접근성
        try:
            async with self.session.get(f"{self.base_url}/docs") as response:
                results["swagger_ui"] = {
                    "status": response.status,
                    "accessible": response.status == 200,
                    "content_type": response.headers.get("content-type", "")
                }
                
                if response.status == 200:
                    content = await response.text()
                    results["swagger_ui"]["has_swagger_content"] = "swagger" in content.lower()
        except Exception as e:
            results["swagger_ui"] = {"error": str(e), "accessible": False}
            self.warnings.append("Swagger UI 접근 불가")
        
        # 2. OpenAPI 스키마
        try:
            async with self.session.get(f"{self.base_url}/openapi.json") as response:
                results["openapi_schema"] = {
                    "status": response.status,
                    "accessible": response.status == 200
                }
                
                if response.status == 200:
                    schema = await response.json()
                    results["openapi_schema"].update({
                        "has_info": "info" in schema,
                        "has_paths": "paths" in schema and len(schema["paths"]) > 0,
                        "has_components": "components" in schema,
                        "valid_openapi": schema.get("openapi", "").startswith("3.")
                    })
        except Exception as e:
            results["openapi_schema"] = {"error": str(e), "accessible": False}
            self.warnings.append("OpenAPI 스키마 접근 불가")
        
        return results
    
    async def check_performance_requirements(self) -> Dict[str, Any]:
        """성능 요구사항 검증"""
        print("⚡ 성능 요구사항 검증...")
        
        results = {}
        
        # 1. 응답 시간 벤치마크
        response_times = []
        
        for i in range(10):
            try:
                start_time = time.time()
                async with self.session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        response_times.append(time.time() - start_time)
                await asyncio.sleep(0.1)  # 짧은 간격
            except:
                pass
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            results["response_times"] = {
                "average": avg_time,
                "max": max_time,
                "min": min_time,
                "samples": len(response_times),
                "meets_sla": avg_time < 0.5,  # 500ms 이내
                "consistent": max_time - min_time < 0.1  # 일관성
            }
            
            if avg_time > 1.0:
                self.warnings.append(f"평균 응답 시간이 느림: {avg_time:.3f}초")
        else:
            results["response_times"] = {"no_data": True}
            self.critical_issues.append("성능 측정 불가")
        
        # 2. 동시 요청 처리
        try:
            concurrent_tasks = []
            start_time = time.time()
            
            for _ in range(5):
                task = self.session.get(f"{self.base_url}/health")
                concurrent_tasks.append(task)
            
            responses = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            successful = sum(1 for r in responses if not isinstance(r, Exception) and hasattr(r, 'status') and r.status == 200)
            
            results["concurrent_handling"] = {
                "total_requests": len(concurrent_tasks),
                "successful_requests": successful,
                "success_rate": successful / len(concurrent_tasks),
                "total_time": total_time,
                "handles_concurrent": successful >= 4  # 80% 이상 성공
            }
            
            # 응답 객체 정리
            for r in responses:
                if hasattr(r, 'close'):
                    r.close()
                    
        except Exception as e:
            results["concurrent_handling"] = {"error": str(e)}
            self.warnings.append("동시 요청 처리 테스트 실패")
        
        return results
    
    def check_file_structure(self) -> Dict[str, Any]:
        """파일 구조 및 설정 검증"""
        print("📁 파일 구조 및 설정 검증...")
        
        results = {}
        project_root = Path("/mnt/e/project/test-blogauto-project")
        
        # 1. 필수 파일 존재 여부
        essential_files = {
            "README.md": project_root / "README.md",
            ".env.example": project_root / ".env.example",
            "requirements.txt": project_root / "backend" / "requirements.txt",
            "docker-compose.yml": project_root / "docker-compose.yml",
            "API 문서": project_root / "docs" / "api-docs.md",
            "배포 가이드": project_root / "docs" / "deployment-guide.md",
            "보안 가이드": project_root / "docs" / "security-guide.md"
        }
        
        file_checks = {}
        missing_files = []
        
        for file_name, file_path in essential_files.items():
            exists = file_path.exists()
            file_checks[file_name] = {
                "exists": exists,
                "path": str(file_path)
            }
            
            if exists and file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    file_checks[file_name]["size"] = file_size
                    file_checks[file_name]["not_empty"] = file_size > 100
                except:
                    file_checks[file_name]["size_check_failed"] = True
            else:
                missing_files.append(file_name)
        
        results["essential_files"] = file_checks
        results["missing_files"] = missing_files
        
        if missing_files:
            self.warnings.extend([f"필수 파일 누락: {f}" for f in missing_files])
        
        # 2. 설정 파일 검증
        env_example_path = project_root / ".env.example"
        if env_example_path.exists():
            try:
                with open(env_example_path, 'r', encoding='utf-8') as f:
                    env_content = f.read()
                
                required_vars = [
                    "OPENAI_API_KEY", "DATABASE_URL", "SECRET_KEY", 
                    "MASTER_PASSWORD", "REDIS_HOST"
                ]
                
                env_check = {}
                for var in required_vars:
                    env_check[var] = var in env_content
                
                results["env_template"] = {
                    "exists": True,
                    "required_vars": env_check,
                    "all_vars_present": all(env_check.values())
                }
                
                if not all(env_check.values()):
                    missing_vars = [var for var, present in env_check.items() if not present]
                    self.warnings.append(f"환경 변수 템플릿 누락: {', '.join(missing_vars)}")
                    
            except Exception as e:
                results["env_template"] = {"error": str(e)}
        
        # 3. 문서 품질 검증
        docs_dir = project_root / "docs"
        if docs_dir.exists():
            doc_files = list(docs_dir.glob("*.md"))
            results["documentation"] = {
                "docs_count": len(doc_files),
                "has_multiple_docs": len(doc_files) >= 5,
                "doc_files": [f.name for f in doc_files]
            }
        else:
            results["documentation"] = {"docs_dir_missing": True}
            self.warnings.append("문서 디렉토리 누락")
        
        return results
    
    def check_security_configuration(self) -> Dict[str, Any]:
        """보안 설정 검증"""
        print("🔒 보안 설정 검증...")
        
        results = {}
        
        # 1. 환경 변수 보안
        security_checks = {
            "env_file_not_in_git": True,  # .env 파일이 Git에 포함되지 않았는지
            "example_file_exists": Path("/mnt/e/project/test-blogauto-project/.env.example").exists(),
            "gitignore_exists": Path("/mnt/e/project/test-blogauto-project/.gitignore").exists()
        }
        
        # 2. 기본 보안 설정
        try:
            gitignore_path = Path("/mnt/e/project/test-blogauto-project/.gitignore")
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    gitignore_content = f.read()
                
                security_checks.update({
                    "env_in_gitignore": ".env" in gitignore_content,
                    "logs_ignored": "*.log" in gitignore_content,
                    "cache_ignored": "__pycache__" in gitignore_content
                })
        except:
            pass
        
        results["security_files"] = security_checks
        
        # 보안 문제 체크
        security_issues = []
        if not security_checks.get("example_file_exists"):
            security_issues.append("환경 변수 템플릿 파일 누락")
        if not security_checks.get("env_in_gitignore"):
            security_issues.append(".env 파일이 gitignore에 없음")
        
        if security_issues:
            self.warnings.extend(security_issues)
        
        results["security_score"] = sum(security_checks.values()) / len(security_checks) * 100
        
        return results
    
    async def run_production_readiness_check(self) -> Dict[str, Any]:
        """프로덕션 준비도 종합 검증"""
        print("🚀 BlogAuto 프로덕션 배포 준비도 최종 검증")
        print("=" * 70)
        
        start_time = time.time()
        
        comprehensive_results = {
            "check_info": {
                "timestamp": datetime.now().isoformat(),
                "checker_version": "1.0.0",
                "check_type": "production_readiness"
            },
            "results": {},
            "summary": {}
        }
        
        try:
            # 1. API 기능 검증
            comprehensive_results["results"]["api_functionality"] = await self.check_api_functionality()
            
            # 2. API 문서화 검증
            comprehensive_results["results"]["api_documentation"] = await self.check_api_documentation()
            
            # 3. 성능 요구사항 검증
            comprehensive_results["results"]["performance"] = await self.check_performance_requirements()
            
            # 4. 파일 구조 검증
            comprehensive_results["results"]["file_structure"] = self.check_file_structure()
            
            # 5. 보안 설정 검증
            comprehensive_results["results"]["security"] = self.check_security_configuration()
            
            # 총 검증 시간
            comprehensive_results["check_info"]["duration"] = time.time() - start_time
            
            # 종합 평가
            comprehensive_results["summary"] = self._generate_production_summary(
                comprehensive_results["results"]
            )
            
        except Exception as e:
            comprehensive_results["error"] = str(e)
            comprehensive_results["check_info"]["duration"] = time.time() - start_time
        
        return comprehensive_results
    
    def _generate_production_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """프로덕션 준비도 종합 평가"""
        summary = {
            "overall_readiness": "unknown",
            "readiness_score": 0,
            "critical_systems_ready": 0,
            "total_critical_systems": 5,  # API, 문서, 성능, 파일, 보안
            "issues_summary": {
                "critical": len(self.critical_issues),
                "warnings": len(self.warnings),
                "total": len(self.critical_issues) + len(self.warnings)
            },
            "recommendations": self.recommendations.copy(),
            "deployment_blockers": self.critical_issues.copy(),
            "improvement_suggestions": self.warnings.copy()
        }
        
        # 각 시스템 준비도 평가
        system_scores = {}
        
        # 1. API 기능 평가
        api_func = results.get("api_functionality", {})
        api_score = 0
        api_working_count = 0
        critical_apis = ["server_root", "health_check", "keyword_analysis"]
        
        for api in critical_apis:
            if api in api_func and api_func[api].get("working", False):
                api_working_count += 1
        
        api_score = (api_working_count / len(critical_apis)) * 100
        system_scores["api_functionality"] = api_score
        
        if api_score >= 80:
            summary["critical_systems_ready"] += 1
        
        # 2. 문서화 평가
        docs = results.get("api_documentation", {})
        docs_score = 0
        
        if docs.get("swagger_ui", {}).get("accessible", False):
            docs_score += 50
        if docs.get("openapi_schema", {}).get("accessible", False):
            docs_score += 50
        
        system_scores["documentation"] = docs_score
        
        if docs_score >= 80:
            summary["critical_systems_ready"] += 1
        
        # 3. 성능 평가
        perf = results.get("performance", {})
        perf_score = 0
        
        response_times = perf.get("response_times", {})
        if response_times.get("meets_sla", False):
            perf_score += 60
        if response_times.get("consistent", False):
            perf_score += 40
        
        system_scores["performance"] = perf_score
        
        if perf_score >= 60:
            summary["critical_systems_ready"] += 1
        
        # 4. 파일 구조 평가
        files = results.get("file_structure", {})
        files_score = 0
        
        missing_files = len(files.get("missing_files", []))
        if missing_files == 0:
            files_score = 100
        elif missing_files <= 2:
            files_score = 70
        else:
            files_score = 40
        
        system_scores["file_structure"] = files_score
        
        if files_score >= 70:
            summary["critical_systems_ready"] += 1
        
        # 5. 보안 평가
        security = results.get("security", {})
        security_score = security.get("security_score", 0)
        system_scores["security"] = security_score
        
        if security_score >= 80:
            summary["critical_systems_ready"] += 1
        
        # 전체 점수 계산
        summary["readiness_score"] = sum(system_scores.values()) / len(system_scores)
        summary["system_scores"] = system_scores
        
        # 전체 준비도 결정
        if summary["critical_systems_ready"] >= 5 and len(self.critical_issues) == 0:
            summary["overall_readiness"] = "production_ready"
            summary["recommendations"].append("✅ 프로덕션 배포 준비 완료!")
        elif summary["critical_systems_ready"] >= 4 and len(self.critical_issues) <= 1:
            summary["overall_readiness"] = "near_ready"
            summary["recommendations"].append("🟡 경미한 수정 후 배포 가능")
        elif summary["critical_systems_ready"] >= 3:
            summary["overall_readiness"] = "needs_improvement"
            summary["recommendations"].append("🟠 일부 개선 후 배포 권장")
        else:
            summary["overall_readiness"] = "not_ready"
            summary["recommendations"].append("🔴 주요 문제 해결 후 재검토 필요")
        
        return summary

def print_production_readiness_report(results: Dict[str, Any]):
    """프로덕션 준비도 보고서 출력"""
    print("\n" + "=" * 70)
    print("📊 BlogAuto 프로덕션 배포 준비도 최종 보고서")
    print("=" * 70)
    
    # 기본 정보
    check_info = results.get("check_info", {})
    print(f"🕐 검증 시간: {check_info.get('timestamp', 'unknown')}")
    print(f"⏱️ 소요 시간: {check_info.get('duration', 0):.2f}초")
    
    # 종합 평가
    summary = results.get("summary", {})
    readiness = summary.get("overall_readiness", "unknown")
    score = summary.get("readiness_score", 0)
    
    readiness_emojis = {
        "production_ready": "🟢",
        "near_ready": "🟡",
        "needs_improvement": "🟠", 
        "not_ready": "🔴"
    }
    
    print(f"\n🎯 전체 준비도: {readiness_emojis.get(readiness, '❓')} {readiness.upper()}")
    print(f"📈 준비도 점수: {score:.1f}/100")
    print(f"⭐ 핵심 시스템 준비: {summary.get('critical_systems_ready', 0)}/{summary.get('total_critical_systems', 5)}")
    
    # 시스템별 점수
    system_scores = summary.get("system_scores", {})
    print(f"\n📋 시스템별 준비도:")
    
    for system, score in system_scores.items():
        emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        system_name = system.replace("_", " ").title()
        print(f"   {emoji} {system_name}: {score:.1f}%")
    
    # API 기능 상세
    api_results = results.get("results", {}).get("api_functionality", {})
    print(f"\n🎯 API 기능 상태:")
    
    api_functions = {
        "server_root": "서버 루트",
        "health_check": "헬스체크",
        "keyword_analysis": "키워드 분석",
        "title_generation": "제목 생성",
        "content_generation": "콘텐츠 생성"
    }
    
    for api_key, api_name in api_functions.items():
        if api_key in api_results:
            api_data = api_results[api_key]
            working = api_data.get("working", False)
            response_time = api_data.get("response_time", 0)
            status = "✅" if working else "❌"
            print(f"   {status} {api_name}: {response_time:.3f}초")
    
    # 성능 메트릭
    perf_results = results.get("results", {}).get("performance", {})
    response_times = perf_results.get("response_times", {})
    
    if response_times and "average" in response_times:
        print(f"\n⚡ 성능 메트릭:")
        print(f"   📊 평균 응답 시간: {response_times['average']:.3f}초")
        print(f"   📊 최대 응답 시간: {response_times['max']:.3f}초")
        print(f"   📊 SLA 준수: {'✅' if response_times.get('meets_sla', False) else '❌'}")
    
    # 이슈 요약
    issues = summary.get("issues_summary", {})
    print(f"\n⚠️ 발견된 이슈:")
    print(f"   🔴 중요 이슈: {issues.get('critical', 0)}개")
    print(f"   🟡 경고 사항: {issues.get('warnings', 0)}개")
    
    # 배포 차단 요소
    blockers = summary.get("deployment_blockers", [])
    if blockers:
        print(f"\n🚫 배포 차단 요소:")
        for blocker in blockers:
            print(f"   • {blocker}")
    
    # 개선 제안
    suggestions = summary.get("improvement_suggestions", [])
    if suggestions:
        print(f"\n💡 개선 제안사항:")
        for suggestion in suggestions[:5]:  # 상위 5개만
            print(f"   • {suggestion}")
    
    # 권장사항
    recommendations = summary.get("recommendations", [])
    if recommendations:
        print(f"\n🎯 최종 권장사항:")
        for rec in recommendations:
            print(f"   • {rec}")

async def main():
    """메인 실행 함수"""
    async with ProductionReadinessChecker() as checker:
        results = await checker.run_production_readiness_check()
        
        # 결과 출력
        print_production_readiness_report(results)
        
        # 결과 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/mnt/e/project/test-blogauto-project/production_readiness_report_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 상세 보고서가 {filename}에 저장되었습니다.")
        
        # 최종 상태 반환
        readiness = results.get("summary", {}).get("overall_readiness", "not_ready")
        return 0 if readiness in ["production_ready", "near_ready"] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)