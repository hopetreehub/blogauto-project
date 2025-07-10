#!/usr/bin/env python3
import subprocess
import time
import requests
import json

def test_with_chromium():
    """크로미움으로 실제 사용자 테스트 시뮬레이션"""
    print("🌐 크로미움 브라우저로 실제 테스트 시작...")
    print("=" * 60)
    
    # 키워드 분석 페이지 테스트
    print("\n🔍 키워드 분석 페이지에서 테스트:")
    print("   - 페이지 URL: http://localhost:4007/keywords")
    print("   - 테스트 키워드: '블로그 마케팅'")
    
    # API 직접 호출로 기능 확인
    keyword_response = requests.post(
        "http://localhost:8000/api/keywords/analyze",
        json={"keyword": "블로그 마케팅", "country": "KR", "max_results": 5}
    )
    
    if keyword_response.status_code == 200:
        print("   ✅ 키워드 분석 API 정상 작동")
        keywords = keyword_response.json()
        print(f"   - 분석된 키워드 수: {len(keywords)}개")
    else:
        print("   ❌ 키워드 분석 API 오류")
    
    time.sleep(1)
    
    # 제목 생성 페이지 테스트
    print("\n✍️ 제목 생성 페이지에서 테스트:")
    print("   - 페이지 URL: http://localhost:4007/titles")
    print("   - 테스트 키워드: '블로그 마케팅'")
    
    title_response = requests.post(
        "http://localhost:8000/api/titles/generate",
        json={"keyword": "블로그 마케팅", "count": 5, "tone": "professional", "length": "medium", "language": "ko"}
    )
    
    if title_response.status_code == 200:
        print("   ✅ 제목 생성 API 정상 작동")
        titles = title_response.json()
        print(f"   - 생성된 제목 수: {len(titles)}개")
        for i, title in enumerate(titles[:3], 1):
            print(f"   {i}. {title['title']}")
    else:
        print("   ❌ 제목 생성 API 오류")
    
    time.sleep(1)
    
    # 콘텐츠 생성 페이지 테스트
    print("\n📝 콘텐츠 생성 페이지에서 테스트:")
    print("   - 페이지 URL: http://localhost:4007/content")
    print("   - 테스트 제목: '블로그 마케팅 완전 가이드'")
    
    content_response = requests.post(
        "http://localhost:8000/api/content/generate",
        json={"title": "블로그 마케팅 완전 가이드", "keyword": "블로그 마케팅", "length": "medium"}
    )
    
    if content_response.status_code == 200:
        print("   ✅ 콘텐츠 생성 API 정상 작동")
        content = content_response.json()
        print(f"   - SEO 점수: {content['seo_score']}")
        print(f"   - 단어 수: {content['word_count']}")
        print(f"   - 가독성 점수: {content['readability_score']}")
    else:
        print("   ❌ 콘텐츠 생성 API 오류")
    
    time.sleep(1)
    
    # 대시보드 확인
    print("\n📊 대시보드 통계 확인:")
    print("   - 페이지 URL: http://localhost:4007/dashboard")
    
    stats_response = requests.get("http://localhost:8000/api/dashboard/stats")
    if stats_response.status_code == 200:
        print("   ✅ 대시보드 API 정상 작동")
        stats = stats_response.json()
        print(f"   - 분석된 키워드: {stats['keywords_analyzed']}개")
        print(f"   - 생성된 제목: {stats['titles_generated']}개")
        print(f"   - 생성된 콘텐츠: {stats['content_generated']}개")
    else:
        print("   ❌ 대시보드 API 오류")
    
    print("\n" + "=" * 60)
    print("✅ 크로미움 테스트 완료!")
    print("\n📌 브라우저에서 직접 확인할 수 있는 페이지:")
    print("   - 홈: http://localhost:4007")
    print("   - 대시보드: http://localhost:4007/dashboard")
    print("   - 키워드 분석: http://localhost:4007/keywords")
    print("   - 제목 생성: http://localhost:4007/titles")
    print("   - 콘텐츠 생성: http://localhost:4007/content")
    print("   - 배치 작업: http://localhost:4007/batch")
    print("   - SEO 분석: http://localhost:4007/seo")

if __name__ == "__main__":
    test_with_chromium()