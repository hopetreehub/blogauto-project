'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface SavedContent {
  id: string
  title: string
  keyword: string
  content_type: string
  created_at: string
  updated_at: string
  word_count: number
  seo_score: number
  status: string
}

interface ContentStats {
  total_content: number
  total_words: number
  avg_seo_score: number
  status_counts: { [key: string]: number }
  storage_size_mb: number
}

export default function SavedContentPage() {
  const [savedContent, setSavedContent] = useState<SavedContent[]>([])
  const [stats, setStats] = useState<ContentStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedContent, setSelectedContent] = useState<any>(null)
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    loadSavedContent()
    loadStats()
  }, [query, statusFilter])

  const loadSavedContent = async () => {
    try {
      const params = new URLSearchParams()
      if (query) params.append('query', query)
      if (statusFilter) params.append('status', statusFilter)
      params.append('limit', '50')

      const response = await fetch(`http://localhost:8000/api/content/saved?${params}`)
      const data = await response.json()
      
      if (data.success) {
        setSavedContent(data.content)
      }
    } catch (error) {
      console.error('저장된 콘텐츠 로드 실패:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/content/stats')
      const data = await response.json()
      
      if (data.success) {
        setStats(data.stats)
      }
    } catch (error) {
      console.error('통계 로드 실패:', error)
    }
  }

  const viewContent = async (contentId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/content/saved/${contentId}`)
      const data = await response.json()
      
      if (data.success) {
        setSelectedContent(data.content)
      }
    } catch (error) {
      console.error('콘텐츠 상세 조회 실패:', error)
    }
  }

  const deleteContent = async (contentId: string) => {
    if (!confirm('이 콘텐츠를 삭제하시겠습니까?')) return

    try {
      const response = await fetch(`http://localhost:8000/api/content/saved/${contentId}`, {
        method: 'DELETE'
      })
      const data = await response.json()
      
      if (data.success) {
        setSavedContent(prev => prev.filter(item => item.id !== contentId))
        setSelectedContent(null)
        loadStats()
        alert('콘텐츠가 삭제되었습니다.')
      }
    } catch (error) {
      console.error('콘텐츠 삭제 실패:', error)
      alert('콘텐츠 삭제에 실패했습니다.')
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusBadge = (status: string) => {
    const statusStyles: {[key: string]: string} = {
      draft: 'bg-gray-100 text-gray-800',
      published: 'bg-green-100 text-green-800',
      archived: 'bg-red-100 text-red-800'
    }
    
    const statusNames: {[key: string]: string} = {
      draft: '초안',
      published: '발행',
      archived: '보관'
    }

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusStyles[status] || statusStyles.draft}`}>
        {statusNames[status] || status}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">💾 저장된 콘텐츠</h1>
          <p className="text-gray-600 mt-2">생성된 모든 콘텐츠를 확인하고 관리할 수 있습니다</p>
        </div>

        {/* 통계 카드 */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-blue-600">{stats.total_content}</div>
              <div className="text-sm text-gray-600">총 콘텐츠</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-green-600">{stats.total_words.toLocaleString()}</div>
              <div className="text-sm text-gray-600">총 단어 수</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-purple-600">{stats.avg_seo_score}</div>
              <div className="text-sm text-gray-600">평균 SEO 점수</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-2xl font-bold text-orange-600">{stats.storage_size_mb} MB</div>
              <div className="text-sm text-gray-600">저장소 사용량</div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* 콘텐츠 목록 */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b">
                <div className="flex flex-col md:flex-row gap-4">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="제목 또는 키워드로 검색..."
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">모든 상태</option>
                    <option value="draft">초안</option>
                    <option value="published">발행</option>
                    <option value="archived">보관</option>
                  </select>
                </div>
              </div>
              
              <div className="p-6">
                {loading ? (
                  <div className="text-center py-8">
                    <div className="text-gray-500">로딩 중...</div>
                  </div>
                ) : savedContent.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-6xl mb-4">📝</div>
                    <div className="text-gray-500">저장된 콘텐츠가 없습니다</div>
                    <div className="text-sm text-gray-400 mt-2">
                      <Link href="/content" className="text-blue-500 hover:underline">
                        콘텐츠 생성하기
                      </Link>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {savedContent.map((content) => (
                      <div
                        key={content.id}
                        className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 cursor-pointer transition-colors"
                        onClick={() => viewContent(content.id)}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="font-medium text-gray-900 truncate flex-1">
                            {content.title}
                          </h3>
                          {getStatusBadge(content.status)}
                        </div>
                        
                        <div className="text-sm text-gray-600 mb-2">
                          키워드: {content.keyword || '없음'}
                        </div>
                        
                        <div className="flex justify-between items-center text-xs text-gray-500">
                          <div>
                            {content.word_count}자 · SEO {content.seo_score}점
                          </div>
                          <div>
                            {formatDate(content.created_at)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 콘텐츠 상세 */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow">
              <div className="p-6">
                <h2 className="text-lg font-semibold mb-4">콘텐츠 상세</h2>
                
                {!selectedContent ? (
                  <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-2">👁️</div>
                    <div>콘텐츠를 선택하여 상세 내용을 확인하세요</div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">
                        {selectedContent.title}
                      </h3>
                      <div className="text-sm text-gray-600 space-y-1">
                        <div>키워드: {selectedContent.keyword || '없음'}</div>
                        <div>생성일: {formatDate(selectedContent.created_at)}</div>
                        <div>단어 수: {selectedContent.word_count}자</div>
                        <div>SEO 점수: {selectedContent.seo_score}점</div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">콘텐츠 미리보기</h4>
                      <div className="bg-gray-50 p-3 rounded text-sm text-gray-700 max-h-60 overflow-y-auto">
                        {selectedContent.content?.substring(0, 500)}
                        {selectedContent.content?.length > 500 && '...'}
                      </div>
                    </div>
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(selectedContent.content)
                          alert('콘텐츠가 클립보드에 복사되었습니다!')
                        }}
                        className="flex-1 bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600"
                      >
                        복사
                      </button>
                      <button
                        onClick={() => deleteContent(selectedContent.id)}
                        className="px-3 py-2 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                      >
                        삭제
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}