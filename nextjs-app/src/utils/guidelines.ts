// 콘텐츠 작성 지침 유틸리티

export interface Guidelines {
  keyword_guidelines: string;
  title_guidelines: string;
  content_guidelines: string;
  seo_guidelines: string;
}

const DEFAULT_GUIDELINES: Guidelines = {
  keyword_guidelines: `# 키워드 분석 지침

## 기본 원칙
- 검색량 1,000 이상의 키워드 우선 선별
- 경쟁도 0.7 이하의 키워드 중심 분석
- 롱테일 키워드 포함 필수

## 키워드 유형별 분석
- 정보성 키워드: "방법", "가이드", "팁" 
- 상업성 키워드: "추천", "비교", "후기"
- 네비게이션 키워드: 브랜드명, 서비스명

## 제외 키워드
- 성인 콘텐츠 관련
- 의료/건강 민감 정보
- 법적 문제 관련`,

  title_guidelines: `# 제목 생성 지침

## SEO 최적화 원칙
- 타겟 키워드 제목 앞부분 배치
- 제목 길이 30-60자 유지
- 숫자 활용으로 구체성 강화

## 시점 정확성 (중요!)
- 현재 연도(2025년) 기준으로 작성
- "2024년", "작년", "내년" 등 부정확한 시점 표현 금지
- "2025년 최신", "현재", "최근" 등 정확한 표현 사용

## 클릭률 향상 요소
- 호기심 유발 문구 사용
- 혜택/결과 명시
- 긴급성/희소성 표현
- 최신 트렌드 반영

## 제목 패턴 (2025년 기준)
- "완벽 가이드": "[키워드] 완벽 가이드: 초보자부터 전문가까지"
- "최신 트렌드": "2025년 최신 [키워드] 트렌드와 실전 활용법"
- "비밀 공개": "[키워드]의 숨겨진 비밀 7가지 완전 공개"
- "실전 활용": "실제로 효과본 [키워드] 전략 10가지"
- "현재 상황": "지금 당장 시작하는 [키워드] 성공 전략"

## 금지 사항
- 과장된 표현 지양
- 클릭베이트 성격 제목 금지
- 오해의 소지가 있는 제목 배제
- 부정확한 시점 표현 사용 금지`,

  content_guidelines: `# 콘텐츠 작성 지침

## 구조화 원칙
- H1 태그: 제목 (키워드 포함)
- H2 태그: 주요 섹션 (2-3개)
- H3 태그: 세부 내용 (섹션당 2-4개)

## 시점 정확성 (필수!)
- 2025년 현재 시점 기준으로 작성
- 최신 트렌드와 현재 시장 상황 반영
- "2024년", "작년", "내년" 등 부정확한 표현 금지
- "2025년 현재", "최근", "현재" 등 정확한 시점 표현 사용

## SEO 최적화
- 키워드 밀도 2-3% 유지
- 동의어/관련어 자연스럽게 포함
- 메타 설명에 맞는 도입부 작성
- 현재 검색 트렌드 반영

## 콘텐츠 품질 기준
- 최소 1,500자 이상
- 실용적이고 현재 적용 가능한 정보 제공
- 단계별 설명 포함
- 2025년 현재 기준의 최신 사례 활용
- 업계 현재 동향 및 전망 포함

## 필수 포함 요소 (REQUIRED)

### Q&A 섹션 (반드시 포함)
- 제목: "자주 묻는 질문 (FAQ)" 또는 "Q&A"
- 최소 5개 이상의 질문-답변 쌍
- 실제 사용자가 궁금해할 만한 현실적 질문
- 간결하고 명확한 답변 제공
- 형식 예시:
  Q: [구체적인 질문]
  A: [명확하고 실용적인 답변]

### 태그 생성 (자동 처리)
- 키워드 기반 관련 태그 자동 생성
- 5-10개의 태그를 쉼표로 구분
- 형식: "태그: 키워드1, 키워드2, 관련어1, 관련어2, ..."
- WordPress 태그 필드에 자동 입력됨

## 독자 경험 최적화
- 짧은 문단 (3-4줄)
- 불릿 포인트 활용
- 이미지/차트 위치 표시
- 현실적이고 실행 가능한 CTA 포함

## 피해야 할 요소
- 키워드 남용
- 중복 내용 반복
- 광고성 문구 과다
- 구시대적 정보나 과거 시점 기준 내용
- 부정확한 시점 표현
- Q&A 섹션 누락 (필수 포함)`,

  seo_guidelines: `# SEO 최적화 지침

## 현재 시점 기준 (2025년)
- 2025년 최신 검색 알고리즘 변화 반영
- 현재 검색 트렌드와 사용자 행동 패턴 고려
- 최신 SEO 베스트 프랙티스 적용

## 기술적 SEO
- 페이지 로딩 속도 최적화 (Core Web Vitals)
- 모바일 친화적 디자인 (Mobile-First Indexing)
- 구조화된 데이터 마크업
- AI 검색 최적화 (AI Overviews, SGE 대응)

## 콘텐츠 SEO
- E-A-T (전문성, 권위성, 신뢰성) 준수
- 사용자 검색 의도 파악 및 만족
- 관련 키워드 클러스터링
- 의미적 검색 최적화 (Semantic Search)
- 현재 시점의 정확한 정보 제공

## 링크 최적화
- 내부 링크 전략적 배치
- 외부 링크 신뢰도 확인 (2025년 기준 최신 소스)
- 앵커 텍스트 최적화
- 주제별 클러스터 구조 구축

## 측정 지표 (2025년 기준)
- 유기적 트래픽 증가율
- 키워드 순위 상승
- 클릭률(CTR) 개선
- 체류 시간 증가
- AI 검색 결과 노출률
- 브랜드 검색량 증가`
};

export function getGuidelines(): Guidelines {
  if (typeof window === 'undefined') return DEFAULT_GUIDELINES;
  
  const saved = localStorage.getItem('content_guidelines');
  return saved ? JSON.parse(saved) : DEFAULT_GUIDELINES;
}

export function saveGuidelines(guidelines: Guidelines): void {
  if (typeof window === 'undefined') return;
  
  localStorage.setItem('content_guidelines', JSON.stringify(guidelines));
}

export function getGuidelineByType(type: keyof Guidelines): string {
  const guidelines = getGuidelines();
  return guidelines[type] || '';
}

// API 호출 시 지침을 포함하는 함수
export function addGuidelinesToPrompt(basePrompt: string, guidelineType: keyof Guidelines): string {
  const guideline = getGuidelineByType(guidelineType);
  
  if (!guideline) return basePrompt;
  
  return `${basePrompt}

다음 지침을 반드시 준수하여 생성해주세요:

${guideline}`;
}

export { DEFAULT_GUIDELINES };