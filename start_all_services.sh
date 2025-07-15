#!/bin/bash
echo "🚀 BlogAuto 서비스 시작..."

# 현재 디렉토리로 이동
cd /mnt/e/project/test-blogauto-project

# 기존 프로세스 정리 (선택사항)
echo "기존 프로세스 확인 중..."
pkill -f "python3 real_api_simple.py" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true

# 백엔드 시작
echo "📡 백엔드 API 서버 시작..."
cd backend
nohup python3 real_api_simple.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 백엔드 시작됨 (PID: $BACKEND_PID)"

# 프론트엔드 시작  
echo "🌐 프론트엔드 서버 시작..."
cd ../nextjs-app
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 프론트엔드 시작됨 (PID: $FRONTEND_PID)"

# 서비스 상태 확인
sleep 5
echo ""
echo "🔍 서비스 상태 확인:"
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ 백엔드 API: 정상 작동 (포트 8000)"
else
    echo "❌ 백엔드 API: 연결 실패"
fi

if curl -s http://localhost:4007 > /dev/null; then
    echo "✅ 프론트엔드: 정상 작동 (포트 4007)"
else
    echo "❌ 프론트엔드: 연결 실패"
fi

echo ""
echo "🎉 BlogAuto 시스템 준비 완료!"
echo "📋 접속 정보:"
echo "   메인 페이지: http://172.24.194.195:4007"
echo "   백엔드 API: http://172.24.194.195:8000"
echo ""
echo "📝 테스트 페이지:"
echo "   콘텐츠 생성: http://172.24.194.195:4007/content"
echo "   키워드 분석: http://172.24.194.195:4007/keywords"
echo "   제목 생성: http://172.24.194.195:4007/titles"
echo "   지침 관리: http://172.24.194.195:4007/guidelines"
echo ""
echo "💡 설정 페이지에서 OpenAI API 키를 입력하세요!"
echo "⚠️  서비스 중지: pkill -f 'python3 real_api_simple.py' && pkill -f 'next dev'"