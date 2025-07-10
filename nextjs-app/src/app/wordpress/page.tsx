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
  
  const [publishForm, setPublishForm] = useState({
    title: '',
    content: '',
    status: 'draft',
    categories: [] as number[],
    tags: [] as number[],
    generate_image: false,
    image_prompt: ''
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

  // WordPress에 포스팅
  const publishToWordPress = async () => {
    if (!publishForm.title || !publishForm.content) {
      toastError('제목과 콘텐츠를 입력해주세요.');
      return;
    }

    if (connectionStatus !== 'success') {
      toastError('먼저 WordPress 연결을 테스트해주세요.');
      return;
    }

    setPublishing(true);

    try {
      const publishData = {
        ...publishForm,
        wp_config: wpConfig
      };

      const response = await apiCall('http://localhost:8000/api/wordpress/publish', {
        method: 'POST',
        body: JSON.stringify(publishData)
      });

      const result = await response.json();

      if (result.success) {
        success(`포스팅 성공! 상태: ${result.status}`);
        setPublishForm({
          title: '',
          content: '',
          status: 'draft',
          categories: [],
          tags: [],
          generate_image: false,
          image_prompt: ''
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">상태</label>
                  <select
                    value={publishForm.status}
                    onChange={(e) => setPublishForm({...publishForm, status: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                {publishing ? 'WordPress에 발행 중...' : 'WordPress에 발행'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}