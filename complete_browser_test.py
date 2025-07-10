#!/usr/bin/env python3
"""크로미움에서 모든 페이지 완전 테스트"""
import subprocess
import time
import requests
import json

def open_in_chromium(url, delay=3):
    """크로미움에서 URL 열기"""
    subprocess.Popen(['chromium', url], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)
    time.sleep(delay)
    return True

def test_page_and_function(page_name, page_url, api_test_func=None):
    """페이지 열고 기능 테스트"""
    print(f"\n{'='*60}")
    print(f"📄 {page_name} 테스트")
    print(f"{'='*60}")
    
    # 페이지 열기
    print(f"1. 페이지 열기: {page_url}")
    try:
        response = requests.get(page_url, timeout=5)
        if response.status_code == 200:
            print("   ✅ 페이지 로드 성공")
            open_in_chromium(page_url)
            print("   ✅ 크로미움에서 열림")
        else:
            print(f"   ❌ 페이지 로드 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # API 기능 테스트
    if api_test_func:
        print(f"\n2. API 기능 테스트")
        api_test_func()
    
    time.sleep(2)

def test_keywords_api():
    """키워드 분석 API 테스트"""
    try:
        response = requests.post(
            "http://localhost:8000/api/keywords/analyze",
            json={"keyword": "SEO 최적화", "country": "KR", "max_results": 3},
            timeout=5
        )
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ 키워드 분석 성공: {len(results)}개")
            for r in results[:2]:
                print(f"      - {r['keyword']}: 검색량 {r['search_volume']:,}")
        else:
            print(f"   ❌ API 오류: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")

def test_titles_api():
    """제목 생성 API 테스트"""
    try:
        response = requests.post(
            "http://localhost:8000/api/titles/generate",
            json={
                "keyword": "AI 블로그",
                "count": 3,
                "tone": "professional",
                "length": "medium",
                "language": "ko"
            },
            timeout=5
        )
        if response.status_code == 200:
            titles = response.json()
            print(f"   ✅ 제목 생성 성공: {len(titles)}개")
            for i, t in enumerate(titles[:2], 1):
                print(f"      {i}. {t.get('title', 'N/A')}")
                if 'duplicate_rate' in t:
                    print(f"         (중복률: {t['duplicate_rate']}%)")
        else:
            print(f"   ❌ API 오류: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")

def test_content_api():
    """콘텐츠 생성 API 테스트"""
    try:
        response = requests.post(
            "http://localhost:8000/api/content/generate",
            json={
                "title": "AI 블로그 운영 가이드",
                "keyword": "AI 블로그",
                "length": "short"
            },
            timeout=5
        )
        if response.status_code == 200:
            content = response.json()
            print(f"   ✅ 콘텐츠 생성 성공")
            print(f"      - SEO 점수: {content.get('seo_score', 'N/A')}")
            print(f"      - 단어 수: {content.get('word_count', 'N/A')}")
        else:
            print(f"   ❌ API 오류: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")

def test_dashboard_api():
    """대시보드 API 테스트"""
    try:
        response = requests.get("http://localhost:8000/api/dashboard/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 통계 로드 성공")
            print(f"      - 키워드: {stats.get('keywords_analyzed', 0)}개")
            print(f"      - 제목: {stats.get('titles_generated', 0)}개")
            print(f"      - 콘텐츠: {stats.get('content_generated', 0)}개")
        else:
            print(f"   ❌ API 오류: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")

def main():
    print("🚀 블로그 자동화 시스템 - 크로미움 완전 테스트")
    print("=" * 80)
    
    # 각 페이지 테스트
    pages = [
        ("홈페이지", "http://localhost:4007/", None),
        ("대시보드", "http://localhost:4007/dashboard", test_dashboard_api),
        ("키워드 분석", "http://localhost:4007/keywords", test_keywords_api),
        ("제목 생성", "http://localhost:4007/titles", test_titles_api),
        ("콘텐츠 생성", "http://localhost:4007/content", test_content_api),
        ("배치 작업", "http://localhost:4007/batch", None),
        ("SEO 분석", "http://localhost:4007/seo", None)
    ]
    
    for page_name, url, api_test in pages:
        test_page_and_function(page_name, url, api_test)
    
    print("\n" + "=" * 80)
    print("✅ 모든 테스트 완료!")
    print("\n📌 브라우저 탭 확인사항:")
    print("   1. 각 페이지가 정상적으로 로드되었는지")
    print("   2. 콘솔(F12)에 오류가 없는지")
    print("   3. 실제 버튼 클릭 시 기능이 작동하는지")
    print("\n🌐 메인 URL: http://localhost:4007")

if __name__ == "__main__":
    main()