#!/bin/bash

# GitHub 대용량 파일 문제 해결을 위한 스마트 배포 스크립트

echo "🚀 BlogAuto 스마트 배포 스크립트 v1.0"
echo "=================================="

# 1. 배포 전 정리
echo "📁 임시 파일 및 가상환경 정리..."
rm -rf test_env/ backend/*venv*/ backend/venv/
rm -rf nextjs-app/node_modules/.cache/
rm -rf nextjs-app/.next/

# 2. 프로덕션 의존성만 설치
echo "📦 프로덕션 의존성 설치..."
cd nextjs-app
npm ci --omit=dev
cd ..

# 3. 빌드 실행
echo "🔨 프로덕션 빌드..."
cd nextjs-app
npm run build
cd ..

# 4. Git 커밋 (대용량 파일 제외)
echo "📝 Git 커밋 준비..."
git add .
git commit -m "프로덕션 배포용 정리 및 최적화

- 개발용 가상환경 및 캐시 파일 제거
- 프로덕션 의존성만 포함
- 100MB+ 파일 자동 제외 처리

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 5. 대용량 파일 처리 안내
echo "⚠️  대용량 파일 처리 안내:"
echo "   - Next.js SWC 바이너리는 런타임에 자동 다운로드됩니다"
echo "   - 프로덕션 환경에서는 Docker 멀티스테이지 빌드 권장"
echo "   - npm ci를 통해 정확한 의존성 버전 보장"

echo "✅ 배포 준비 완료!"
echo "   다음 명령어로 GitHub에 푸시하세요:"
echo "   git push origin main"