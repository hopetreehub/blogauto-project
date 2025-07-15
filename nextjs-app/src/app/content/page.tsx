'use client';

import { useState, useEffect } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';
import { apiCall } from '@/utils/api';
import { useRouter } from 'next/navigation';
import GuidelinesModal from '@/components/GuidelinesModal';
import { useWorkflow } from '@/contexts/WorkflowContext';
import { useAutoSave, useBeforeUnload } from '@/hooks/useAutoSave';
import { AutoSaveStatus } from '@/components/AutoSaveStatus';
import WorkflowStepper from '@/components/WorkflowStepper';
import { 
  DocumentIcon, 
  ClipboardIcon, 
  SearchIcon, 
  PencilIcon, 
  CopyIcon, 
  DownloadIcon, 
  ImageIcon, 
  RocketIcon
} from '@/components/Icons';
import { AccessibleButton } from '@/components/AccessibleButton';
import { OptimizedImage } from '@/components/OptimizedImage';

interface ContentResult {
  content: string;
  seo_score: number;
  word_count: number;
  readability_score: number;
}

interface WordPressConfig {
  site_url: string;
  username: string;
  password: string;
}

export default function ContentPage() {
  const [title, setTitle] = useState('');
  const [keywords, setKeywords] = useState('');
  const [length, setLength] = useState('medium');
  const [result, setResult] = useState<ContentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showGuidelines, setShowGuidelines] = useState(false);
  const [publishingToWP, setPublishingToWP] = useState(false);
  const [generatingImage, setGeneratingImage] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const { toasts, success, error: toastError, removeToast } = useToast();
  const router = useRouter();
  
  // 워크플로우 상태 관리
  const { state: workflowState, actions: workflowActions } = useWorkflow();
  
  // 자동저장 설정
  const autoSaveData = {
    title,
    keywords,
    length,
    result,
    timestamp: Date.now()
  };
  
  const {
    saveNow,
    hasUnsavedChanges,
    lastSaved,
    restoreData
  } = useAutoSave(autoSaveData, {
    key: 'content_page',
    interval: 30000, // 30초마다 저장
    enabled: true
  });
  
  // 페이지 이탈 경고
  useBeforeUnload(hasUnsavedChanges);
  
  // 페이지 로드 시 워크플로우 설정 및 데이터 복원
  useEffect(() => {
    workflowActions.setStep('content');
    
    // 워크플로우에서 선택된 데이터 사용
    if (workflowState.selectedTitle) {
      setTitle(workflowState.selectedTitle);
    }
    if (workflowState.selectedKeyword) {
      setKeywords(workflowState.selectedKeyword);
    }
    
    // 저장된 데이터 복원
    const saved = restoreData();
    if (saved?.data) {
      setTitle(saved.data.title || workflowState.selectedTitle || '');
      setKeywords(saved.data.keywords || workflowState.selectedKeyword || '');
      setLength(saved.data.length || 'medium');
      setResult(saved.data.result || null);
    }
  }, []);

  const generateContent = async () => {
    if (!title.trim()) {
      toastError('제목을 입력해주세요.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await apiCall('http://localhost:8000/api/content/generate', {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim(),
          keyword: keywords.trim(),
          length
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        let errorMessage = '콘텐츠 생성에 실패했습니다.';
        
        switch (response.status) {
          case 400:
            errorMessage = '입력 데이터가 올바르지 않습니다. 제목을 확인해주세요.';
            break;
          case 401:
            errorMessage = 'API 키가 설정되지 않았습니다. 설정 페이지에서 API 키를 입력해주세요.';
            toastError('설정 페이지로 이동합니다.');
            setTimeout(() => router.push('/settings'), 2000);
            break;
          case 429:
            errorMessage = '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
            break;
          case 500:
            errorMessage = '서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.';
            break;
          default:
            errorMessage = errorData?.message || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setResult(data);
      workflowActions.setContent(data.content);
      success('고품질 콘텐츠가 성공적으로 생성되었습니다.');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.';
      
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('네트워크 연결을 확인해주세요. 인터넷 연결이 불안정할 수 있습니다.');
        toastError('네트워크 연결 오류');
      } else {
        setError(errorMessage);
        toastError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      success('콘텐츠가 클립보드에 복사되었습니다');
    } catch {
      toastError('복사에 실패했습니다');
    }
  };

  const downloadAsFile = () => {
    if (!result) return;
    
    try {
      const blob = new Blob([result.content], { type: 'text/plain;charset=utf-8' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${title.replace(/[^a-zA-Z0-9가-힣]/g, '_')}.txt`;
      link.click();
      success('파일이 다운로드되었습니다');
      URL.revokeObjectURL(link.href);
    } catch {
      toastError('다운로드에 실패했습니다');
    }
  };

  const publishToWordPress = async (publishType: 'now' | 'schedule' = 'now', scheduleDate?: string) => {
    if (!result) {
      toastError('먼저 콘텐츠를 생성해주세요.');
      return;
    }

    // WordPress 설정 확인
    const wpConfigStr = localStorage.getItem('wordpress_config');
    if (!wpConfigStr) {
      toastError('WordPress 설정이 필요합니다. WordPress 페이지에서 설정을 완료해주세요.');
      setTimeout(() => router.push('/wordpress'), 2000);
      return;
    }

    let wpConfig: WordPressConfig;
    try {
      wpConfig = JSON.parse(wpConfigStr);
      if (!wpConfig.site_url || !wpConfig.username || !wpConfig.password) {
        throw new Error('WordPress 설정이 완전하지 않습니다.');
      }
    } catch {
      toastError('WordPress 설정이 올바르지 않습니다. 다시 설정해주세요.');
      setTimeout(() => router.push('/wordpress'), 2000);
      return;
    }

    setPublishingToWP(true);

    try {
      let endpoint = 'http://localhost:8000/api/wordpress/publish-now';
      let publishData: any = {
        title: title,
        content: result.content,
        status: 'publish',
        categories: [],
        tags: extractTagsFromContent(result.content),
        generate_image: generatedImage ? false : true,
        image_url: generatedImage,
        image_prompt: title,
        wp_config: wpConfig
      };

      // 예약 발행인 경우
      if (publishType === 'schedule' && scheduleDate) {
        endpoint = 'http://localhost:8000/api/wordpress/schedule';
        publishData = {
          title: title,
          content: result.content,
          categories: [],
          tags: extractTagsFromContent(result.content),
          generate_image: generatedImage ? false : true,
          image_url: generatedImage,
          image_prompt: title,
          publish_datetime: scheduleDate,
          wp_config: wpConfig
        };
      }

      const response = await apiCall(endpoint, {
        method: 'POST',
        body: JSON.stringify(publishData)
      });

      const resultData = await response.json();

      if (resultData.success) {
        if (publishType === 'schedule') {
          success(`WordPress 예약 발행 성공! ${new Date(scheduleDate!).toLocaleString('ko-KR')}에 자동 발행됩니다.`);
        } else {
          success(`WordPress에 성공적으로 발행되었습니다! 상태: ${resultData.status_message}`);
          // 워크플로우 완료 상태로 이동
          setTimeout(() => {
            router.push('/wordpress');
          }, 2000);
        }
      } else {
        toastError(`WordPress 발행 실패: ${resultData.error}`);
      }
    } catch (err) {
      toastError('WordPress 발행 중 오류가 발생했습니다.');
    } finally {
      setPublishingToWP(false);
    }
  };

  // 태그 추출 함수
  const extractTagsFromContent = (content: string): string[] => {
    // 태그 패턴 매칭 및 생성
    const tagPatterns = [
      /키워드:\s*([^\n]+)/g,
      /태그:\s*([^\n]+)/g,
      /#([a-zA-Z가-힣0-9]+)/g
    ];
    
    const tags = new Set<string>();
    
    // 키워드에서 태그 추출
    if (keywords) {
      keywords.split(',').forEach(k => {
        const tag = k.trim();
        if (tag) tags.add(tag);
      });
    }
    
    // 콘텐츠에서 태그 패턴 추출
    tagPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        if (match[1]) {
          match[1].split(',').forEach((tag: string) => {
            const cleanTag = tag.trim().replace(/[#]/g, '');
            if (cleanTag) tags.add(cleanTag);
          });
        }
      }
    });
    
    return Array.from(tags).slice(0, 10); // 최대 10개 태그
  };

  // 이미지 생성 함수
  const generateImageForContent = async () => {
    if (!title) {
      toastError('먼저 제목을 입력해주세요.');
      return;
    }

    // 🔬 전문가 디버깅: API 키 상태 사전 체크
    const settings = localStorage.getItem('api_settings');
    const parsedSettings = settings ? JSON.parse(settings) : null;
    console.log('🔍 [Image Generation Debug] Pre-check:', {
      hasLocalStorage: !!settings,
      hasOpenAIKey: !!(parsedSettings?.openai_api_key),
      keyLength: parsedSettings?.openai_api_key?.length || 0,
      title: title,
      keywords: keywords
    });

    setGeneratingImage(true);
    try {
      const response = await apiCall('http://localhost:8000/api/images/generate', {
        method: 'POST',
        body: JSON.stringify({
          title: title,
          keyword: keywords,
          prompt: '',
          style: 'professional',
          size: '1024x1024',
          quality: 'standard'
        })
      });

      console.log('🔍 [Image Generation Debug] Response Status:', response.status);
      
      const imageResult = await response.json();
      console.log('🔍 [Image Generation Debug] Response Body:', imageResult);
      
      if (imageResult.success && imageResult.image_url) {
        setGeneratedImage(imageResult.image_url);
        success('이미지가 성공적으로 생성되었습니다!');
      } else {
        console.error('🔍 [Image Generation Error]:', imageResult);
        if (response.status === 401) {
          toastError('API 키 인증 실패. 설정 페이지에서 OpenAI API 키를 확인해주세요.');
        } else {
          toastError(imageResult.error || '이미지 생성에 실패했습니다.');
        }
      }
    } catch (err) {
      console.error('🔍 [Image Generation Exception]:', err);
      toastError('이미지 생성 중 오류가 발생했습니다.');
    } finally {
      setGeneratingImage(false);
    }
  };

  const showPublishOptions = () => {
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const scheduleOptions = [
      { label: '지금 즈시 발행', action: () => publishToWordPress('now') },
      { label: '1시간 후 발행', action: () => {
        const oneHourLater = new Date(now.getTime() + 60 * 60 * 1000);
        publishToWordPress('schedule', oneHourLater.toISOString());
      }},
      { label: '내일 오전 9시 발행', action: () => {
        const tomorrow9AM = new Date(tomorrow);
        tomorrow9AM.setHours(9, 0, 0, 0);
        publishToWordPress('schedule', tomorrow9AM.toISOString());
      }},
      { label: '사용자 지정 예약', action: () => {
        const customDate = prompt('예약 날짜와 시간을 입력해주세요 (YYYY-MM-DD HH:MM)', 
          tomorrow.toISOString().slice(0, 16).replace('T', ' '));
        if (customDate) {
          const scheduleDateTime = new Date(customDate.replace(' ', 'T'));
          if (scheduleDateTime > now) {
            publishToWordPress('schedule', scheduleDateTime.toISOString());
          } else {
            toastError('예약 시간은 현재 시간보다 이후여야 합니다.');
          }
        }
      }}
    ];

    // 간단한 옵션 메뉴 표시
    const optionsList = scheduleOptions.map((option, index) => 
      `${index + 1}. ${option.label}`
    ).join('\n');
    
    const choice = prompt(`WordPress 발행 옵션을 선택해주세요:\n\n${optionsList}\n\n번호를 입력하세요:`);
    
    const choiceIndex = parseInt(choice || '0') - 1;
    if (choiceIndex >= 0 && choiceIndex < scheduleOptions.length) {
      scheduleOptions[choiceIndex].action();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-7xl mx-auto">
        {/* 워크플로우 스테퍼 */}
        <WorkflowStepper className="mb-6" />
        
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">콘텐츠 생성</h1>
              <p className="text-gray-600 mt-2">AI가 고품질 블로그 콘텐츠를 자동으로 생성해드립니다</p>
              
              {(workflowState.selectedKeyword || workflowState.selectedTitle) && (
                <div className="mt-2 space-y-1">
                  {workflowState.selectedKeyword && (
                    <div className="flex items-center text-sm text-blue-600">
                      <SearchIcon className="mr-2" size={16} />
                      선택된 키워드: <span className="font-medium ml-1">{workflowState.selectedKeyword}</span>
                    </div>
                  )}
                  {workflowState.selectedTitle && (
                    <div className="flex items-center text-sm text-green-600">
                      <PencilIcon className="mr-2" size={16} />
                      선택된 제목: <span className="font-medium ml-1">{workflowState.selectedTitle}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
            <div className="flex items-center gap-4">
              {/* 자동저장 상태 */}
              <AutoSaveStatus 
                hasUnsavedChanges={hasUnsavedChanges}
                lastSaved={lastSaved}
                onSaveNow={saveNow}
              />
              <AccessibleButton
                onClick={() => setShowGuidelines(true)}
                variant="secondary"
                icon={<ClipboardIcon size={16} />}
                ariaLabel="콘텐츠 작성 지침 보기"
              >
                작성 지침 보기
              </AccessibleButton>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                제목 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="예: AI 마케팅 전략의 모든 것"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                키워드 (선택사항)
              </label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="예: AI, 마케팅, 디지털 전략"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                콘텐츠 길이
              </label>
              <select
                value={length}
                onChange={(e) => setLength(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="short">짧게 (500-800자)</option>
                <option value="medium">보통 (800-1500자)</option>
                <option value="long">길게 (1500-3000자)</option>
              </select>
            </div>
          </div>

          <AccessibleButton
            onClick={generateContent}
            disabled={loading}
            loading={loading}
            icon={<DocumentIcon size={18} />}
            ariaLabel="AI 콘텐츠 생성 시작"
            size="lg"
          >
            콘텐츠 생성
          </AccessibleButton>

          {error && !loading && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3 flex-1">
                  <h3 className="text-sm font-medium text-red-800">문제가 발생했습니다</h3>
                  <div className="mt-2 text-sm text-red-700">
                    {error}
                  </div>
                  <div className="mt-3">
                    <AccessibleButton
                      onClick={() => setError('')}
                      variant="ghost"
                      size="sm"
                      ariaLabel="오류 메시지 닫기"
                      className="bg-red-100 text-red-800 hover:bg-red-200"
                    >
                      닫기
                    </AccessibleButton>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {result && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-gray-900">생성된 콘텐츠</h2>
                <div className="flex space-x-2">
                  <AccessibleButton
                    onClick={() => copyToClipboard(result.content)}
                    variant="secondary"
                    icon={<CopyIcon size={16} />}
                    ariaLabel="생성된 콘텐츠 복사"
                    size="sm"
                  >
                    복사
                  </AccessibleButton>
                  <AccessibleButton
                    onClick={downloadAsFile}
                    icon={<DownloadIcon size={16} />}
                    ariaLabel="콘텐츠를 텍스트 파일로 다운로드"
                    size="sm"
                  >
                    다운로드
                  </AccessibleButton>
                  <AccessibleButton
                    onClick={generateImageForContent}
                    disabled={generatingImage}
                    loading={generatingImage}
                    variant="secondary"
                    icon={<ImageIcon size={16} />}
                    ariaLabel="콘텐츠에 맞는 이미지 생성"
                    size="sm"
                    className="bg-purple-600 text-white hover:bg-purple-700"
                  >
                    이미지 생성
                  </AccessibleButton>
                  <AccessibleButton
                    onClick={showPublishOptions}
                    disabled={publishingToWP}
                    loading={publishingToWP}
                    variant="secondary"
                    icon={<RocketIcon size={16} />}
                    ariaLabel="WordPress에 콘텐츠 발행"
                    size="sm"
                    className="bg-green-600 text-white hover:bg-green-700"
                  >
                    WordPress 발행
                  </AccessibleButton>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              {/* 분석 점수 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-500 mb-1">SEO 점수</div>
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-green-600 h-2 rounded-full" 
                        style={{ width: `${result.seo_score}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{result.seo_score}</span>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-500 mb-1">가독성 점수</div>
                  <div className="flex items-center">
                    <div className="w-full bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${result.readability_score}%` }}
                      ></div>
                    </div>
                    <span className="text-lg font-bold text-gray-900">{result.readability_score}</span>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-500 mb-1">단어 수</div>
                  <div className="flex items-center">
                    <span className="text-lg font-bold text-gray-900">{result.word_count}자</span>
                  </div>
                </div>
              </div>
              
              {/* 생성된 이미지 표시 */}
              {generatedImage && (
                <div className="border border-gray-200 rounded-lg p-6 mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <ImageIcon className="mr-2" size={20} />
                    생성된 이미지
                  </h3>
                  <div className="flex justify-center">
                    <OptimizedImage
                      src={generatedImage}
                      alt={`${title}에 대한 생성된 이미지`}
                      width={400}
                      height={400}
                      className="max-w-full h-auto rounded-lg shadow-md"
                      priority={false}
                    />
                  </div>
                  <div className="mt-4 text-sm text-gray-500 text-center">
                    이 이미지는 WordPress 발행 시 자동으로 업로드됩니다.
                  </div>
                </div>
              )}

              {/* 콘텐츠 본문 */}
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap font-sans text-gray-900 leading-relaxed">
                    {result.content}
                  </pre>
                </div>
              </div>
              
              <div className="mt-4 text-sm text-gray-500">
                글자 수: {result.content.length.toLocaleString()}자
              </div>
            </div>
          </div>
        )}
      </div>
      
      <GuidelinesModal 
        isOpen={showGuidelines}
        onClose={() => setShowGuidelines(false)}
        type="content_guidelines"
      />
    </div>
  );
}