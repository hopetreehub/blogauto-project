'use client';

import { useState } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';
import { apiCall } from '@/utils/api';

interface SEOAnalysisResult {
  score: number;
  keyword_density: number;
  recommendations: string[];
}

export default function SEOPage() {
  const [url, setUrl] = useState('');
  const [content, setContent] = useState('');
  const [keyword, setKeyword] = useState('');
  const [result, setResult] = useState<SEOAnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { toasts, success, error: toastError, removeToast } = useToast();

  const analyzeSEO = async () => {
    if (!content.trim() && !url.trim()) {
      toastError('URL 또는 콘텐츠를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await apiCall('http://localhost:8000/api/seo/analyze', {
        method: 'POST',
        body: JSON.stringify({
          url: url.trim(),
          content: content.trim(),
          keyword: keyword.trim()
        })
      });

      if (!response.ok) {
        throw new Error('SEO 분석에 실패했습니다.');
      }

      const data = await response.json();
      setResult(data);
      success('SEO 분석이 완료되었습니다.');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'SEO 분석 중 오류가 발생했습니다.';
      setError(errorMessage);
      toastError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">SEO 분석</h1>
          <p className="text-gray-600 mt-2">콘텐츠의 SEO 최적화 수준을 분석합니다</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                URL (선택)
              </label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/blog-post"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                분석할 콘텐츠
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="분석할 콘텐츠를 입력하세요..."
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                타겟 키워드 (선택)
              </label>
              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="SEO 최적화할 키워드"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <div className="mt-6">
            <button
              onClick={analyzeSEO}
              disabled={loading}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'SEO 분석 중...' : 'SEO 분석 시작'}
            </button>
          </div>
        </div>

        {result && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-6">SEO 분석 결과</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 mb-2">전체 SEO 점수</div>
                <div className="flex items-center">
                  <div className="w-full bg-gray-200 rounded-full h-3 mr-3">
                    <div 
                      className={`h-3 rounded-full ${
                        result.score >= 80 ? 'bg-green-600' :
                        result.score >= 60 ? 'bg-yellow-600' : 'bg-red-600'
                      }`}
                      style={{ width: `${result.score}%` }}
                    ></div>
                  </div>
                  <span className="text-2xl font-bold text-gray-900">{result.score}</span>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm font-medium text-gray-500 mb-2">키워드 밀도</div>
                <div className="flex items-center">
                  <span className="text-2xl font-bold text-gray-900">{result.keyword_density}%</span>
                  <span className="ml-2 text-sm text-gray-500">
                    (권장: 2-3%)
                  </span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">개선 권장사항</h3>
              <div className="space-y-2">
                {result.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start">
                    <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium mr-3">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{recommendation}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}