'use client'

import { useState, useEffect } from 'react'
import { apiCall } from '@/utils/api'

interface ImageResult {
  success: boolean;
  error?: string;
  image_url?: string;
  local_path?: string;
  revised_prompt?: string;
}

export default function ImagesPage() {
  const [title, setTitle] = useState('')
  const [keyword, setKeyword] = useState('')
  const [customPrompt, setCustomPrompt] = useState('')
  const [selectedStyle, setSelectedStyle] = useState('professional')
  const [selectedSize, setSelectedSize] = useState('1024x1024')
  const [quality, setQuality] = useState('standard')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ImageResult | null>(null)

  const generateImage = async () => {
    // API 키 확인
    const savedSettings = localStorage.getItem('api_settings')
    if (!savedSettings || !JSON.parse(savedSettings).openai_api_key) {
      alert('설정 페이지에서 OpenAI API 키를 먼저 입력해주세요!')
      window.location.href = '/settings'
      return
    }

    if (!title && !keyword && !customPrompt) {
      alert('제목, 키워드 또는 사용자 정의 프롬프트 중 하나는 입력해주세요!')
      return
    }

    setLoading(true)
    setResult(null)

    try {
      const response = await apiCall('http://localhost:8000/api/images/generate', {
        method: 'POST',
        body: JSON.stringify({
          title: title,
          keyword: keyword,
          prompt: customPrompt,
          size: selectedSize,
          quality: quality,
          style: selectedStyle
        })
      })

      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('이미지 생성 실패:', error)
      setResult({
        success: false,
        error: '이미지 생성 중 오류가 발생했습니다.',
        image_url: '',
        local_path: '',
        revised_prompt: ''
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🎨 이미지 생성</h1>
          <p className="text-gray-600 mt-2">AI를 활용하여 블로그용 고품질 이미지를 생성합니다</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 입력 폼 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">이미지 생성 설정</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  제목 (선택사항)
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="예: 디지털 마케팅 완벽 가이드"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  키워드 (선택사항)
                </label>
                <input
                  type="text"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  placeholder="예: 마케팅, SEO, 전략"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  사용자 정의 프롬프트 (선택사항)
                </label>
                <textarea
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="원하는 이미지를 구체적으로 설명해주세요"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    스타일
                  </label>
                  <select
                    value={selectedStyle}
                    onChange={(e) => setSelectedStyle(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="professional">전문적 - 깔끔하고 전문적인 스타일</option>
                    <option value="creative">창의적 - 예술적이고 창의적인 스타일</option>
                    <option value="minimalist">미니멀 - 단순하고 깔끔한 디자인</option>
                    <option value="infographic">인포그래픽 - 데이터 시각화 스타일</option>
                    <option value="illustration">일러스트 - 디지털 일러스트 스타일</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    크기
                  </label>
                  <select
                    value={selectedSize}
                    onChange={(e) => setSelectedSize(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="1024x1024">정사각형 (1024x1024)</option>
                    <option value="1792x1024">가로형 (1792x1024)</option>
                    <option value="1024x1792">세로형 (1024x1792)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  품질
                </label>
                <select
                  value={quality}
                  onChange={(e) => setQuality(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="standard">표준</option>
                  <option value="hd">고화질 (HD)</option>
                </select>
              </div>

              <button
                onClick={generateImage}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? '이미지 생성 중...' : '🎨 이미지 생성'}
              </button>
            </div>
          </div>

          {/* 결과 표시 */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">생성 결과</h2>
            
            {!result && !loading && (
              <div className="text-center py-12 text-gray-500">
                <div className="text-6xl mb-4">🖼️</div>
                <p>이미지를 생성하면 여기에 표시됩니다</p>
              </div>
            )}

            {loading && (
              <div className="text-center py-12 text-gray-500">
                <div className="text-6xl mb-4">⏳</div>
                <p>AI가 이미지를 생성하고 있습니다...</p>
                <p className="text-sm mt-2">보통 10-30초 정도 소요됩니다</p>
              </div>
            )}

            {result && result.success && (
              <div className="space-y-4">
                <div className="border rounded-lg overflow-hidden">
                  <img 
                    src={result.image_url} 
                    alt="Generated Image"
                    className="w-full h-auto"
                  />
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                  <div>
                    <label className="text-sm font-medium text-gray-700">수정된 프롬프트:</label>
                    <p className="text-sm text-gray-600 mt-1">{result.revised_prompt}</p>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => window.open(result.image_url, '_blank')}
                      className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                    >
                      원본 보기
                    </button>
                    <button
                      onClick={() => {
                        if (result.image_url) {
                          const link = document.createElement('a')
                          link.href = result.image_url
                          link.download = 'generated-image.png'
                          link.click()
                        }
                      }}
                      className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                    >
                      다운로드
                    </button>
                  </div>
                </div>
              </div>
            )}

            {result && !result.success && (
              <div className="text-center py-12 text-red-500">
                <div className="text-6xl mb-4">❌</div>
                <p className="font-medium">이미지 생성 실패</p>
                <p className="text-sm mt-2">{result.error}</p>
              </div>
            )}
          </div>
        </div>

        {/* 사용법 안내 */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">💡 사용법 안내</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
            <div>
              <h4 className="font-medium mb-2">📝 입력 방법</h4>
              <ul className="space-y-1">
                <li>• 제목과 키워드만 입력하면 자동 프롬프트 생성</li>
                <li>• 사용자 정의 프롬프트로 구체적인 이미지 요청</li>
                <li>• 스타일을 선택하여 원하는 느낌 조절</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">🎨 최적화 팁</h4>
              <ul className="space-y-1">
                <li>• 블로그 글과 관련된 키워드 사용</li>
                <li>• 구체적이고 명확한 설명 작성</li>
                <li>• 고화질(HD)는 더 선명하지만 생성 시간 증가</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}