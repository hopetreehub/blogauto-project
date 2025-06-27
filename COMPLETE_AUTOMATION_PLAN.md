# 🚀 완전 자동화 블로그 관리 시스템 설계서

## 📋 시스템 개요

### 목표
사이트 설정부터 키워드 생성 → 제목 생성 → 블로그 글 작성 → 자동 포스팅까지 완전 자동화된 블로그 운영 시스템 구축

### 워크플로우
```
사이트 설정 → 카테고리 선택 → 키워드 자동생성 → 제목 자동생성 → 블로그 글 자동생성 → 자동 포스팅
```

## 🏗️ 시스템 구조

### 1. 사이트 관리 시스템
- **사이트 정보**: 이름, 주소, 설명
- **카테고리**: 여행, 맛집, 패션, IT 등 
- **플랫폼 설정**: WordPress 계정 정보 (URL, 아이디, 비밀번호)
- **지침 설정**: 키워드/제목/블로그 작성 지침 선택

### 2. 자동화 워크플로우
1. **카테고리 기반 키워드 자동 생성**
   - 트렌드 분석 + SEO 최적화
   - 생성 개수 선택 가능 (5~50개)
   - 키워드 품질 점수 표시

2. **키워드 기반 제목 자동 생성**
   - 바이럴 + SEO + 시의성 최적화
   - 생성 개수 선택 가능 (5~20개)
   - 제목 점수 및 예상 클릭률 표시

3. **제목 기반 블로그 글 자동 생성**
   - 체크박스로 다중 선택
   - SEO + GEO 완전 최적화
   - 800-1200자 전문 블로그 글

4. **자동 포스팅**
   - WordPress 직접 연동
   - 예약 포스팅 기능
   - 이미지 자동 생성 및 삽입

## 📁 파일 구조 설계

### Frontend 새로운 페이지
- `BlogAutomationHub.tsx` - 메인 자동화 허브
- `SiteManager.tsx` - 사이트 관리
- `AutomationWorkflow.tsx` - 자동화 워크플로우
- `components/KeywordGenerator.tsx` - 키워드 생성
- `components/TitleGenerator.tsx` - 제목 생성  
- `components/BlogGenerator.tsx` - 블로그 생성
- `components/AutoPoster.tsx` - 자동 포스팅

### Backend 새로운 API
- `/api/sites/*` - 사이트 관리
- `/api/automation/*` - 자동화 워크플로우
- `/api/keywords/auto-generate` - 자동 키워드 생성
- `/api/titles/auto-generate` - 자동 제목 생성
- `/api/content/auto-generate` - 자동 블로그 생성

## 🎯 핵심 기능

### 지침 기반 AI 생성
- 키워드 분석 지침
- 제목 생성 지침  
- 블로그 글쓰기 지침
- 모든 생성 과정에서 지침 활용

### 배치 처리
- 한 번에 여러 키워드 생성
- 한 번에 여러 제목 생성
- 한 번에 여러 블로그 글 생성
- 선택적 포스팅

### 품질 관리
- SEO 점수 실시간 계산
- 바이럴 점수 분석
- 가독성 점수 평가
- 중복도 검사

## 🔧 기술 스택

### 기존 유지
- FastAPI (Backend)
- React + TypeScript (Frontend)
- SQLite (Database)
- JWT 인증

### 새로운 추가
- 사이트 관리 데이터베이스 스키마
- 자동화 워크플로우 엔진
- 배치 처리 시스템
- WordPress API 연동

## 📊 데이터베이스 스키마

### Sites 테이블
```sql
- id: PRIMARY KEY
- name: 사이트 이름
- url: 사이트 주소
- description: 설명
- category: 카테고리
- wordpress_url: WordPress URL
- wordpress_username: 사용자명
- wordpress_password: 비밀번호 (암호화)
- keyword_guideline_id: 키워드 지침 ID
- title_guideline_id: 제목 지침 ID
- blog_guideline_id: 블로그 지침 ID
- created_at, updated_at
```

### Automation_Sessions 테이블
```sql
- id: PRIMARY KEY
- site_id: 사이트 ID
- category: 카테고리
- keywords: 생성된 키워드 (JSON)
- titles: 생성된 제목 (JSON)
- contents: 생성된 콘텐츠 (JSON)
- status: 진행상태
- created_at
```

## 🚀 구현 단계

### Phase 1: 기반 구조 (현재)
- [x] 데이터베이스 스키마 설계
- [x] 사이트 관리 백엔드 API
- [x] 사이트 관리 프론트엔드

### Phase 2: 자동화 엔진
- [ ] 카테고리 기반 키워드 자동 생성
- [ ] 키워드 기반 제목 자동 생성
- [ ] 제목 기반 블로그 글 자동 생성

### Phase 3: 통합 워크플로우
- [ ] 메인 자동화 허브 페이지
- [ ] 단계별 진행 시스템
- [ ] 배치 선택 및 처리

### Phase 4: 자동 포스팅
- [ ] WordPress API 연동
- [ ] 예약 포스팅
- [ ] 결과 모니터링

## 💡 예상 사용 시나리오

1. **사이트 등록**: "여행 블로그" 사이트 등록, WordPress 정보 입력
2. **카테고리 선택**: "국내여행" 카테고리 선택
3. **키워드 생성**: "국내여행" 관련 트렌드 키워드 20개 자동 생성
4. **제목 생성**: 선택한 키워드들로 바이럴 제목 10개씩 생성
5. **블로그 생성**: 체크박스로 원하는 제목 5개 선택, 블로그 글 자동 생성
6. **자동 포스팅**: WordPress에 30분 간격으로 자동 포스팅

## 🎯 성공 지표

- 키워드 → 제목 → 블로그 → 포스팅까지 5분 이내 완료
- 생성된 블로그 글의 SEO 점수 85점 이상
- 자동 포스팅 성공률 95% 이상
- 사용자 만족도 (클릭 몇 번으로 완성)

---

**최종 목표**: 클릭 몇 번으로 전문적인 블로그 운영이 가능한 완전 자동화 시스템