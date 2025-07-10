#!/usr/bin/env python3
"""콘텐츠 생성 기능 테스트"""
import requests
import json

def test_content_generation():
    print("📝 콘텐츠 생성 API 테스트")
    print("=" * 60)
    
    # 1. API 키 없이 테스트
    print("\n1. API 키 없이 콘텐츠 생성 요청")
    try:
        response = requests.post(
            "http://localhost:8000/api/content/generate",
            json={
                "title": "AI 블로그 작성 가이드",
                "keyword": "AI 블로그",
                "length": "medium"
            }
        )
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 401:
            error_data = response.json()
            print(f"   에러 메시지: {error_data['detail']}")
        else:
            print(f"   예상과 다른 응답: {response.text[:100]}...")
    except Exception as e:
        print(f"   오류: {e}")
    
    # 2. API 키 포함하여 테스트
    print("\n2. API 키 포함하여 콘텐츠 생성 요청")
    try:
        headers = {"X-Openai-Key": "demo_api_key"}
        response = requests.post(
            "http://localhost:8000/api/content/generate",
            json={
                "title": "AI 블로그 작성 완벽 가이드",
                "keyword": "AI 블로그",
                "length": "medium",
                "tone": "professional",
                "language": "ko"
            },
            headers=headers
        )
        
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 콘텐츠 생성 성공!")
            print(f"   - SEO 점수: {data.get('seo_score', 'N/A')}")
            print(f"   - 단어 수: {data.get('word_count', 'N/A')}")
            print(f"   - 가독성 점수: {data.get('readability_score', 'N/A')}")
            print(f"   - 콘텐츠 미리보기:")
            content = data.get('content', '')
            print(f"     {content[:200]}...")
        else:
            print(f"   ❌ 콘텐츠 생성 실패: {response.status_code}")
            print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   오류: {e}")
    
    # 3. 프론트엔드 시뮬레이션 테스트
    print("\n3. 프론트엔드에서 호출하는 방식으로 테스트")
    try:
        headers = {
            "Content-Type": "application/json",
            "X-Openai-Key": "demo_api_key"
        }
        response = requests.post(
            "http://localhost:8000/api/content/generate",
            headers=headers,
            json={
                "title": "블로그 마케팅 전략",
                "keyword": "블로그 마케팅",
                "length": "short"
            }
        )
        
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 프론트엔드 방식 테스트 성공!")
            print(f"   응답 데이터 구조:")
            for key, value in data.items():
                if key == 'content':
                    print(f"     {key}: {len(value)}자 ('{value[:50]}...')")
                else:
                    print(f"     {key}: {value}")
        else:
            print(f"   ❌ 실패: {response.status_code}")
            print(f"   에러: {response.text}")
    except Exception as e:
        print(f"   오류: {e}")
    
    print("\n" + "=" * 60)
    print("📌 브라우저에서 테스트하려면:")
    print("   1. http://localhost:4007/settings에서 API 키 입력")
    print("   2. http://localhost:4007/content에서 콘텐츠 생성 테스트")
    print("   3. 제목: '테스트 제목', 키워드: '테스트' 입력 후 생성")

if __name__ == "__main__":
    test_content_generation()