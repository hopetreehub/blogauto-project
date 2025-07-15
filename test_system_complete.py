#!/usr/bin/env python3
"""
BlogAuto 시스템 전체 테스트 및 이미지 생성 확인
"""
import asyncio
import requests
import json
import time
from datetime import datetime

# API 베이스 URL
API_BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("\n🔍 API 엔드포인트 상태 확인...")
    
    endpoints = [
        ("/", "메인"),
        ("/api/keywords/analyze", "키워드 분석"),
        ("/api/titles/generate", "제목 생성"),
        ("/api/content/generate", "콘텐츠 생성"),
        ("/api/images/generate", "이미지 생성"),
    ]
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            status = "✅" if response.status_code in [200, 405] else "❌"
            print(f"   {status} {name}: {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {endpoint} - 오류: {str(e)}")

def test_image_generation():
    """이미지 생성 기능 테스트"""
    print("\n🖼️ 이미지 생성 기능 테스트...")
    
    # 이미지 생성 엔드포인트가 있는지 확인
    print("\n1. 이미지 생성 엔드포인트 확인...")
    
    # POST 요청으로 이미지 생성 테스트
    test_data = {
        "title": "AI가 바꾸는 미래의 교육",
        "keyword": "인공지능 교육",
        "style": "professional"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/images/generate",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 이미지 생성 성공!")
            print(f"   - URL: {result.get('image_url', 'N/A')}")
            print(f"   - 프롬프트: {result.get('prompt', 'N/A')[:50]}...")
        else:
            print(f"   ❌ 이미지 생성 실패: {response.status_code}")
            print(f"   - 응답: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 요청 중 오류: {str(e)}")

def test_content_with_image():
    """콘텐츠 생성 시 이미지 포함 테스트"""
    print("\n📝 콘텐츠 생성 (이미지 포함) 테스트...")
    
    content_data = {
        "title": "2025년 블로그 마케팅 트렌드",
        "keyword": "블로그 마케팅",
        "length": "medium",
        "tone": "professional",
        "language": "ko"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/content/generate",
            json=content_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ 콘텐츠 생성 성공!")
            print(f"   - 제목: {result.get('title', 'N/A')}")
            print(f"   - 콘텐츠 길이: {len(result.get('content', ''))} 자")
            
            # 콘텐츠에 이미지가 포함되어 있는지 확인
            content = result.get('content', '')
            if '<img' in content or '![' in content:
                print(f"   ✅ 이미지 포함 확인됨")
            else:
                print(f"   ⚠️ 콘텐츠에 이미지가 포함되지 않음")
                
        else:
            print(f"   ❌ 콘텐츠 생성 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 요청 중 오류: {str(e)}")

def check_redis_status():
    """Redis 연결 상태 확인"""
    print("\n🔴 Redis 캐싱 상태 확인...")
    
    try:
        # Redis 상태 확인 (백엔드 로그에서 확인)
        with open('/mnt/e/project/test-blogauto-project/backend/backend.log', 'r') as f:
            logs = f.read()
            if 'Redis connected' in logs:
                print("   ✅ Redis 연결 성공")
            elif 'Redis connection failed' in logs:
                print("   ⚠️ Redis 연결 실패 - 캐싱 비활성화 상태")
            else:
                print("   ℹ️ Redis 상태 불명확")
    except:
        print("   ℹ️ 로그 파일을 읽을 수 없음")

def check_performance_optimization():
    """성능 최적화 설정 확인"""
    print("\n⚡ 성능 최적화 설정 확인...")
    
    # 압축 확인
    response = requests.get(f"{API_BASE_URL}/", headers={'Accept-Encoding': 'gzip'})
    if 'gzip' in response.headers.get('Content-Encoding', ''):
        print("   ✅ Gzip 압축 활성화")
    else:
        print("   ⚠️ Gzip 압축 비활성화")
    
    # 응답 시간 측정
    times = []
    for _ in range(3):
        start = time.time()
        requests.get(f"{API_BASE_URL}/")
        times.append(time.time() - start)
    
    avg_time = sum(times) / len(times)
    print(f"   📊 평균 응답 시간: {avg_time*1000:.2f}ms")

def main():
    """메인 테스트 실행"""
    print("🚀 BlogAuto 시스템 종합 테스트 시작...")
    print(f"   시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   API: {API_BASE_URL}")
    
    # 1. API 상태 확인
    test_api_endpoints()
    
    # 2. Redis 상태 확인
    check_redis_status()
    
    # 3. 이미지 생성 테스트
    test_image_generation()
    
    # 4. 콘텐츠 + 이미지 테스트
    test_content_with_image()
    
    # 5. 성능 최적화 확인
    check_performance_optimization()
    
    print("\n✅ 테스트 완료!")
    print("\n📌 웹 브라우저에서 확인:")
    print(f"   - 시스템 UI: http://localhost:4007")
    print(f"   - 이미지 생성: http://localhost:4007/images")
    print(f"   - 설정 페이지: http://localhost:4007/settings")

if __name__ == "__main__":
    main()