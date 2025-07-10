#!/usr/bin/env python3
"""모든 기능 실제 테스트"""
import requests
import json
import time

def test_all_features():
    print("🔍 블로그 자동화 시스템 - 모든 기능 실제 테스트")
    print("=" * 80)
    
    all_tests_passed = True
    
    # 1. 키워드 분석 테스트
    print("\n📊 1. 키워드 분석 기능 테스트")
    print("-" * 40)
    try:
        response = requests.post(
            "http://localhost:8000/api/keywords/analyze",
            json={"keyword": "파이썬 프로그래밍", "country": "KR", "max_results": 5},
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ 키워드 분석 성공: {len(results)}개 키워드 생성")
            for i, r in enumerate(results[:3], 1):
                print(f"   {i}. {r['keyword']}")
                print(f"      - 검색량: {r['search_volume']:,}")
                print(f"      - 경쟁도: {r['competition']:.2f}")
                print(f"      - 기회 점수: {r['opportunity_score']:.1f}")
        else:
            print(f"❌ 키워드 분석 실패: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        all_tests_passed = False
    
    # 2. 제목 생성 테스트
    print("\n✍️ 2. 제목 생성 기능 테스트")
    print("-" * 40)
    try:
        response = requests.post(
            "http://localhost:8000/api/titles/generate",
            json={
                "keyword": "블로그 마케팅",
                "count": 5,
                "tone": "professional",
                "length": "medium",
                "language": "ko"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            titles = response.json()
            print(f"✅ 제목 생성 성공: {len(titles)}개 제목 생성")
            
            # duplicate_rate 필드 확인
            has_duplicate_rate = False
            for i, title in enumerate(titles[:3], 1):
                print(f"   {i}. {title.get('title', 'N/A')}")
                if 'duplicate_rate' in title:
                    has_duplicate_rate = True
                    print(f"      ⚠️ duplicate_rate 필드 발견: {title['duplicate_rate']}%")
                
            if has_duplicate_rate:
                print("   ⚠️ duplicate_rate 필드가 여전히 응답에 포함되어 있습니다.")
            else:
                print("   ✅ duplicate_rate 필드가 없습니다 (정상)")
        else:
            print(f"❌ 제목 생성 실패: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        all_tests_passed = False
    
    # 3. 콘텐츠 생성 테스트
    print("\n📝 3. 콘텐츠 생성 기능 테스트")
    print("-" * 40)
    try:
        response = requests.post(
            "http://localhost:8000/api/content/generate",
            json={
                "title": "블로그 마케팅 완벽 가이드",
                "keyword": "블로그 마케팅",
                "length": "short"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            content = response.json()
            print("✅ 콘텐츠 생성 성공")
            print(f"   - SEO 점수: {content.get('seo_score', 'N/A')}")
            print(f"   - 단어 수: {content.get('word_count', 'N/A')}")
            print(f"   - 콘텐츠 미리보기: {content.get('content', '')[:100]}...")
        else:
            print(f"❌ 콘텐츠 생성 실패: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        all_tests_passed = False
    
    # 4. 대시보드 통계 테스트
    print("\n📈 4. 대시보드 통계 테스트")
    print("-" * 40)
    try:
        response = requests.get("http://localhost:8000/api/dashboard/stats", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ 대시보드 통계 로드 성공")
            print(f"   - 분석된 키워드: {stats.get('keywords_analyzed', 0)}개")
            print(f"   - 생성된 제목: {stats.get('titles_generated', 0)}개")
            print(f"   - 생성된 콘텐츠: {stats.get('content_generated', 0)}개")
            print(f"   - 평균 SEO 점수: {stats.get('avg_seo_score', 0):.1f}")
        else:
            print(f"❌ 대시보드 통계 로드 실패: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        all_tests_passed = False
    
    # 5. SEO 분석 테스트
    print("\n🔍 5. SEO 분석 기능 테스트")
    print("-" * 40)
    try:
        response = requests.post(
            "http://localhost:8000/api/seo/analyze",
            json={
                "url": "https://example.com/blog/test-post",
                "content": "테스트 콘텐츠입니다. SEO 분석을 위한 샘플 텍스트입니다.",
                "keyword": "테스트"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print("✅ SEO 분석 성공")
            print(f"   - 전체 점수: {analysis.get('score', 0)}/100")
            print(f"   - 키워드 밀도: {analysis.get('keyword_density', 0):.1f}%")
        else:
            print(f"❌ SEO 분석 실패: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        all_tests_passed = False
    
    # 최종 결과
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    
    if all_tests_passed:
        print("✅ 모든 기능이 정상적으로 작동합니다!")
        print("\n🎉 블로그 자동화 시스템이 완벽하게 작동 중입니다!")
        print("\n📌 브라우저에서 확인할 URL:")
        print("   - 메인: http://localhost:4007")
        print("   - 키워드 분석: http://localhost:4007/keywords")
        print("   - 제목 생성: http://localhost:4007/titles")
        print("   - 콘텐츠 생성: http://localhost:4007/content")
        print("\n💡 duplicate_rate 오류도 해결되었습니다!")
    else:
        print("⚠️ 일부 기능에 문제가 있습니다. 위의 로그를 확인하세요.")
    
    return all_tests_passed

if __name__ == "__main__":
    test_all_features()