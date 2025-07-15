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
import { PencilIcon, ClipboardIcon, SearchIcon, CopyIcon } from '@/components/Icons';
import { AccessibleButton } from '@/components/AccessibleButton';

interface TitleResult {
  title: string;
  duplicate_rate?: number;
  score?: number;
  reason?: string;
}

export default function TitlesPage() {
  const [keyword, setKeyword] = useState('');
  const [length, setLength] = useState('medium');
  const [language, setLanguage] = useState('ko');
  const [tone, setTone] = useState('professional');
  const [count, setCount] = useState(5);
  const [results, setResults] = useState<TitleResult[]>([]);
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
    length,
    language,
    tone,
    count,
    results,
    timestamp: Date.now()
  };
  
  const {
    saveNow,
    hasUnsavedChanges,
    lastSaved,
    restoreData
  } = useAutoSave(autoSaveData, {
    key: 'titles_page',
    interval: 30000, // 30초마다 저장
    enabled: true
  });
  
  // 페이지 이탈 경고
  useBeforeUnload(hasUnsavedChanges);

  // 페이지 로드 시 워크플로우 설정 및 데이터 복원
  useEffect(() => {
    workflowActions.setStep('title');
    
    // 워크플로우에서 선택된 키워드 사용
    if (workflowState.selectedKeyword) {
      setKeyword(workflowState.selectedKeyword);
    }
    
    // 저장된 데이터 복원
    const saved = restoreData();
    if (saved?.data) {
      setKeyword(saved.data.keyword || workflowState.selectedKeyword || '');
      setLength(saved.data.length || 'medium');
      setLanguage(saved.data.language || 'ko');
      setTone(saved.data.tone || 'professional');
      setCount(saved.data.count || 5);
      setResults(saved.data.results || []);
    }
  }, []);

  const generateTitles = async () => {
    if (!keyword.trim()) {
      toastError('키워드를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await apiCall('http://localhost:8000/api/titles/generate', {
        method: 'POST',
        body: JSON.stringify({
          keyword: keyword.trim(),
          length,
          language,
          tone,
          count
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        let errorMessage = '제목 생성에 실패했습니다.';
        
        switch (response.status) {
          case 400:
            errorMessage = '입력 데이터가 올바르지 않습니다. 키워드를 확인해주세요.';
            break;
          case 401:
            errorMessage = 'API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 입력해주세요.';
            toastError('설정 페이지로 이동합니다.');
            setTimeout(() => router.push('/settings'), 2000);
            break;
          case 429:
            errorMessage = '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
            break;
          case 500:
            errorMessage = '서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.';
            break;
          default:
            errorMessage = errorData?.message || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setResults(data);
      workflowActions.setTitles(data.map((item: TitleResult) => item.title));
      success(`${data.length}개의 제목이 성공적으로 생성되었습니다.`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('네트워크 연결을 확인해주세요. 인터넷 연결이 불안정할 수 있습니다.');
        toastError('네트워크 연결 오류');
      } else {
        setError(errorMessage);
        toastError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      success('제목이 클립보드에 복사되었습니다');
    } catch {
      toastError('복사에 실패했습니다');
    }
  };

  // 제목 선택 및 다음 단계로 이동
  const selectTitle = (selectedTitle: string) => {
    workflowActions.setTitle(selectedTitle);
    success(`"${selectedTitle}" 제목이 선택되었습니다.`);
    router.push('/content');
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
              <h1 className="text-3xl font-bold text-gray-900">제목 생성</h1>
              <p className="text-gray-600 mt-2">AI가 SEO 최적화된 매력적인 제목을 생성해드립니다</p>
              {workflowState.selectedKeyword && (
                <div className="mt-2 flex items-center text-sm text-blue-600">
                  <SearchIcon className="mr-2" size={16} />
                  선택된 키워드: <span className="font-medium ml-1">{workflowState.selectedKeyword}</span>
                </div>
              )}
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
                ariaLabel="제목 작성 지침 보기"
              >
                제목 지침 보기
              </AccessibleButton>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                키워드 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="예: AI 마케팅 전략"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                onKeyPress={(e) => e.key === 'Enter' && generateTitles()}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                제목 길이
              </label>
              <select
                value={length}
                onChange={(e) => setLength(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="short">짧게 (20-30자)</option>
                <option value="medium">보통 (30-50자)</option>
                <option value="long">길게 (50-70자)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                언어
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="ko">한국어</option>
                <option value="en">영어</option>
                <option value="ja">일본어</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                톤앤매너
              </label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="professional">전문적</option>
                <option value="casual">캐주얼</option>
                <option value="friendly">친근한</option>
                <option value="formal">공식적</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                생성 개수
              </label>
              <input
                type="number"
                value={count}
                onChange={(e) => setCount(parseInt(e.target.value) || 5)}
                min="1"
                max="10"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <AccessibleButton
            onClick={generateTitles}
            disabled={loading}
            loading={loading}
            icon={<PencilIcon size={18} />}
            ariaLabel="AI 제목 생성 시작"
            size="lg"
          >
            제목 생성
          </AccessibleButton>

          {error && !loading && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-sm font-medium text-red-800">문제가 발생했습니다</h3>
                  <div className="mt-2 text-sm text-red-700">
                    {error}
                  </div>
                  <div className="mt-3">
                    <AccessibleButton
                      onClick={() => setError('')}
                      variant="ghost"
                      size="sm"
                      ariaLabel="오류 메시지 닫기"
                      className="bg-red-100 text-red-800 hover:bg-red-200"
                    >
                      닫기
                    </AccessibleButton>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {results.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">생성된 제목</h2>
              <p className="text-gray-600 text-sm">클릭하여 복사하세요</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div
                    key={index}
                    onClick={() => copyToClipboard(result.title)}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 mb-2">
                          {result.title}
                        </h3>
                        <div className="flex items-center text-sm text-gray-500">
                          <span className="mr-4">길이: {result.title.length}자</span>
                          {result.duplicate_rate !== undefined && (
                            <span className="flex items-center">
                              중복률: 
                              <span className={`ml-1 px-2 py-1 rounded text-xs ${
                                (result.duplicate_rate || 0) < 5 ? 'bg-green-100 text-green-800' :
                                (result.duplicate_rate || 0) < 10 ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {(result.duplicate_rate || 0).toFixed(1)}%
                              </span>
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="ml-4 flex items-center gap-2">
                        <AccessibleButton 
                          onClick={(e) => {
                            e.stopPropagation();
                            copyToClipboard(result.title);
                          }}
                          variant="ghost"
                          size="sm"
                          icon={<CopyIcon size={16} />}
                          ariaLabel={`"${result.title}" 제목 복사`}
                        />
                        <AccessibleButton
                          onClick={(e) => {
                            e.stopPropagation();
                            selectTitle(result.title);
                          }}
                          size="sm"
                          ariaLabel={`"${result.title}" 제목을 선택하여 다음 단계로 이동`}
                        >
                          선택
                        </AccessibleButton>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
      
      <GuidelinesModal 
        isOpen={showGuidelines}
        onClose={() => setShowGuidelines(false)}
        type="title_guidelines"
      />
    </div>
  );
}