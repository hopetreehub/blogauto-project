#!/bin/bash

# 로컬에서 innerbot.inbecs.com 테스트하기

echo "🧪 로컬 테스트 환경 설정..."

# 1. hosts 파일에 임시 도메인 추가
echo "1. hosts 파일 설정 (관리자 권한 필요):"
echo "다음 줄을 /etc/hosts 파일에 추가하세요:"
echo "127.0.0.1    innerbot.inbecs.com"
echo "127.0.0.1    api.innerbot.inbecs.com"
echo ""

# 2. 로컬 서버 실행
echo "2. 로컬 서버 실행:"
echo "터미널 1 - 백엔드:"
echo "cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""
echo "터미널 2 - 프론트엔드:"
echo "cd frontend && npx serve -s build -p 80"
echo ""

echo "3. 테스트 접속:"
echo "브라우저에서 http://innerbot.inbecs.com 접속"
echo ""

echo "⚠️  주의: 이는 임시 테스트용입니다. 실제 배포는 서버에서 해야 합니다."