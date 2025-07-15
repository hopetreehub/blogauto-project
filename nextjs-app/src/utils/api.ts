// API 유틸리티 함수들

export function getAPISettings() {
  if (typeof window === 'undefined') return null;
  
  const settings = localStorage.getItem('api_settings');
  return settings ? JSON.parse(settings) : null;
}

export async function apiCall(endpoint: string, options: RequestInit = {}) {
  const settings = getAPISettings();
  
  // 🔬 전문가 디버깅: API 설정 상태 로깅
  console.log('🔍 [API Debug] Settings:', {
    hasSettings: !!settings,
    hasOpenAIKey: !!(settings?.openai_api_key),
    openaiKeyLength: settings?.openai_api_key?.length || 0,
    endpoint: endpoint
  });
  
  // 지침 가져오기
  const guidelines = localStorage.getItem('content_guidelines');
  
  // 헤더에 API 키와 지침 추가
  const headers = {
    'Content-Type': 'application/json',
    ...(settings?.openai_api_key && {
      'X-OpenAI-Key': settings.openai_api_key,
    }),
    ...(settings?.gemini_api_key && {
      'X-Gemini-Key': settings.gemini_api_key,
    }),
    ...(settings?.google_api_key && {
      'X-Google-Key': settings.google_api_key,
    }),
    ...(settings?.google_search_engine_id && {
      'X-Google-Search-ID': settings.google_search_engine_id,
    }),
    ...(guidelines && {
      'X-Guidelines': guidelines,
    }),
    ...options.headers
  };
  
  // 🔬 전문가 디버깅: 최종 헤더 상태 로깅
  console.log('🔍 [API Debug] Final Headers:', {
    'Content-Type': headers['Content-Type'],
    'X-OpenAI-Key': headers['X-OpenAI-Key'] ? `${headers['X-OpenAI-Key'].substring(0, 10)}...` : 'NOT_SET',
    allHeaderKeys: Object.keys(headers)
  });
  
  return fetch(endpoint, {
    ...options,
    headers
  });
}