#!/usr/bin/env python3
"""
API 엔드포인트 전체 테스트
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, headers=None):
    """API 엔드포인트 테스트"""
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        
        return {
            "success": True,
            "status": response.status_code,
            "headers": dict(response.headers),
            "content_length": len(response.text),
            "content": response.text[:200] if response.text else ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """메인 테스트 실행"""
    print("🔍 API 엔드포인트 종합 테스트")
    print(f"시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"대상: {API_BASE}")
    print("-" * 60)
    
    tests = [
        # 기본 상태 확인
        ("GET", "/", None, "메인 엔드포인트"),
        ("GET", "/api/health", None, "헬스체크"),
        
        # 저장된 콘텐츠 (문제 있었던 부분)
        ("GET", "/api/content/saved?limit=5", None, "저장된 콘텐츠 조회"),
        ("GET", "/api/content/stats", None, "콘텐츠 통계"),
        
        # 키워드 분석 (POST)
        ("POST", "/api/keywords/analyze", {
            "keyword": "테스트",
            "country": "KR",
            "max_results": 5
        }, "키워드 분석"),
        
        # 제목 생성 (POST)
        ("POST", "/api/titles/generate", {
            "keyword": "테스트 블로그",
            "count": 3,
            "tone": "professional",
            "language": "ko"
        }, "제목 생성"),
        
        # 이미지 스타일 조회
        ("GET", "/api/images/styles", None, "이미지 스타일 목록"),
    ]
    
    results = {}
    
    for method, endpoint, data, description in tests:
        print(f"\n📋 {description}")
        print(f"   {method} {endpoint}")
        
        result = test_endpoint(method, endpoint, data)
        results[endpoint] = result
        
        if result["success"]:
            status = result["status"]
            size = result["content_length"]
            
            # 상태 표시
            if status == 200:
                print(f"   ✅ {status} - {size} bytes")
            elif status in [401, 422]:
                print(f"   ⚠️ {status} - {size} bytes (예상된 오류)")
            else:
                print(f"   ❌ {status} - {size} bytes")
                
            # Content-Encoding 확인 (압축)
            if "content-encoding" in result["headers"]:
                encoding = result["headers"]["content-encoding"]
                print(f"   🗜️ 압축: {encoding}")
            
            # 내용 미리보기
            if result["content"]:
                preview = result["content"].replace('\n', ' ')
                print(f"   📄 응답: {preview}...")
                
        else:
            print(f"   ❌ 오류: {result['error']}")
    
    # 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    
    success_count = sum(1 for r in results.values() if r["success"] and r.get("status") == 200)
    expected_errors = sum(1 for r in results.values() if r["success"] and r.get("status") in [401, 422])
    actual_errors = sum(1 for r in results.values() if not r["success"] or r.get("status", 0) not in [200, 401, 422])
    
    print(f"✅ 성공: {success_count}")
    print(f"⚠️ 예상된 오류 (API 키 등): {expected_errors}")
    print(f"❌ 실제 오류: {actual_errors}")
    
    if actual_errors == 0:
        print("\n🎉 모든 테스트 통과! ERR_INCOMPLETE_CHUNKED_ENCODING 문제 해결됨")
    else:
        print(f"\n⚠️ {actual_errors}개 엔드포인트에서 문제 발견")
    
    return results

if __name__ == "__main__":
    main()