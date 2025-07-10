'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigation = [
  { name: '대시보드', href: '/dashboard', icon: '📊' },
  { name: '키워드 분석', href: '/keywords', icon: '🔍' },
  { name: '제목 생성', href: '/titles', icon: '✍️' },
  { name: '콘텐츠 생성', href: '/content', icon: '📝' },
  { name: 'SEO 분석', href: '/seo', icon: '📈' },
  { name: '배치 작업', href: '/batch', icon: '⚡' },
  { name: 'WordPress', href: '/wordpress', icon: '🚀' },
  { name: '작성 지침', href: '/guidelines', icon: '📋' },
  { name: '설정', href: '/settings', icon: '⚙️' },
];

export default function Navigation() {
  const pathname = usePathname();

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between">
          <div className="flex">
            <Link href="/" className="flex items-center py-4 px-2">
              <span className="text-xl font-bold text-gray-800">🤖 블로그 자동화</span>
            </Link>
          </div>
          
          <div className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`py-4 px-2 text-sm font-medium transition-colors ${
                  pathname === item.href
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-500 hover:text-blue-600'
                }`}
              >
                <span className="mr-1">{item.icon}</span>
                {item.name}
              </Link>
            ))}
          </div>
          
          <div className="md:hidden flex items-center">
            <button className="outline-none mobile-menu-button">
              <svg className="w-6 h-6 text-gray-500" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} viewBox="0 0 24 24" stroke="currentColor" suppressHydrationWarning>
                <path d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <div className="hidden mobile-menu">
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`block px-3 py-2 text-sm font-medium ${
                pathname === item.href
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-500 hover:text-blue-600'
              }`}
            >
              <span className="mr-2">{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}