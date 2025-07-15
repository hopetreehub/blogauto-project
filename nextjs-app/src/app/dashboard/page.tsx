'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getLocalStorageItem, setLocalStorageItem } from '@/types';
import { 
  SearchIcon, 
  PencilIcon, 
  DocumentIcon, 
  ImageIcon, 
  RocketIcon,
  ClipboardIcon,
  TrendingIcon,
  BroadcastIcon,
  BoltIcon,
  SparkleIcon,
  BookIcon,
  ChartIcon
} from '@/components/Icons';
import { AccessibleButton } from '@/components/AccessibleButton';

interface QuickAction {
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  href: string;
  color: string;
}

export default function Dashboard() {
  const [userLevel, setUserLevel] = useState<'beginner' | 'professional' | 'advanced'>('beginner');
  const [stats, setStats] = useState({
    totalPosts: 0,
    totalKeywords: 0,
    totalImages: 0,
    avgSEOScore: 0
  });

  // 초보자용 퀵 액션
  const beginnerActions: QuickAction[] = [
    {
      title: '첫 블로그 글 작성하기',
      description: '키워드부터 콘텐츠까지 한번에!',
      icon: SparkleIcon,
      href: '/keywords',
      color: 'bg-blue-500'
    },
    {
      title: '가이드 보기',
      description: '블로그 자동화 시작하기',
      icon: BookIcon,
      href: '/guidelines',
      color: 'bg-green-500'
    }
  ];

  // 전문가용 퀵 액션
  const professionalActions: QuickAction[] = [
    {
      title: '배치 작업 시작',
      description: '대량 콘텐츠 생성',
      icon: BoltIcon,
      href: '/batch',
      color: 'bg-purple-500'
    },
    {
      title: 'SEO 성과 분석',
      description: '검색 순위 최적화',
      icon: TrendingIcon,
      href: '/seo',
      color: 'bg-orange-500'
    },
    {
      title: 'SNS 캠페인',
      description: '멀티채널 마케팅',
      icon: BroadcastIcon,
      href: '/sns',
      color: 'bg-pink-500'
    }
  ];

  const currentActions = userLevel === 'beginner' ? beginnerActions : professionalActions;

  useEffect(() => {
    // API에서 통계 데이터 가져오기 (시뮬레이션)
    setStats({
      totalPosts: 42,
      totalKeywords: 156,
      totalImages: 89,
      avgSEOScore: 87
    });

    // 로컬 스토리지에서 사용자 레벨 불러오기
    const savedLevel = getLocalStorageItem<'beginner' | 'professional' | 'advanced'>('userLevel', 'beginner');
    setUserLevel(savedLevel);
  }, []);

  const handleLevelChange = (level: typeof userLevel) => {
    setUserLevel(level);
    setLocalStorageItem('userLevel', level);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
          <div className="flex gap-2">
            <AccessibleButton
              onClick={() => handleLevelChange('beginner')}
              variant={userLevel === 'beginner' ? 'primary' : 'secondary'}
              size="sm"
              ariaLabel="초보 모드로 전환"
            >
              초보 모드
            </AccessibleButton>
            <AccessibleButton
              onClick={() => handleLevelChange('professional')}
              variant={userLevel === 'professional' ? 'primary' : 'secondary'}
              size="sm"
              ariaLabel="전문가 모드로 전환"
            >
              전문가 모드
            </AccessibleButton>
          </div>
        </div>
        
        {userLevel === 'beginner' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-blue-800">
              <span className="font-semibold">👋 환영합니다!</span> 블로그 자동화가 처음이신가요? 
              아래 가이드를 따라 첫 블로그 글을 작성해보세요.
            </p>
          </div>
        )}
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">전체 포스트</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalPosts}</p>
            </div>
            <DocumentIcon className="text-blue-600" size={32} />
          </div>
          <p className="text-xs text-green-600 mt-2">↑ 12% 증가</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">분석된 키워드</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalKeywords}</p>
            </div>
            <SearchIcon className="text-green-600" size={32} />
          </div>
          <p className="text-xs text-green-600 mt-2">↑ 8% 증가</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">생성된 이미지</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalImages}</p>
            </div>
            <ImageIcon className="text-purple-600" size={32} />
          </div>
          <p className="text-xs text-green-600 mt-2">↑ 23% 증가</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">평균 SEO 점수</p>
              <p className="text-2xl font-bold text-gray-900">{stats.avgSEOScore}점</p>
            </div>
            <TrendingIcon className="text-orange-600" size={32} />
          </div>
          <p className="text-xs text-green-600 mt-2">↑ 5점 상승</p>
        </div>
      </div>

      {/* 퀵 액션 */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">
          {userLevel === 'beginner' ? '🚀 빠른 시작' : '⚡ 퀵 액션'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {currentActions.map((action, index) => (
            <Link key={index} href={action.href}>
              <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 cursor-pointer border hover:border-blue-300">
                <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center mb-4`}>
                  <action.icon className="text-white" size={24} />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{action.title}</h3>
                <p className="text-sm text-gray-600">{action.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* 워크플로우 가이드 (초보자 모드) */}
      {userLevel === 'beginner' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">📋 블로그 작성 단계</h2>
          <div className="space-y-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">1</div>
              <div className="ml-4">
                <Link href="/keywords" className="font-medium text-blue-600 hover:underline">키워드 분석</Link>
                <p className="text-sm text-gray-600">인기 키워드를 찾아 트렌드를 파악하세요</p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">2</div>
              <div className="ml-4">
                <Link href="/titles" className="font-medium text-blue-600 hover:underline">제목 생성</Link>
                <p className="text-sm text-gray-600">매력적인 제목으로 클릭률을 높이세요</p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">3</div>
              <div className="ml-4">
                <Link href="/content" className="font-medium text-blue-600 hover:underline">콘텐츠 작성</Link>
                <p className="text-sm text-gray-600">AI가 고품질 콘텐츠를 생성합니다</p>
              </div>
            </div>
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold">4</div>
              <div className="ml-4">
                <Link href="/wordpress" className="font-medium text-blue-600 hover:underline">발행하기</Link>
                <p className="text-sm text-gray-600">WordPress나 SNS에 자동으로 발행하세요</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 최근 활동 (전문가 모드) */}
      {userLevel === 'professional' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">📊 최근 활동</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b">
              <div className="flex items-center">
                <DocumentIcon className="text-blue-600 mr-3" size={24} />
                <div>
                  <p className="font-medium">배치 작업 완료</p>
                  <p className="text-sm text-gray-600">10개 콘텐츠 생성</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">2시간 전</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <div className="flex items-center">
                <BroadcastIcon className="text-purple-600 mr-3" size={24} />
                <div>
                  <p className="font-medium">SNS 자동 포스팅</p>
                  <p className="text-sm text-gray-600">5개 플랫폼 동시 배포</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">3시간 전</span>
            </div>
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center">
                <TrendingIcon className="text-green-600 mr-3" size={24} />
                <div>
                  <p className="font-medium">SEO 순위 상승</p>
                  <p className="text-sm text-gray-600">&quot;AI 마케팅&quot; 키워드 3위</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">어제</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}