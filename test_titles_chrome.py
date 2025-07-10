#!/usr/bin/env python3
"""크로미움에서 제목 생성 기능 테스트"""
import subprocess
import time
import requests
import json

print("🔍 제목 생성 페이지 테스트 시작...")
print("=" * 60)

# 1. 크로미움에서 제목 생성 페이지 열기
print("\n1. 크로미움에서 제목 생성 페이지 열기")
subprocess.Popen(['chromium-browser', 'http://localhost:4007/titles'], 
                 stdout=subprocess.DEVNULL, 
                 stderr=subprocess.DEVNULL)
print("   ✅ 브라우저 실행됨")
time.sleep(3)

# 2. API 직접 테스트
print("\n2. 제목 생성 API 테스트")
test_data = {
    "keyword": "블로그 마케팅",
    "count": 5,
    "tone": "professional",
    "length": "medium",
    "language": "ko"
}

try:
    response = requests.post(
        "http://localhost:8000/api/titles/generate",
        json=test_data,
        timeout=10
    )
    
    if response.status_code == 200:
        titles = response.json()
        print(f"   ✅ API 응답 성공: {len(titles)}개 제목 생성")
        
        for i, title in enumerate(titles[:3], 1):
            print(f"\n   제목 {i}:")
            print(f"   - 제목: {title.get('title', 'N/A')}")
            print(f"   - 점수: {title.get('score', 'N/A')}")
            print(f"   - 이유: {title.get('reason', 'N/A')}")
            print(f"   - 중복률: {title.get('duplicate_rate', 'N/A')}")
    else:
        print(f"   ❌ API 오류: {response.status_code}")
        print(f"   응답: {response.text}")
        
except Exception as e:
    print(f"   ❌ 요청 실패: {e}")

print("\n3. 브라우저에서 수동 테스트 방법:")
print("   1) 키워드 입력: '블로그 마케팅'")
print("   2) 설정 선택: professional, medium, 한국어")
print("   3) '제목 생성' 버튼 클릭")
print("   4) 콘솔에서 오류 확인 (F12)")

print("\n" + "=" * 60)
print("✅ 테스트 완료. 브라우저에서 직접 확인하세요.")
print("   URL: http://localhost:4007/titles")