#!/bin/bash

# 블로그 자동화 시스템 시작 스크립트
echo "🚀 블로그 자동화 시스템 시작 중..."

# 작업 디렉토리 설정
PROJECT_DIR="/mnt/e/project/test-blogauto-project"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/nextjs-app"

# 기존 프로세스 종료
echo "📋 기존 프로세스 정리 중..."
pkill -f "python3 real_api_simple.py" 2>/dev/null
pkill -f "node.*server.js" 2>/dev/null
pkill -f "next.*dev" 2>/dev/null

# 잠시 대기
sleep 2

# 백엔드 서버 시작
echo "🔧 백엔드 API 서버 시작 중..."
cd "$BACKEND_DIR"
nohup python3 real_api_simple.py > backend.log 2>&1 &
BACKEND_PID=$!

# 백엔드 서버 시작 대기
echo "⏳ 백엔드 서버 초기화 대기 중..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ 백엔드 서버 시작 완료 (PID: $BACKEND_PID)"
        break
    fi
    sleep 1
done

# 프론트엔드 서버 시작  
echo "🎨 프론트엔드 서버 시작 중..."
cd "$FRONTEND_DIR"
nohup node server.js > frontend.log 2>&1 &
FRONTEND_PID=$!

# 프론트엔드 서버 시작 대기
echo "⏳ 프론트엔드 서버 초기화 대기 중..."
for i in {1..30}; do
    if curl -s http://localhost:4007 > /dev/null 2>&1; then
        echo "✅ 프론트엔드 서버 시작 완료 (PID: $FRONTEND_PID)"
        break
    fi
    sleep 1
done

echo ""
echo "🎉 블로그 자동화 시스템이 성공적으로 시작되었습니다!"
echo ""
echo "📍 서비스 URL:"
echo "   🌐 프론트엔드: http://localhost:4007"
echo "   🔧 백엔드 API: http://localhost:8000"
echo ""
echo "📊 프로세스 정보:"
echo "   🔧 백엔드 PID: $BACKEND_PID"
echo "   🎨 프론트엔드 PID: $FRONTEND_PID"
echo ""
echo "📝 로그 파일:"
echo "   🔧 백엔드: $BACKEND_DIR/backend.log"
echo "   🎨 프론트엔드: $FRONTEND_DIR/frontend.log"
echo ""
echo "🛑 서비스 중지: $PROJECT_DIR/stop-blogauto.sh"
echo "📊 상태 확인: $PROJECT_DIR/status-blogauto.sh"
echo ""