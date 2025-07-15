import Link from 'next/link';
import { 
  SearchIcon, 
  PencilIcon, 
  DocumentIcon, 
  ImageIcon, 
  RocketIcon 
} from '@/components/Icons';
import { AccessibleButton } from '@/components/AccessibleButton';

export default function Home() {
  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-20">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
              블로그 자동화 프로세스
            </h1>
            <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
              AI 기반 키워드 분석부터 콘텐츠 생성, 자동 포스팅까지 한 번에 처리하는 완전 자동화 솔루션
            </p>
            <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
              <Link href="/dashboard">
                <AccessibleButton size="lg" ariaLabel="블로그 자동화 시작하기">
                  시작하기
                </AccessibleButton>
              </Link>
            </div>
          </div>

          <div className="mt-20">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-5">
              <div className="text-center group hover:transform hover:scale-105 transition-transform duration-200">
                <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-blue-100 rounded-full">
                  <SearchIcon className="text-blue-600" size={32} />
                </div>
                <h3 className="text-lg font-medium text-gray-900">키워드 분석</h3>
                <p className="mt-2 text-sm text-gray-500">
                  검색량, 경쟁도, CPC 분석으로 최적의 키워드 발굴
                </p>
              </div>
              <div className="text-center group hover:transform hover:scale-105 transition-transform duration-200">
                <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-green-100 rounded-full">
                  <PencilIcon className="text-green-600" size={32} />
                </div>
                <h3 className="text-lg font-medium text-gray-900">제목 생성</h3>
                <p className="mt-2 text-sm text-gray-500">
                  AI 기반 매력적이고 SEO 최적화된 제목 자동 생성
                </p>
              </div>
              <div className="text-center group hover:transform hover:scale-105 transition-transform duration-200">
                <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-purple-100 rounded-full">
                  <DocumentIcon className="text-purple-600" size={32} />
                </div>
                <h3 className="text-lg font-medium text-gray-900">콘텐츠 생성</h3>
                <p className="mt-2 text-sm text-gray-500">
                  전문가급 블로그 콘텐츠를 AI로 자동 생성
                </p>
              </div>
              <div className="text-center group hover:transform hover:scale-105 transition-transform duration-200">
                <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-orange-100 rounded-full">
                  <ImageIcon className="text-orange-600" size={32} />
                </div>
                <h3 className="text-lg font-medium text-gray-900">이미지 생성</h3>
                <p className="mt-2 text-sm text-gray-500">
                  DALL-E 3로 고품질 블로그용 이미지 자동 생성
                </p>
              </div>
              <div className="text-center group hover:transform hover:scale-105 transition-transform duration-200">
                <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-red-100 rounded-full">
                  <RocketIcon className="text-red-600" size={32} />
                </div>
                <h3 className="text-lg font-medium text-gray-900">자동 포스팅</h3>
                <p className="mt-2 text-sm text-gray-500">
                  워드프레스, 블로그스팟 등에 예약 포스팅 자동화
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
