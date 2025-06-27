import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/api';

interface Site {
  id: string;
  name: string;
  category: string;
  url: string;
}

interface AutomationSession {
  session_id: string;
  site_id: string;
  category: string;
  step_status: string;
  keywords_count: number;
  titles_count: number;
  contents_count: number;
  published_count: number;
  created_at: string;
  keywords?: any[];
  titles?: any[];
  contents?: any[];
  posting_results?: any[];
}

interface Keyword {
  keyword: string;
  search_volume: string;
  competition: string;
  seasonal: boolean;
  reason: string;
  seo_score: number;
  trend_score: number;
}

interface Title {
  title: string;
  seo_score: number;
  viral_score: number;
  geo_score: number;
  click_potential: number;
  keyword: string;
}

interface Content {
  title: string;
  content: string;
  seo_keywords: string[];
  lsi_keywords: string[];
  word_count: number;
  seo_score: number;
  geo_score: number;
  readability_score: number;
}

interface ApiResponse {
  success?: boolean;
  status?: string;
  data?: any;
  keywords?: any[];
  titles?: any[];
  contents?: any[];
  results?: any[];
  total_count?: number;
  successful?: number;
  failed?: number;
  message?: string;
  user_info?: any;
  lsi_keywords: string[];
  word_count: number;
  seo_score: number;
  geo_score: number;
  readability_score: number;
}

const AutomationWorkflow: React.FC = () => {
  const { token } = useAuth();
  const [currentSite, setCurrentSite] = useState<Site | null>(null);
  const [session, setSession] = useState<AutomationSession | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Step 1: 키워드 생성 설정
  const [keywordCount, setKeywordCount] = useState(20);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);

  // Step 2: 제목 생성 설정
  const [titlesPerKeyword, setTitlesPerKeyword] = useState(10);
  const [selectedTitles, setSelectedTitles] = useState<string[]>([]);

  // Step 3: 콘텐츠 생성 결과
  const [selectedContents, setSelectedContents] = useState<string[]>([]);

  // Step 4: 포스팅 설정
  const [scheduleSettings, setScheduleSettings] = useState({
    immediate: true,
    start_delay_minutes: 0,
    interval_minutes: 30,
    platform_delay_minutes: 5
  });

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const siteId = urlParams.get('site_id');
    const category = urlParams.get('category');

    if (siteId && category && token) {
      // 사이트 정보 설정
      setCurrentSite({
        id: siteId,
        name: 'Loading...',
        category: category,
        url: ''
      });
      
      // 새 자동화 세션 시작
      startAutomationSession(siteId, category);
    }
  }, [token]);

  const startAutomationSession = async (siteId: string, category: string) => {
    try {
      setLoading(true);
      apiClient.setToken(token);
      
      const response = await apiClient.request('/api/automation/start', {
        method: 'POST',
        body: JSON.stringify({
          site_id: siteId,
          category: category,
          auto_posting: false
        })
      }) as ApiResponse;

      if (response.success) {
        setSession(response.data);
        setCurrentStep(1);
      }
    } catch (err) {
      setError('자동화 세션 시작 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateKeywords = async () => {
    if (!session) return;

    try {
      setLoading(true);
      setError('');
      
      apiClient.setToken(token);
      const response = await apiClient.request('/api/automation/keywords/generate', {
        method: 'POST',
        body: JSON.stringify({
          session_id: session.session_id,
          category: session.category,
          count: keywordCount,
          use_trends: true
        })
      }) as ApiResponse;

      if (response.status === 'success') {
        setSession(prev => prev ? {
          ...prev,
          step_status: 'keywords_generated',
          keywords: response.keywords,
          keywords_count: response.total_count || 0
        } : null);
        setSuccess(`${response.total_count}개의 키워드가 생성되었습니다.`);
      }
    } catch (err) {
      setError('키워드 생성 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateTitles = async () => {
    if (!session || selectedKeywords.length === 0) return;

    try {
      setLoading(true);
      setError('');
      
      apiClient.setToken(token);
      const response = await apiClient.request('/api/automation/titles/generate', {
        method: 'POST',
        body: JSON.stringify({
          session_id: session.session_id,
          selected_keywords: selectedKeywords,
          titles_per_keyword: titlesPerKeyword
        })
      }) as ApiResponse;

      if (response.status === 'success') {
        setSession(prev => prev ? {
          ...prev,
          step_status: 'titles_generated',
          titles: response.titles,
          titles_count: response.total_count || 0
        } : null);
        setSuccess(`${response.total_count}개의 제목이 생성되었습니다.`);
        setCurrentStep(3);
      }
    } catch (err) {
      setError('제목 생성 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateContents = async () => {
    if (!session || selectedTitles.length === 0) return;

    try {
      setLoading(true);
      setError('');
      
      apiClient.setToken(token);
      const response = await apiClient.request('/api/automation/content/generate', {
        method: 'POST',
        body: JSON.stringify({
          session_id: session.session_id,
          selected_titles: selectedTitles
        })
      }) as ApiResponse;

      if (response.status === 'success') {
        setSession(prev => prev ? {
          ...prev,
          step_status: 'content_generated',
          contents: response.contents,
          contents_count: response.total_count || 0
        } : null);
        setSuccess(`${response.total_count}개의 블로그 글이 생성되었습니다.`);
        setCurrentStep(4);
      }
    } catch (err) {
      setError('블로그 글 생성 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const publishContents = async () => {
    if (!session || selectedContents.length === 0) return;

    try {
      setLoading(true);
      setError('');
      
      apiClient.setToken(token);
      const response = await apiClient.request('/api/automation/publish', {
        method: 'POST',
        body: JSON.stringify({
          session_id: session.session_id,
          selected_content_titles: selectedContents,
          schedule_settings: scheduleSettings
        })
      }) as ApiResponse;

      if (response.status === 'completed' || response.status === 'failed') {
        setSession(prev => prev ? {
          ...prev,
          step_status: response.status || 'unknown',
          posting_results: response.results,
          published_count: response.successful || 0
        } : null);
        
        if ((response.successful || 0) > 0) {
          setSuccess(`${response.successful}개의 글이 성공적으로 포스팅되었습니다.`);
        }
        
        if ((response.failed || 0) > 0) {
          setError(`${response.failed}개의 글 포스팅이 실패했습니다.`);
        }
      }
    } catch (err) {
      setError('자동 포스팅 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleKeywordSelection = (keyword: string) => {
    setSelectedKeywords(prev => 
      prev.includes(keyword) 
        ? prev.filter(k => k !== keyword)
        : [...prev, keyword]
    );
  };

  const toggleTitleSelection = (title: string) => {
    setSelectedTitles(prev => 
      prev.includes(title) 
        ? prev.filter(t => t !== title)
        : [...prev, title]
    );
  };

  const toggleContentSelection = (title: string) => {
    setSelectedContents(prev => 
      prev.includes(title) 
        ? prev.filter(t => t !== title)
        : [...prev, title]
    );
  };

  const saveContentsLocally = () => {
    if (!session?.contents) return;

    const selectedContentData = session.contents.filter((content: Content) => 
      selectedContents.includes(content.title)
    );

    selectedContentData.forEach((content: Content) => {
      const blob = new Blob([content.content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${content.title.replace(/[^a-zA-Z0-9가-힣]/g, '_')}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });

    setSuccess(`${selectedContentData.length}개의 파일이 로컬에 저장되었습니다.`);
  };

  if (!session) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '10px' }}>🔄</div>
          <div>자동화 세션을 시작하는 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🤖 자동화 워크플로우</h1>
        <p className="page-description">
          {currentSite?.name} - {session.category} 카테고리 자동화
        </p>
      </div>

      {/* 진행 상황 표시 */}
      <div className="card">
        <h3 style={{ marginBottom: '20px' }}>📈 진행 상황</h3>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
          {[1, 2, 3, 4].map((step) => (
            <React.Fragment key={step}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: currentStep >= step ? 
                  'linear-gradient(135deg, #28a745 0%, #20c997 100%)' : '#e9ecef',
                color: currentStep >= step ? 'white' : '#6c757d',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold'
              }}>
                {step}
              </div>
              {step < 4 && (
                <div style={{
                  flex: 1,
                  height: '4px',
                  background: currentStep > step ? '#28a745' : '#e9ecef',
                  margin: '0 10px'
                }} />
              )}
            </React.Fragment>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', fontSize: '0.9rem' }}>
          <div style={{ textAlign: 'center', color: currentStep >= 1 ? '#28a745' : '#6c757d' }}>
            키워드 생성
          </div>
          <div style={{ textAlign: 'center', color: currentStep >= 2 ? '#28a745' : '#6c757d' }}>
            제목 생성
          </div>
          <div style={{ textAlign: 'center', color: currentStep >= 3 ? '#28a745' : '#6c757d' }}>
            블로그 글 생성
          </div>
          <div style={{ textAlign: 'center', color: currentStep >= 4 ? '#28a745' : '#6c757d' }}>
            자동 포스팅
          </div>
        </div>
      </div>

      {/* 알림 메시지 */}
      {error && (
        <div style={{ 
          background: '#f8d7da', 
          color: '#721c24', 
          padding: '12px', 
          borderRadius: '6px', 
          marginBottom: '20px'
        }}>
          ❌ {error}
        </div>
      )}

      {success && (
        <div style={{ 
          background: '#d4edda', 
          color: '#155724', 
          padding: '12px', 
          borderRadius: '6px', 
          marginBottom: '20px'
        }}>
          ✅ {success}
        </div>
      )}

      {/* Step 1: 키워드 생성 */}
      {currentStep === 1 && (
        <div className="card">
          <h3>🎯 Step 1: 키워드 자동 생성</h3>
          <p>카테고리 "{session.category}"를 기반으로 트렌드 키워드를 생성합니다.</p>
          
          <div className="form-group" style={{ maxWidth: '200px' }}>
            <label className="form-label">생성할 키워드 개수</label>
            <select
              className="form-input"
              value={keywordCount}
              onChange={(e) => setKeywordCount(parseInt(e.target.value))}
            >
              <option value={10}>10개</option>
              <option value={20}>20개</option>
              <option value={30}>30개</option>
              <option value={50}>50개</option>
            </select>
          </div>

          <button
            onClick={generateKeywords}
            disabled={loading}
            style={{
              background: loading ? '#6c757d' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              padding: '15px 30px',
              borderRadius: '8px',
              fontSize: '1.1rem',
              fontWeight: 'bold',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? '🔄 키워드 생성 중...' : '🎯 키워드 자동 생성'}
          </button>

          {session.keywords && session.keywords.length > 0 && (
            <div style={{ marginTop: '30px' }}>
              <h4>생성된 키워드 ({session.keywords.length}개)</h4>
              <p style={{ color: '#666', marginBottom: '15px' }}>
                원하는 키워드를 선택하여 제목 생성을 진행하세요.
              </p>
              
              <div style={{ display: 'grid', gap: '10px' }}>
                {session.keywords.map((kw: Keyword, index: number) => (
                  <div 
                    key={index}
                    style={{
                      border: selectedKeywords.includes(kw.keyword) ? '2px solid #007bff' : '1px solid #ddd',
                      borderRadius: '8px',
                      padding: '15px',
                      background: selectedKeywords.includes(kw.keyword) ? '#f8f9ff' : 'white',
                      cursor: 'pointer'
                    }}
                    onClick={() => toggleKeywordSelection(kw.keyword)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                      <input
                        type="checkbox"
                        checked={selectedKeywords.includes(kw.keyword)}
                        onChange={() => toggleKeywordSelection(kw.keyword)}
                        style={{ marginRight: '10px', transform: 'scale(1.2)' }}
                      />
                      <h5 style={{ margin: 0, flex: 1 }}>{kw.keyword}</h5>
                      <div style={{ display: 'flex', gap: '15px', fontSize: '0.85rem' }}>
                        <span>SEO: <strong>{kw.seo_score}</strong></span>
                        <span>트렌드: <strong>{kw.trend_score.toFixed(1)}</strong></span>
                        <span>검색량: <strong>{kw.search_volume}</strong></span>
                      </div>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#666' }}>
                      경쟁도: {kw.competition} | {kw.seasonal ? '계절성 ✓' : '일반성'}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#888', marginTop: '5px' }}>
                      {kw.reason}
                    </div>
                  </div>
                ))}
              </div>

              {selectedKeywords.length > 0 && (
                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                  <button
                    onClick={() => setCurrentStep(2)}
                    style={{
                      background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
                      color: 'white',
                      border: 'none',
                      padding: '12px 25px',
                      borderRadius: '8px',
                      fontSize: '1rem',
                      fontWeight: 'bold',
                      cursor: 'pointer'
                    }}
                  >
                    ✅ 선택된 {selectedKeywords.length}개 키워드로 제목 생성 단계로
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Step 2: 제목 생성 */}
      {currentStep === 2 && (
        <div className="card">
          <h3>📝 Step 2: 제목 자동 생성</h3>
          <p>선택된 {selectedKeywords.length}개 키워드로 바이럴 제목을 생성합니다.</p>
          
          <div style={{ marginBottom: '20px' }}>
            <h5>선택된 키워드:</h5>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {selectedKeywords.map((keyword, index) => (
                <span 
                  key={index}
                  style={{
                    background: '#667eea',
                    color: 'white',
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '0.85rem'
                  }}
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>

          <div className="form-group" style={{ maxWidth: '200px' }}>
            <label className="form-label">키워드당 제목 개수</label>
            <select
              className="form-input"
              value={titlesPerKeyword}
              onChange={(e) => setTitlesPerKeyword(parseInt(e.target.value))}
            >
              <option value={5}>5개</option>
              <option value={10}>10개</option>
              <option value={15}>15개</option>
              <option value={20}>20개</option>
            </select>
          </div>

          <button
            onClick={generateTitles}
            disabled={loading}
            style={{
              background: loading ? '#6c757d' : 'linear-gradient(135deg, #007bff 0%, #6610f2 100%)',
              color: 'white',
              border: 'none',
              padding: '15px 30px',
              borderRadius: '8px',
              fontSize: '1.1rem',
              fontWeight: 'bold',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? '🔄 제목 생성 중...' : '📝 제목 자동 생성'}
          </button>

          {session.titles && session.titles.length > 0 && (
            <div style={{ marginTop: '30px' }}>
              <h4>생성된 제목 ({session.titles.length}개)</h4>
              <p style={{ color: '#666', marginBottom: '15px' }}>
                블로그 글로 만들 제목들을 선택하세요.
              </p>
              
              <div style={{ display: 'grid', gap: '10px' }}>
                {session.titles.map((title: Title, index: number) => (
                  <div 
                    key={index}
                    style={{
                      border: selectedTitles.includes(title.title) ? '2px solid #007bff' : '1px solid #ddd',
                      borderRadius: '8px',
                      padding: '15px',
                      background: selectedTitles.includes(title.title) ? '#f8f9ff' : 'white',
                      cursor: 'pointer'
                    }}
                    onClick={() => toggleTitleSelection(title.title)}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                      <input
                        type="checkbox"
                        checked={selectedTitles.includes(title.title)}
                        onChange={() => toggleTitleSelection(title.title)}
                        style={{ marginRight: '10px', transform: 'scale(1.2)' }}
                      />
                      <h5 style={{ margin: 0, flex: 1 }}>{title.title}</h5>
                    </div>
                    <div style={{ display: 'flex', gap: '15px', fontSize: '0.85rem', color: '#666' }}>
                      <span>SEO: <strong>{title.seo_score}</strong></span>
                      <span>바이럴: <strong>{title.viral_score}</strong></span>
                      <span>GEO: <strong>{title.geo_score}</strong></span>
                      <span>클릭률: <strong>{title.click_potential.toFixed(1)}</strong></span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#888', marginTop: '5px' }}>
                      키워드: {title.keyword}
                    </div>
                  </div>
                ))}
              </div>

              {selectedTitles.length > 0 && (
                <div style={{ marginTop: '20px', textAlign: 'center' }}>
                  <button
                    onClick={generateContents}
                    disabled={loading}
                    style={{
                      background: loading ? '#6c757d' : 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
                      color: 'white',
                      border: 'none',
                      padding: '12px 25px',
                      borderRadius: '8px',
                      fontSize: '1rem',
                      fontWeight: 'bold',
                      cursor: loading ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {loading ? '🔄 블로그 글 생성 중...' : `✅ 선택된 ${selectedTitles.length}개 제목으로 블로그 글 생성`}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Step 3: 블로그 글 생성 결과 */}
      {currentStep === 3 && session.contents && (
        <div className="card">
          <h3>📄 Step 3: 생성된 블로그 글</h3>
          <p>{session.contents.length}개의 전문 블로그 글이 생성되었습니다.</p>
          
          <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
            <button
              onClick={saveContentsLocally}
              disabled={selectedContents.length === 0}
              style={{
                background: selectedContents.length === 0 ? '#6c757d' : '#28a745',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '6px',
                cursor: selectedContents.length === 0 ? 'not-allowed' : 'pointer'
              }}
            >
              💾 선택한 글 로컬 저장 ({selectedContents.length}개)
            </button>
            
            <button
              onClick={() => setCurrentStep(4)}
              disabled={selectedContents.length === 0}
              style={{
                background: selectedContents.length === 0 ? '#6c757d' : 'linear-gradient(135deg, #fd7e14 0%, #e83e8c 100%)',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '6px',
                cursor: selectedContents.length === 0 ? 'not-allowed' : 'pointer'
              }}
            >
              📤 자동 포스팅 설정으로 ({selectedContents.length}개)
            </button>
          </div>

          <div style={{ display: 'grid', gap: '15px' }}>
            {session.contents.map((content: Content, index: number) => (
              <div 
                key={index}
                style={{
                  border: selectedContents.includes(content.title) ? '2px solid #007bff' : '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '20px',
                  background: selectedContents.includes(content.title) ? '#f8f9ff' : 'white'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '15px' }}>
                  <input
                    type="checkbox"
                    checked={selectedContents.includes(content.title)}
                    onChange={() => toggleContentSelection(content.title)}
                    style={{ marginRight: '15px', marginTop: '5px', transform: 'scale(1.2)' }}
                  />
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 10px 0' }}>{content.title}</h4>
                    
                    {/* 콘텐츠 통계 */}
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', 
                      gap: '10px',
                      marginBottom: '15px',
                      fontSize: '0.85rem'
                    }}>
                      <div style={{ textAlign: 'center', padding: '8px', background: '#f8f9fa', borderRadius: '6px' }}>
                        <div style={{ fontWeight: 'bold', color: '#667eea' }}>{content.word_count}</div>
                        <div>글자수</div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px', background: '#f8f9fa', borderRadius: '6px' }}>
                        <div style={{ fontWeight: 'bold', color: '#28a745' }}>{content.seo_score}</div>
                        <div>SEO점수</div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px', background: '#f8f9fa', borderRadius: '6px' }}>
                        <div style={{ fontWeight: 'bold', color: '#dc3545' }}>{content.geo_score}</div>
                        <div>GEO점수</div>
                      </div>
                      <div style={{ textAlign: 'center', padding: '8px', background: '#f8f9fa', borderRadius: '6px' }}>
                        <div style={{ fontWeight: 'bold', color: '#fd7e14' }}>{content.readability_score}</div>
                        <div>가독성</div>
                      </div>
                    </div>

                    {/* 키워드 정보 */}
                    <div style={{ marginBottom: '15px' }}>
                      <div style={{ marginBottom: '8px' }}>
                        <strong style={{ color: '#667eea' }}>🎯 SEO 키워드:</strong>
                        <div style={{ marginTop: '5px' }}>
                          {content.seo_keywords.map((kw, i) => (
                            <span key={i} style={{
                              display: 'inline-block',
                              background: '#667eea',
                              color: 'white',
                              padding: '2px 6px',
                              borderRadius: '10px',
                              fontSize: '0.75rem',
                              margin: '2px'
                            }}>
                              {kw}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <strong style={{ color: '#764ba2' }}>🔗 LSI 키워드:</strong>
                        <div style={{ marginTop: '5px' }}>
                          {content.lsi_keywords.map((kw, i) => (
                            <span key={i} style={{
                              display: 'inline-block',
                              background: '#764ba2',
                              color: 'white',
                              padding: '2px 6px',
                              borderRadius: '10px',
                              fontSize: '0.75rem',
                              margin: '2px'
                            }}>
                              {kw}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* 콘텐츠 미리보기 */}
                    <div style={{
                      background: '#f8f9fa',
                      padding: '15px',
                      borderRadius: '6px',
                      border: '1px solid #ddd',
                      maxHeight: '200px',
                      overflowY: 'auto'
                    }}>
                      <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', fontSize: '0.9rem' }}>
                        {content.content.substring(0, 500)}
                        {content.content.length > 500 && '...'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step 4: 자동 포스팅 설정 */}
      {currentStep === 4 && (
        <div className="card">
          <h3>📤 Step 4: 자동 포스팅 설정</h3>
          <p>선택된 {selectedContents.length}개의 블로그 글을 WordPress에 자동 포스팅합니다.</p>
          
          <div style={{ marginBottom: '20px' }}>
            <h5>포스팅할 글 목록:</h5>
            <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '6px' }}>
              {selectedContents.map((title, index) => (
                <div key={index} style={{ marginBottom: '5px' }}>
                  {index + 1}. {title}
                </div>
              ))}
            </div>
          </div>

          {/* 스케줄 설정 */}
          <div style={{ marginBottom: '30px' }}>
            <h4>⏰ 포스팅 스케줄 설정</h4>
            
            <div className="form-group">
              <label className="form-label">
                <input
                  type="checkbox"
                  checked={scheduleSettings.immediate}
                  onChange={(e) => setScheduleSettings({
                    ...scheduleSettings,
                    immediate: e.target.checked
                  })}
                  style={{ marginRight: '8px' }}
                />
                즉시 포스팅
              </label>
            </div>

            {!scheduleSettings.immediate && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                <div className="form-group">
                  <label className="form-label">시작 지연 (분)</label>
                  <input
                    type="number"
                    className="form-input"
                    value={scheduleSettings.start_delay_minutes}
                    onChange={(e) => setScheduleSettings({
                      ...scheduleSettings,
                      start_delay_minutes: parseInt(e.target.value) || 0
                    })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">포스팅 간격 (분)</label>
                  <input
                    type="number"
                    className="form-input"
                    value={scheduleSettings.interval_minutes}
                    onChange={(e) => setScheduleSettings({
                      ...scheduleSettings,
                      interval_minutes: parseInt(e.target.value) || 30
                    })}
                  />
                </div>
              </div>
            )}
          </div>

          <div style={{ textAlign: 'center' }}>
            <button
              onClick={publishContents}
              disabled={loading}
              style={{
                background: loading ? '#6c757d' : 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)',
                color: 'white',
                border: 'none',
                padding: '15px 30px',
                borderRadius: '8px',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? '🔄 포스팅 중...' : '🚀 자동 포스팅 시작'}
            </button>
          </div>

          {/* 포스팅 결과 */}
          {session.posting_results && (
            <div style={{ marginTop: '30px' }}>
              <h4>📊 포스팅 결과</h4>
              <div style={{ display: 'grid', gap: '10px' }}>
                {session.posting_results.map((result: any, index: number) => (
                  <div 
                    key={index}
                    style={{
                      border: `2px solid ${result.status === 'success' ? '#28a745' : '#dc3545'}`,
                      borderRadius: '8px',
                      padding: '15px',
                      background: result.status === 'success' ? '#f8fff8' : '#fff8f8'
                    }}
                  >
                    <h5 style={{ margin: '0 0 10px 0' }}>
                      {result.status === 'success' ? '✅' : '❌'} {result.title}
                    </h5>
                    {result.status === 'success' ? (
                      <div>
                        <div><strong>포스트 ID:</strong> {result.post_id}</div>
                        <div><strong>URL:</strong> 
                          <a href={result.post_url} target="_blank" rel="noopener noreferrer" style={{ marginLeft: '5px', color: '#007bff' }}>
                            {result.post_url}
                          </a>
                        </div>
                        {result.scheduled_time && (
                          <div><strong>예약 시간:</strong> {new Date(result.scheduled_time).toLocaleString()}</div>
                        )}
                      </div>
                    ) : (
                      <div style={{ color: '#dc3545' }}>
                        <strong>오류:</strong> {result.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 완료 메시지 */}
      {session.step_status === 'completed' && (
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎉</div>
            <h2 style={{ color: '#28a745', marginBottom: '15px' }}>자동화 완료!</h2>
            <p style={{ fontSize: '1.1rem', marginBottom: '30px' }}>
              총 {session.published_count}개의 블로그 글이 성공적으로 포스팅되었습니다.
            </p>
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
              <button
                onClick={() => window.location.href = '/blog-automation-hub.html'}
                style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                🏠 메인으로 돌아가기
              </button>
              
              <button
                onClick={() => window.location.reload()}
                style={{
                  background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 'bold'
                }}
              >
                🔄 새 자동화 시작
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AutomationWorkflow;