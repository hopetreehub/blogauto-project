#!/usr/bin/env python3
import requests
import json
import time
import sys

def test_api_endpoint(url, method="GET", data=None):
    """API 엔드포인트 테스트"""
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} {method} {url} - Status: {response.status_code}")
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        print(f"❌ {method} {url} - Error: {str(e)}")
        return False, str(e)

def test_all_features():
    """모든 기능 테스트"""
    print("🔍 블로그 자동화 시스템 전체 테스트 시작...")
    print("=" * 60)
    
    # 1. 프론트엔드 페이지 테스트
    print("\n📄 프론트엔드 페이지 테스트:")
    frontend_pages = [
        "http://localhost:4007/",
        "http://localhost:4007/dashboard",
        "http://localhost:4007/keywords",
        "http://localhost:4007/titles",
        "http://localhost:4007/content",
        "http://localhost:4007/batch",
        "http://localhost:4007/seo"
    ]
    
    for page in frontend_pages:
        success, _ = test_api_endpoint(page)
        time.sleep(0.5)
    
    # 2. 백엔드 API 테스트
    print("\n🔌 백엔드 API 테스트:")
    backend_health, _ = test_api_endpoint("http://localhost:8000/api/health")
    
    # 3. 대시보드 통계
    print("\n📊 대시보드 통계:")
    success, data = test_api_endpoint("http://localhost:8000/api/dashboard/stats")
    if success:
        print(f"   - 키워드 분석: {data['keywords_analyzed']}건")
        print(f"   - 제목 생성: {data['titles_generated']}건")
        print(f"   - 콘텐츠 생성: {data['content_generated']}건")
    
    # 4. 키워드 분석 기능 테스트
    print("\n🔍 키워드 분석 기능 테스트:")
    keyword_data = {
        "keyword": "블로그 마케팅",
        "country": "KR",
        "max_results": 3
    }
    success, keywords = test_api_endpoint(
        "http://localhost:8000/api/keywords/analyze", 
        "POST", 
        keyword_data
    )
    if success:
        for kw in keywords[:3]:
            print(f"   - {kw['keyword']}: 검색량 {kw['search_volume']}, 경쟁도 {kw['competition']}")
    
    # 5. 제목 생성 기능 테스트
    print("\n✍️ 제목 생성 기능 테스트:")
    title_data = {
        "keyword": "블로그 마케팅",
        "count": 3,
        "tone": "professional",
        "length": "medium",
        "language": "ko"
    }
    success, titles = test_api_endpoint(
        "http://localhost:8000/api/titles/generate",
        "POST",
        title_data
    )
    if success:
        for title in titles[:3]:
            print(f"   - {title['title']} (점수: {title['score']})")
    
    # 6. 콘텐츠 생성 기능 테스트
    print("\n📝 콘텐츠 생성 기능 테스트:")
    content_data = {
        "title": "블로그 마케팅 완전 가이드",
        "keyword": "블로그 마케팅",
        "length": "short"
    }
    success, content = test_api_endpoint(
        "http://localhost:8000/api/content/generate",
        "POST",
        content_data
    )
    if success:
        print(f"   - 콘텐츠 생성 완료")
        print(f"   - SEO 점수: {content['seo_score']}")
        print(f"   - 단어 수: {content['word_count']}")
        print(f"   - 가독성 점수: {content['readability_score']}")
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")

if __name__ == "__main__":
    test_all_features()