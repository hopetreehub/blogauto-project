'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useMemo, useCallback, memo } from 'react';
import { useSidebar } from './SidebarLayout';
import { ThemeToggle } from './ThemeToggle';
import { 
  SearchIcon, 
  PencilIcon, 
  DocumentIcon, 
  ImageIcon, 
  RocketIcon,
  DatabaseIcon,
  ChartIcon,
  SettingsIcon,
  CheckmarkIcon,
  TrendingIcon,
  BroadcastIcon,
  ClipboardIcon,
  RobotIcon,
  BoltIcon,
  PaletteIcon
} from './Icons';

interface NavigationCategory {
  name: string;
  icon: React.ComponentType<any>;
  items: {
    name: string;
    href: string;
    icon: React.ComponentType<any>;
  }[];
}

const navigationCategories: NavigationCategory[] = [
  {
    name: '콘텐츠 워크플로우',
    icon: PaletteIcon,
    items: [
      { name: '키워드 분석', href: '/keywords', icon: SearchIcon },
      { name: '제목 생성', href: '/titles', icon: PencilIcon },
      { name: '콘텐츠 생성', href: '/content', icon: DocumentIcon },
      { name: '이미지 생성', href: '/images', icon: ImageIcon },
      { name: '저장된 콘텐츠', href: '/saved', icon: DatabaseIcon },
    ]
  },
  {
    name: '발행 & 마케팅',
    icon: RocketIcon,
    items: [
      { name: 'WordPress', href: '/wordpress', icon: RocketIcon },
      { name: 'SNS 포스팅', href: '/sns', icon: BroadcastIcon },
    ]
  },
  {
    name: '분석 & 최적화',
    icon: ChartIcon,
    items: [
      { name: '대시보드', href: '/dashboard', icon: ChartIcon },
      { name: 'SEO 분석', href: '/seo', icon: TrendingIcon },
      { name: '품질 검사', href: '/quality', icon: CheckmarkIcon },
    ]
  },
  {
    name: '설정 & 관리',
    icon: SettingsIcon,
    items: [
      { name: '설정', href: '/settings', icon: SettingsIcon },
      { name: '작성 지침', href: '/guidelines', icon: ClipboardIcon },
      { name: '배치 작업', href: '/batch', icon: BoltIcon },
    ]
  },
];

function Navigation() {
  const pathname = usePathname();
  const { isOpen: isSidebarOpen, toggle: toggleSidebar } = useSidebar();
  
  // 초기 확장 카테고리 메모이제이션
  const initialExpandedCategories = useMemo(
    () => navigationCategories.map(cat => cat.name),
    []
  );
  
  const [expandedCategories, setExpandedCategories] = useState<string[]>(
    initialExpandedCategories
  );

  // 카테고리 토글 함수 메모이제이션
  const toggleCategory = useCallback((categoryName: string) => {
    setExpandedCategories(prev => 
      prev.includes(categoryName)
        ? prev.filter(name => name !== categoryName)
        : [...prev, categoryName]
    );
  }, []);

  return (
    <>
      <div className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 shadow-md h-16 flex items-center justify-between px-4">
        <div className="flex items-center">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors"
            aria-label={isSidebarOpen ? '사이드바 닫기' : '사이드바 열기'}
            aria-expanded={isSidebarOpen}
          >
            <svg 
              className="w-6 h-6 text-gray-600 dark:text-gray-400" 
              fill="none" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              viewBox="0 0 24 24" 
              stroke="currentColor"
              suppressHydrationWarning
            >
              <path d={isSidebarOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} suppressHydrationWarning></path>
            </svg>
          </button>
          <Link href="/" className="ml-4 flex items-center">
            <RobotIcon className="text-blue-600 dark:text-blue-400 mr-2" size={24} />
            <span className="text-xl font-bold text-gray-800 dark:text-gray-200">블로그 자동화</span>
          </Link>
        </div>
        
        {/* 테마 토글 */}
        <div className="flex items-center space-x-2">
          <ThemeToggle variant="icon" size="md" />
        </div>
      </div>

      <aside className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white dark:bg-gray-900 shadow-lg transition-all duration-300 z-40 ${
        isSidebarOpen ? 'w-64' : 'w-16'
      } overflow-hidden`}>
        <div className="p-4 overflow-y-auto h-full">
          <nav className="space-y-2">
            {navigationCategories.map((category) => (
              <div key={category.name} className="space-y-1">
                <button
                  onClick={() => toggleCategory(category.name)}
                  className={`w-full flex items-center justify-between px-3 py-2 text-sm font-semibold rounded-lg transition-colors ${
                    isSidebarOpen ? 'hover:bg-gray-100 dark:hover:bg-gray-800 focus:ring-2 focus:ring-blue-500 focus:outline-none' : ''
                  }`}
                  title={!isSidebarOpen ? category.name : ''}
                  aria-expanded={expandedCategories.includes(category.name)}
                  aria-controls={`category-${category.name}`}
                >
                  <div className="flex items-center">
                    <category.icon className="text-gray-600 dark:text-gray-400 flex-shrink-0" size={20} />
                    <span className={`ml-3 transition-all duration-300 ${
                      isSidebarOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0'
                    } overflow-hidden whitespace-nowrap text-gray-900 dark:text-gray-100`}>
                      {category.name}
                    </span>
                  </div>
                  {isSidebarOpen && (
                    <svg
                      className={`w-4 h-4 transition-transform duration-200 text-gray-500 dark:text-gray-400 ${
                        expandedCategories.includes(category.name) ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path d="M19 9l-7 7-7-7"></path>
                    </svg>
                  )}
                </button>
                <div 
                  id={`category-${category.name}`}
                  className={`${
                    expandedCategories.includes(category.name) ? 'block' : 'hidden'
                  } ${isSidebarOpen ? 'ml-8' : 'ml-0'} space-y-1`}
                >
                  {category.items.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors group ${
                        pathname === item.href
                          ? 'bg-blue-100 text-blue-700'
                          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                      }`}
                      title={!isSidebarOpen ? item.name : ''}
                    >
                      <item.icon className={`flex-shrink-0 ${
                        pathname === item.href ? 'text-blue-700' : 'text-gray-500'
                      }`} size={16} />
                      <span className={`ml-3 transition-all duration-300 ${
                        isSidebarOpen ? 'opacity-100 w-auto' : 'opacity-0 w-0'
                      } overflow-hidden whitespace-nowrap`}>{item.name}</span>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </nav>
        </div>
      </aside>

      <div className={`fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden transition-opacity duration-300 ${
        isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
      }`} onClick={toggleSidebar} />
    </>
  );
}

export default memo(Navigation);