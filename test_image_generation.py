#!/usr/bin/env python3
"""
이미지 생성 기능 테스트 스크립트
"""
import asyncio
import requests
import json
from datetime import datetime

# API 베이스 URL
API_BASE_URL = "http://localhost:8000"

def test_content_generation_with_image():
    """콘텐츠 생성과 이미지 생성 테스트"""
    print("\n🖼️ 이미지 생성 기능 테스트 시작...")
    
    # 1. API 키 확인
    print("\n1️⃣ API 키 설정 확인...")
    settings_response = requests.get(f"{API_BASE_URL}/api/settings")
    if settings_response.status_code == 200:
        settings = settings_response.json()
        has_openai = settings.get("has_openai", False)
        print(f"   ✅ OpenAI API 키 설정: {'있음' if has_openai else '없음'}")
        
        if not has_openai:
            print("   ⚠️ OpenAI API 키가 설정되지 않았습니다.")
            print("   👉 http://localhost:4007/settings 에서 설정해주세요.")
            return
    else:
        print(f"   ❌ 설정 확인 실패: {settings_response.status_code}")
        return
    
    # 2. 이미지 생성 기능 테스트
    print("\n2️⃣ 이미지 생성 API 테스트...")
    
    image_request = {
        "title": "인공지능이 바꾸는 미래의 교육",
        "keyword": "AI 교육",
        "style": "professional",
        "size": "1024x1024"
    }
    
    try:
        print(f"   요청 데이터: {json.dumps(image_request, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/images/generate",
            json=image_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 이미지 생성 성공!")
            print(f"   - 이미지 URL: {result.get('image_url', 'N/A')}")
            print(f"   - 프롬프트: {result.get('prompt', 'N/A')}")
            print(f"   - 로컬 경로: {result.get('local_path', 'N/A')}")
            
            # 이미지 접근 가능 여부 확인
            if result.get('image_url'):
                img_response = requests.head(result['image_url'])
                print(f"   - 이미지 접근 가능: {'✅' if img_response.status_code == 200 else '❌'}")
                
        else:
            print(f"   ❌ 이미지 생성 실패: {response.status_code}")
            print(f"   오류: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 요청 중 오류 발생: {str(e)}")
    
    # 3. 콘텐츠 생성 시 이미지 포함 테스트
    print("\n3️⃣ 콘텐츠 생성 시 이미지 자동 생성 테스트...")
    
    content_request = {
        "title": "2025년 디지털 마케팅 트렌드",
        "keyword": "디지털 마케팅",
        "length": "medium",
        "tone": "professional",
        "language": "ko",
        "include_images": True  # 이미지 포함 옵션
    }
    
    try:
        print(f"   요청 데이터: {json.dumps(content_request, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            f"{API_BASE_URL}/api/content/generate",
            json=content_request,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 콘텐츠 생성 성공!")
            print(f"   - 제목: {result.get('title', 'N/A')}")
            print(f"   - 콘텐츠 길이: {len(result.get('content', ''))} 자")
            
            # 이미지 정보 확인
            images = result.get('images', [])
            if images:
                print(f"   - 생성된 이미지 수: {len(images)}")
                for i, img in enumerate(images, 1):
                    print(f"   - 이미지 {i}: {img.get('url', 'N/A')}")
            else:
                print("   - 생성된 이미지: 없음")
                
        else:
            print(f"   ❌ 콘텐츠 생성 실패: {response.status_code}")
            print(f"   오류: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 요청 중 오류 발생: {str(e)}")
    
    # 4. 성능 측정
    print("\n4️⃣ 성능 측정...")
    
    # 여러 번 테스트하여 평균 시간 측정
    times = []
    for i in range(3):
        start_time = datetime.now()
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/images/generate",
                json={
                    "title": f"테스트 이미지 {i+1}",
                    "keyword": "성능 테스트",
                    "style": "minimalist"
                },
                timeout=30
            )
            end_time = datetime.now()
            
            if response.status_code == 200:
                elapsed = (end_time - start_time).total_seconds()
                times.append(elapsed)
                print(f"   - 테스트 {i+1}: {elapsed:.2f}초")
        except:
            print(f"   - 테스트 {i+1}: 실패")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"   📊 평균 생성 시간: {avg_time:.2f}초")
    
    print("\n✅ 이미지 생성 기능 테스트 완료!")

if __name__ == "__main__":
    test_content_generation_with_image()