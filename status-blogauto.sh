#!/bin/bash

# 블로그 자동화 시스템 상태 확인 스크립트
echo "📊 블로그 자동화 시스템 상태 확인"
echo "========================================"

# 프로세스 상태 확인
echo ""
echo "🔧 백엔드 서버 상태:"
BACKEND_PID=$(pgrep -f "python3 real_api_simple.py")
if [ ! -z "$BACKEND_PID" ]; then
    echo "   ✅ 실행 중 (PID: $BACKEND_PID)"
    
    # API 헬스 체크
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "   ✅ API 응답 정상"
    else
        echo "   ⚠️ API 응답 없음"
    fi
else
    echo "   ❌ 중지됨"
fi

echo ""
echo "🎨 프론트엔드 서버 상태:"
FRONTEND_PID=$(pgrep -f "node.*server.js")
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   ✅ 실행 중 (PID: $FRONTEND_PID)"
    
    # 웹 서버 체크
    if curl -s http://localhost:4007 > /dev/null 2>&1; then
        echo "   ✅ 웹 서버 응답 정상"
    else
        echo "   ⚠️ 웹 서버 응답 없음"
    fi
else
    echo "   ❌ 중지됨"
fi

# 포트 사용 상태 확인
echo ""
echo "🌐 포트 사용 상태:"
PORT_8000=$(lsof -ti:8000 2>/dev/null | wc -l)
PORT_4007=$(lsof -ti:4007 2>/dev/null | wc -l)

if [ $PORT_8000 -gt 0 ]; then
    echo "   ✅ 포트 8000 (백엔드): 사용 중"
else
    echo "   ❌ 포트 8000 (백엔드): 사용 안함"
fi

if [ $PORT_4007 -gt 0 ]; then
    echo "   ✅ 포트 4007 (프론트엔드): 사용 중"
else
    echo "   ❌ 포트 4007 (프론트엔드): 사용 안함"
fi

# 전체 시스템 상태
echo ""
echo "🎯 전체 시스템 상태:"
if [ ! -z "$BACKEND_PID" ] && [ ! -z "$FRONTEND_PID" ] && [ $PORT_8000 -gt 0 ] && [ $PORT_4007 -gt 0 ]; then
    echo "   ✅ 모든 서비스 정상 운영 중"
    echo ""
    echo "📍 접속 URL:"
    echo "   🌐 메인 서비스: http://localhost:4007"
    echo "   🔧 API 서버: http://localhost:8000"
elif [ ! -z "$BACKEND_PID" ] || [ ! -z "$FRONTEND_PID" ]; then
    echo "   ⚠️ 일부 서비스만 실행 중"
else
    echo "   ❌ 모든 서비스 중지됨"
fi

# 리소스 사용량
echo ""
echo "📈 리소스 사용량:"
if [ ! -z "$BACKEND_PID" ]; then
    BACKEND_CPU=$(ps -p $BACKEND_PID -o %cpu --no-headers 2>/dev/null | tr -d ' ')
    BACKEND_MEM=$(ps -p $BACKEND_PID -o %mem --no-headers 2>/dev/null | tr -d ' ')
    echo "   🔧 백엔드: CPU ${BACKEND_CPU}%, MEM ${BACKEND_MEM}%"
fi

if [ ! -z "$FRONTEND_PID" ]; then
    FRONTEND_CPU=$(ps -p $FRONTEND_PID -o %cpu --no-headers 2>/dev/null | tr -d ' ')
    FRONTEND_MEM=$(ps -p $FRONTEND_PID -o %mem --no-headers 2>/dev/null | tr -d ' ')
    echo "   🎨 프론트엔드: CPU ${FRONTEND_CPU}%, MEM ${FRONTEND_MEM}%"
fi

echo ""