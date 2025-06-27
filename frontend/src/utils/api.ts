const API_BASE_URL = process.env.REACT_APP_API_URL || (
  process.env.NODE_ENV === 'production' 
    ? 'https://api.innerbot.inbecs.com' 
    : 'http://localhost:8000'
);

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  private getHeaders() {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Always get the latest token from localStorage
    const currentToken = localStorage.getItem('auth_token') || this.token;
    if (currentToken) {
      headers['Authorization'] = `Bearer ${currentToken}`;
      this.token = currentToken; // Update internal token
    }

    return headers;
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    console.log('API Request:', {
      url,
      method: config.method || 'GET',
      headers: config.headers,
      body: config.body
    });

    const response = await fetch(url, config);

    if (!response.ok) {
      console.error('API Error:', {
        status: response.status,
        statusText: response.statusText,
        url
      });
      
      if (response.status === 401) {
        // Token expired or invalid
        this.setToken(null);
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
        window.location.reload();
      }
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  // Auth methods
  async login(email: string, password: string) {
    return this.request<{ access_token: string; token_type: string }>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, username: string, password: string) {
    return this.request<any>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    });
  }

  async getCurrentUser() {
    return this.request<any>('/api/auth/me');
  }

  // Keyword analysis
  async analyzeKeywords(keyword: string, country: string = 'KR', maxResults: number = 10) {
    return this.request<any>('/api/keywords/analyze', {
      method: 'POST',
      body: JSON.stringify({
        keyword,
        country,
        max_results: maxResults,
      }),
    });
  }

  // Title generation
  async generateTitles(
    keyword: string,
    length: string = 'medium',
    language: string = 'ko',
    tone: string = 'professional',
    count: number = 5
  ) {
    return this.request<any>('/api/titles/generate', {
      method: 'POST',
      body: JSON.stringify({
        keyword,
        length,
        language,
        tone,
        count,
      }),
    });
  }

  // Advanced title generation (시의성, SEO, 바이럴성 최적화)
  async generateAdvancedTitles(keyword: string, count: number = 5) {
    return this.request<any>('/api/titles/advanced-generate', {
      method: 'POST',
      body: JSON.stringify({
        keyword,
        count,
      }),
    });
  }

  // Content generation
  async generateContent(title: string, keywords?: string, length: string = 'medium') {
    return this.request<any>('/api/content/generate', {
      method: 'POST',
      body: JSON.stringify({
        title,
        keywords,
        length,
      }),
    });
  }

  // Dashboard stats
  async getDashboardStats() {
    return this.request<any>('/api/dashboard/stats');
  }

  // Golden keywords
  async generateGoldenKeywords(category: string, domain: string = '', platform: string = 'wordpress') {
    return this.request<any>('/api/keywords/golden', {
      method: 'POST',
      body: JSON.stringify({
        category,
        domain,
        platform,
      }),
    });
  }

  // SEO keyword analysis
  async analyzeSEOKeywords(itemName: string, category: string) {
    return this.request<any>('/api/keywords/seo-analysis', {
      method: 'POST',
      body: JSON.stringify({
        item_name: itemName,
        category,
      }),
    });
  }

  // Integrated keyword analysis (Naver + Google + SEO)
  async analyzeIntegratedKeywords(itemName: string, category: string, includeVariations: boolean = true) {
    return this.request<any>('/api/keywords/integrated-analysis', {
      method: 'POST',
      body: JSON.stringify({
        item_name: itemName,
        category,
        include_variations: includeVariations,
      }),
    });
  }

  // Batch content generation
  async generateBatchContent(titles: string[], guidelines: string = '', seoGuidelines: string = '', geoGuidelines: string = '') {
    return this.request<any>('/api/content/batch-generate', {
      method: 'POST',
      body: JSON.stringify({
        titles,
        guidelines,
        seo_guidelines: seoGuidelines,
        geo_guidelines: geoGuidelines,
      }),
    });
  }

  // Auto posting
  async autoPublishPosts(
    titles: string[],
    contentData: any,
    platforms: any[],
    scheduleSettings: any,
    imageSettings: any
  ) {
    return this.request<any>('/api/posts/auto-publish', {
      method: 'POST',
      body: JSON.stringify({
        titles,
        content_data: contentData,
        platforms,
        schedule_settings: scheduleSettings,
        image_settings: imageSettings,
      }),
    });
  }

  // Advanced blog content generation (SEO + GEO optimized)
  async generateAdvancedBlogContent(keyword: string) {
    return this.request<any>('/api/content/advanced-generate', {
      method: 'POST',
      body: JSON.stringify({
        keyword,
      }),
    });
  }

  // Admin - Prompt Management
  async getPromptsSummary() {
    return this.request<any>('/api/admin/prompts/summary');
  }

  async getPromptsByType(promptType: string) {
    return this.request<any>(`/api/admin/prompts/${promptType}`);
  }

  async createPrompt(promptData: any) {
    return this.request<any>('/api/admin/prompts', {
      method: 'POST',
      body: JSON.stringify(promptData),
    });
  }

  async updatePrompt(promptId: string, promptData: any) {
    return this.request<any>(`/api/admin/prompts/${promptId}`, {
      method: 'PUT',
      body: JSON.stringify(promptData),
    });
  }

  async deletePrompt(promptId: string) {
    return this.request<any>(`/api/admin/prompts/${promptId}`, {
      method: 'DELETE',
    });
  }

  async exportPrompts(promptType: string) {
    return this.request<any>(`/api/admin/prompts/${promptType}/export`);
  }

  async importPrompts(importData: any) {
    return this.request<any>('/api/admin/prompts/import', {
      method: 'POST',
      body: JSON.stringify(importData),
    });
  }

  // Site Management APIs
  async createSite(siteData: any) {
    return this.request<any>('/api/sites', {
      method: 'POST',
      body: JSON.stringify(siteData),
    });
  }

  async getUserSites() {
    return this.request<any>('/api/sites');
  }

  async getSiteDetails(siteId: string) {
    return this.request<any>(`/api/sites/${siteId}`);
  }

  async updateSite(siteId: string, siteData: any) {
    return this.request<any>(`/api/sites/${siteId}`, {
      method: 'PUT',
      body: JSON.stringify(siteData),
    });
  }

  async deleteSite(siteId: string) {
    return this.request<any>(`/api/sites/${siteId}`, {
      method: 'DELETE',
    });
  }

  async testWordPressConnection(connectionData: any) {
    return this.request<any>('/api/sites/test-wordpress', {
      method: 'POST',
      body: JSON.stringify(connectionData),
    });
  }

  async getAvailableGuidelines() {
    return this.request<any>('/api/sites/guidelines/available');
  }

  // Automation Workflow APIs
  async startAutomationSession(sessionData: any) {
    return this.request<any>('/api/automation/start', {
      method: 'POST',
      body: JSON.stringify(sessionData),
    });
  }

  async generateCategoryKeywords(keywordData: any) {
    return this.request<any>('/api/automation/keywords/generate', {
      method: 'POST',
      body: JSON.stringify(keywordData),
    });
  }

  async generateKeywordTitles(titleData: any) {
    return this.request<any>('/api/automation/titles/generate', {
      method: 'POST',
      body: JSON.stringify(titleData),
    });
  }

  async generateTitleContents(contentData: any) {
    return this.request<any>('/api/automation/content/generate', {
      method: 'POST',
      body: JSON.stringify(contentData),
    });
  }

  async publishAutomationContents(publishData: any) {
    return this.request<any>('/api/automation/publish', {
      method: 'POST',
      body: JSON.stringify(publishData),
    });
  }

  async getAutomationSessionStatus(sessionId: string) {
    return this.request<any>(`/api/automation/sessions/${sessionId}/status`);
  }

  // Generic POST method for flexibility
  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
export default apiClient;