# 🚀 블로그 자동화 시스템 - 개인 사용 가이드

## 📋 5분 만에 시작하기

### 1️⃣ 빠른 설정 (1분)
```bash
# 프로젝트 폴더에서 실행
./quick-start.sh
```

### 2️⃣ API 키 설정 (2분)
`backend/.env` 파일을 열어서 최소 하나의 AI API 키를 입력:

```env
# 필수: OpenAI 또는 Gemini 중 하나
OPENAI_API_KEY=sk-실제키입력
# 또는
GEMINI_API_KEY=실제키입력
```

**API 키 얻는 방법:**
- OpenAI: https://platform.openai.com/api-keys
- Gemini: https://makersuite.google.com/app/apikey

### 3️⃣ 서버 실행 (1분)
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn main:app --reload
```

### 4️⃣ 첫 사용 (1분)
1. 브라우저에서 http://localhost:8000/docs 접속
2. **POST /auth/register** 클릭 → Try it out → 계정 생성
3. **POST /auth/login** 클릭 → 로그인
4. 받은 토큰을 복사해서 상단 **Authorize** 버튼 클릭 → 붙여넣기

## 🎯 주요 기능 사용법

### 1. 키워드 분석
```
POST /api/v1/keywords/analyze
{
  "keyword": "파이썬 프로그래밍",
  "include_trends": true
}
```

### 2. AI 제목 생성
```
POST /api/v1/titles/generate
{
  "keyword": "파이썬 프로그래밍",
  "count": 5,
  "style": "viral"  // viral, professional, casual
}
```

### 3. 콘텐츠 생성
```
POST /api/v1/content/generate
{
  "title": "파이썬으로 10분 만에 웹 스크래퍼 만들기",
  "keywords": ["파이썬", "웹스크래핑", "BeautifulSoup"],
  "tone": "friendly",
  "length": "medium"
}
```

### 4. WordPress 자동 포스팅
```
# 1. 먼저 사이트 등록
POST /api/v1/sites
{
  "name": "내 블로그",
  "url": "https://myblog.com",
  "username": "admin",
  "application_password": "wordpress-app-password"
}

# 2. 자동 포스팅
POST /api/v1/wordpress/post
{
  "site_id": 1,
  "title": "제목",
  "content": "내용",
  "status": "draft"  // draft 또는 publish
}
```

## 💡 개인 사용 팁

### 1. 비용 절약 팁
- OpenAI API는 사용량 기반 과금 (포스트당 약 $0.02~0.05)
- 월 $5 정도면 100~200개 포스트 생성 가능
- Gemini API는 무료 티어 제공 (일 60회)

### 2. 효율적인 워크플로우
```
1. 키워드 분석 → 트렌드 파악
2. 제목 5개 생성 → 베스트 선택
3. 콘텐츠 생성 → 편집
4. WordPress 초안 저장 → 최종 검토 후 발행
```

### 3. 백업 방법
```bash
# 데이터베이스 백업
cp backend/blogauto_personal.db backend/backup/blogauto_$(date +%Y%m%d).db

# 생성된 콘텐츠 내보내기
GET /api/v1/content/export
```

## 🔧 문제 해결

### API 키 오류
```
"Invalid API key" 에러 → .env 파일의 API 키 확인
```

### 서버 시작 안 됨
```bash
# 포트 충돌 시
lsof -i :8000  # 사용 중인 프로세스 확인
kill -9 [PID]  # 프로세스 종료

# 또는 다른 포트 사용
uvicorn main:app --port 8001
```

### 데이터베이스 오류
```bash
# 데이터베이스 초기화
rm backend/blogauto_personal.db
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

## 📱 모바일에서 사용하기

로컬 네트워크에서 모바일 접속:
1. PC의 IP 주소 확인: `ipconfig` (Windows) 또는 `ifconfig` (Mac/Linux)
2. 서버 실행 시: `uvicorn main:app --host 0.0.0.0`
3. 모바일에서: `http://[PC-IP]:8000/docs`

## 🚀 다음 단계

### 프론트엔드 UI 사용 (선택사항)
```bash
# React 앱 실행
cd frontend
npm install
npm start
# http://localhost:3000 접속

# 또는 Next.js 앱
cd nextjs-app
npm install
npm run dev
# http://localhost:3000 접속
```

### 자동화 스케줄 설정
```python
# 매일 오전 9시 자동 포스팅 (cron 사용)
0 9 * * * /path/to/python /path/to/auto_post_script.py
```

## 🎉 축하합니다!

이제 개인 블로그 자동화 시스템을 사용할 준비가 되었습니다. 
궁금한 점이 있다면 `/docs` 페이지의 API 문서를 참고하세요.

**Happy Blogging! 🚀**