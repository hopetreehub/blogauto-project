'use client';

import { useState } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';
import { apiCall } from '@/utils/api';
import { useRouter } from 'next/navigation';
import GuidelinesModal from '@/components/GuidelinesModal';

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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">제목 생성</h1>
              <p className="text-gray-600 mt-2">AI가 SEO 최적화된 매력적인 제목을 생성해드립니다</p>
            </div>
            <button
              onClick={() => setShowGuidelines(true)}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 flex items-center"
            >
              <span className="mr-2">📋</span>
              제목 지침 보기
            </button>
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

          <button
            onClick={generateTitles}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading && (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            {loading ? '생성 중...' : '제목 생성'}
          </button>

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
                    <button
                      onClick={() => setError('')}
                      className="bg-red-100 text-red-800 px-3 py-1.5 rounded-md text-sm font-medium hover:bg-red-200 transition-colors"
                    >
                      닫기
                    </button>
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
                      <button className="ml-4 p-2 hover:bg-gray-100 rounded">
                        <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
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