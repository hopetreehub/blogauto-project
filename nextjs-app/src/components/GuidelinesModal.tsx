'use client';

import { useState, useEffect } from 'react';
import { getGuidelineByType } from '@/utils/guidelines';

interface GuidelinesModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'keyword_guidelines' | 'title_guidelines' | 'content_guidelines' | 'seo_guidelines';
}

const GUIDELINE_TITLES = {
  keyword_guidelines: '키워드 분석 지침',
  title_guidelines: '제목 생성 지침', 
  content_guidelines: '콘텐츠 작성 지침',
  seo_guidelines: 'SEO 최적화 지침'
};

export default function GuidelinesModal({ isOpen, onClose, type }: GuidelinesModalProps) {
  const [guidelines, setGuidelines] = useState('');

  useEffect(() => {
    if (isOpen) {
      const guideline = getGuidelineByType(type);
      setGuidelines(guideline);
    }
  }, [isOpen, type]);

  if (!isOpen) return null;

  // 마크다운 텍스트를 간단한 HTML로 변환
  const formatGuidelines = (text: string) => {
    return text
      .split('\n')
      .map((line, index) => {
        if (line.startsWith('# ')) {
          return <h2 key={index} className="text-xl font-bold mt-4 mb-2">{line.slice(2)}</h2>;
        } else if (line.startsWith('## ')) {
          return <h3 key={index} className="text-lg font-semibold mt-3 mb-2">{line.slice(3)}</h3>;
        } else if (line.startsWith('### ')) {
          return <h4 key={index} className="text-md font-medium mt-2 mb-1">{line.slice(4)}</h4>;
        } else if (line.startsWith('- ')) {
          return <li key={index} className="ml-4 mb-1">{line.slice(2)}</li>;
        } else if (line.trim() === '') {
          return <br key={index} />;
        } else {
          return <p key={index} className="mb-2">{line}</p>;
        }
      });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-4xl max-h-[80vh] overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold">{GUIDELINE_TITLES[type]}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="px-6 py-4 overflow-y-auto max-h-[60vh]">
          <div className="prose prose-sm max-w-none">
            {formatGuidelines(guidelines)}
          </div>
        </div>
        
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
}