'use client';

import { useState, useEffect } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';
import { apiCall } from '@/utils/api';
import { useRouter } from 'next/navigation';
import GuidelinesModal from '@/components/GuidelinesModal';
import { useWorkflow } from '@/contexts/WorkflowContext';
import { useAutoSave, useBeforeUnload } from '@/hooks/useAutoSave';
import { AutoSaveStatus } from '@/components/AutoSaveStatus';
import WorkflowStepper from '@/components/WorkflowStepper';
import { SearchIcon, ClipboardIcon, DownloadIcon } from '@/components/Icons';
import { AccessibleButton } from '@/components/AccessibleButton';

interface KeywordResult {
  keyword: string;
  search_volume: number;
  competition: string;
  cpc: number;
  opportunity_score: number;
}

export default function Keywords() {
  const [keyword, setKeyword] = useState('');
  const [country, setCountry] = useState('KR');
  const [results, setResults] = useState<KeywordResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showGuidelines, setShowGuidelines] = useState(false);
  const { toasts, success, error: toastError, removeToast } = useToast();
  const router = useRouter();
  
  // 워크플로우 상태 관리
  const { state: workflowState, actions: workflowActions } = useWorkflow();
  
  // 자동저장 설정
  const autoSaveData = {
    keyword,
    country,
    results,
    timestamp: Date.now()
  };
  
  const {
    saveNow,
    hasUnsavedChanges,
    lastSaved,
    restoreData
  } = useAutoSave(autoSaveData, {
    key: 'keywords_page',
    interval: 30000, // 30초마다 저장
    enabled: true
  });
  
  // 페이지 이탈 경고
  useBeforeUnload(hasUnsavedChanges);
  
  // 페이지 로드 시 워크플로우 설정 및 데이터 복원
  useEffect(() => {
    workflowActions.setStep('keyword');
    
    // 저장된 데이터 복원
    const saved = restoreData();
    if (saved?.data) {
      setKeyword(saved.data.keyword || '');
      setCountry(saved.data.country || 'KR');
      setResults(saved.data.results || []);
    }
  }, []);

  const handleAnalyze = async () => {
    if (!keyword.trim()) {
      setError('키워드를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await apiCall('http://localhost:8000/api/keywords/analyze', {
        method: 'POST',
        body: JSON.stringify({
          keyword,
          country,
          max_results: 10
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          toastError('API 키를 설정하세요');
          router.push('/settings');
          return;
        }
        throw new Error('API 호출 실패');
      }

      const data = await response.json();
      setResults(data);
      workflowActions.setKeywordResults(data);
      success(`${data.length}개의 키워드가 분석되었습니다.`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '키워드 분석 중 오류가 발생했습니다.';
      setError(errorMessage);
      toastError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = () => {
    if (results.length === 0) return;

    const csvContent = [
      ['키워드', '검색량', '경쟁도', 'CPC', '기회점수'],
      ...results.map(r => [r.keyword, r.search_volume, r.competition, r.cpc, r.opportunity_score])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `keywords_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  // 키워드 선택 및 다음 단계로 이동
  const selectKeyword = (selectedKeyword: string) => {
    workflowActions.setKeyword(selectedKeyword);
    success(`"${selectedKeyword}" 키워드가 선택되었습니다.`);
    router.push('/titles');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-7xl mx-auto">
        {/* 워크플로우 스테퍼 */}
        <WorkflowStepper className="mb-6" />
        
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">키워드 분석</h1>
              <p className="text-gray-600 mt-2">키워드 검색량, 경쟁도, 기회점수를 분석합니다</p>
            </div>
            <div className="flex items-center gap-4">
              {/* 자동저장 상태 */}
              <AutoSaveStatus 
                hasUnsavedChanges={hasUnsavedChanges}
                lastSaved={lastSaved}
                onSaveNow={saveNow}
              />
              <AccessibleButton
                onClick={() => setShowGuidelines(true)}
                variant="secondary"
                icon={<ClipboardIcon size={16} />}
                ariaLabel="키워드 작성 지침 보기"
              >
                키워드 지침 보기
              </AccessibleButton>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                키워드
              </label>
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="분석할 키워드를 입력하세요"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                국가
              </label>
              <select
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="KR">한국</option>
                <option value="US">미국</option>
                <option value="JP">일본</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <AccessibleButton
            onClick={handleAnalyze}
            disabled={loading}
            loading={loading}
            icon={<SearchIcon size={18} />}
            ariaLabel="키워드 분석 시작"
            size="lg"
          >
            키워드 분석
          </AccessibleButton>
        </div>

        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">분석 결과</h2>
              <AccessibleButton
                onClick={downloadCSV}
                variant="secondary"
                icon={<DownloadIcon size={16} />}
                ariaLabel="분석 결과 CSV 파일로 다운로드"
              >
                CSV 다운로드
              </AccessibleButton>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      키워드
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      검색량
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      경쟁도
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CPC
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      기회점수
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      선택
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.map((result, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {result.keyword}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {result.search_volume.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {result.competition}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${result.cpc}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {result.opportunity_score}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <AccessibleButton
                          onClick={() => selectKeyword(result.keyword)}
                          size="sm"
                          ariaLabel={`"${result.keyword}" 키워드를 선택하여 다음 단계로 이동`}
                        >
                          선택
                        </AccessibleButton>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
      
      <GuidelinesModal 
        isOpen={showGuidelines}
        onClose={() => setShowGuidelines(false)}
        type="keyword_guidelines"
      />
    </div>
  );
}