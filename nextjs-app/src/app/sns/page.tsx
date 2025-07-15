'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface SocialPlatform {
  id: string;
  name: string;
  icon: string;
  color: string;
  connected: boolean;
  apiEnabled?: boolean;
  requiredFields?: string[];
}

interface PlatformConfig {
  [key: string]: {
    api_key?: string;
    api_secret?: string;
    access_token?: string;
    access_token_secret?: string;
    app_id?: string;
    app_secret?: string;
    page_id?: string;
    business_account_id?: string;
  };
}

export default function SNSIntegration() {
  const [platforms, setPlatforms] = useState<SocialPlatform[]>([
    { 
      id: 'twitter', 
      name: 'Twitter/X', 
      icon: '𝕏', 
      color: 'bg-black', 
      connected: false, 
      apiEnabled: true,
      requiredFields: ['api_key', 'api_secret', 'access_token', 'access_token_secret']
    },
    { 
      id: 'facebook', 
      name: 'Facebook', 
      icon: '📘', 
      color: 'bg-blue-600', 
      connected: false, 
      apiEnabled: true,
      requiredFields: ['app_id', 'app_secret', 'access_token']
    },
    { 
      id: 'instagram', 
      name: 'Instagram', 
      icon: '📷', 
      color: 'bg-gradient-to-r from-purple-500 to-pink-500', 
      connected: false, 
      apiEnabled: true,
      requiredFields: ['app_id', 'app_secret', 'access_token', 'business_account_id']
    },
    { 
      id: 'linkedin', 
      name: 'LinkedIn', 
      icon: '💼', 
      color: 'bg-blue-700', 
      connected: false, 
      apiEnabled: true,
      requiredFields: ['api_key', 'api_secret', 'access_token']
    },
    { 
      id: 'youtube', 
      name: 'YouTube', 
      icon: '📺', 
      color: 'bg-red-600', 
      connected: false, 
      apiEnabled: true,
      requiredFields: ['api_key', 'api_secret', 'access_token']
    },
    { 
      id: 'tiktok', 
      name: 'TikTok', 
      icon: '🎵', 
      color: 'bg-black', 
      connected: false, 
      apiEnabled: true,
      requiredFields: ['api_key', 'api_secret', 'access_token']
    },
    { 
      id: 'pinterest', 
      name: 'Pinterest', 
      icon: '📌', 
      color: 'bg-red-700', 
      connected: false, 
      apiEnabled: true,
      requiredFields: ['api_key', 'api_secret', 'access_token']
    },
    { 
      id: 'threads', 
      name: 'Threads', 
      icon: '🧵', 
      color: 'bg-gray-900', 
      connected: false, 
      apiEnabled: true,
      requiredFields: ['api_key', 'api_secret', 'access_token']
    },
  ]);

  const [scheduledPosts, setScheduledPosts] = useState([
    {
      id: 1,
      content: '새로운 블로그 포스트를 확인하세요! "AI 시대의 콘텐츠 마케팅 전략"',
      platforms: ['twitter', 'facebook', 'linkedin'],
      scheduledTime: '2025-07-14 09:00',
      status: 'scheduled'
    },
    {
      id: 2,
      content: '이번 주 가장 인기 있었던 포스트 TOP 5를 소개합니다 🌟',
      platforms: ['instagram', 'threads'],
      scheduledTime: '2025-07-15 18:00',
      status: 'scheduled'
    }
  ]);

  const [showScheduler, setShowScheduler] = useState(false);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState<string>('');
  const [platformConfigs, setPlatformConfigs] = useState<PlatformConfig>({});
  const [configForm, setConfigForm] = useState<{ [key: string]: string }>({});
  const [newPost, setNewPost] = useState({
    content: '',
    platforms: [] as string[],
    scheduledTime: '',
    hashtags: '',
    imageUrl: ''
  });

  const handleConnect = (platformId: string) => {
    const platform = platforms.find(p => p.id === platformId);
    if (platform?.connected) {
      // 연결 해제
      setPlatforms(prev => prev.map(p => 
        p.id === platformId ? { ...p, connected: false } : p
      ));
      // 저장된 설정 제거
      const updatedConfigs = { ...platformConfigs };
      delete updatedConfigs[platformId];
      setPlatformConfigs(updatedConfigs);
      localStorage.setItem('sns_configs', JSON.stringify(updatedConfigs));
    } else {
      // 설정 모달 열기
      setSelectedPlatform(platformId);
      setShowConfigModal(true);
      // 기존 설정이 있으면 폼에 로드
      if (platformConfigs[platformId]) {
        setConfigForm(platformConfigs[platformId]);
      } else {
        setConfigForm({});
      }
    }
  };

  const handleSaveConfig = () => {
    if (selectedPlatform) {
      // 설정 저장
      const updatedConfigs = {
        ...platformConfigs,
        [selectedPlatform]: configForm
      };
      setPlatformConfigs(updatedConfigs);
      localStorage.setItem('sns_configs', JSON.stringify(updatedConfigs));
      
      // 플랫폼 연결 상태 업데이트
      setPlatforms(prev => prev.map(p => 
        p.id === selectedPlatform ? { ...p, connected: true } : p
      ));
      
      // 모달 닫기
      setShowConfigModal(false);
      setSelectedPlatform('');
      setConfigForm({});
    }
  };

  const getFieldLabel = (field: string) => {
    const labels: { [key: string]: string } = {
      api_key: 'API 키',
      api_secret: 'API 시크릿',
      access_token: '액세스 토큰',
      access_token_secret: '액세스 토큰 시크릿',
      app_id: '앱 ID',
      app_secret: '앱 시크릿',
      page_id: '페이지 ID',
      business_account_id: '비즈니스 계정 ID'
    };
    return labels[field] || field;
  };

  // 컴포넌트 마운트 시 저장된 설정 로드
  useEffect(() => {
    const savedConfigs = localStorage.getItem('sns_configs');
    if (savedConfigs) {
      const configs = JSON.parse(savedConfigs);
      setPlatformConfigs(configs);
      
      // 연결 상태 업데이트
      setPlatforms(prev => prev.map(platform => ({
        ...platform,
        connected: !!configs[platform.id]
      })));
    }
  }, []);

  const handleSchedulePost = () => {
    if (newPost.content && newPost.platforms.length > 0 && newPost.scheduledTime) {
      const post = {
        id: Date.now(),
        content: newPost.content,
        platforms: newPost.platforms,
        scheduledTime: newPost.scheduledTime,
        status: 'scheduled'
      };
      setScheduledPosts([...scheduledPosts, post]);
      setNewPost({ content: '', platforms: [], scheduledTime: '', hashtags: '', imageUrl: '' });
      setShowScheduler(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">SNS 자동 포스팅</h1>
        <p className="text-gray-600">블로그 콘텐츠를 다양한 소셜 미디어 플랫폼에 자동으로 배포하세요</p>
      </div>

      {/* SNS 플랫폼 연동 현황 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">플랫폼 연동 현황</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {platforms.map(platform => (
            <div key={platform.id} className="border rounded-lg p-4">
              <div className={`w-12 h-12 rounded-lg ${platform.color} flex items-center justify-center text-white text-2xl mb-3`}>
                {platform.icon}
              </div>
              <h3 className="font-semibold mb-2">{platform.name}</h3>
              <button
                onClick={() => handleConnect(platform.id)}
                className={`w-full py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  platform.connected
                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {platform.connected ? '✓ 연동됨' : '연동하기'}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 포스팅 도구 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">포스팅 도구</h2>
          <button
            onClick={() => setShowScheduler(!showScheduler)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            + 새 포스트 예약
          </button>
        </div>

        {showScheduler && (
          <div className="border rounded-lg p-4 mb-4 bg-gray-50">
            <h3 className="font-semibold mb-3">새 포스트 예약하기</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  콘텐츠
                </label>
                <textarea
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="포스팅할 내용을 입력하세요..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  플랫폼 선택
                </label>
                <div className="flex flex-wrap gap-2">
                  {platforms.filter(p => p.connected).map(platform => (
                    <label key={platform.id} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={newPost.platforms.includes(platform.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewPost({ ...newPost, platforms: [...newPost.platforms, platform.id] });
                          } else {
                            setNewPost({ ...newPost, platforms: newPost.platforms.filter(p => p !== platform.id) });
                          }
                        }}
                        className="mr-2"
                      />
                      <span className="text-sm">{platform.name}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  예약 시간
                </label>
                <input
                  type="datetime-local"
                  value={newPost.scheduledTime}
                  onChange={(e) => setNewPost({ ...newPost, scheduledTime: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  해시태그
                </label>
                <input
                  type="text"
                  value={newPost.hashtags}
                  onChange={(e) => setNewPost({ ...newPost, hashtags: e.target.value })}
                  className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                  placeholder="#AI #블로그 #마케팅"
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleSchedulePost}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  예약하기
                </button>
                <button
                  onClick={() => setShowScheduler(false)}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
                >
                  취소
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 예약된 포스트 목록 */}
        <div className="space-y-3">
          {scheduledPosts.map(post => (
            <div key={post.id} className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <p className="text-gray-800 mb-2">{post.content}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>📅 {post.scheduledTime}</span>
                    <span>
                      🔗 {post.platforms.map(p => 
                        platforms.find(platform => platform.id === p)?.name
                      ).join(', ')}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      post.status === 'scheduled' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {post.status === 'scheduled' ? '예약됨' : '게시됨'}
                    </span>
                  </div>
                </div>
                <button className="text-gray-400 hover:text-gray-600">
                  ⋮
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SNS 성과 분석 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">SNS 성과 분석</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-3xl font-bold text-blue-600">1,234</div>
            <div className="text-sm text-gray-600">총 도달 수</div>
            <div className="text-xs text-green-600 mt-1">↑ 23.5%</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-3xl font-bold text-green-600">89</div>
            <div className="text-sm text-gray-600">참여율</div>
            <div className="text-xs text-green-600 mt-1">↑ 12.3%</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <div className="text-3xl font-bold text-purple-600">456</div>
            <div className="text-sm text-gray-600">클릭 수</div>
            <div className="text-xs text-green-600 mt-1">↑ 8.7%</div>
          </div>
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="text-3xl font-bold text-orange-600">67</div>
            <div className="text-sm text-gray-600">신규 팔로워</div>
            <div className="text-xs text-red-600 mt-1">↓ 2.1%</div>
          </div>
        </div>

        <div className="mt-6">
          <h3 className="font-semibold mb-3">플랫폼별 성과</h3>
          <div className="space-y-2">
            {['Twitter/X', 'Facebook', 'Instagram', 'LinkedIn'].map((platform, idx) => (
              <div key={platform} className="flex items-center gap-3">
                <div className="w-24 text-sm">{platform}</div>
                <div className="flex-1 bg-gray-200 rounded-full h-4 relative">
                  <div 
                    className="absolute top-0 left-0 h-full bg-blue-500 rounded-full"
                    style={{ width: `${[67, 82, 45, 91][idx]}%` }}
                  />
                </div>
                <div className="text-sm text-gray-600">{[67, 82, 45, 91][idx]}%</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* SNS 플랫폼 설정 모달 */}
      {showConfigModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">
                {platforms.find(p => p.id === selectedPlatform)?.name} 연동 설정
              </h3>
              <button
                onClick={() => setShowConfigModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
                <strong>📌 설정 안내:</strong><br/>
                각 플랫폼의 개발자 콘솔에서 API 키를 발급받아 입력해주세요.
              </div>
              
              {platforms.find(p => p.id === selectedPlatform)?.requiredFields?.map(field => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {getFieldLabel(field)} <span className="text-red-500">*</span>
                  </label>
                  <input
                    type={field.includes('secret') || field.includes('token') ? 'password' : 'text'}
                    value={configForm[field] || ''}
                    onChange={(e) => setConfigForm({ ...configForm, [field]: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                    placeholder={`${getFieldLabel(field)}을 입력하세요`}
                  />
                </div>
              ))}
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
                <strong>🔒 보안:</strong> 입력된 정보는 브라우저에 안전하게 저장됩니다.
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSaveConfig}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                disabled={!platforms.find(p => p.id === selectedPlatform)?.requiredFields?.every(field => configForm[field])}
              >
                연동하기
              </button>
              <button
                onClick={() => setShowConfigModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
              >
                취소
              </button>
            </div>
            
            <div className="mt-4 text-xs text-gray-500">
              <strong>API 키 발급 방법:</strong><br/>
              • Twitter/X: developer.twitter.com<br/>
              • Facebook: developers.facebook.com<br/>
              • Instagram: developers.facebook.com<br/>
              • LinkedIn: developer.linkedin.com<br/>
              • YouTube: console.developers.google.com
            </div>
          </div>
        </div>
      )}
    </div>
  );
}