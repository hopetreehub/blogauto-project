/**
 * 최적화된 API 클라이언트
 * - 요청 디바운싱
 * - 응답 캐싱
 * - 재시도 로직
 * - 취소 가능한 요청
 */

import React from 'react';
import { debounce } from './performance';

interface CacheEntry {
  data: any;
  timestamp: number;
  ttl: number;
}

interface RequestConfig extends Omit<RequestInit, 'cache'> {
  cache?: boolean;
  cacheTTL?: number;
  retry?: number;
  retryDelay?: number;
  timeout?: number;
}

export class OptimizedApiClient {
  private baseUrl: string;
  private cache: Map<string, CacheEntry> = new Map();
  private pendingRequests: Map<string, AbortController> = new Map();
  private defaultHeaders: HeadersInit;
  
  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
    
    // 주기적으로 캐시 정리
    if (typeof window !== 'undefined') {
      setInterval(() => this.cleanupCache(), 60000); // 1분마다
    }
  }
  
  private getCacheKey(url: string, config?: RequestConfig): string {
    return `${config?.method || 'GET'}:${url}:${JSON.stringify(config?.body || '')}`;
  }
  
  private cleanupCache() {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key);
      }
    }
  }
  
  private async fetchWithTimeout(
    url: string,
    config: RequestConfig
  ): Promise<Response> {
    const timeout = config.timeout || 30000; // 기본 30초
    const controller = new AbortController();
    
    const timeoutId = setTimeout(() => {
      controller.abort();
    }, timeout);
    
    try {
      // RequestConfig에서 fetch 호환 옵션만 추출
      const { cache: enableCache, cacheTTL, retry, retryDelay, timeout: _, ...fetchConfig } = config;
      const response = await fetch(url, { 
        ...fetchConfig, 
        signal: controller.signal 
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      throw error;
    }
  }
  
  private async fetchWithRetry(
    url: string,
    config: RequestConfig
  ): Promise<Response> {
    const maxRetries = config.retry || 3;
    const retryDelay = config.retryDelay || 1000;
    
    for (let i = 0; i <= maxRetries; i++) {
      try {
        const response = await this.fetchWithTimeout(url, config);
        
        if (response.ok || i === maxRetries) {
          return response;
        }
        
        // 5xx 에러인 경우에만 재시도
        if (response.status >= 500) {
          await new Promise(resolve => setTimeout(resolve, retryDelay * (i + 1)));
          continue;
        }
        
        return response;
      } catch (error) {
        if (i === maxRetries) throw error;
        
        // 네트워크 에러인 경우 재시도
        await new Promise(resolve => setTimeout(resolve, retryDelay * (i + 1)));
      }
    }
    
    throw new Error('Max retries reached');
  }
  
  async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const cacheKey = this.getCacheKey(url, config);
    
    // 캐시 확인
    if (config.cache !== false && config.method === 'GET') {
      const cached = this.cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < cached.ttl) {
        return cached.data;
      }
    }
    
    // 이전 요청 취소
    const existingController = this.pendingRequests.get(cacheKey);
    if (existingController) {
      existingController.abort();
    }
    
    // 새 요청 시작
    const controller = new AbortController();
    this.pendingRequests.set(cacheKey, controller);
    
    try {
      const token = localStorage.getItem('access_token');
      const headers = {
        ...this.defaultHeaders,
        ...config.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      };
      
      const response = await this.fetchWithRetry(url, {
        ...config,
        headers,
        signal: controller.signal,
      });
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Request failed' }));
        throw new Error(error.message || `HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // 캐시 저장
      if (config.cache !== false && config.method === 'GET') {
        this.cache.set(cacheKey, {
          data,
          timestamp: Date.now(),
          ttl: config.cacheTTL || 300000, // 기본 5분
        });
      }
      
      return data;
    } finally {
      this.pendingRequests.delete(cacheKey);
    }
  }
  
  // 편의 메서드들
  get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }
  
  post<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
  
  put<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }
  
  delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }
  
  // 디바운스된 검색
  createDebouncedSearch<T>(
    endpoint: string,
    delay: number = 300
  ): (query: string) => Promise<T | null> {
    let lastQuery = '';
    
    const search = debounce(async (
      query: string,
      resolve: (value: T | null) => void,
      reject: (error: any) => void
    ) => {
      if (query !== lastQuery) return;
      
      try {
        const result = await this.get<T>(`${endpoint}?q=${encodeURIComponent(query)}`);
        if (query === lastQuery) {
          resolve(result);
        }
      } catch (error) {
        if (query === lastQuery) {
          reject(error);
        }
      }
    }, delay);
    
    return (query: string) => {
      lastQuery = query;
      
      if (!query.trim()) {
        return Promise.resolve(null);
      }
      
      return new Promise((resolve, reject) => {
        search(query, resolve, reject);
      });
    };
  }
  
  // 스트리밍 응답 처리
  async *stream(
    endpoint: string,
    config?: RequestConfig
  ): AsyncGenerator<any, void, unknown> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = localStorage.getItem('access_token');
    
    // RequestConfig에서 fetch 호환 옵션만 추출
    const { cache: enableCache, cacheTTL, retry, retryDelay, timeout, ...fetchConfig } = config || {};
    
    const response = await fetch(url, {
      ...fetchConfig,
      headers: {
        ...this.defaultHeaders,
        ...fetchConfig?.headers,
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');
    
    const decoder = new TextDecoder();
    let buffer = '';
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') return;
            
            try {
              yield JSON.parse(data);
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
  
  // 배치 요청
  async batch<T>(
    requests: Array<{
      endpoint: string;
      method?: string;
      data?: any;
    }>
  ): Promise<T[]> {
    const promises = requests.map(req =>
      this.request<T>(req.endpoint, {
        method: req.method || 'GET',
        body: req.data ? JSON.stringify(req.data) : undefined,
        cache: false, // 배치 요청은 캐싱하지 않음
      })
    );
    
    return Promise.all(promises);
  }
  
  // 캐시 관리
  clearCache(pattern?: string) {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }
  
  // 모든 진행 중인 요청 취소
  cancelAll() {
    for (const controller of this.pendingRequests.values()) {
      controller.abort();
    }
    this.pendingRequests.clear();
  }
}

// 싱글톤 인스턴스
export const apiClient = new OptimizedApiClient();

// React Hook
export function useApi() {
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);
  
  const request = React.useCallback(async <T,>(
    endpoint: string,
    config?: RequestConfig
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiClient.request<T>(endpoint, config);
      return data;
    } catch (err) {
      setError(err as Error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);
  
  React.useEffect(() => {
    return () => {
      // 컴포넌트 언마운트 시 진행 중인 요청 취소
      apiClient.cancelAll();
    };
  }, []);
  
  return {
    request,
    loading,
    error,
    get: apiClient.get.bind(apiClient),
    post: apiClient.post.bind(apiClient),
    put: apiClient.put.bind(apiClient),
    delete: apiClient.delete.bind(apiClient),
  };
}