'use client';

import { useState } from 'react';

interface QualityMetric {
  name: string;
  score: number;
  status: 'good' | 'warning' | 'error';
  feedback: string;
}

interface ContentAnalysis {
  overallScore: number;
  metrics: QualityMetric[];
  suggestions: string[];
}

export default function QualityChecker() {
  const [content, setContent] = useState('');
  const [analysis, setAnalysis] = useState<ContentAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeContent = async () => {
    if (!content.trim()) return;
    
    setIsAnalyzing(true);
    
    // 실제로는 API 호출
    setTimeout(() => {
      const mockAnalysis: ContentAnalysis = {
        overallScore: 85,
        metrics: [
          {
            name: 'SEO 최적화',
            score: 90,
            status: 'good',
            feedback: '키워드 밀도와 메타 태그가 적절합니다'
          },
          {
            name: '가독성',
            score: 85,
            status: 'good',
            feedback: '문장 길이와 단락 구성이 좋습니다'
          },
          {
            name: '독창성',
            score: 75,
            status: 'warning',
            feedback: '일부 표현이 일반적입니다. 더 독특한 관점을 추가해보세요'
          },
          {
            name: '문법 정확도',
            score: 95,
            status: 'good',
            feedback: '문법 오류가 거의 없습니다'
          },
          {
            name: '참여도',
            score: 80,
            status: 'good',
            feedback: 'CTA가 명확하고 질문이 포함되어 있습니다'
          },
          {
            name: '정보 정확성',
            score: 88,
            status: 'good',
            feedback: '사실 확인이 필요한 부분이 표시되었습니다'
          }
        ],
        suggestions: [
          '도입부에 더 강력한 훅(hook)을 추가하세요',
          '3번째 단락에 구체적인 예시를 추가하면 좋겠습니다',
          '결론 부분을 더 명확하게 정리해주세요',
          '이미지 alt 텍스트를 추가하세요'
        ]
      };
      
      setAnalysis(mockAnalysis);
      setIsAnalyzing(false);
    }, 2000);
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return '📊';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI 콘텐츠 품질 검사</h1>
        <p className="text-gray-600">AI가 생성한 콘텐츠의 품질을 다각도로 분석하고 개선점을 제시합니다</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 입력 섹션 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">콘텐츠 입력</h2>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full h-96 p-4 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500"
            placeholder="검사할 콘텐츠를 입력하세요..."
          />
          <button
            onClick={analyzeContent}
            disabled={!content.trim() || isAnalyzing}
            className="mt-4 w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
          >
            {isAnalyzing ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                분석 중...
              </span>
            ) : '품질 검사 시작'}
          </button>
        </div>

        {/* 결과 섹션 */}
        <div className="space-y-6">
          {analysis && (
            <>
              {/* 종합 점수 */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">종합 품질 점수</h2>
                <div className="text-center">
                  <div className={`text-6xl font-bold ${getScoreColor(analysis.overallScore)}`}>
                    {analysis.overallScore}
                  </div>
                  <div className="text-gray-600 mt-2">
                    {analysis.overallScore >= 85 ? '우수' : 
                     analysis.overallScore >= 70 ? '양호' : '개선 필요'}
                  </div>
                </div>
                <div className="mt-4 bg-gray-200 rounded-full h-4">
                  <div 
                    className={`h-4 rounded-full transition-all duration-500 ${
                      analysis.overallScore >= 85 ? 'bg-green-500' :
                      analysis.overallScore >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${analysis.overallScore}%` }}
                  />
                </div>
              </div>

              {/* 세부 지표 */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">세부 품질 지표</h2>
                <div className="space-y-3">
                  {analysis.metrics.map((metric, index) => (
                    <div key={index} className="border-b pb-3 last:border-0">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span>{getStatusIcon(metric.status)}</span>
                          <span className="font-medium">{metric.name}</span>
                        </div>
                        <span className={`font-bold ${getScoreColor(metric.score)}`}>
                          {metric.score}점
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">{metric.feedback}</div>
                      <div className="mt-2 bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-500 ${
                            metric.score >= 85 ? 'bg-green-500' :
                            metric.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${metric.score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 개선 제안 */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">개선 제안</h2>
                <ul className="space-y-2">
                  {analysis.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-blue-600 mr-2">💡</span>
                      <span className="text-gray-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}

          {/* 품질 기준 설명 */}
          {!analysis && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">품질 검사 항목</h2>
              <div className="space-y-3">
                <div className="flex items-start">
                  <span className="text-2xl mr-3">🔍</span>
                  <div>
                    <h3 className="font-medium">SEO 최적화</h3>
                    <p className="text-sm text-gray-600">키워드 밀도, 메타 태그, 구조화된 데이터</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3">📖</span>
                  <div>
                    <h3 className="font-medium">가독성</h3>
                    <p className="text-sm text-gray-600">문장 길이, 단락 구성, 제목 계층구조</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3">💡</span>
                  <div>
                    <h3 className="font-medium">독창성</h3>
                    <p className="text-sm text-gray-600">고유한 관점, 창의적 표현, 차별화된 내용</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3">✍️</span>
                  <div>
                    <h3 className="font-medium">문법 정확도</h3>
                    <p className="text-sm text-gray-600">맞춤법, 문법, 문장 구조</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3">💬</span>
                  <div>
                    <h3 className="font-medium">참여도</h3>
                    <p className="text-sm text-gray-600">CTA, 질문, 상호작용 요소</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="text-2xl mr-3">✅</span>
                  <div>
                    <h3 className="font-medium">정보 정확성</h3>
                    <p className="text-sm text-gray-600">사실 확인, 출처 신뢰도, 최신 정보</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}