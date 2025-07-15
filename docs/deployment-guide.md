# BlogAuto 배포 가이드

## 📋 목차

1. [배포 전 준비사항](#배포-전-준비사항)
2. [프로덕션 환경 설정](#프로덕션-환경-설정)
3. [Docker 배포](#docker-배포)
4. [클라우드 플랫폼 배포](#클라우드-플랫폼-배포)
5. [모니터링 설정](#모니터링-설정)
6. [백업 및 복구](#백업-및-복구)
7. [트러블슈팅](#트러블슈팅)

## 🚀 배포 전 준비사항

### 1. 시스템 요구사항

**최소 사양**:
- CPU: 2 vCPU
- Memory: 4GB RAM
- Storage: 20GB SSD
- Network: 100Mbps

**권장 사양**:
- CPU: 4 vCPU
- Memory: 8GB RAM
- Storage: 50GB SSD
- Network: 1Gbps

### 2. 필수 소프트웨어

```bash
# Docker 설치 확인
docker --version  # Docker version 20.10.0 이상
docker-compose --version  # Docker Compose version 1.29.0 이상

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 패키지 설치
sudo apt install -y git curl wget htop
```

### 3. 도메인 및 SSL 준비

- 도메인 이름 준비 (예: blog.example.com)
- SSL 인증서 준비 (Let's Encrypt 권장)

## 🔧 프로덕션 환경 설정

### 1. 환경 변수 설정

```bash
# .env.production 파일 생성
cp .env.example .env.production
```

**필수 환경 변수 설정**:

```bash
# 기본 설정
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API Keys (필수)
OPENAI_API_KEY=sk-prod-xxx
GOOGLE_API_KEY=AIzaSy-prod-xxx
GOOGLE_CSE_ID=prod-cse-id
UNSPLASH_ACCESS_KEY=prod-unsplash-key

# Database
DATABASE_URL=postgresql://blogauto:secure_password@postgres:5432/blogauto_prod
DB_USER=blogauto
DB_PASSWORD=very_secure_password_here
DB_NAME=blogauto_prod

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_password

# Security
SECRET_KEY=$(openssl rand -hex 32)
MASTER_PASSWORD=$(openssl rand -base64 32)
ALLOWED_HOSTS=blog.example.com,www.blog.example.com
CORS_ORIGINS=https://blog.example.com,https://www.blog.example.com

# WordPress
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=admin
WORDPRESS_PASSWORD=wp_secure_password

# Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
GRAFANA_USER=admin
GRAFANA_PASSWORD=grafana_secure_password

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Performance
WORKERS=4
WORKER_CONNECTIONS=1000
CACHE_TTL=3600
```

### 2. 프로덕션 Docker Compose 설정

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  backend:
    image: blogauto/backend:latest
    container_name: blogauto-backend
    restart: always
    env_file: .env.production
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    command: >
      sh -c "
        python -m alembic upgrade head &&
        gunicorn real_api_simple:app
          --workers ${WORKERS:-4}
          --worker-class uvicorn.workers.UvicornWorker
          --bind 0.0.0.0:8000
          --access-logfile /app/logs/access.log
          --error-logfile /app/logs/error.log
          --log-level ${LOG_LEVEL:-info}
      "
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    image: blogauto/frontend:latest
    container_name: blogauto-frontend
    restart: always
    env_file: .env.production
    ports:
      - "3000:3000"
    depends_on:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: blogauto-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend

  postgres:
    image: postgres:15-alpine
    container_name: blogauto-postgres
    restart: always
    env_file: .env.production
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups/postgres:/backups
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8"
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    container_name: blogauto-redis
    restart: always
    command: >
      redis-server
        --requirepass ${REDIS_PASSWORD}
        --maxmemory 512mb
        --maxmemory-policy allkeys-lru
        --save 900 1
        --save 300 10
        --save 60 10000
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: blogauto-network
```

### 3. Nginx 설정

```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 로깅 설정
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;

    # 성능 최적화
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 50M;

    # gzip 압축
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;

    # SSL 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HTTP to HTTPS 리다이렉트
    server {
        listen 80;
        server_name blog.example.com www.blog.example.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS 서버
    server {
        listen 443 ssl http2;
        server_name blog.example.com www.blog.example.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # 보안 헤더
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Frontend
        location / {
            proxy_pass http://frontend:3000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            
            # Rate limiting
            limit_req zone=general_limit burst=20 nodelay;
        }

        # Backend API
        location /api {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Rate limiting for API
            limit_req zone=api_limit burst=5 nodelay;
            
            # Timeout 설정
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 정적 파일
        location /static {
            alias /app/static;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # 헬스체크
        location /health {
            access_log off;
            proxy_pass http://backend:8000/health;
        }
    }
}
```

## 🐳 Docker 배포

### 1. 이미지 빌드

```bash
# Backend 이미지 빌드
cd backend
docker build -t blogauto/backend:latest .

# Frontend 이미지 빌드
cd ../frontend
docker build -t blogauto/frontend:latest .

# 또는 빌드 스크립트 사용
./scripts/build-images.sh
```

### 2. 배포 실행

```bash
# 프로덕션 환경으로 배포
docker-compose -f docker-compose.production.yml up -d

# 로그 확인
docker-compose -f docker-compose.production.yml logs -f

# 상태 확인
docker-compose -f docker-compose.production.yml ps
```

### 3. 데이터베이스 초기화

```bash
# 데이터베이스 마이그레이션
docker-compose -f docker-compose.production.yml exec backend python -m alembic upgrade head

# 초기 데이터 설정 (필요 시)
docker-compose -f docker-compose.production.yml exec backend python scripts/init_data.py
```

## ☁️ 클라우드 플랫폼 배포

### AWS EC2 배포

1. **EC2 인스턴스 생성**:
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (최소) / t3.large (권장)
   - Storage: 50GB gp3
   - Security Group: 80, 443, 22 포트 개방

2. **배포 스크립트**:

```bash
#!/bin/bash
# deploy-aws.sh

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 프로젝트 클론
git clone https://github.com/your-org/test-blogauto-project.git
cd test-blogauto-project

# 환경 변수 설정
cp .env.example .env.production
# 편집기로 .env.production 수정

# SSL 인증서 설정 (Let's Encrypt)
sudo apt install -y certbot
sudo certbot certonly --standalone -d blog.example.com -d www.blog.example.com

# 배포 실행
docker-compose -f docker-compose.production.yml up -d
```

### Google Cloud Platform 배포

1. **Compute Engine 인스턴스 생성**:
   - Machine Type: e2-standard-2 (최소) / e2-standard-4 (권장)
   - Boot Disk: Ubuntu 22.04 LTS, 50GB
   - Firewall: HTTP, HTTPS 허용

2. **Cloud SQL 연동** (선택사항):

```bash
# Cloud SQL Proxy 설치
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy

# 연결 설정
./cloud_sql_proxy -instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432 &
```

### Kubernetes 배포

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blogauto-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: blogauto-backend
  template:
    metadata:
      labels:
        app: blogauto-backend
    spec:
      containers:
      - name: backend
        image: blogauto/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: blogauto-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: blogauto-backend
spec:
  selector:
    app: blogauto-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

## 📊 모니터링 설정

### 1. 모니터링 스택 배포

```bash
# 모니터링 스택 시작
docker-compose -f docker-compose.monitoring.yml up -d

# Grafana 대시보드 임포트
curl -X POST http://admin:admin@localhost:3001/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d @monitoring/dashboards/blogauto-dashboard.json
```

### 2. 알림 설정

```yaml
# prometheus/alert.rules.yml
groups:
  - name: blogauto
    rules:
      - alert: HighErrorRate
        expr: rate(blogauto_api_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for 5 minutes"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(blogauto_api_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          description: "95th percentile response time is above 2 seconds"
```

## 💾 백업 및 복구

### 1. 자동 백업 설정

```bash
# backup.sh
#!/bin/bash

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# PostgreSQL 백업
docker-compose -f docker-compose.production.yml exec -T postgres \
  pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/postgres_backup.sql.gz

# Redis 백업
docker-compose -f docker-compose.production.yml exec -T redis \
  redis-cli --rdb /data/dump.rdb BGSAVE

# 업로드 파일 백업
tar -czf $BACKUP_DIR/uploads_backup.tar.gz ./uploads/

# S3 업로드 (선택사항)
aws s3 sync $BACKUP_DIR s3://your-backup-bucket/blogauto/$BACKUP_DIR

# 오래된 백업 삭제 (30일 이상)
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

### 2. 복구 절차

```bash
# PostgreSQL 복구
gunzip < /backups/20250712/postgres_backup.sql.gz | \
  docker-compose -f docker-compose.production.yml exec -T postgres \
  psql -U $DB_USER $DB_NAME

# Redis 복구
docker-compose -f docker-compose.production.yml exec redis \
  redis-cli --rdb /data/dump.rdb shutdown nosave
docker cp /backups/20250712/dump.rdb blogauto-redis:/data/dump.rdb
docker-compose -f docker-compose.production.yml restart redis

# 업로드 파일 복구
tar -xzf /backups/20250712/uploads_backup.tar.gz -C ./
```

## 🔧 트러블슈팅

### 1. 일반적인 문제 해결

**서비스가 시작되지 않음**:
```bash
# 로그 확인
docker-compose -f docker-compose.production.yml logs backend

# 권한 문제 해결
sudo chown -R $USER:$USER .
chmod -R 755 ./logs ./uploads
```

**메모리 부족**:
```bash
# Docker 메모리 제한 확인
docker stats

# 스왑 메모리 추가
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**데이터베이스 연결 실패**:
```bash
# 연결 테스트
docker-compose -f docker-compose.production.yml exec backend \
  python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); engine.connect()"

# PostgreSQL 로그 확인
docker-compose -f docker-compose.production.yml logs postgres
```

### 2. 성능 튜닝

```bash
# PostgreSQL 튜닝
docker-compose -f docker-compose.production.yml exec postgres \
  psql -U $DB_USER -c "ALTER SYSTEM SET shared_buffers = '256MB';"
  
# Redis 메모리 정책
docker-compose -f docker-compose.production.yml exec redis \
  redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### 3. 보안 강화

```bash
# 방화벽 설정
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# fail2ban 설치
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📝 체크리스트

배포 전 확인사항:

- [ ] 모든 환경 변수가 프로덕션 값으로 설정되었는가?
- [ ] SSL 인증서가 올바르게 설정되었는가?
- [ ] 데이터베이스 백업이 설정되었는가?
- [ ] 모니터링 및 알림이 작동하는가?
- [ ] 로그 로테이션이 설정되었는가?
- [ ] 보안 그룹/방화벽이 올바르게 설정되었는가?
- [ ] 헬스체크가 정상 작동하는가?
- [ ] 자동 재시작이 설정되었는가?

## 🔗 관련 문서

- [모니터링 가이드](./monitoring-guide.md)
- [보안 가이드](./security-guide.md)
- [성능 가이드](./performance-guide.md)
- [백업 가이드](./backup-guide.md)

---

**마지막 업데이트**: 2025년 7월 12일  
**버전**: v1.0.0  
**담당자**: BlogAuto 개발팀