#!/bin/bash

# 블로그 자동화 시스템 - 개인용 빠른 시작 스크립트
echo "🚀 블로그 자동화 시스템 - 개인용 설정 시작"
echo "================================================"

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Python 버전 확인
echo -e "\n${YELLOW}1. Python 버전 확인중...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python3가 설치되어 있지 않습니다. 먼저 Python 3.8+ 를 설치하세요.${NC}"
    exit 1
fi

# 2. 백엔드 디렉토리로 이동
cd backend

# 3. .env 파일 생성
echo -e "\n${YELLOW}2. 환경 설정 파일 생성중...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env 파일이 생성되었습니다.${NC}"
    echo -e "${YELLOW}⚠️  중요: backend/.env 파일을 열어서 다음 API 키를 설정하세요:${NC}"
    echo "   - OPENAI_API_KEY: OpenAI API 키 (필수)"
    echo "   - GEMINI_API_KEY: Google Gemini API 키 (선택)"
    echo "   - NAVER_CLIENT_ID/SECRET: 네이버 API (선택)"
else
    echo -e "${GREEN}✓ .env 파일이 이미 존재합니다.${NC}"
fi

# 4. 가상환경 생성
echo -e "\n${YELLOW}3. Python 가상환경 설정중...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ 가상환경이 생성되었습니다.${NC}"
else
    echo -e "${GREEN}✓ 가상환경이 이미 존재합니다.${NC}"
fi

# 5. 가상환경 활성화 및 패키지 설치
echo -e "\n${YELLOW}4. 필요한 패키지 설치중... (2-3분 소요)${NC}"
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
pip install pydantic-settings

# 6. 데이터베이스 초기화
echo -e "\n${YELLOW}5. 데이터베이스 초기화중...${NC}"
python3 -c "
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)
print('✓ 데이터베이스가 초기화되었습니다.')
" 2>/dev/null || echo -e "${YELLOW}⚠️  데이터베이스는 서버 첫 실행시 자동으로 생성됩니다.${NC}"

# 7. 실행 명령어 안내
echo -e "\n${GREEN}================================================"
echo -e "✅ 개인용 설정이 완료되었습니다!"
echo -e "================================================${NC}"
echo -e "\n${YELLOW}📋 다음 단계:${NC}"
echo -e "1. API 키 설정: ${GREEN}backend/.env${NC} 파일을 열어서 API 키를 입력하세요"
echo -e "2. 서버 실행: ${GREEN}cd backend && source venv/bin/activate && python -m uvicorn main:app --reload${NC}"
echo -e "3. 브라우저에서 접속: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}💡 팁:${NC}"
echo -e "- Swagger UI에서 모든 API를 테스트할 수 있습니다"
echo -e "- 먼저 /auth/register로 계정을 만드세요"
echo -e "- 그 다음 /auth/login으로 로그인하세요"
echo -e "- 받은 토큰을 Swagger UI의 Authorize 버튼에 입력하세요"
echo -e "\n${GREEN}즐거운 블로깅 되세요! 🚀${NC}"