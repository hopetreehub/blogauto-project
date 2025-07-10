'use client';

import { useState, useEffect } from 'react';
import { useToast } from '@/hooks/useToast';
import ToastContainer from '@/components/ToastContainer';

interface APISettings {
  openai_api_key: string;
  gemini_api_key: string;
  google_api_key: string;
  google_search_engine_id: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<APISettings>({
    openai_api_key: '',
    gemini_api_key: '',
    google_api_key: '',
    google_search_engine_id: ''
  });
  const [showKeys, setShowKeys] = useState(false);
  const [loading, setLoading] = useState(false);
  const { toasts, success, error: toastError, removeToast } = useToast();

  useEffect(() => {
    // 로컬 스토리지에서 설정 불러오기
    const savedSettings = localStorage.getItem('api_settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSave = async () => {
    setLoading(true);
    
    try {
      // 로컬 스토리지에 저장
      localStorage.setItem('api_settings', JSON.stringify(settings));
      
      // 백엔드에 설정 전송 (옵션)
      const response = await fetch('http://localhost:8000/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        success('API 설정이 저장되었습니다.');
      } else {
        // 백엔드가 없어도 로컬에는 저장됨
        success('API 설정이 로컬에 저장되었습니다.');
      }
    } catch (err) {
      // 로컬 저장만 성공해도 OK
      success('API 설정이 로컬에 저장되었습니다.');
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/health');
      const data = await response.json();
      
      if (data.apis) {
        const configured = Object.entries(data.apis)
          .filter(([_, status]) => status === 'configured')
          .map(([api, _]) => api);
        
        if (configured.length > 0) {
          success(`연결 성공: ${configured.join(', ')}`);
        } else {
          toastError('API 키가 설정되지 않았습니다.');
        }
      }
    } catch (err) {
      toastError('API 서버에 연결할 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">API 설정</h1>
          <p className="text-gray-600 mt-2">블로그 자동화에 필요한 API 키를 설정하세요</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">API 키 설정</h2>
              <button
                onClick={() => setShowKeys(!showKeys)}
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                {showKeys ? '숨기기' : '표시'}
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key
                  <span className="text-red-500 ml-1">*</span>
                </label>
                <input
                  type={showKeys ? 'text' : 'password'}
                  value={settings.openai_api_key}
                  onChange={(e) => setSettings({...settings, openai_api_key: e.target.value})}
                  placeholder="sk-..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  제목 생성, 콘텐츠 작성에 사용됩니다.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Google Gemini API Key (선택)
                </label>
                <input
                  type={showKeys ? 'text' : 'password'}
                  value={settings.gemini_api_key}
                  onChange={(e) => setSettings({...settings, gemini_api_key: e.target.value})}
                  placeholder="AIza..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  대체 AI 모델로 사용할 수 있습니다.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Google API Key (선택)
                </label>
                <input
                  type={showKeys ? 'text' : 'password'}
                  value={settings.google_api_key}
                  onChange={(e) => setSettings({...settings, google_api_key: e.target.value})}
                  placeholder="AIza..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  키워드 검색량 확인에 사용됩니다.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Google Search Engine ID (선택)
                </label>
                <input
                  type="text"
                  value={settings.google_search_engine_id}
                  onChange={(e) => setSettings({...settings, google_search_engine_id: e.target.value})}
                  placeholder="cx:..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Google Custom Search에서 사용됩니다.
                </p>
              </div>
            </div>
          </div>

          <div className="border-t pt-6">
            <h3 className="text-lg font-medium mb-4">API 키 얻는 방법</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div>
                <strong>OpenAI API Key:</strong>
                <ol className="ml-4 mt-1 list-decimal">
                  <li><a href="https://platform.openai.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">platform.openai.com</a> 접속</li>
                  <li>로그인 후 API keys 메뉴 클릭</li>
                  <li>Create new secret key 클릭</li>
                </ol>
              </div>
              
              <div>
                <strong>Google Gemini API Key:</strong>
                <ol className="ml-4 mt-1 list-decimal">
                  <li><a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google AI Studio</a> 접속</li>
                  <li>Get API key 클릭</li>
                </ol>
              </div>
            </div>
          </div>

          <div className="flex gap-3 mt-8">
            <button
              onClick={handleSave}
              disabled={loading || !settings.openai_api_key}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '저장 중...' : '설정 저장'}
            </button>
            
            <button
              onClick={testConnection}
              disabled={loading}
              className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              연결 테스트
            </button>
          </div>
        </div>

        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">주의사항</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>API 키는 안전하게 보관하세요</li>
                  <li>프로덕션 환경에서는 서버 측에서 관리하세요</li>
                  <li>무료 계정은 사용량 제한이 있습니다</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}