'use client';

import { useState, useEffect } from 'react';

interface TestVariant {
  id: string;
  name: string;
  content: string;
  metrics: {
    views: number;
    clicks: number;
    conversions: number;
    bounceRate: number;
    avgTimeOnPage: number;
  };
  isWinner?: boolean;
}

interface ABTest {
  id: string;
  name: string;
  status: 'draft' | 'running' | 'paused' | 'completed';
  startDate?: string;
  endDate?: string;
  variants: TestVariant[];
  targetMetric: string;
  confidenceLevel: number;
  sampleSize: number;
  currentSampleSize: number;
}

export default function ABTesting() {
  const [tests, setTests] = useState<ABTest[]>([
    {
      id: '1',
      name: 'AI 마케팅 가이드 제목 테스트',
      status: 'running',
      startDate: '2025-07-10',
      targetMetric: 'clicks',
      confidenceLevel: 95,
      sampleSize: 1000,
      currentSampleSize: 723,
      variants: [
        {
          id: 'a',
          name: 'Variant A',
          content: 'AI 시대의 콘텐츠 마케팅: 완벽한 가이드',
          metrics: {
            views: 412,
            clicks: 89,
            conversions: 34,
            bounceRate: 35.2,
            avgTimeOnPage: 124
          }
        },
        {
          id: 'b',
          name: 'Variant B',
          content: '2025년 AI 콘텐츠 마케팅 마스터하기',
          metrics: {
            views: 311,
            clicks: 98,
            conversions: 42,
            bounceRate: 28.5,
            avgTimeOnPage: 145
          },
          isWinner: true
        }
      ]
    }
  ]);

  const [newTest, setNewTest] = useState<Partial<ABTest>>({
    name: '',
    targetMetric: 'clicks',
    confidenceLevel: 95,
    sampleSize: 1000,
    variants: [
      { id: 'a', name: 'Variant A', content: '', metrics: { views: 0, clicks: 0, conversions: 0, bounceRate: 0, avgTimeOnPage: 0 } },
      { id: 'b', name: 'Variant B', content: '', metrics: { views: 0, clicks: 0, conversions: 0, bounceRate: 0, avgTimeOnPage: 0 } }
    ]
  });

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedTest, setSelectedTest] = useState<ABTest | null>(null);

  const calculateConversionRate = (variant: TestVariant) => {
    if (variant.metrics.views === 0) return 0;
    return ((variant.metrics.clicks / variant.metrics.views) * 100).toFixed(2);
  };

  const calculateStatisticalSignificance = (test: ABTest) => {
    // 간단한 통계적 유의성 계산 시뮬레이션
    const variantA = test.variants[0];
    const variantB = test.variants[1];
    
    const conversionA = variantA.metrics.clicks / variantA.metrics.views;
    const conversionB = variantB.metrics.clicks / variantB.metrics.views;
    
    const difference = Math.abs(conversionB - conversionA);
    const significance = difference > 0.05 ? 95 : difference > 0.03 ? 80 : 60;
    
    return significance;
  };

  const createTest = () => {
    const test: ABTest = {
      id: Date.now().toString(),
      name: newTest.name || '새 A/B 테스트',
      status: 'draft',
      targetMetric: newTest.targetMetric || 'clicks',
      confidenceLevel: newTest.confidenceLevel || 95,
      sampleSize: newTest.sampleSize || 1000,
      currentSampleSize: 0,
      variants: newTest.variants || []
    };

    setTests([...tests, test]);
    setShowCreateModal(false);
    setNewTest({
      name: '',
      targetMetric: 'clicks',
      confidenceLevel: 95,
      sampleSize: 1000,
      variants: [
        { id: 'a', name: 'Variant A', content: '', metrics: { views: 0, clicks: 0, conversions: 0, bounceRate: 0, avgTimeOnPage: 0 } },
        { id: 'b', name: 'Variant B', content: '', metrics: { views: 0, clicks: 0, conversions: 0, bounceRate: 0, avgTimeOnPage: 0 } }
      ]
    });
  };

  const updateTestStatus = (testId: string, status: ABTest['status']) => {
    setTests(tests.map(test => 
      test.id === testId 
        ? { 
            ...test, 
            status,
            startDate: status === 'running' ? new Date().toISOString().split('T')[0] : test.startDate,
            endDate: status === 'completed' ? new Date().toISOString().split('T')[0] : test.endDate
          }
        : test
    ));
  };

  const targetMetricOptions = [
    { value: 'clicks', label: '클릭률 (CTR)', icon: '👆' },
    { value: 'conversions', label: '전환율', icon: '🎯' },
    { value: 'time', label: '체류 시간', icon: '⏱️' },
    { value: 'bounce', label: '이탈률', icon: '📉' }
  ];

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">A/B 테스팅</h1>
            <p className="text-gray-600">콘텐츠 성과를 비교하고 최적화하세요</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            + 새 테스트 만들기
          </button>
        </div>
      </div>

      {/* 테스트 목록 */}
      <div className="space-y-6">
        {tests.map((test) => (
          <div key={test.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-xl font-semibold mb-2">{test.name}</h2>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span className={`px-3 py-1 rounded-full font-medium ${
                      test.status === 'running' ? 'bg-green-100 text-green-700' :
                      test.status === 'completed' ? 'bg-blue-100 text-blue-700' :
                      test.status === 'paused' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {test.status === 'running' ? '진행 중' :
                       test.status === 'completed' ? '완료' :
                       test.status === 'paused' ? '일시정지' : '초안'}
                    </span>
                    {test.startDate && (
                      <span>시작일: {test.startDate}</span>
                    )}
                    <span>목표: {test.sampleSize}명</span>
                    <span>현재: {test.currentSampleSize}명</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  {test.status === 'draft' && (
                    <button
                      onClick={() => updateTestStatus(test.id, 'running')}
                      className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
                    >
                      시작
                    </button>
                  )}
                  {test.status === 'running' && (
                    <>
                      <button
                        onClick={() => updateTestStatus(test.id, 'paused')}
                        className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700 transition-colors"
                      >
                        일시정지
                      </button>
                      <button
                        onClick={() => updateTestStatus(test.id, 'completed')}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                      >
                        종료
                      </button>
                    </>
                  )}
                  {test.status === 'paused' && (
                    <button
                      onClick={() => updateTestStatus(test.id, 'running')}
                      className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors"
                    >
                      재개
                    </button>
                  )}
                  <button
                    onClick={() => setSelectedTest(test)}
                    className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
                  >
                    상세보기
                  </button>
                </div>
              </div>

              {/* 진행률 */}
              <div className="mb-6">
                <div className="flex justify-between text-sm text-gray-600 mb-1">
                  <span>진행률</span>
                  <span>{Math.round((test.currentSampleSize / test.sampleSize) * 100)}%</span>
                </div>
                <div className="bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${(test.currentSampleSize / test.sampleSize) * 100}%` }}
                  />
                </div>
              </div>

              {/* 변형 비교 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {test.variants.map((variant) => (
                  <div key={variant.id} className={`border rounded-lg p-4 ${
                    variant.isWinner ? 'border-green-500 bg-green-50' : 'border-gray-200'
                  }`}>
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-medium">{variant.name}</h3>
                      {variant.isWinner && (
                        <span className="text-green-600 font-medium">🏆 승자</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 mb-4">{variant.content}</p>
                    
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-gray-600">조회수</p>
                        <p className="font-medium">{variant.metrics.views}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">클릭률</p>
                        <p className="font-medium">{calculateConversionRate(variant)}%</p>
                      </div>
                      <div>
                        <p className="text-gray-600">전환수</p>
                        <p className="font-medium">{variant.metrics.conversions}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">이탈률</p>
                        <p className="font-medium">{variant.metrics.bounceRate}%</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 통계적 유의성 */}
              {test.status !== 'draft' && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">통계적 유의성</span>
                    <span className={`text-sm font-medium ${
                      calculateStatisticalSignificance(test) >= test.confidenceLevel
                        ? 'text-green-600' : 'text-gray-600'
                    }`}>
                      {calculateStatisticalSignificance(test)}%
                    </span>
                  </div>
                  <div className="mt-2 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-500 ${
                        calculateStatisticalSignificance(test) >= test.confidenceLevel
                          ? 'bg-green-500' : 'bg-gray-400'
                      }`}
                      style={{ width: `${calculateStatisticalSignificance(test)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 테스트 생성 모달 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">새 A/B 테스트 만들기</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  테스트 이름
                </label>
                <input
                  type="text"
                  value={newTest.name}
                  onChange={(e) => setNewTest({ ...newTest, name: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="예: 블로그 제목 CTR 테스트"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  목표 지표
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {targetMetricOptions.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setNewTest({ ...newTest, targetMetric: option.value })}
                      className={`p-3 rounded-lg border transition-colors ${
                        newTest.targetMetric === option.value
                          ? 'border-blue-500 bg-blue-50 text-blue-700'
                          : 'border-gray-300 hover:border-gray-400'
                      }`}
                    >
                      <span className="text-xl mb-1 block">{option.icon}</span>
                      <span className="text-sm">{option.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    신뢰도 수준
                  </label>
                  <select
                    value={newTest.confidenceLevel}
                    onChange={(e) => setNewTest({ ...newTest, confidenceLevel: Number(e.target.value) })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={90}>90%</option>
                    <option value={95}>95%</option>
                    <option value={99}>99%</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    목표 샘플 크기
                  </label>
                  <input
                    type="number"
                    value={newTest.sampleSize}
                    onChange={(e) => setNewTest({ ...newTest, sampleSize: Number(e.target.value) })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    min={100}
                    step={100}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  테스트 변형
                </label>
                {newTest.variants?.map((variant, index) => (
                  <div key={variant.id} className="mb-3 p-4 border rounded-lg">
                    <input
                      type="text"
                      value={variant.content}
                      onChange={(e) => {
                        const updatedVariants = [...(newTest.variants || [])];
                        updatedVariants[index] = { ...variant, content: e.target.value };
                        setNewTest({ ...newTest, variants: updatedVariants });
                      }}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder={`${variant.name} 콘텐츠 입력`}
                    />
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                취소
              </button>
              <button
                onClick={createTest}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                테스트 생성
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 상세보기 모달 */}
      {selectedTest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-2xl font-bold">{selectedTest.name} 상세 분석</h2>
              <button
                onClick={() => setSelectedTest(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {/* 상세 차트와 분석 내용 */}
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-blue-700 mb-1">총 참여자</p>
                  <p className="text-2xl font-bold text-blue-900">{selectedTest.currentSampleSize}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm text-green-700 mb-1">통계적 유의성</p>
                  <p className="text-2xl font-bold text-green-900">{calculateStatisticalSignificance(selectedTest)}%</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-sm text-purple-700 mb-1">테스트 기간</p>
                  <p className="text-2xl font-bold text-purple-900">
                    {selectedTest.startDate && selectedTest.endDate 
                      ? `${Math.ceil((new Date(selectedTest.endDate).getTime() - new Date(selectedTest.startDate).getTime()) / (1000 * 60 * 60 * 24))}일`
                      : '-'}
                  </p>
                </div>
              </div>

              {/* 권장사항 */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h3 className="font-medium text-yellow-900 mb-2">💡 권장사항</h3>
                <ul className="space-y-1 text-sm text-yellow-800">
                  <li>• 통계적 유의성이 95% 이상일 때 결과를 신뢰할 수 있습니다</li>
                  <li>• 최소 2주 이상 테스트를 진행하여 주기적 변동을 고려하세요</li>
                  <li>• 승자가 결정되면 즉시 모든 트래픽을 승자 변형으로 전환하세요</li>
                </ul>
              </div>
            </div>

            <div className="flex justify-end mt-6">
              <button
                onClick={() => setSelectedTest(null)}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}