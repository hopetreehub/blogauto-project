'use client'

import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/useToast'
import ToastContainer from '@/components/ToastContainer'
import { AccessibleButton } from '@/components/AccessibleButton'
import { SettingsIcon, TestIcon, SaveIcon, EyeIcon, EyeOffIcon } from '@/components/Icons'
import { ThemeToggle } from '@/components/ThemeToggle'

interface APISettings {
  openai_api_key: string
  gemini_api_key: string
  google_api_key: string
  google_search_engine_id: string
  groq_api_key: string
  deepseek_api_key: string
  huggingface_api_key: string
  openrouter_api_key: string
  grok_api_key: string
}

interface AIProvider {
  name: string
  displayName: string
  is_free: boolean
  available: boolean
  rate_limit: number
  max_tokens: number
  description: string
  website: string
}

interface AIConfig {
  mode: 'free_first' | 'performance_first'
  providers: { [key: string]: AIProvider }
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<APISettings>({
    openai_api_key: '',
    gemini_api_key: '',
    google_api_key: '',
    google_search_engine_id: '',
    groq_api_key: '',
    deepseek_api_key: '',
    huggingface_api_key: '',
    openrouter_api_key: '',
    grok_api_key: ''
  })
  
  const [aiConfig, setAiConfig] = useState<AIConfig | null>(null)
  const [aiMode, setAiMode] = useState<'free_first' | 'performance_first'>('free_first')
  const [showKeys, setShowKeys] = useState(false)
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState<'general' | 'ai' | 'theme'>('general')
  const { toasts, success, error: toastError, removeToast } = useToast()

  useEffect(() => {
    loadSettings()
    loadAIProviders()
  }, [])

  const loadSettings = () => {
    const savedSettings = localStorage.getItem('api_settings')
    if (savedSettings) {
      const parsed = JSON.parse(savedSettings)
      setSettings({
        openai_api_key: parsed.openai_api_key || '',
        gemini_api_key: parsed.gemini_api_key || '',
        google_api_key: parsed.google_api_key || '',
        google_search_engine_id: parsed.google_search_engine_id || '',
        groq_api_key: parsed.groq_api_key || '',
        deepseek_api_key: parsed.deepseek_api_key || '',
        huggingface_api_key: parsed.huggingface_api_key || '',
        openrouter_api_key: parsed.openrouter_api_key || '',
        grok_api_key: parsed.grok_api_key || ''
      })
    }
  }

  const loadAIProviders = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ai/providers')
      const data = await response.json()
      
      if (data.success) {
        setAiConfig(data.data)
        setAiMode(data.data.mode || 'free_first')
      }
    } catch (error) {
      console.warn('AI 제공자 정보 로드 실패:', error)
    }
  }

  const handleSave = async () => {
    setLoading(true)
    
    try {
      // 로컬 스토리지에 저장
      localStorage.setItem('api_settings', JSON.stringify(settings))
      
      // 백엔드에 설정 전송 (옵션)
      try {
        const response = await fetch('http://localhost:8000/api/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(settings)
        })

        if (response.ok) {
          success('API 설정이 저장되었습니다.')
        } else {
          success('API 설정이 로컬에 저장되었습니다.')
        }
      } catch {
        success('API 설정이 로컬에 저장되었습니다.')
      }

      // AI 설정도 함께 저장
      if (activeTab === 'ai') {
        await saveAIConfig()
      }
      
    } catch (err) {
      success('API 설정이 로컬에 저장되었습니다.')
    } finally {
      setLoading(false)
    }
  }

  const saveAIConfig = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ai/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          api_keys: {
            openai: settings.openai_api_key,
            gemini: settings.gemini_api_key,
            groq: settings.groq_api_key,
            deepseek: settings.deepseek_api_key,
            huggingface: settings.huggingface_api_key,
            openrouter: settings.openrouter_api_key,
            grok: settings.grok_api_key
          },
          mode: aiMode
        })
      })

      const data = await response.json()
      
      if (data.success) {
        success('AI 설정이 저장되었습니다!')
        loadAIProviders()
      }
    } catch (error) {
      console.warn('AI 설정 저장 실패:', error)
    }
  }

  const testConnection = async () => {
    setLoading(true)
    
    try {
      const response = await fetch('http://localhost:8000/api/health')
      const data = await response.json()
      
      if (data.apis) {
        const configured = Object.entries(data.apis)
          .filter(([_, status]) => status === 'configured')
          .map(([api, _]) => api)
        
        if (configured.length > 0) {
          success(`연결 성공: ${configured.join(', ')}`)
        } else {
          toastError('API 키가 설정되지 않았습니다.')
        }
      }
    } catch (err) {
      toastError('API 서버에 연결할 수 없습니다.')
    } finally {
      setLoading(false)
    }
  }

  const testProvider = async (provider: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/ai/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(settings.openai_api_key && { 'X-OpenAI-Key': settings.openai_api_key }),
          ...(settings.gemini_api_key && { 'X-Gemini-Key': settings.gemini_api_key })
        },
        body: JSON.stringify({
          prompt: '안녕하세요. 짧게 자기소개 해주세요.',
          provider: provider
        })
      })

      const data = await response.json()
      
      if (data.success) {
        success(`${provider} 테스트 성공!`)
      } else {
        toastError(`${provider} 테스트 실패: ${data.error}`)
      }
    } catch (error) {
      toastError(`${provider} 테스트 중 오류 발생`)
    }
  }

  const providers = aiConfig?.providers || {}
  const providerList = Object.entries(providers).map(([key, value]) => ({
    key,
    ...value
  }))

  const freeProviders = providerList.filter(p => p.is_free)
  const paidProviders = providerList.filter(p => !p.is_free)

  const providerNames: { [key: string]: string } = {
    gemini: 'Google Gemini',
    groq: 'Groq',
    deepseek: 'DeepSeek',
    huggingface: 'Hugging Face',
    openrouter: 'OpenRouter',
    grok: 'Grok (X.AI)',
    openai: 'OpenAI'
  }

  const getProviderKey = (provider: string): keyof APISettings => {
    const keyMap: { [key: string]: keyof APISettings } = {
      openai: 'openai_api_key',
      gemini: 'gemini_api_key',
      groq: 'groq_api_key',
      deepseek: 'deepseek_api_key',
      huggingface: 'huggingface_api_key',
      openrouter: 'openrouter_api_key',
      grok: 'grok_api_key'
    }
    return keyMap[provider] || 'openai_api_key'
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 flex items-center">
            <SettingsIcon className="mr-3" size={32} />
            통합 설정
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            API 키, AI 제공자, 테마 등 모든 설정을 한곳에서 관리하세요
          </p>
        </div>

        {/* 탭 내비게이션 */}
        <div className="mb-8">
          <nav className="flex space-x-8">
            {[
              { id: 'general', name: 'API 설정', icon: '🔑' },
              { id: 'ai', name: 'AI 제공자', icon: '🤖' },
              { id: 'theme', name: '테마 설정', icon: '🎨' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* API 설정 탭 */}
        {activeTab === 'general' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                  🔑 API 키 설정
                </h2>
                <AccessibleButton
                  onClick={() => setShowKeys(!showKeys)}
                  variant="ghost"
                  size="sm"
                  icon={showKeys ? <EyeOffIcon size={16} /> : <EyeIcon size={16} />}
                  ariaLabel={showKeys ? 'API 키 숨기기' : 'API 키 보이기'}
                >
                  {showKeys ? '숨기기' : '표시'}
                </AccessibleButton>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    OpenAI API Key <span className="text-red-500">*</span>
                  </label>
                  <input
                    type={showKeys ? 'text' : 'password'}
                    value={settings.openai_api_key}
                    onChange={(e) => setSettings({...settings, openai_api_key: e.target.value})}
                    placeholder="sk-..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    제목 생성, 콘텐츠 작성, 이미지 생성에 사용됩니다.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Google Gemini API Key (선택)
                  </label>
                  <input
                    type={showKeys ? 'text' : 'password'}
                    value={settings.gemini_api_key}
                    onChange={(e) => setSettings({...settings, gemini_api_key: e.target.value})}
                    placeholder="AIza..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    대체 AI 모델로 사용할 수 있습니다.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Google API Key (선택)
                  </label>
                  <input
                    type={showKeys ? 'text' : 'password'}
                    value={settings.google_api_key}
                    onChange={(e) => setSettings({...settings, google_api_key: e.target.value})}
                    placeholder="AIza..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    키워드 검색량 확인에 사용됩니다.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Google Search Engine ID (선택)
                  </label>
                  <input
                    type="text"
                    value={settings.google_search_engine_id}
                    onChange={(e) => setSettings({...settings, google_search_engine_id: e.target.value})}
                    placeholder="cx:..."
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Google Custom Search에서 사용됩니다.
                  </p>
                </div>
              </div>
            </div>

            <div className="border-t dark:border-gray-700 pt-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                📚 API 키 얻는 방법
              </h3>
              <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                <div>
                  <strong>OpenAI API Key:</strong>
                  <ol className="ml-4 mt-1 list-decimal">
                    <li><a href="https://platform.openai.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">platform.openai.com</a> 접속</li>
                    <li>로그인 후 API keys 메뉴 클릭</li>
                    <li>Create new secret key 클릭</li>
                  </ol>
                </div>
                
                <div>
                  <strong>Google Gemini API Key:</strong>
                  <ol className="ml-4 mt-1 list-decimal">
                    <li><a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">Google AI Studio</a> 접속</li>
                    <li>Get API key 클릭</li>
                  </ol>
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-8">
              <AccessibleButton
                onClick={handleSave}
                disabled={loading || !settings.openai_api_key}
                loading={loading}
                icon={<SaveIcon size={16} />}
                ariaLabel="API 설정 저장"
              >
                설정 저장
              </AccessibleButton>
              
              <AccessibleButton
                onClick={testConnection}
                disabled={loading}
                variant="secondary"
                icon={<TestIcon size={16} />}
                ariaLabel="API 연결 테스트"
              >
                연결 테스트
              </AccessibleButton>
            </div>
          </div>
        )}

        {/* AI 제공자 탭 */}
        {activeTab === 'ai' && (
          <div className="space-y-6">
            {/* 사용 모드 선택 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                ⚙️ AI 사용 모드
              </h2>
              <div className="space-y-3">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="mode"
                    value="free_first"
                    checked={aiMode === 'free_first'}
                    onChange={(e) => setAiMode(e.target.value as 'free_first')}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-medium text-gray-900 dark:text-gray-100">💸 무료 우선 모드</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">무료 AI 제공자를 우선적으로 사용합니다</div>
                  </div>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name="mode"
                    value="performance_first"
                    checked={aiMode === 'performance_first'}
                    onChange={(e) => setAiMode(e.target.value as 'performance_first')}
                    className="mr-3"
                  />
                  <div>
                    <div className="font-medium text-gray-900 dark:text-gray-100">🚀 성능 우선 모드</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">성능이 좋은 AI 제공자를 우선적으로 사용합니다</div>
                  </div>
                </label>
              </div>
            </div>

            {/* 무료 AI 제공자 */}
            {freeProviders.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  💎 무료 AI 제공자
                </h2>
                <div className="space-y-4">
                  {freeProviders.map(provider => (
                    <div key={provider.key} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-medium text-gray-900 dark:text-gray-100">
                            {providerNames[provider.key] || provider.key}
                          </h3>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            Rate Limit: {provider.rate_limit}/분 | Max Tokens: {provider.max_tokens}
                          </div>
                        </div>
                        <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs font-medium rounded">
                          무료
                        </span>
                      </div>
                      <div className="flex space-x-2">
                        <input
                          type={showKeys ? 'text' : 'password'}
                          placeholder="API 키를 입력하세요"
                          value={settings[getProviderKey(provider.key)]}
                          onChange={(e) => setSettings({...settings, [getProviderKey(provider.key)]: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
                        />
                        <AccessibleButton
                          onClick={() => testProvider(provider.key)}
                          disabled={!settings[getProviderKey(provider.key)]}
                          variant="secondary"
                          size="sm"
                          ariaLabel={`${provider.key} API 테스트`}
                        >
                          테스트
                        </AccessibleButton>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 유료 AI 제공자 */}
            {paidProviders.length > 0 && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  💳 유료 AI 제공자
                </h2>
                <div className="space-y-4">
                  {paidProviders.map(provider => (
                    <div key={provider.key} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h3 className="font-medium text-gray-900 dark:text-gray-100">
                            {providerNames[provider.key] || provider.key}
                          </h3>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            Rate Limit: {provider.rate_limit}/분 | Max Tokens: {provider.max_tokens}
                          </div>
                        </div>
                        <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs font-medium rounded">
                          유료
                        </span>
                      </div>
                      <div className="flex space-x-2">
                        <input
                          type={showKeys ? 'text' : 'password'}
                          placeholder="API 키를 입력하세요"
                          value={settings[getProviderKey(provider.key)]}
                          onChange={(e) => setSettings({...settings, [getProviderKey(provider.key)]: e.target.value})}
                          className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100"
                        />
                        <AccessibleButton
                          onClick={() => testProvider(provider.key)}
                          disabled={!settings[getProviderKey(provider.key)]}
                          variant="secondary"
                          size="sm"
                          ariaLabel={`${provider.key} API 테스트`}
                        >
                          테스트
                        </AccessibleButton>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end">
              <AccessibleButton
                onClick={saveAIConfig}
                loading={loading}
                icon={<SaveIcon size={16} />}
                ariaLabel="AI 설정 저장"
              >
                AI 설정 저장
              </AccessibleButton>
            </div>
          </div>
        )}

        {/* 테마 설정 탭 */}
        {activeTab === 'theme' && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
              🎨 테마 설정
            </h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                  테마 선택
                </h3>
                <div className="flex flex-col space-y-4">
                  <ThemeToggle variant="buttons" size="md" />
                  <ThemeToggle variant="dropdown" />
                </div>
              </div>

              <div className="border-t dark:border-gray-700 pt-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                  테마 미리보기
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">라이트 모드</h4>
                    <div className="bg-white border rounded p-3 text-gray-900">
                      <div className="text-sm">깔끔하고 밝은 인터페이스</div>
                    </div>
                  </div>
                  <div className="border border-gray-600 rounded-lg p-4 bg-gray-800">
                    <h4 className="font-medium text-gray-100 mb-2">다크 모드</h4>
                    <div className="bg-gray-900 border border-gray-700 rounded p-3 text-gray-100">
                      <div className="text-sm">눈이 편안한 어두운 인터페이스</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 주의사항 */}
        <div className="mt-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">주의사항</h3>
              <div className="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                <ul className="list-disc list-inside space-y-1">
                  <li>API 키는 안전하게 보관하세요</li>
                  <li>모든 기능에는 OpenAI API 키가 필요합니다 (이미지 생성 포함)</li>
                  <li>무료 계정은 사용량 제한이 있습니다</li>
                  <li>설정은 브라우저 로컬 스토리지에 저장됩니다</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}