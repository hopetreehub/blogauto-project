'use client';

import { useState } from 'react';

interface ContentResult {
  content: string;
  seo_score: number;
  geo_score: number;
  copyscape_result: string;
}

export default function ContentPage() {
  const [title, setTitle] = useState('');
  const [keywords, setKeywords] = useState('');
  const [length, setLength] = useState('medium');
  const [result, setResult] = useState<ContentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateContent = async () => {
    if (!title.trim()) {
      setError('제목을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/proxy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          endpoint: '/api/content/generate',
          method: 'POST',
          data: {
            title: title.trim(),
            keywords: keywords.trim(),
            length
          }
        })
      });

      if (!response.ok) {
        throw new Error('콘텐츠 생성에 실패했습니다.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // TODO: 토스트 메시지 표시
  };

  const downloadAsFile = () => {
    if (!result) return;
    
    const blob = new Blob([result.content], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${title.replace(/[^a-zA-Z0-9가-힣]/g, '_')}.txt`;
    link.click();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">콘텐츠 생성</h1>
          <p className="text-gray-600 mt-2">AI가 고품질 블로그 콘텐츠를 자동으로 생성해드립니다</p>
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

          {error && (
            <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
              {error}
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
                        style={{ width: `${result.geo_score}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{result.geo_score}</span>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-500 mb-1">중복 검사</div>
                  <div className="flex items-center">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      result.copyscape_result === 'Pass' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {result.copyscape_result === 'Pass' ? '통과' : '주의'}
                    </span>
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
    </div>
  );
}