'use client';

import { useState, useEffect } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';
import { apiCall } from '@/utils/api';

interface WordPressConfig {
  site_url: string;
  username: string;
  password: string;
}

interface WordPressCategory {
  id: number;
  name: string;
}

interface WordPressTag {
  id: number;
  name: string;
}

export default function WordPressPage() {
  const [wpConfig, setWpConfig] = useState<WordPressConfig>({
    site_url: '',
    username: '',
    password: ''
  });
  
  const [connectionStatus, setConnectionStatus] = useState<'none' | 'testing' | 'success' | 'failed'>('none');
  const [connectionResult, setConnectionResult] = useState<any>(null);
  const [categories, setCategories] = useState<WordPressCategory[]>([]);
  const [tags, setTags] = useState<WordPressTag[]>([]);
  const [publishing, setPublishing] = useState(false);
  const [scheduledPosts, setScheduledPosts] = useState([]);
  const [showScheduledPosts, setShowScheduledPosts] = useState(false);
  
  const [publishForm, setPublishForm] = useState({
    title: '',
    content: '',
    status: 'draft',
    categories: [] as number[],
    tags: [] as number[],
    generate_image: false,
    image_prompt: '',
    publish_type: 'now', // 'now', 'schedule'
    schedule_date: '',
    schedule_time: '',
    excerpt: '',
    meta_description: ''
  });

  const { toasts, success, error: toastError, removeToast } = useToast();

  // localStorage에서 WordPress 설정 불러오기
  useEffect(() => {
    const saved = localStorage.getItem('wordpress_config');
    if (saved) {
      setWpConfig(JSON.parse(saved));
    }
  }, []);

  // WordPress 설정 저장
  const saveConfig = () => {
    if (!wpConfig.site_url || !wpConfig.username || !wpConfig.password) {
      toastError('모든 필드를 입력해주세요.');
      return;
    }

    localStorage.setItem('wordpress_config', JSON.stringify(wpConfig));
    success('WordPress 설정이 저장되었습니다.');
  };

  // WordPress 연결 테스트
  const testConnection = async () => {
    if (!wpConfig.site_url || !wpConfig.username || !wpConfig.password) {
      toastError('WordPress 설정을 먼저 입력해주세요.');
      return;
    }

    setConnectionStatus('testing');
    setConnectionResult(null);

    try {
      const response = await apiCall('http://localhost:8000/api/wordpress/test-connection', {
        method: 'POST',
        body: JSON.stringify(wpConfig)
      });

      const data = await response.json();
      setConnectionResult(data);
      
      if (data.success) {
        setConnectionStatus('success');
        success(`연결 성공! 사용자: ${data.user}`);
        await loadCategoriesAndTags();
        await loadScheduledPosts();
      } else {
        setConnectionStatus('failed');
        toastError(`연결 실패: ${data.error}`);
      }
    } catch (err) {
      setConnectionStatus('failed');
      setConnectionResult({ success: false, error: '연결 테스트 중 오류 발생' });
      toastError('연결 테스트 실패');
    }
  };

  // 카테고리와 태그 불러오기
  const loadCategoriesAndTags = async () => {
    try {
      const [catResponse, tagResponse] = await Promise.all([
        fetch(`http://localhost:8000/api/wordpress/categories?site_url=${encodeURIComponent(wpConfig.site_url)}&username=${encodeURIComponent(wpConfig.username)}&password=${encodeURIComponent(wpConfig.password)}`),
        fetch(`http://localhost:8000/api/wordpress/tags?site_url=${encodeURIComponent(wpConfig.site_url)}&username=${encodeURIComponent(wpConfig.username)}&password=${encodeURIComponent(wpConfig.password)}`)
      ]);

      const catData = await catResponse.json();
      const tagData = await tagResponse.json();

      if (catData.success) setCategories(catData.categories);
      if (tagData.success) setTags(tagData.tags);
    } catch (err) {
      console.error('카테고리/태그 로드 실패:', err);
    }
  };

  // 컴포넌트 마운트 시 예약된 포스트 로드
  useEffect(() => {
    if (connectionStatus === 'success') {
      loadScheduledPosts();
    }
  }, [connectionStatus]);

  // 예약된 포스트 목록 불러오기
  const loadScheduledPosts = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/wordpress/scheduled-posts');
      const data = await response.json();
      if (data.success) {
        setScheduledPosts(data.scheduled_posts);
      }
    } catch (err) {
      console.error('예약된 포스트 로드 실패:', err);
    }
  };

  // WordPress에 포스팅 (즈시 또는 예약)
  const publishToWordPress = async () => {
    if (!publishForm.title || !publishForm.content) {
      toastError('제목과 콘텐츠를 입력해주세요.');
      return;
    }

    if (connectionStatus !== 'success') {
      toastError('먼저 WordPress 연결을 테스트해주세요.');
      return;
    }

    // 예약 발행 유효성 검사
    if (publishForm.publish_type === 'schedule') {
      if (!publishForm.schedule_date || !publishForm.schedule_time) {
        toastError('예약 날짜와 시간을 설정해주세요.');
        return;
      }

      const scheduleDateTime = new Date(`${publishForm.schedule_date}T${publishForm.schedule_time}`);
      if (scheduleDateTime <= new Date()) {
        toastError('예약 시간은 현재 시간보다 이후여야 합니다.');
        return;
      }
    }

    setPublishing(true);

    try {
      let endpoint = 'http://localhost:8000/api/wordpress/publish-now';
      let publishData: any = {
        title: publishForm.title,
        content: publishForm.content,
        status: publishForm.status,
        categories: publishForm.categories,
        tags: publishForm.tags,
        generate_image: publishForm.generate_image,
        image_prompt: publishForm.image_prompt,
        excerpt: publishForm.excerpt,
        meta_description: publishForm.meta_description,
        wp_config: wpConfig
      };

      // 예약 발행인 경우
      if (publishForm.publish_type === 'schedule') {
        endpoint = 'http://localhost:8000/api/wordpress/schedule';
        const scheduleDateTime = new Date(`${publishForm.schedule_date}T${publishForm.schedule_time}`);
        publishData = {
          title: publishForm.title,
          content: publishForm.content,
          categories: publishForm.categories,
          tags: publishForm.tags,
          generate_image: publishForm.generate_image,
          image_prompt: publishForm.image_prompt,
          excerpt: publishForm.excerpt,
          meta_description: publishForm.meta_description,
          publish_datetime: scheduleDateTime.toISOString(),
          wp_config: wpConfig
        };
      }

      const response = await apiCall(endpoint, {
        method: 'POST',
        body: JSON.stringify(publishData)
      });

      const result = await response.json();

      if (result.success) {
        if (publishForm.publish_type === 'schedule') {
          success(`예약 발행 성공! ${result.publish_datetime}에 자동 발행됩니다.`);
          await loadScheduledPosts(); // 예약 목록 새로고침
        } else {
          success(`포스팅 성공! 상태: ${result.status_message}`);
        }
        
        // 폼 초기화
        setPublishForm({
          title: '',
          content: '',
          status: 'draft',
          categories: [],
          tags: [],
          generate_image: false,
          image_prompt: '',
          publish_type: 'now',
          schedule_date: '',
          schedule_time: '',
          excerpt: '',
          meta_description: ''
        });
      } else {
        toastError(`포스팅 실패: ${result.error}`);
      }
    } catch (err) {
      toastError('포스팅 중 오류 발생');
    } finally {
      setPublishing(false);
    }
  };

  // 예약 포스트 취소
  const cancelScheduledPost = async (scheduleId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/wordpress/scheduled-posts/${scheduleId}`, {
        method: 'DELETE'
      });
      const result = await response.json();
      
      if (result.success) {
        success('예약이 취소되었습니다.');
        await loadScheduledPosts();
      } else {
        toastError(`예약 취소 실패: ${result.error}`);
      }
    } catch (err) {
      toastError('예약 취소 중 오류 발생');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">WordPress 자동 포스팅</h1>
          <p className="text-gray-600 mt-2">WordPress 사이트에 생성된 콘텐츠를 자동으로 발행합니다</p>
        </div>

        {/* WordPress 설정 */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">WordPress 설정</h2>
          
          <div className="grid grid-cols-1 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                사이트 URL <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                value={wpConfig.site_url}
                onChange={(e) => setWpConfig({...wpConfig, site_url: e.target.value})}
                placeholder="https://your-wordpress-site.com"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                사용자명 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={wpConfig.username}
                onChange={(e) => setWpConfig({...wpConfig, username: e.target.value})}
                placeholder="WordPress 사용자명"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                애플리케이션 비밀번호 <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                value={wpConfig.password}
                onChange={(e) => setWpConfig({...wpConfig, password: e.target.value})}
                placeholder="WordPress 애플리케이션 비밀번호"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-sm text-gray-500 mt-1">
                WordPress 관리자 → 사용자 → 프로필에서 애플리케이션 비밀번호를 생성하세요
              </p>
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={saveConfig}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              설정 저장
            </button>
            
            <button
              onClick={testConnection}
              disabled={connectionStatus === 'testing'}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {connectionStatus === 'testing' ? '테스트 중...' : '연결 테스트'}
            </button>
          </div>

          {/* 연결 상태 표시 */}
          {connectionResult && (
            <div className={`mt-4 p-4 rounded-lg ${connectionResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-3 ${connectionResult.success ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <div>
                  <p className={`font-medium ${connectionResult.success ? 'text-green-800' : 'text-red-800'}`}>
                    {connectionResult.success ? '연결 성공' : '연결 실패'}
                  </p>
                  <p className={`text-sm ${connectionResult.success ? 'text-green-600' : 'text-red-600'}`}>
                    {connectionResult.success ? `사용자: ${connectionResult.user}` : connectionResult.error}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 포스팅 양식 */}
        {connectionStatus === 'success' && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">콘텐츠 발행</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  제목 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={publishForm.title}
                  onChange={(e) => setPublishForm({...publishForm, title: e.target.value})}
                  placeholder="포스트 제목"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  콘텐츠 <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={publishForm.content}
                  onChange={(e) => setPublishForm({...publishForm, content: e.target.value})}
                  placeholder="포스트 내용"
                  rows={10}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* 발행 유형 선택 */}
              <div className="border-t pt-4">
                <label className="block text-sm font-medium text-gray-700 mb-3">발행 유형</label>
                <div className="flex space-x-4 mb-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="publish_type"
                      value="now"
                      checked={publishForm.publish_type === 'now'}
                      onChange={(e) => setPublishForm({...publishForm, publish_type: e.target.value})}
                      className="mr-2"
                    />
                    즈시 발행
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="publish_type"
                      value="schedule"
                      checked={publishForm.publish_type === 'schedule'}
                      onChange={(e) => setPublishForm({...publishForm, publish_type: e.target.value})}
                      className="mr-2"
                    />
                    예약 발행
                  </label>
                </div>

                {/* 예약 발행 옵션 */}
                {publishForm.publish_type === 'schedule' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 p-4 bg-blue-50 rounded-lg">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        예약 날짜 <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="date"
                        value={publishForm.schedule_date}
                        onChange={(e) => setPublishForm({...publishForm, schedule_date: e.target.value})}
                        min={new Date().toISOString().split('T')[0]}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        예약 시간 <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="time"
                        value={publishForm.schedule_time}
                        onChange={(e) => setPublishForm({...publishForm, schedule_time: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    상태 {publishForm.publish_type === 'schedule' ? '(예약시 자동 결정)' : ''}
                  </label>
                  <select
                    value={publishForm.status}
                    onChange={(e) => setPublishForm({...publishForm, status: e.target.value})}
                    disabled={publishForm.publish_type === 'schedule'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  >
                    <option value="draft">임시저장</option>
                    <option value="publish">발행</option>
                    <option value="private">비공개</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">카테고리</label>
                  <select
                    multiple
                    value={publishForm.categories.map(String)}
                    onChange={(e) => setPublishForm({
                      ...publishForm, 
                      categories: Array.from(e.target.selectedOptions, option => parseInt(option.value))
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    size={4}
                  >
                    {categories.map(cat => (
                      <option key={cat.id} value={cat.id}>{cat.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* 추가 옵션 */}
              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">발취문 (선택사항)</label>
                  <textarea
                    value={publishForm.excerpt}
                    onChange={(e) => setPublishForm({...publishForm, excerpt: e.target.value})}
                    placeholder="짧은 소개글 (검색 결과에 표시)"
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">메타 설명 (선택사항)</label>
                  <textarea
                    value={publishForm.meta_description}
                    onChange={(e) => setPublishForm({...publishForm, meta_description: e.target.value})}
                    placeholder="SEO를 위한 메타 설명 (150-160자 권장)"
                    rows={2}
                    maxLength={160}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <div className="text-sm text-gray-500 mt-1">
                    {publishForm.meta_description.length}/160자
                  </div>
                </div>
              </div>

              {/* 이미지 생성 옵션 */}
              <div className="border-t pt-4">
                <div className="flex items-center mb-4">
                  <input
                    type="checkbox"
                    id="generate_image"
                    checked={publishForm.generate_image}
                    onChange={(e) => setPublishForm({...publishForm, generate_image: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="generate_image" className="ml-2 block text-sm text-gray-900">
                    AI로 대표 이미지 생성 (DALL-E 3)
                  </label>
                </div>

                {publishForm.generate_image && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      이미지 프롬프트 (선택사항)
                    </label>
                    <input
                      type="text"
                      value={publishForm.image_prompt}
                      onChange={(e) => setPublishForm({...publishForm, image_prompt: e.target.value})}
                      placeholder="이미지 설명 (비워두면 제목 사용)"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                )}
              </div>

              <button
                onClick={publishToWordPress}
                disabled={publishing}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
              >
                {publishing && (
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                )}
                {publishing ? (
                  publishForm.publish_type === 'schedule' ? '예약 설정 중...' : 'WordPress에 발행 중...'
                ) : (
                  publishForm.publish_type === 'schedule' ? '예약 발행 설정' : 'WordPress에 즈시 발행'
                )}
              </button>
            </div>
          </div>
        )}

        {/* 예약된 포스트 관리 */}
        {connectionStatus === 'success' && (
          <div className="bg-white rounded-lg shadow p-6 mt-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">예약된 포스트 관리</h2>
              <div className="flex space-x-2">
                <button
                  onClick={loadScheduledPosts}
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-sm"
                >
                  새로고침
                </button>
                <button
                  onClick={() => setShowScheduledPosts(!showScheduledPosts)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
                >
                  {showScheduledPosts ? '숨기기' : '보기'} ({scheduledPosts.length})
                </button>
              </div>
            </div>

            {showScheduledPosts && (
              <div className="space-y-4">
                {scheduledPosts.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    예약된 포스트가 없습니다.
                  </div>
                ) : (
                  scheduledPosts.map((post: any) => (
                    <div key={post.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 mb-2">{post.title}</h3>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div>
                              <span className="font-medium">예약 시간:</span> 
                              {new Date(post.publish_date).toLocaleString('ko-KR', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </div>
                            <div>
                              <span className="font-medium">상태:</span>
                              <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                                post.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                                post.status === 'published' ? 'bg-green-100 text-green-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {post.status === 'scheduled' ? '예약됨' :
                                 post.status === 'published' ? '발행됨' : '실패'}
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex space-x-2 ml-4">
                          {post.status === 'scheduled' && (
                            <button
                              onClick={() => cancelScheduledPost(post.id)}
                              className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                            >
                              취소
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}