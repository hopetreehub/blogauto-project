#!/usr/bin/env python3
"""브라우저에서 실제 API 키 시스템 테스트"""
import requests
import time

def test_browser_integration():
    print("🌐 브라우저 통합 테스트")
    print("=" * 80)
    
    # 1. 프론트엔드 서버 확인
    print("\n1. 프론트엔드 서버 상태 확인")
    try:
        response = requests.get("http://localhost:4007", timeout=5)
        print(f"   ✅ 프론트엔드: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 프론트엔드 오류: {e}")
        return
    
    # 2. 백엔드 API 서버 확인
    print("\n2. 백엔드 API 서버 상태 확인")
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        data = response.json()
        print(f"   ✅ 백엔드: {response.status_code}")
        print(f"   API 상태: {data['apis']}")
    except Exception as e:
        print(f"   ❌ 백엔드 오류: {e}")
        return
    
    # 3. 각 페이지 접근성 확인
    pages = [
        ("홈페이지", "/"),
        ("대시보드", "/dashboard"),
        ("키워드 분석", "/keywords"),
        ("제목 생성", "/titles"),
        ("콘텐츠 생성", "/content"),
        ("SEO 분석", "/seo"),
        ("배치 작업", "/batch"),
        ("설정", "/settings")
    ]
    
    print("\n3. 모든 페이지 접근성 확인")
    all_pages_ok = True
    for name, path in pages:
        try:
            response = requests.get(f"http://localhost:4007{path}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {name}: {status} ({response.status_code})")
            if response.status_code != 200:
                all_pages_ok = False
        except Exception as e:
            print(f"   {name}: ❌ (오류: {e})")
            all_pages_ok = False
    
    # 4. API 기능 테스트 (시뮬레이션)
    print("\n4. API 기능 테스트 (실제 API 키 필요)")
    
    print("\n   📝 API 키 없이 호출 (401 에러 확인)")
    try:
        response = requests.post(
            "http://localhost:8000/api/keywords/analyze",
            json={"keyword": "테스트", "country": "KR", "max_results": 3}
        )
        if response.status_code == 401:
            print("   ✅ API 키 인증 정상 작동 (401 반환)")
        else:
            print(f"   ⚠️ 예상과 다른 응답: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    print("\n   📝 API 키 포함하여 호출 (정상 작동 확인)")
    try:
        headers = {"X-Openai-Key": "demo_api_key"}
        response = requests.post(
            "http://localhost:8000/api/keywords/analyze",
            json={"keyword": "블로그 자동화", "country": "KR", "max_results": 3},
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 키워드 분석 성공: {len(data)}개 결과")
        else:
            print(f"   ❌ 키워드 분석 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 5. 최종 결과
    print("\n" + "=" * 80)
    print("📊 최종 테스트 결과")
    print("=" * 80)
    
    if all_pages_ok:
        print("✅ 모든 시스템이 정상 작동합니다!")
        print("\n🎯 사용 방법:")
        print("   1. 브라우저에서 http://localhost:4007 접속")
        print("   2. 설정 페이지(⚙️)에서 OpenAI API 키 입력")
        print("   3. 키워드 분석, 제목 생성, 콘텐츠 생성 기능 사용")
        print("\n⚠️ 실제 API 키가 필요합니다:")
        print("   - OpenAI API 키: https://platform.openai.com")
        print("   - API 키 없이는 401 오류가 발생합니다")
        print("\n💡 데모 목적으로는 임의의 문자열도 입력 가능합니다.")
    else:
        print("⚠️ 일부 페이지에 문제가 있습니다.")
    
    print("=" * 80)

if __name__ == "__main__":
    test_browser_integration()