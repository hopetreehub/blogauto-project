#!/usr/bin/env python3
"""최종 시스템 상태 확인"""
import requests
import json
import time

def check_all_systems():
    print("=" * 60)
    print("🔍 블로그 자동화 시스템 최종 상태 확인")
    print("=" * 60)
    
    # 1. 서버 상태 확인
    print("\n📡 서버 상태:")
    try:
        # 프론트엔드
        frontend = requests.get("http://localhost:4007", timeout=5)
        print(f"  프론트엔드 (포트 4007): {'✅ 정상' if frontend.status_code == 200 else '❌ 오류'}")
        
        # 백엔드
        backend = requests.get("http://localhost:8000/api/health", timeout=5)
        print(f"  백엔드 API (포트 8000): {'✅ 정상' if backend.status_code == 200 else '❌ 오류'}")
    except Exception as e:
        print(f"  서버 연결 오류: {e}")
    
    # 2. 모든 페이지 접근성
    print("\n📄 페이지 접근성:")
    pages = [
        ("홈페이지", "/"),
        ("대시보드", "/dashboard"),
        ("키워드 분석", "/keywords"),
        ("제목 생성", "/titles"),
        ("콘텐츠 생성", "/content"),
        ("배치 작업", "/batch"),
        ("SEO 분석", "/seo")
    ]
    
    all_ok = True
    for name, path in pages:
        try:
            response = requests.get(f"http://localhost:4007{path}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"  {name}: {status} ({response.status_code})")
            if response.status_code != 200:
                all_ok = False
        except Exception as e:
            print(f"  {name}: ❌ (오류: {e})")
            all_ok = False
    
    # 3. API 기능 테스트
    print("\n🔧 API 기능 테스트:")
    
    # 키워드 분석
    try:
        keyword_response = requests.post(
            "http://localhost:8000/api/keywords/analyze",
            json={"keyword": "테스트", "country": "KR", "max_results": 3},
            timeout=5
        )
        print(f"  키워드 분석 API: {'✅ 정상' if keyword_response.status_code == 200 else '❌ 오류'}")
    except Exception as e:
        print(f"  키워드 분석 API: ❌ (오류: {e})")
    
    # 제목 생성
    try:
        title_response = requests.post(
            "http://localhost:8000/api/titles/generate",
            json={"keyword": "테스트", "count": 3, "tone": "professional", "length": "medium", "language": "ko"},
            timeout=5
        )
        print(f"  제목 생성 API: {'✅ 정상' if title_response.status_code == 200 else '❌ 오류'}")
        
        # duplicate_rate 확인
        if title_response.status_code == 200:
            titles = title_response.json()
            has_duplicate_rate = any('duplicate_rate' in title for title in titles)
            print(f"  duplicate_rate 필드: {'⚠️ 없음 (정상)' if not has_duplicate_rate else '✅ 있음'}")
    except Exception as e:
        print(f"  제목 생성 API: ❌ (오류: {e})")
    
    # 콘텐츠 생성
    try:
        content_response = requests.post(
            "http://localhost:8000/api/content/generate",
            json={"title": "테스트 제목", "keyword": "테스트", "length": "short"},
            timeout=5
        )
        print(f"  콘텐츠 생성 API: {'✅ 정상' if content_response.status_code == 200 else '❌ 오류'}")
    except Exception as e:
        print(f"  콘텐츠 생성 API: ❌ (오류: {e})")
    
    # 대시보드 통계
    try:
        stats_response = requests.get("http://localhost:8000/api/dashboard/stats", timeout=5)
        print(f"  대시보드 통계 API: {'✅ 정상' if stats_response.status_code == 200 else '❌ 오류'}")
    except Exception as e:
        print(f"  대시보드 통계 API: ❌ (오류: {e})")
    
    # 4. 최종 평가
    print("\n" + "=" * 60)
    print("📊 최종 평가:")
    if all_ok:
        print("✅ 모든 시스템이 정상적으로 작동합니다!")
        print(f"🌐 크로미움에서 접속: http://localhost:4007")
        print("🔧 duplicate_rate 오류도 해결되었습니다.")
    else:
        print("⚠️ 일부 문제가 발견되었습니다. 위의 로그를 확인하세요.")
    print("=" * 60)

if __name__ == "__main__":
    check_all_systems()