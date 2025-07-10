'use client';

import { useState, useEffect } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';

interface Guidelines {
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

## 클릭률 향상 요소
- 호기심 유발 문구 사용
- 혜택/결과 명시
- 긴급성/희소성 표현

## 제목 패턴
- "완벽 가이드": "[키워드] 완벽 가이드: 초보자부터 전문가까지"
- "비밀 공개": "[키워드]의 숨겨진 비밀 5가지"
- "실전 활용": "실제로 효과본 [키워드] 전략 10가지"

## 금지 사항
- 과장된 표현 지양
- 클릭베이트 성격 제목 금지
- 오해의 소지가 있는 제목 배제`,

  content_guidelines: `# 콘텐츠 작성 지침

## 구조화 원칙
- H1 태그: 제목 (키워드 포함)
- H2 태그: 주요 섹션 (2-3개)
- H3 태그: 세부 내용 (섹션당 2-4개)

## SEO 최적화
- 키워드 밀도 2-3% 유지
- 동의어/관련어 자연스럽게 포함
- 메타 설명에 맞는 도입부 작성

## 콘텐츠 품질 기준
- 최소 1,500자 이상
- 실용적 정보 제공
- 단계별 설명 포함
- 예시/사례 활용

## 독자 경험 최적화
- 짧은 문단 (3-4줄)
- 불릿 포인트 활용
- 이미지/차트 위치 표시
- CTA(Call to Action) 포함

## 피해야 할 요소
- 키워드 남용
- 중복 내용 반복
- 광고성 문구 과다`,

  seo_guidelines: `# SEO 최적화 지침

## 기술적 SEO
- 페이지 로딩 속도 최적화
- 모바일 친화적 디자인
- 구조화된 데이터 마크업

## 콘텐츠 SEO
- E-A-T (전문성, 권위성, 신뢰성) 준수
- 사용자 검색 의도 파악
- 관련 키워드 클러스터링

## 링크 최적화
- 내부 링크 전략적 배치
- 외부 링크 신뢰도 확인
- 앵커 텍스트 최적화

## 측정 지표
- 유기적 트래픽 증가율
- 키워드 순위 상승
- 클릭률(CTR) 개선
- 체류 시간 증가`
};

export default function GuidelinesPage() {
  const [guidelines, setGuidelines] = useState<Guidelines>(DEFAULT_GUIDELINES);
  const [activeTab, setActiveTab] = useState<keyof Guidelines>('keyword_guidelines');
  const [loading, setLoading] = useState(false);
  const { toasts, success, error: toastError, removeToast } = useToast();

  useEffect(() => {
    // 로컬 스토리지에서 지침 불러오기
    const savedGuidelines = localStorage.getItem('content_guidelines');
    if (savedGuidelines) {
      setGuidelines(JSON.parse(savedGuidelines));
    }
  }, []);

  const handleSave = async () => {
    setLoading(true);
    
    try {
      // 로컬 스토리지에 저장
      localStorage.setItem('content_guidelines', JSON.stringify(guidelines));
      success('지침이 저장되었습니다.');
    } catch (err) {
      toastError('지침 저장에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setGuidelines(DEFAULT_GUIDELINES);
    success('기본 지침으로 초기화되었습니다.');
  };

  const tabs = [
    { key: 'keyword_guidelines', label: '키워드 지침', icon: '🔍' },
    { key: 'title_guidelines', label: '제목 지침', icon: '✍️' },
    { key: 'content_guidelines', label: '콘텐츠 지침', icon: '📝' },
    { key: 'seo_guidelines', label: 'SEO 지침', icon: '📈' }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">콘텐츠 작성 지침</h1>
          <p className="text-gray-600 mt-2">AI 생성 콘텐츠의 품질과 SEO 최적화를 위한 지침을 관리합니다</p>
        </div>

        <div className="bg-white rounded-lg shadow">
          {/* 탭 헤더 */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as keyof Guidelines)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* 탭 콘텐츠 */}
          <div className="p-6">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {tabs.find(t => t.key === activeTab)?.label} 설정
              </label>
              <textarea
                value={guidelines[activeTab]}
                onChange={(e) => setGuidelines({
                  ...guidelines,
                  [activeTab]: e.target.value
                })}
                rows={20}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                placeholder="지침을 입력하세요..."
              />
            </div>

            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">
                마크다운 형식으로 작성하세요. # 제목, ## 소제목, - 목록 등을 사용할 수 있습니다.
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={handleReset}
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
                >
                  기본값 복원
                </button>
                
                <button
                  onClick={handleSave}
                  disabled={loading}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? '저장 중...' : '저장'}
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">지침 활용 방법</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium mb-2">자동 적용</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 키워드 분석 시 지침 자동 반영</li>
                <li>• 제목 생성 시 패턴 및 원칙 적용</li>
                <li>• 콘텐츠 생성 시 구조화 지침 활용</li>
                <li>• SEO 분석 시 최적화 기준 적용</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">수동 참조</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• 각 페이지에서 지침 버튼으로 확인</li>
                <li>• 생성 결과와 지침 비교 검토</li>
                <li>• 품질 개선을 위한 참고 자료</li>
                <li>• 일관성 있는 콘텐츠 제작</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}