'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Stats {
  keywords_analyzed: number;
  titles_generated: number;
  content_generated: number;
  posts_published: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    keywords_analyzed: 0,
    titles_generated: 0,
    content_generated: 0,
    posts_published: 0
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/dashboard/stats');

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('통계 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: '키워드 분석',
      description: '새로운 키워드를 분석하여 기회를 찾아보세요',
      icon: '🔍',
      href: '/keywords',
      color: 'bg-blue-500'
    },
    {
      title: '제목 생성',
      description: 'AI로 매력적인 제목을 자동 생성하세요',
      icon: '✍️',
      href: '/titles',
      color: 'bg-green-500'
    },
    {
      title: '콘텐츠 생성',
      description: '고품질 블로그 콘텐츠를 AI로 작성하세요',
      icon: '📝',
      href: '/content',
      color: 'bg-purple-500'
    },
    {
      title: 'SEO 분석',
      description: '성과를 분석하고 최적화 방향을 확인하세요',
      icon: '📈',
      href: '/seo',
      color: 'bg-orange-500'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">블로그 자동화 대시보드</h1>
          <p className="text-gray-600 mt-2">프로젝트 현황을 한눈에 확인하고 새로운 작업을 시작하세요</p>
        </div>

        {/* 통계 카드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-3xl mb-2">🔍</div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">키워드 분석</p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : stats.keywords_analyzed.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-3xl mb-2">✍️</div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">제목 생성</p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : stats.titles_generated.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-3xl mb-2">📝</div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">콘텐츠 생성</p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : stats.content_generated.toLocaleString()}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="text-3xl mb-2">🚀</div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">포스팅 완료</p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : stats.posts_published.toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* 빠른 작업 */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">빠른 작업</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <Link
                key={index}
                href={action.href}
                className="block p-4 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-md transition-all"
              >
                <div className="flex items-center mb-3">
                  <div className={`w-10 h-10 ${action.color} rounded-lg flex items-center justify-center text-white text-xl mr-3`}>
                    {action.icon}
                  </div>
                  <h3 className="font-medium text-gray-900">{action.title}</h3>
                </div>
                <p className="text-sm text-gray-600">{action.description}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* 최근 활동 */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">시작하기</h2>
          <div className="text-gray-600">
            <p className="mb-4">
              블로그 자동화 시스템에 오신 것을 환영합니다! 다음 단계를 따라 시작해보세요:
            </p>
            <ol className="list-decimal list-inside space-y-2">
              <li>
                <Link href="/keywords" className="text-blue-600 hover:text-blue-800">
                  키워드 분석
                </Link>
                으로 타겟 키워드를 찾아보세요
              </li>
              <li>
                <Link href="/titles" className="text-blue-600 hover:text-blue-800">
                  제목 생성
                </Link>
                으로 매력적인 제목을 만들어보세요
              </li>
              <li>
                <Link href="/content" className="text-blue-600 hover:text-blue-800">
                  콘텐츠 생성
                </Link>
                으로 고품질 블로그 글을 작성하세요
              </li>
              <li>
                <Link href="/seo" className="text-blue-600 hover:text-blue-800">
                  SEO 분석
                </Link>
                으로 성과를 모니터링하세요
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}