'use client';

import { useState } from 'react';

interface Language {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  rtl?: boolean;
}

interface TranslationTask {
  id: string;
  sourceText: string;
  targetLanguage: string;
  translatedText: string;
  status: 'pending' | 'translating' | 'completed' | 'error';
  quality: number;
}

export default function LanguageSupport() {
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>(['ko', 'en', 'ja']);
  const [sourceContent, setSourceContent] = useState('');
  const [translationTasks, setTranslationTasks] = useState<TranslationTask[]>([]);
  const [isTranslating, setIsTranslating] = useState(false);
  const [selectedContentType, setSelectedContentType] = useState<'blog' | 'title' | 'meta'>('blog');

  const languages: Language[] = [
    { code: 'ko', name: 'Korean', nativeName: '한국어', flag: '🇰🇷' },
    { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
    { code: 'ja', name: 'Japanese', nativeName: '日本語', flag: '🇯🇵' },
    { code: 'zh', name: 'Chinese', nativeName: '中文', flag: '🇨🇳' },
    { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
    { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇵🇹' },
    { code: 'ru', name: 'Russian', nativeName: 'Русский', flag: '🇷🇺' },
    { code: 'ar', name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦', rtl: true },
    { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', flag: '🇮🇳' },
    { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt', flag: '🇻🇳' },
    { code: 'th', name: 'Thai', nativeName: 'ไทย', flag: '🇹🇭' },
    { code: 'id', name: 'Indonesian', nativeName: 'Bahasa Indonesia', flag: '🇮🇩' }
  ];

  const contentTypeOptions = [
    { value: 'blog', label: '블로그 포스트', icon: '📝' },
    { value: 'title', label: '제목 & 헤드라인', icon: '📰' },
    { value: 'meta', label: '메타 설명', icon: '🏷️' }
  ];

  const toggleLanguage = (code: string) => {
    setSelectedLanguages(prev =>
      prev.includes(code)
        ? prev.filter(lang => lang !== code)
        : [...prev, code]
    );
  };

  const translateContent = async () => {
    if (!sourceContent.trim() || selectedLanguages.length === 0) return;

    setIsTranslating(true);
    const tasks: TranslationTask[] = selectedLanguages.map(lang => ({
      id: `${lang}_${Date.now()}`,
      sourceText: sourceContent,
      targetLanguage: lang,
      translatedText: '',
      status: 'pending' as const,
      quality: 0
    }));

    setTranslationTasks(tasks);

    // 시뮬레이션: 각 언어별로 순차적으로 번역
    for (let i = 0; i < tasks.length; i++) {
      const task = tasks[i];
      
      // 번역 중 상태로 업데이트
      setTranslationTasks(prev => 
        prev.map(t => t.id === task.id ? { ...t, status: 'translating' as const } : t)
      );

      // 번역 시뮬레이션 (실제로는 API 호출)
      await new Promise(resolve => setTimeout(resolve, 1500));

      // 번역 완료
      const translatedText = generateMockTranslation(task.sourceText, task.targetLanguage);
      setTranslationTasks(prev => 
        prev.map(t => t.id === task.id ? { 
          ...t, 
          status: 'completed' as const,
          translatedText,
          quality: Math.floor(Math.random() * 20) + 80
        } : t)
      );
    }

    setIsTranslating(false);
  };

  const generateMockTranslation = (text: string, targetLang: string): string => {
    const translations: Record<string, string> = {
      en: 'AI-powered content marketing strategies are transforming how businesses engage with their audiences...',
      ja: 'AIを活用したコンテンツマーケティング戦略は、企業が顧客と関わる方法を変革しています...',
      zh: 'AI驱动的内容营销策略正在改变企业与受众互动的方式...',
      es: 'Las estrategias de marketing de contenidos impulsadas por IA están transformando la forma en que las empresas interactúan con sus audiencias...',
      fr: 'Les stratégies de marketing de contenu alimentées par l\'IA transforment la façon dont les entreprises interagissent avec leur public...',
      de: 'KI-gestützte Content-Marketing-Strategien verändern die Art und Weise, wie Unternehmen mit ihrem Publikum interagieren...',
      pt: 'As estratégias de marketing de conteúdo alimentadas por IA estão transformando a forma como as empresas se envolvem com seu público...',
      ru: 'Стратегии контент-маркетинга на основе ИИ трансформируют способы взаимодействия бизнеса с аудиторией...',
      ar: 'تعمل استراتيجيات تسويق المحتوى المدعومة بالذكاء الاصطناعي على تحويل طريقة تفاعل الشركات مع جماهيرها...',
      hi: 'एआई-संचालित सामग्री विपणन रणनीतियां व्यवसायों के अपने दर्शकों से जुड़ने के तरीके को बदल रही हैं...',
      vi: 'Chiến lược tiếp thị nội dung được hỗ trợ bởi AI đang thay đổi cách doanh nghiệp tương tác với khán giả...',
      th: 'กลยุทธ์การตลาดเนื้อหาที่ขับเคลื่อนด้วย AI กำลังเปลี่ยนแปลงวิธีที่ธุรกิจมีส่วนร่วมกับผู้ชม...',
      id: 'Strategi pemasaran konten yang didukung AI mengubah cara bisnis berinteraksi dengan audiens mereka...'
    };

    return translations[targetLang] || text;
  };

  const getQualityColor = (quality: number) => {
    if (quality >= 90) return 'text-green-600';
    if (quality >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const exportTranslations = () => {
    const completedTasks = translationTasks.filter(t => t.status === 'completed');
    const exportData = completedTasks.reduce((acc, task) => {
      const lang = languages.find(l => l.code === task.targetLanguage);
      acc[task.targetLanguage] = {
        language: lang?.name || task.targetLanguage,
        text: task.translatedText,
        quality: task.quality
      };
      return acc;
    }, {} as Record<string, any>);

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `translations_${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">다국어 지원</h1>
        <p className="text-gray-600">콘텐츠를 여러 언어로 번역하고 글로벌 독자에게 도달하세요</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 언어 선택 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">대상 언어 선택</h2>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => toggleLanguage(lang.code)}
                  className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                    selectedLanguages.includes(lang.code)
                      ? 'bg-blue-100 border-2 border-blue-500'
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{lang.flag}</span>
                    <div className="text-left">
                      <p className="font-medium">{lang.name}</p>
                      <p className="text-sm text-gray-600">{lang.nativeName}</p>
                    </div>
                  </div>
                  {selectedLanguages.includes(lang.code) && (
                    <span className="text-blue-600">✓</span>
                  )}
                </button>
              ))}
            </div>
            <div className="mt-4 text-sm text-gray-600">
              {selectedLanguages.length}개 언어 선택됨
            </div>
          </div>

          {/* 콘텐츠 타입 선택 */}
          <div className="bg-white rounded-lg shadow-md p-6 mt-4">
            <h3 className="text-lg font-semibold mb-3">콘텐츠 타입</h3>
            <div className="space-y-2">
              {contentTypeOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setSelectedContentType(option.value as any)}
                  className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors ${
                    selectedContentType === option.value
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <span className="text-xl">{option.icon}</span>
                  <span className="font-medium">{option.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 번역 영역 */}
        <div className="lg:col-span-2 space-y-6">
          {/* 원본 콘텐츠 입력 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">원본 콘텐츠</h2>
            <textarea
              value={sourceContent}
              onChange={(e) => setSourceContent(e.target.value)}
              className="w-full h-40 p-4 border rounded-lg resize-none focus:ring-2 focus:ring-blue-500"
              placeholder={
                selectedContentType === 'blog' ? '번역할 블로그 콘텐츠를 입력하세요...' :
                selectedContentType === 'title' ? '번역할 제목을 입력하세요...' :
                '번역할 메타 설명을 입력하세요...'
              }
            />
            <div className="mt-4 flex justify-between items-center">
              <span className="text-sm text-gray-600">
                {sourceContent.length}자
              </span>
              <button
                onClick={translateContent}
                disabled={!sourceContent.trim() || selectedLanguages.length === 0 || isTranslating}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
              >
                {isTranslating ? '번역 중...' : '번역 시작'}
              </button>
            </div>
          </div>

          {/* 번역 결과 */}
          {translationTasks.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">번역 결과</h2>
                {translationTasks.some(t => t.status === 'completed') && (
                  <button
                    onClick={exportTranslations}
                    className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                  >
                    📥 내보내기
                  </button>
                )}
              </div>
              <div className="space-y-4">
                {translationTasks.map((task) => {
                  const lang = languages.find(l => l.code === task.targetLanguage);
                  return (
                    <div key={task.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{lang?.flag}</span>
                          <span className="font-medium">{lang?.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {task.status === 'translating' && (
                            <span className="text-blue-600">번역 중...</span>
                          )}
                          {task.status === 'completed' && (
                            <>
                              <span className={`font-medium ${getQualityColor(task.quality)}`}>
                                품질: {task.quality}%
                              </span>
                              <button className="text-sm text-blue-600 hover:underline">
                                📋 복사
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                      <div className={`bg-gray-50 p-3 rounded ${lang?.rtl ? 'text-right' : ''}`}>
                        {task.status === 'completed' ? (
                          <p className="text-gray-800">{task.translatedText}</p>
                        ) : (
                          <div className="animate-pulse">
                            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* 번역 팁 */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 번역 최적화 팁</h3>
            <ul className="space-y-2 text-blue-800">
              <li>• 원본 콘텐츠는 명확하고 간결하게 작성하세요</li>
              <li>• 문화적 맥락을 고려하여 현지화가 필요한 부분을 표시하세요</li>
              <li>• SEO 키워드는 각 언어별로 최적화가 필요합니다</li>
              <li>• 번역 후 네이티브 스피커의 검토를 받는 것을 추천합니다</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}