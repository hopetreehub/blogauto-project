#!/bin/bash

# Blog Auto Project 배포 스크립트
# 프로덕션 환경을 위한 자동 배포 스크립트

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 메인 배포 함수
deploy() {
    log_info "🚀 Blog Auto Project 배포를 시작합니다..."
    
    # 1. 환경 확인
    log_info "환경 확인 중..."
    if ! command -v node &> /dev/null; then
        log_error "Node.js가 설치되어 있지 않습니다."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되어 있지 않습니다."
        exit 1
    fi
    
    # 2. 프론트엔드 빌드
    log_info "프론트엔드 빌드 중..."
    cd frontend
    npm install
    npm run build
    cd ..
    log_success "프론트엔드 빌드 완료"
    
    # 3. 백엔드 환경 설정
    log_info "백엔드 환경 설정 중..."
    cd backend
    
    # 가상환경이 없으면 생성
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    log_success "백엔드 환경 설정 완료"
    
    # 4. Docker Compose 배포
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose로 배포 중..."
        docker-compose up -d --build
        log_success "Docker 컨테이너 배포 완료"
    else
        log_warning "Docker Compose가 설치되어 있지 않습니다. 수동 배포를 계속합니다."
        
        # 5. 수동 서비스 시작
        log_info "백엔드 서버 시작 중..."
        cd backend
        source venv/bin/activate
        nohup uvicorn main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
        cd ..
        
        log_info "프론트엔드 서버 시작 중..."
        cd frontend
        nohup npx serve -s build -l 3000 > frontend.log 2>&1 &
        cd ..
    fi
    
    # 6. 배포 상태 확인
    log_info "배포 상태 확인 중..."
    sleep 5
    
    # 백엔드 상태 확인
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "백엔드 서버가 정상적으로 실행 중입니다."
    else
        log_error "백엔드 서버 실행에 실패했습니다."
    fi
    
    # 프론트엔드 상태 확인
    if curl -s http://localhost:3000 > /dev/null; then
        log_success "프론트엔드 서버가 정상적으로 실행 중입니다."
    else
        log_warning "프론트엔드 서버 상태를 확인할 수 없습니다."
    fi
    
    # 7. 배포 완료 안내
    log_success "🎉 배포가 완료되었습니다!"
    echo ""
    echo "접속 주소:"
    echo "  - 프론트엔드: http://localhost:3000"
    echo "  - 백엔드 API: http://localhost:8000"
    echo "  - API 문서: http://localhost:8000/docs"
    echo ""
    echo "로그 파일:"
    echo "  - 백엔드: backend/server.log"
    echo "  - 프론트엔드: frontend/frontend.log"
}

# 옵션 처리
case "${1:-}" in
    "stop")
        log_info "서비스 중지 중..."
        if command -v docker-compose &> /dev/null; then
            docker-compose down
        else
            pkill -f "uvicorn main:app" || true
            pkill -f "serve -s build" || true
        fi
        log_success "서비스가 중지되었습니다."
        ;;
    "restart")
        $0 stop
        sleep 2
        $0
        ;;
    "logs")
        if [ -f "backend/server.log" ]; then
            echo "=== 백엔드 로그 ==="
            tail -f backend/server.log
        fi
        ;;
    *)
        deploy
        ;;
esac