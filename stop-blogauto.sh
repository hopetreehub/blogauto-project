#!/bin/bash

# 블로그 자동화 시스템 중지 스크립트
echo "🛑 블로그 자동화 시스템 중지 중..."

# 백엔드 프로세스 종료
echo "🔧 백엔드 서버 중지 중..."
pkill -f "python3 real_api_simple.py"
if [ $? -eq 0 ]; then
    echo "✅ 백엔드 서버 중지 완료"
else
    echo "ℹ️ 실행 중인 백엔드 서버가 없습니다"
fi

# 프론트엔드 프로세스 종료
echo "🎨 프론트엔드 서버 중지 중..."
pkill -f "node.*server.js"
pkill -f "next.*dev"
if [ $? -eq 0 ]; then
    echo "✅ 프론트엔드 서버 중지 완료"
else
    echo "ℹ️ 실행 중인 프론트엔드 서버가 없습니다"
fi

# 잠시 대기
sleep 2

# 상태 확인
echo ""
echo "📊 최종 상태 확인:"
BACKEND_RUNNING=$(pgrep -f "python3 real_api_simple.py" | wc -l)
FRONTEND_RUNNING=$(pgrep -f "node.*server.js" | wc -l)

if [ $BACKEND_RUNNING -eq 0 ] && [ $FRONTEND_RUNNING -eq 0 ]; then
    echo "✅ 모든 서비스가 성공적으로 중지되었습니다"
else
    echo "⚠️ 일부 프로세스가 여전히 실행 중일 수 있습니다"
    echo "   백엔드: $BACKEND_RUNNING 개 프로세스"
    echo "   프론트엔드: $FRONTEND_RUNNING 개 프로세스"
fi

echo ""