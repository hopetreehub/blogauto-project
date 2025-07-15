#!/bin/bash

# BlogAuto 배포 스크립트
# 사용법: ./deploy.sh [staging|production] [version]

set -euo pipefail

# 색상 출력을 위한 변수들
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수들
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

# 사용법 출력
usage() {
    echo "Usage: $0 [staging|production] [version]"
    echo "  staging     - Deploy to staging environment"
    echo "  production  - Deploy to production environment"
    echo "  version     - Version tag (e.g., v1.0.0)"
    echo ""
    echo "Examples:"
    echo "  $0 staging v1.0.0"
    echo "  $0 production v1.2.3"
    exit 1
}

# 파라미터 검증
if [ $# -lt 2 ]; then
    log_error "Missing required parameters"
    usage
fi

ENVIRONMENT=$1
VERSION=$2

# 환경 검증
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    usage
fi

# 버전 형식 검증
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log_error "Invalid version format: $VERSION (expected: v1.0.0)"
    exit 1
fi

# 환경 변수 설정
DOCKER_REGISTRY="ghcr.io"
REPO_NAME="blogauto"
BACKEND_IMAGE="${DOCKER_REGISTRY}/${REPO_NAME}:${VERSION}-backend"
FRONTEND_IMAGE="${DOCKER_REGISTRY}/${REPO_NAME}:${VERSION}-frontend"

log_info "Starting deployment to $ENVIRONMENT environment"
log_info "Version: $VERSION"
log_info "Backend Image: $BACKEND_IMAGE"
log_info "Frontend Image: $FRONTEND_IMAGE"

# 필수 도구 확인
check_requirements() {
    log_info "Checking deployment requirements..."
    
    local missing_tools=()
    
    if ! command -v docker &> /dev/null; then
        missing_tools+=("docker")
    fi
    
    if ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    fi
    
    if ! command -v helm &> /dev/null; then
        missing_tools+=("helm")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "All required tools are available"
}

# Docker 이미지 존재 확인
verify_images() {
    log_info "Verifying Docker images..."
    
    if ! docker manifest inspect "$BACKEND_IMAGE" &> /dev/null; then
        log_error "Backend image not found: $BACKEND_IMAGE"
        exit 1
    fi
    
    if ! docker manifest inspect "$FRONTEND_IMAGE" &> /dev/null; then
        log_error "Frontend image not found: $FRONTEND_IMAGE"
        exit 1
    fi
    
    log_success "Docker images verified"
}

# Kubernetes 클러스터 연결 확인
verify_kubernetes() {
    log_info "Verifying Kubernetes connection..."
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # 네임스페이스 확인/생성
    if ! kubectl get namespace "$ENVIRONMENT" &> /dev/null; then
        log_info "Creating namespace: $ENVIRONMENT"
        kubectl create namespace "$ENVIRONMENT"
    fi
    
    log_success "Kubernetes connection verified"
}

# 환경별 설정 로드
load_environment_config() {
    log_info "Loading $ENVIRONMENT configuration..."
    
    case $ENVIRONMENT in
        staging)
            export DATABASE_HOST="staging-db.blogauto.com"
            export REDIS_HOST="staging-redis.blogauto.com"
            export REPLICAS=2
            export STRATEGY="rolling"
            ;;
        production)
            export DATABASE_HOST="prod-db.blogauto.com"
            export REDIS_HOST="prod-redis.blogauto.com"
            export REPLICAS=3
            export STRATEGY="blue-green"
            ;;
    esac
    
    log_success "Environment configuration loaded"
}

# 백업 생성 (프로덕션만)
create_backup() {
    if [ "$ENVIRONMENT" = "production" ]; then
        log_info "Creating production backup..."
        
        # 데이터베이스 백업
        kubectl exec -n production deployment/postgres -- pg_dump blogauto_production > "backup_${VERSION}_$(date +%Y%m%d_%H%M%S).sql"
        
        # 현재 배포 상태 백업
        kubectl get all -n production -o yaml > "k8s_state_${VERSION}_$(date +%Y%m%d_%H%M%S).yaml"
        
        log_success "Backup created"
    fi
}

# 배포 실행
deploy_application() {
    log_info "Deploying application with $STRATEGY strategy..."
    
    # Helm 값 파일 생성
    cat > values-${ENVIRONMENT}.yaml << EOF
environment: ${ENVIRONMENT}
version: ${VERSION}

backend:
  image: ${BACKEND_IMAGE}
  replicas: ${REPLICAS}
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"

frontend:
  image: ${FRONTEND_IMAGE}
  replicas: ${REPLICAS}
  resources:
    requests:
      cpu: "250m"
      memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "2Gi"

database:
  host: ${DATABASE_HOST}
  
redis:
  host: ${REDIS_HOST}

monitoring:
  enabled: true
  
security:
  networkPolicies: true
EOF

    # Helm 배포
    if [ "$STRATEGY" = "blue-green" ]; then
        deploy_blue_green
    else
        deploy_rolling
    fi
    
    log_success "Application deployed"
}

# Rolling 배포
deploy_rolling() {
    log_info "Performing rolling deployment..."
    
    helm upgrade --install blogauto-${ENVIRONMENT} ./helm-chart \
        --namespace $ENVIRONMENT \
        --values values-${ENVIRONMENT}.yaml \
        --wait \
        --timeout 600s
}

# Blue-Green 배포
deploy_blue_green() {
    log_info "Performing blue-green deployment..."
    
    # Green 환경 배포
    helm upgrade --install blogauto-${ENVIRONMENT}-green ./helm-chart \
        --namespace $ENVIRONMENT \
        --values values-${ENVIRONMENT}.yaml \
        --set nameOverride="blogauto-green" \
        --wait \
        --timeout 600s
    
    # 헬스체크 대기
    log_info "Waiting for green environment health check..."
    sleep 30
    
    # 트래픽 전환
    log_info "Switching traffic to green environment..."
    kubectl patch service blogauto-${ENVIRONMENT} -n $ENVIRONMENT -p '{"spec":{"selector":{"app":"blogauto-green"}}}'
    
    # Blue 환경 정리 (5분 후)
    log_info "Scheduling blue environment cleanup..."
    (sleep 300 && kubectl delete deployment blogauto-${ENVIRONMENT}-blue -n $ENVIRONMENT --ignore-not-found=true) &
}

# 헬스체크 실행
health_check() {
    log_info "Running health checks..."
    
    local service_url
    case $ENVIRONMENT in
        staging)
            service_url="https://staging.blogauto.com"
            ;;
        production)
            service_url="https://blogauto.com"
            ;;
    esac
    
    # API 헬스체크
    for i in {1..30}; do
        if curl -f "${service_url}/api/health" &> /dev/null; then
            log_success "API health check passed"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "API health check failed after 30 attempts"
            exit 1
        fi
        
        log_info "Health check attempt $i/30 failed, retrying in 10 seconds..."
        sleep 10
    done
    
    # 프론트엔드 헬스체크
    if curl -f "$service_url" &> /dev/null; then
        log_success "Frontend health check passed"
    else
        log_warning "Frontend health check failed"
    fi
}

# 배포 후 테스트
post_deployment_tests() {
    log_info "Running post-deployment tests..."
    
    # API 기능 테스트
    local service_url
    case $ENVIRONMENT in
        staging)
            service_url="https://staging.blogauto.com"
            ;;
        production)
            service_url="https://blogauto.com"
            ;;
    esac
    
    # Rate limiting 테스트
    if curl -f "${service_url}/api/admin/rate-limit-stats" &> /dev/null; then
        log_success "Rate limiting endpoint test passed"
    else
        log_warning "Rate limiting endpoint test failed"
    fi
    
    # 암호화 시스템 테스트
    if curl -f "${service_url}/api/secure/list-keys" &> /dev/null; then
        log_success "Crypto system endpoint test passed"
    else
        log_warning "Crypto system endpoint test failed"
    fi
    
    log_success "Post-deployment tests completed"
}

# 모니터링 설정
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Prometheus 규칙 업데이트
    kubectl apply -f monitoring/prometheus-rules-${ENVIRONMENT}.yaml
    
    # Grafana 대시보드 업데이트
    kubectl apply -f monitoring/grafana-dashboard-${ENVIRONMENT}.yaml
    
    log_success "Monitoring configured"
}

# 롤백 함수
rollback() {
    log_warning "Initiating rollback..."
    
    # 이전 버전으로 롤백
    helm rollback blogauto-${ENVIRONMENT} -n $ENVIRONMENT
    
    log_success "Rollback completed"
}

# 정리
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f values-${ENVIRONMENT}.yaml
    log_success "Cleanup completed"
}

# 트랩 설정 (스크립트 중단 시 정리)
trap cleanup EXIT

# 메인 실행 흐름
main() {
    log_info "🚀 Starting BlogAuto deployment process"
    
    check_requirements
    verify_images
    verify_kubernetes
    load_environment_config
    create_backup
    deploy_application
    health_check
    post_deployment_tests
    setup_monitoring
    
    log_success "🎉 Deployment completed successfully!"
    log_info "Environment: $ENVIRONMENT"
    log_info "Version: $VERSION"
    log_info "Backend Image: $BACKEND_IMAGE"
    log_info "Frontend Image: $FRONTEND_IMAGE"
}

# 스크립트 실행
main