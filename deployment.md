# Blog Auto Project 배포 가이드

## 🚀 빠른 시작

### 자동 배포 (권장)
```bash
# 프로젝트 루트에서 실행
./deploy-script.sh
```

### 서비스 관리
```bash
# 서비스 중지
./deploy-script.sh stop

# 서비스 재시작
./deploy-script.sh restart

# 로그 확인
./deploy-script.sh logs
```

## 🐳 Docker 배포

### Docker Compose 사용
```bash
# Docker 컨테이너로 실행
docker-compose up -d --build

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

## 🔧 수동 배포

### 1. 환경 준비
```bash
# Node.js 18+ 설치 확인
node --version

# Python 3.11+ 설치 확인
python3 --version

# Docker (선택사항) 설치 확인
docker --version
```

### 2. 프론트엔드 배포
```bash
cd frontend
npm install
npm run build

# 빌드된 파일 서빙 (개발용)
npx serve -s build -l 3000
```

### 3. 백엔드 배포
```bash
cd backend

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에서 실제 API 키 설정

# 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🌐 프로덕션 배포

### DNS 설정
```
Type: A
Name: your-domain.com
Content: YOUR_SERVER_IP

Type: A  
Name: api.your-domain.com
Content: YOUR_SERVER_IP
```

### Nginx 설정
```nginx
# /etc/nginx/sites-available/blogauto
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/blogauto/frontend/build;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 80;
    server_name api.your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL 인증서
```bash
# Let's Encrypt 인증서 설치
sudo certbot --nginx -d your-domain.com -d api.your-domain.com
```

### 서비스 등록 (systemd)
```bash
# /etc/systemd/system/blogauto-api.service
[Unit]
Description=Blog Auto API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/blogauto/backend
Environment=PATH=/var/www/blogauto/backend/venv/bin
ExecStart=/var/www/blogauto/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 시작
sudo systemctl enable blogauto-api
sudo systemctl start blogauto-api
sudo systemctl status blogauto-api
```

## 🔧 환경 변수

### 프론트엔드 (.env.production)
```bash
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_DOMAIN=your-domain.com
NODE_ENV=production
```

### 백엔드 (.env)
```bash
# 데이터베이스
DATABASE_URL=sqlite:///./blogauto.db

# JWT 설정
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI API Keys
OPENAI_API_KEY=sk-your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# 키워드 분석 API
SEMRUSH_API_KEY=your-semrush-key
AHREFS_API_KEY=your-ahrefs-key
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret

# CORS 설정
ALLOWED_ORIGINS=https://your-domain.com,http://localhost:3000
```

## ✅ 배포 체크리스트

### 배포 전
- [ ] 모든 API 키가 설정되었는지 확인
- [ ] 데이터베이스 파일 권한 확인
- [ ] CORS 설정에 도메인 추가
- [ ] 프론트엔드 빌드 성공 확인
- [ ] 백엔드 의존성 설치 완료

### 배포 후
- [ ] 프론트엔드 사이트 접속 확인
- [ ] 백엔드 API 응답 확인 (/health)
- [ ] 회원가입/로그인 테스트
- [ ] 키워드 분석 기능 테스트
- [ ] 제목 생성 기능 테스트
- [ ] 콘텐츠 생성 기능 테스트
- [ ] 자동 포스팅 기능 테스트

## 🧪 테스트

### 로컬 테스트
```bash
# 백엔드 API 테스트
curl http://localhost:8000/health

# 프론트엔드 접속 테스트
curl http://localhost:3000
```

### 프로덕션 테스트
```bash
# API 응답 테스트
curl https://api.your-domain.com/health

# 웹사이트 접속 테스트
curl https://your-domain.com
```

## 🔍 문제 해결

### 로그 확인
```bash
# 백엔드 로그
tail -f backend/server.log

# 프론트엔드 로그  
tail -f frontend/frontend.log

# Docker 로그
docker-compose logs -f
```

### 일반적인 문제
1. **CORS 오류**: .env의 ALLOWED_ORIGINS 확인
2. **API 키 오류**: OpenAI/Gemini API 키 유효성 확인
3. **데이터베이스 오류**: 파일 권한 및 경로 확인
4. **포트 충돌**: 8000, 3000 포트 사용 중인지 확인

## 📱 접속 주소

### 로컬 개발
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 프로덕션
- 프론트엔드: https://your-domain.com
- 백엔드 API: https://api.your-domain.com
- API 문서: https://api.your-domain.com/docs