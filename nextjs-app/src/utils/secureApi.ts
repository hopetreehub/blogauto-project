// 보안 강화된 API 유틸리티

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  requireAuth?: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 인증 토큰 관리 (보안 강화)
class AuthManager {
  private static readonly TOKEN_KEY = 'auth_token';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token';

  static getToken(): string | null {
    if (typeof window === 'undefined') return null;
    
    try {
      return sessionStorage.getItem(this.TOKEN_KEY); // localStorage 대신 sessionStorage 사용
    } catch {
      return null;
    }
  }

  static setToken(token: string): void {
    if (typeof window === 'undefined') return;
    
    try {
      sessionStorage.setItem(this.TOKEN_KEY, token);
    } catch (error) {
      console.error('Failed to save auth token:', error);
    }
  }

  static removeToken(): void {
    if (typeof window === 'undefined') return;
    
    try {
      sessionStorage.removeItem(this.TOKEN_KEY);
      sessionStorage.removeItem(this.REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('Failed to remove auth token:', error);
    }
  }

  static isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

// API 호출 래퍼 (보안 강화)
export async function secureApiCall<T = any>(
  endpoint: string, 
  options: ApiOptions = {}
): Promise<ApiResponse<T>> {
  const { 
    method = 'GET', 
    headers = {}, 
    body, 
    requireAuth = false 
  } = options;

  try {
    // 기본 헤더 설정
    const defaultHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest', // CSRF 보호
    };

    // 인증이 필요한 경우
    if (requireAuth) {
      const token = AuthManager.getToken();
      if (!token) {
        return {
          success: false,
          error: '인증이 필요합니다. 로그인해주세요.'
        };
      }
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    // API 키는 백엔드에서 처리하므로 프론트엔드에서 제거
    // 모든 외부 API 호출은 백엔드를 통해 프록시됨

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: { ...defaultHeaders, ...headers },
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'include', // 쿠키 포함 (CSRF 토큰용)
    });

    // 인증 실패 시 자동 로그아웃
    if (response.status === 401) {
      AuthManager.removeToken();
      return {
        success: false,
        error: '인증이 만료되었습니다. 다시 로그인해주세요.'
      };
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        error: errorData.message || `HTTP ${response.status}: ${response.statusText}`
      };
    }

    const data = await response.json();
    return {
      success: true,
      data
    };

  } catch (error) {
    console.error('API call failed:', error);
    
    // 네트워크 에러와 기타 에러 구분
    if (error instanceof TypeError && error.message.includes('fetch')) {
      return {
        success: false,
        error: '네트워크 연결에 실패했습니다. 인터넷 연결을 확인해주세요.'
      };
    }

    return {
      success: false,
      error: '예상치 못한 오류가 발생했습니다.'
    };
  }
}

// 특화된 API 호출 함수들
export const apiCalls = {
  // 키워드 분석 (인증 필요)
  async analyzeKeywords(keyword: string, country: string = 'KR') {
    return secureApiCall('/api/keywords/analyze', {
      method: 'POST',
      body: { keyword, country, max_results: 10 },
      requireAuth: true
    });
  },

  // 제목 생성 (인증 필요)
  async generateTitles(keyword: string, count: number = 5) {
    return secureApiCall('/api/titles/generate', {
      method: 'POST',
      body: { 
        keyword, 
        count, 
        tone: 'professional',
        length: 'medium',
        language: 'ko'
      },
      requireAuth: true
    });
  },

  // 콘텐츠 생성 (인증 필요)
  async generateContent(title: string, keywords: string) {
    return secureApiCall('/api/content/generate', {
      method: 'POST',
      body: { 
        title, 
        keywords,
        length: 'medium'
      },
      requireAuth: true
    });
  },

  // 대시보드 통계 (인증 필요)
  async getDashboardStats() {
    return secureApiCall('/api/dashboard/stats', {
      requireAuth: true
    });
  }
};

// 인증 관련 함수들
export const auth = {
  login: async (email: string, password: string) => {
    const response = await secureApiCall('/api/auth/login', {
      method: 'POST',
      body: { email, password }
    });
    
    if (response.success && response.data?.access_token) {
      AuthManager.setToken(response.data.access_token);
    }
    
    return response;
  },

  logout: () => {
    AuthManager.removeToken();
  },

  isAuthenticated: () => AuthManager.isAuthenticated(),

  getProfile: () => secureApiCall('/api/auth/me', { requireAuth: true })
};

export { AuthManager };