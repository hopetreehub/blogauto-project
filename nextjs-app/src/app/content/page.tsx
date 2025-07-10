'use client';

import { useState } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';
import { apiCall } from '@/utils/api';
import { useRouter } from 'next/navigation';
import GuidelinesModal from '@/components/GuidelinesModal';

interface ContentResult {
  content: string;
  seo_score: number;
  word_count: number;
  readability_score: number;
}

interface WordPressConfig {
  site_url: string;
  username: string;
  password: string;
}

export default function ContentPage() {
  const [title, setTitle] = useState('');
  const [keywords, setKeywords] = useState('');
  const [length, setLength] = useState('medium');
  const [result, setResult] = useState<ContentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showGuidelines, setShowGuidelines] = useState(false);
  const [publishingToWP, setPublishingToWP] = useState(false);
  const { toasts, success, error: toastError, removeToast } = useToast();
  const router = useRouter();

  const generateContent = async () => {
    if (!title.trim()) {
      toastError('제목을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await apiCall('http://localhost:8000/api/content/generate', {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim(),
          keyword: keywords.trim(),
          length
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        let errorMessage = '콘텐츠 생성에 실패했습니다.';
        
        switch (response.status) {
          case 400:
            errorMessage = '입력 데이터가 올바르지 않습니다. 제목을 확인해주세요.';
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
      setResult(data);
      success('고품질 콘텐츠가 성공적으로 생성되었습니다.');
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
      success('콘텐츠가 클립보드에 복사되었습니다');
    } catch {
      toastError('복사에 실패했습니다');
    }
  };

  const downloadAsFile = () => {
    if (!result) return;
    
    try {
      const blob = new Blob([result.content], { type: 'text/plain;charset=utf-8' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${title.replace(/[^a-zA-Z0-9가-힣]/g, '_')}.txt`;
      link.click();
      success('파일이 다운로드되었습니다');
      URL.revokeObjectURL(link.href);
    } catch {
      toastError('다운로드에 실패했습니다');
    }
  };

  const publishToWordPress = async () => {
    if (!result) {
      toastError('먼저 콘텐츠를 생성해주세요.');
      return;
    }

    // WordPress 설정 확인
    const wpConfigStr = localStorage.getItem('wordpress_config');
    if (!wpConfigStr) {
      toastError('WordPress 설정이 필요합니다. WordPress 페이지에서 설정을 완료해주세요.');
      setTimeout(() => router.push('/wordpress'), 2000);
      return;
    }

    let wpConfig: WordPressConfig;
    try {
      wpConfig = JSON.parse(wpConfigStr);
      if (!wpConfig.site_url || !wpConfig.username || !wpConfig.password) {
        throw new Error('WordPress 설정이 완전하지 않습니다.');
      }
    } catch {
      toastError('WordPress 설정이 올바르지 않습니다. 다시 설정해주세요.');
      setTimeout(() => router.push('/wordpress'), 2000);
      return;
    }

    setPublishingToWP(true);

    try {
      const publishData = {
        title: title,
        content: result.content,
        status: 'draft',
        categories: [],
        tags: [],
        generate_image: true,
        image_prompt: title,
        wp_config: wpConfig
      };

      const response = await apiCall('http://localhost:8000/api/wordpress/publish', {
        method: 'POST',
        body: JSON.stringify(publishData)
      });

      const resultData = await response.json();

      if (resultData.success) {
        success(`WordPress에 성공적으로 발행되었습니다! 상태: ${resultData.status}`);
      } else {
        toastError(`WordPress 발행 실패: ${resultData.error}`);
      }
    } catch (err) {
      toastError('WordPress 발행 중 오류가 발생했습니다.');
    } finally {
      setPublishingToWP(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">콘텐츠 생성</h1>
              <p className="text-gray-600 mt-2">AI가 고품질 블로그 콘텐츠를 자동으로 생성해드립니다</p>
            </div>
            <button
              onClick={() => setShowGuidelines(true)}
              className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 flex items-center"
            >
              <span className="mr-2">📋</span>
              작성 지침 보기
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                제목 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="예: AI 마케팅 전략의 모든 것"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                키워드 (선택사항)
              </label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="예: AI, 마케팅, 디지털 전략"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                콘텐츠 길이
              </label>
              <select
                value={length}
                onChange={(e) => setLength(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="short">짧게 (500-800자)</option>
                <option value="medium">보통 (800-1500자)</option>
                <option value="long">길게 (1500-3000자)</option>
              </select>
            </div>
          </div>

          <button
            onClick={generateContent}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading && (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
            {loading ? '생성 중...' : '콘텐츠 생성'}
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

        {result && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">생성된 콘텐츠</h2>
                <div className="flex space-x-2">
                  <button
                    onClick={() => copyToClipboard(result.content)}
                    className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-sm"
                  >
                    복사
                  </button>
                  <button
                    onClick={downloadAsFile}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
                  >
                    다운로드
                  </button>
                  <button
                    onClick={publishToWordPress}
                    disabled={publishingToWP}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm disabled:opacity-50 flex items-center"
                  >
                    {publishingToWP && (
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    )}
                    {publishingToWP ? '발행 중...' : 'WordPress 발행'}
                  </button>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              {/* 분석 점수 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-500 mb-1">SEO 점수</div>
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{ width: `${result.seo_score}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{result.seo_score}</span>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-500 mb-1">가독성 점수</div>
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${result.readability_score}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{result.readability_score}</span>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-500 mb-1">단어 수</div>
                  <div className="flex items-center">
                    <span className="text-lg font-bold text-gray-900">{result.word_count}자</span>
                  </div>
                </div>
              </div>
              
              {/* 콘텐츠 본문 */}
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap font-sans text-gray-900 leading-relaxed">
                    {result.content}
                  </pre>
                </div>
              </div>
              
              <div className="mt-4 text-sm text-gray-500">
                글자 수: {result.content.length.toLocaleString()}자
              </div>
            </div>
          </div>
        )}
      </div>
      
      <GuidelinesModal 
        isOpen={showGuidelines}
        onClose={() => setShowGuidelines(false)}
        type="content_guidelines"
      />
    </div>
  );
}