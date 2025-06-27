'use client';

import { useState, useEffect } from 'react';

interface SEODashboardData {
  keyword_performance: {
    total_keywords: number;
    avg_search_volume: number;
    avg_opportunity_score: number;
    competition_distribution: Record<string, number>;
    top_keywords: Array<{
      keyword: string;
      search_volume: number;
      opportunity_score: number;
      competition: string;
    }>;
  };
  content_analytics: {
    total_content: number;
    avg_seo_score: number;
    avg_geo_score: number;
    content_by_day: Array<{ date: string; count: number }>;
    seo_score_distribution: Record<string, number>;
  };
  title_analytics: {
    total_titles: number;
    avg_duplicate_rate: number;
    language_distribution: Record<string, number>;
    tone_distribution: Record<string, number>;
    titles_by_day: Array<{ date: string; count: number }>;
  };
  productivity_metrics: {
    period_stats: {
      keywords: number;
      titles: number;
      content: number;
    };
    daily_averages: {
      keywords_per_day: number;
      titles_per_day: number;
      content_per_day: number;
    };
    completion_rates: {
      keyword_to_title: number;
      title_to_content: number;
      overall_completion: number;
    };
  };
}

export default function SEOPage() {
  const [data, setData] = useState<SEODashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [days, setDays] = useState(30);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/proxy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          endpoint: `/api/seo/dashboard?days=${days}`,
          method: 'GET'
        })
      });

      if (!response.ok) {
        throw new Error('SEO 데이터를 불러올 수 없습니다.');
      }

      const dashboardData = await response.json();
      setData(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [days]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">SEO 데이터를 불러오는 중...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">SEO 분석 대시보드</h1>
            <p className="text-gray-600 mt-2">키워드, 콘텐츠, 성과를 종합적으로 분석합니다</p>
          </div>
          <div>
            <select
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>최근 7일</option>
              <option value={30}>최근 30일</option>
              <option value={90}>최근 90일</option>
            </select>
          </div>
        </div>

        {data && (
          <div className="space-y-8">
            {/* 키워드 성과 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">키워드 성과</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {data.keyword_performance.total_keywords}
                  </div>
                  <div className="text-gray-600">총 키워드 수</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {Math.round(data.keyword_performance.avg_search_volume).toLocaleString()}
                  </div>
                  <div className="text-gray-600">평균 검색량</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {Math.round(data.keyword_performance.avg_opportunity_score)}
                  </div>
                  <div className="text-gray-600">평균 기회점수</div>
                </div>
              </div>
              
              {data.keyword_performance.top_keywords.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-3">상위 키워드</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">키워드</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">검색량</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">경쟁도</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">기회점수</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {data.keyword_performance.top_keywords.slice(0, 5).map((keyword, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {keyword.keyword}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {keyword.search_volume.toLocaleString()}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                keyword.competition === 'Low' ? 'bg-green-100 text-green-800' :
                                keyword.competition === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {keyword.competition}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {keyword.opportunity_score}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>

            {/* 콘텐츠 분석 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">콘텐츠 분석</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {data.content_analytics.total_content}
                  </div>
                  <div className="text-gray-600">총 콘텐츠 수</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {Math.round(data.content_analytics.avg_seo_score)}
                  </div>
                  <div className="text-gray-600">평균 SEO 점수</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">
                    {Math.round(data.content_analytics.avg_geo_score)}
                  </div>
                  <div className="text-gray-600">평균 가독성 점수</div>
                </div>
              </div>
            </div>

            {/* 생산성 지표 */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">생산성 지표</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">기간별 통계</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-600">키워드:</span>
                      <span className="font-semibold">{data.productivity_metrics.period_stats.keywords}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">제목:</span>
                      <span className="font-semibold">{data.productivity_metrics.period_stats.titles}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">콘텐츠:</span>
                      <span className="font-semibold">{data.productivity_metrics.period_stats.content}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-3">완성률</h3>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-600">키워드 → 제목</span>
                        <span className="text-sm font-medium">
                          {Math.round(data.productivity_metrics.completion_rates.keyword_to_title)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${data.productivity_metrics.completion_rates.keyword_to_title}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-600">제목 → 콘텐츠</span>
                        <span className="text-sm font-medium">
                          {Math.round(data.productivity_metrics.completion_rates.title_to_content)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${data.productivity_metrics.completion_rates.title_to_content}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-gray-600">전체 완성률</span>
                        <span className="text-sm font-medium">
                          {Math.round(data.productivity_metrics.completion_rates.overall_completion)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-600 h-2 rounded-full" 
                          style={{ width: `${data.productivity_metrics.completion_rates.overall_completion}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}