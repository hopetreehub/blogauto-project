import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/api';
import useSessionStorage from '../hooks/useSessionStorage';

interface Domain {
  id: string;
  name: string;
  url: string;
  category: string;
  platform: 'wordpress' | 'blogspot' | 'tistory';
  apiKey?: string;
  isActive: boolean;
}

interface CategoryKeywords {
  category: string;
  goldenKeywords: string[];
  trendingKeywords: string[];
  profitableKeywords: string[];
}

interface SEOKeyword {
  keyword: string;
  search_volume: string;
  competition: string;
  seasonal: boolean;
  reason: string;
  score: number;
}

interface IntegratedKeyword {
  keyword: string;
  integrated_score: number;
  priority: string;
  opportunity: string;
  naver_data: {
    trend_ratio: number;
    trend_direction: string;
    seasonal: boolean;
    competition: string;
  };
  google_data: {
    monthly_searches: number;
    competition: string;
    cpc_range: string;
    difficulty: number;
  };
  seo_data: {
    score: number;
    reason: string;
  };
}

const DomainSelector: React.FC = () => {
  const { token } = useAuth();
  const [domains, setDomains] = useState<Domain[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);
  const [categoryKeywords, setCategoryKeywords] = useState<CategoryKeywords | null>(null);
  const [seoKeywords, setSeoKeywords] = useState<SEOKeyword[]>([]);
  const [integratedKeywords, setIntegratedKeywords] = useState<IntegratedKeyword[]>([]);
  const [loading, setLoading] = useState(false);
  const [seoLoading, setSeoLoading] = useState(false);
  const [integratedLoading, setIntegratedLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedTab, setSelectedTab] = useState<'golden' | 'seo' | 'integrated'>('golden');

  // 새 도메인 추가 상태
  const [showAddDomain, setShowAddDomain] = useState(false);
  const [newDomain, setNewDomain] = useState({
    name: '',
    url: '',
    category: '',
    platform: 'wordpress' as const,
    apiKey: ''
  });

  // SEO 분석 입력 상태
  const [seoAnalysisInput, setSeoAnalysisInput] = useSessionStorage('domainSelector_seoAnalysis', {
    itemName: '',
    category: ''
  });

  const popularCategories = [
    '여행', '음식', '패션', '뷰티', '건강', '운동', '재테크', '투자',
    '부동산', '자동차', '게임', '영화', '음악', '책', '교육', '육아',
    '반려동물', '원예', '인테리어', '요리', '취미', '스포츠', '기술',
    '프로그래밍', '창업', '부업', '온라인쇼핑', '리뷰', '라이프스타일'
  ];

  const handleAddDomain = async () => {
    if (!newDomain.name || !newDomain.url || !newDomain.category) {
      setError('모든 필드를 입력해주세요.');
      return;
    }

    const domain: Domain = {
      id: Date.now().toString(),
      name: newDomain.name,
      url: newDomain.url,
      category: newDomain.category,
      platform: newDomain.platform,
      apiKey: newDomain.apiKey,
      isActive: true
    };

    setDomains([...domains, domain]);
    setNewDomain({ name: '', url: '', category: '', platform: 'wordpress', apiKey: '' });
    setShowAddDomain(false);
    setError('');
  };

  const handleSelectDomain = async (domain: Domain) => {
    setSelectedDomain(domain);
    setLoading(true);
    setError('');

    try {
      if (!token) {
        setError('로그인이 필요합니다.');
        return;
      }

      apiClient.setToken(token);
      
      // 황금 키워드 생성 API 호출
      const response = await apiClient.post('/api/keywords/golden', {
        category: domain.category,
        domain: domain.url,
        platform: domain.platform
      }) as any;

      setCategoryKeywords({
        category: domain.category,
        goldenKeywords: response.data.golden_keywords || [],
        trendingKeywords: response.data.trending_keywords || [],
        profitableKeywords: response.data.profitable_keywords || []
      });

    } catch (err) {
      setError('키워드 생성 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSEOAnalysis = async () => {
    if (!seoAnalysisInput.itemName || !seoAnalysisInput.category) {
      setError('아이템 이름과 카테고리를 입력해주세요.');
      return;
    }

    setSeoLoading(true);
    setError('');

    try {
      if (!token) {
        setError('로그인이 필요합니다.');
        return;
      }

      apiClient.setToken(token);
      
      const response = await apiClient.analyzeSEOKeywords(
        seoAnalysisInput.itemName,
        seoAnalysisInput.category
      ) as any;

      setSeoKeywords(response.data.seo_keywords || []);

    } catch (err) {
      setError('SEO 키워드 분석 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setSeoLoading(false);
    }
  };

  const handleIntegratedAnalysis = async () => {
    if (!seoAnalysisInput.itemName || !seoAnalysisInput.category) {
      setError('아이템 이름과 카테고리를 입력해주세요.');
      return;
    }

    setIntegratedLoading(true);
    setError('');

    try {
      if (!token) {
        setError('로그인이 필요합니다.');
        return;
      }

      apiClient.setToken(token);
      
      const response = await apiClient.analyzeIntegratedKeywords(
        seoAnalysisInput.itemName,
        seoAnalysisInput.category,
        true
      ) as any;

      setIntegratedKeywords(response.data.integrated_keywords || []);

    } catch (err) {
      setError('통합 키워드 분석 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setIntegratedLoading(false);
    }
  };

  const handleKeywordSelect = (keyword: string) => {
    // 키워드 선택 시 제목 생성 페이지로 이동
    if (selectedDomain) {
      window.location.hash = `/titles?keyword=${encodeURIComponent(keyword)}&domain=${selectedDomain.id}&category=${encodeURIComponent(selectedDomain.category || '')}`;
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">도메인 & 카테고리 선택</h1>
        <p className="page-description">블로그 플랫폼을 선택하고 황금 키워드를 발굴하세요</p>
      </div>

      {/* 도메인 추가 버튼 */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>등록된 도메인</h3>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddDomain(true)}
          >
            + 도메인 추가
          </button>
        </div>

        {/* 도메인 추가 폼 */}
        {showAddDomain && (
          <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
            <h4>새 도메인 추가</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px', marginTop: '15px' }}>
              <div className="form-group">
                <label className="form-label">도메인 이름</label>
                <input
                  type="text"
                  className="form-input"
                  value={newDomain.name}
                  onChange={(e) => setNewDomain({...newDomain, name: e.target.value})}
                  placeholder="예: 내 여행 블로그"
                />
              </div>
              <div className="form-group">
                <label className="form-label">도메인 URL</label>
                <input
                  type="text"
                  className="form-input"
                  value={newDomain.url}
                  onChange={(e) => setNewDomain({...newDomain, url: e.target.value})}
                  placeholder="예: innerspell.com"
                />
              </div>
              <div className="form-group">
                <label className="form-label">카테고리</label>
                <select
                  className="form-input"
                  value={newDomain.category}
                  onChange={(e) => setNewDomain({...newDomain, category: e.target.value})}
                >
                  <option value="">카테고리 선택</option>
                  {popularCategories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">플랫폼</label>
                <select
                  className="form-input"
                  value={newDomain.platform}
                  onChange={(e) => setNewDomain({...newDomain, platform: e.target.value as any})}
                >
                  <option value="wordpress">WordPress</option>
                  <option value="blogspot">BlogSpot</option>
                  <option value="tistory">Tistory</option>
                </select>
              </div>
            </div>
            <div className="form-group" style={{ marginTop: '15px' }}>
              <label className="form-label">API 키 (선택사항)</label>
              <input
                type="password"
                className="form-input"
                value={newDomain.apiKey}
                onChange={(e) => setNewDomain({...newDomain, apiKey: e.target.value})}
                placeholder="자동 포스팅을 위한 API 키"
              />
            </div>
            <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
              <button className="btn btn-primary" onClick={handleAddDomain}>
                추가
              </button>
              <button className="btn btn-secondary" onClick={() => setShowAddDomain(false)}>
                취소
              </button>
            </div>
          </div>
        )}

        {/* 도메인 목록 */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '15px' }}>
          {domains.map(domain => (
            <div
              key={domain.id}
              className={`card ${selectedDomain?.id === domain.id ? 'selected' : ''}`}
              style={{
                cursor: 'pointer',
                border: selectedDomain?.id === domain.id ? '2px solid #007bff' : '1px solid #ddd',
                padding: '15px'
              }}
              onClick={() => handleSelectDomain(domain)}
            >
              <h4 style={{ margin: '0 0 10px 0' }}>{domain.name}</h4>
              <p style={{ margin: '0 0 5px 0', color: '#666' }}>
                <strong>URL:</strong> {domain.url}
              </p>
              <p style={{ margin: '0 0 5px 0', color: '#666' }}>
                <strong>카테고리:</strong> {domain.category}
              </p>
              <p style={{ margin: '0', color: '#666' }}>
                <strong>플랫폼:</strong> {domain.platform}
              </p>
            </div>
          ))}
        </div>

        {domains.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            등록된 도메인이 없습니다. 도메인을 추가해주세요.
          </div>
        )}
      </div>

      {/* 키워드 분석 탭 */}
      <div className="card">
        <div style={{ display: 'flex', borderBottom: '2px solid #f0f0f0', marginBottom: '20px' }}>
          <button
            className={`tab-button ${selectedTab === 'golden' ? 'active' : ''}`}
            onClick={() => setSelectedTab('golden')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: selectedTab === 'golden' ? '#007bff' : 'transparent',
              color: selectedTab === 'golden' ? 'white' : '#666',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0'
            }}
          >
            💰 황금 키워드 (기존)
          </button>
          <button
            className={`tab-button ${selectedTab === 'seo' ? 'active' : ''}`}
            onClick={() => setSelectedTab('seo')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: selectedTab === 'seo' ? '#007bff' : 'transparent',
              color: selectedTab === 'seo' ? 'white' : '#666',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              marginLeft: '8px'
            }}
          >
            🔍 SEO 키워드 분석
          </button>
          <button
            className={`tab-button ${selectedTab === 'integrated' ? 'active' : ''}`}
            onClick={() => setSelectedTab('integrated')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: selectedTab === 'integrated' ? '#007bff' : 'transparent',
              color: selectedTab === 'integrated' ? 'white' : '#666',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              marginLeft: '8px'
            }}
          >
            🚀 통합 분석 (네이버+구글)
          </button>
        </div>

        {selectedTab === 'golden' && selectedDomain && (
          <div>
            <h3>{selectedDomain.category} 카테고리 황금 키워드</h3>
            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div>🔍 황금 키워드를 찾는 중...</div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '10px' }}>
                  수익성, 창의성, 유입량을 분석하여 최적의 키워드를 생성합니다.
                </div>
              </div>
            ) : categoryKeywords ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginTop: '20px' }}>
              {/* 황금 키워드 */}
              <div>
                <h4 style={{ color: '#ffd700', marginBottom: '15px' }}>💰 황금 키워드</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {categoryKeywords.goldenKeywords.map((keyword, index) => (
                    <button
                      key={index}
                      className="btn btn-outline"
                      onClick={() => handleKeywordSelect(keyword)}
                      style={{ textAlign: 'left', padding: '8px 12px' }}
                    >
                      {keyword}
                    </button>
                  ))}
                </div>
              </div>

              {/* 트렌딩 키워드 */}
              <div>
                <h4 style={{ color: '#ff6b6b', marginBottom: '15px' }}>🔥 트렌딩 키워드</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {categoryKeywords.trendingKeywords.map((keyword, index) => (
                    <button
                      key={index}
                      className="btn btn-outline"
                      onClick={() => handleKeywordSelect(keyword)}
                      style={{ textAlign: 'left', padding: '8px 12px' }}
                    >
                      {keyword}
                    </button>
                  ))}
                </div>
              </div>

              {/* 수익성 키워드 */}
              <div>
                <h4 style={{ color: '#4ecdc4', marginBottom: '15px' }}>💵 수익성 키워드</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {categoryKeywords.profitableKeywords.map((keyword, index) => (
                    <button
                      key={index}
                      className="btn btn-outline"
                      onClick={() => handleKeywordSelect(keyword)}
                      style={{ textAlign: 'left', padding: '8px 12px' }}
                    >
                      {keyword}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : null}
          </div>
        )}

        {selectedTab === 'seo' && (
          <div>
            <h3>🔍 SEO 키워드 분석 시스템</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              최신 트렌드와 검색량, 경쟁도를 분석하여 Google/Naver 상위노출에 최적화된 키워드를 제공합니다.
            </p>

            {/* SEO 분석 입력 폼 */}
            <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
                <div className="form-group">
                  <label className="form-label">아이템 이름</label>
                  <input
                    type="text"
                    className="form-input"
                    value={seoAnalysisInput.itemName}
                    onChange={(e) => setSeoAnalysisInput({...seoAnalysisInput, itemName: e.target.value})}
                    placeholder="예: 스탠딩책상"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">카테고리</label>
                  <select
                    className="form-input"
                    value={seoAnalysisInput.category}
                    onChange={(e) => setSeoAnalysisInput({...seoAnalysisInput, category: e.target.value})}
                  >
                    <option value="">카테고리 선택</option>
                    {popularCategories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>
              <button 
                className="btn btn-primary" 
                onClick={handleSEOAnalysis}
                disabled={seoLoading}
                style={{ marginTop: '15px' }}
              >
                {seoLoading ? '🔍 분석 중...' : '🚀 SEO 키워드 분석 시작'}
              </button>
            </div>

            {/* SEO 키워드 결과 */}
            {seoLoading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div>🔍 SEO 키워드를 분석하는 중...</div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '10px' }}>
                  최신 트렌드, 검색량, 경쟁도, 계절성을 종합 분석 중입니다.
                </div>
              </div>
            ) : seoKeywords.length > 0 ? (
              <div>
                <h4 style={{ marginBottom: '20px' }}>📊 상위 SEO 키워드 추천 리스트</h4>
                <div style={{ display: 'grid', gap: '15px' }}>
                  {seoKeywords.map((keyword, index) => (
                    <div 
                      key={index}
                      style={{
                        border: '1px solid #e0e0e0',
                        borderRadius: '8px',
                        padding: '15px',
                        background: keyword.score > 80 ? '#f0f8ff' : 'white'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                        <button
                          className="btn btn-outline"
                          onClick={() => handleKeywordSelect(keyword.keyword)}
                          style={{ 
                            textAlign: 'left', 
                            fontWeight: 'bold',
                            fontSize: '1.1rem',
                            background: 'none',
                            border: 'none',
                            color: '#007bff',
                            cursor: 'pointer',
                            padding: '0'
                          }}
                        >
                          {index + 1}. {keyword.keyword}
                        </button>
                        <span style={{
                          background: keyword.score > 80 ? '#28a745' : keyword.score > 60 ? '#ffc107' : '#6c757d',
                          color: 'white',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '0.8rem',
                          fontWeight: 'bold'
                        }}>
                          점수: {keyword.score.toFixed(1)}
                        </span>
                      </div>
                      
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '10px' }}>
                        <div style={{ fontSize: '0.9rem' }}>
                          <strong>예상 검색량:</strong> {keyword.search_volume}
                        </div>
                        <div style={{ fontSize: '0.9rem' }}>
                          <strong>경쟁도:</strong> 
                          <span style={{ 
                            color: keyword.competition === '낮음' ? '#28a745' : 
                                   keyword.competition === '보통' ? '#ffc107' : '#dc3545',
                            fontWeight: 'bold',
                            marginLeft: '5px'
                          }}>
                            {keyword.competition}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.9rem' }}>
                          <strong>계절성:</strong> 
                          <span style={{ marginLeft: '5px' }}>
                            {keyword.seasonal ? '🔥 있음' : '📅 없음'}
                          </span>
                        </div>
                      </div>
                      
                      <div style={{ 
                        background: '#f8f9fa', 
                        padding: '10px', 
                        borderRadius: '4px',
                        fontSize: '0.9rem',
                        color: '#666'
                      }}>
                        <strong>추천 이유:</strong> {keyword.reason}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                아이템 이름과 카테고리를 입력한 후 분석을 시작해주세요.
              </div>
            )}
          </div>
        )}

        {selectedTab === 'integrated' && (
          <div>
            <h3>🚀 통합 키워드 분석 (네이버 + 구글 + SEO)</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>
              네이버 DataLab + Google Ads + SEO 분석을 통합하여 가장 정확하고 전략적인 키워드를 제공합니다.
            </p>

            {/* 통합 분석 입력 폼 */}
            <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
                <div className="form-group">
                  <label className="form-label">아이템 이름</label>
                  <input
                    type="text"
                    className="form-input"
                    value={seoAnalysisInput.itemName}
                    onChange={(e) => setSeoAnalysisInput({...seoAnalysisInput, itemName: e.target.value})}
                    placeholder="예: 스탠딩책상"
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">카테고리</label>
                  <select
                    className="form-input"
                    value={seoAnalysisInput.category}
                    onChange={(e) => setSeoAnalysisInput({...seoAnalysisInput, category: e.target.value})}
                  >
                    <option value="">카테고리 선택</option>
                    {popularCategories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>
              <button 
                className="btn btn-primary" 
                onClick={handleIntegratedAnalysis}
                disabled={integratedLoading}
                style={{ marginTop: '15px' }}
              >
                {integratedLoading ? '🔍 통합 분석 중...' : '🚀 통합 키워드 분석 시작'}
              </button>
            </div>

            {/* 통합 키워드 결과 */}
            {integratedLoading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <div>🔍 통합 키워드 분석 중...</div>
                <div style={{ fontSize: '0.9rem', color: '#666', marginTop: '10px' }}>
                  네이버 DataLab, Google Ads, SEO 데이터를 종합 분석하여 최적의 키워드를 생성합니다.
                </div>
              </div>
            ) : integratedKeywords.length > 0 ? (
              <div>
                <h4 style={{ marginBottom: '20px' }}>🎯 통합 키워드 분석 결과</h4>
                <div style={{ display: 'grid', gap: '20px' }}>
                  {integratedKeywords.map((keyword, index) => (
                    <div 
                      key={index}
                      style={{
                        border: '2px solid #e0e0e0',
                        borderRadius: '12px',
                        padding: '20px',
                        background: keyword.integrated_score > 80 ? 'linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%)' : 
                                   keyword.integrated_score > 60 ? '#f8f9fa' : 'white',
                        borderColor: keyword.integrated_score > 80 ? '#007bff' : '#e0e0e0'
                      }}
                    >
                      {/* 키워드 헤더 */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                        <button
                          className="btn btn-outline"
                          onClick={() => handleKeywordSelect(keyword.keyword)}
                          style={{ 
                            textAlign: 'left', 
                            fontWeight: 'bold',
                            fontSize: '1.2rem',
                            background: 'none',
                            border: 'none',
                            color: '#007bff',
                            cursor: 'pointer',
                            padding: '0'
                          }}
                        >
                          {index + 1}. {keyword.keyword}
                        </button>
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                          <span style={{
                            background: keyword.integrated_score > 80 ? '#28a745' : 
                                       keyword.integrated_score > 60 ? '#ffc107' : '#6c757d',
                            color: 'white',
                            padding: '6px 12px',
                            borderRadius: '20px',
                            fontSize: '0.9rem',
                            fontWeight: 'bold'
                          }}>
                            통합점수: {keyword.integrated_score}
                          </span>
                          <span style={{
                            background: keyword.priority === '매우 높음' ? '#dc3545' :
                                       keyword.priority === '높음' ? '#fd7e14' :
                                       keyword.priority === '보통' ? '#ffc107' : '#6c757d',
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '12px',
                            fontSize: '0.8rem',
                            fontWeight: 'bold'
                          }}>
                            {keyword.priority}
                          </span>
                        </div>
                      </div>
                      
                      {/* 데이터 소스별 정보 */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '15px', marginBottom: '15px' }}>
                        {/* 네이버 데이터 */}
                        <div style={{ 
                          background: 'rgba(3, 199, 90, 0.1)', 
                          padding: '12px', 
                          borderRadius: '8px',
                          border: '1px solid #03c75a'
                        }}>
                          <h6 style={{ margin: '0 0 8px 0', color: '#03c75a', fontWeight: 'bold' }}>📊 네이버 DataLab</h6>
                          <div style={{ fontSize: '0.85rem' }}>
                            <div><strong>트렌드:</strong> {keyword.naver_data.trend_ratio.toFixed(1)}</div>
                            <div><strong>방향:</strong> {keyword.naver_data.trend_direction}</div>
                            <div><strong>계절성:</strong> {keyword.naver_data.seasonal ? '🔥 있음' : '📅 없음'}</div>
                            <div><strong>경쟁도:</strong> {keyword.naver_data.competition}</div>
                          </div>
                        </div>

                        {/* 구글 데이터 */}
                        <div style={{ 
                          background: 'rgba(66, 133, 244, 0.1)', 
                          padding: '12px', 
                          borderRadius: '8px',
                          border: '1px solid #4285f4'
                        }}>
                          <h6 style={{ margin: '0 0 8px 0', color: '#4285f4', fontWeight: 'bold' }}>🔍 Google Ads</h6>
                          <div style={{ fontSize: '0.85rem' }}>
                            <div><strong>검색량:</strong> {keyword.google_data.monthly_searches.toLocaleString()}/월</div>
                            <div><strong>경쟁도:</strong> {keyword.google_data.competition}</div>
                            <div><strong>CPC:</strong> {keyword.google_data.cpc_range}</div>
                            <div><strong>난이도:</strong> {keyword.google_data.difficulty}/100</div>
                          </div>
                        </div>

                        {/* SEO 데이터 */}
                        <div style={{ 
                          background: 'rgba(255, 193, 7, 0.1)', 
                          padding: '12px', 
                          borderRadius: '8px',
                          border: '1px solid #ffc107'
                        }}>
                          <h6 style={{ margin: '0 0 8px 0', color: '#ffc107', fontWeight: 'bold' }}>⚡ SEO 분석</h6>
                          <div style={{ fontSize: '0.85rem' }}>
                            <div><strong>SEO 점수:</strong> {keyword.seo_data.score.toFixed(1)}/100</div>
                            <div style={{ marginTop: '5px', lineHeight: '1.3' }}>
                              <strong>분석:</strong> {keyword.seo_data.reason.substring(0, 40)}...
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      {/* 기회 요소 */}
                      <div style={{ 
                        background: '#e8f5e8', 
                        padding: '12px', 
                        borderRadius: '8px',
                        fontSize: '0.9rem',
                        border: '1px solid #28a745'
                      }}>
                        <strong style={{ color: '#28a745' }}>💡 콘텐츠 기회:</strong> 
                        <span style={{ marginLeft: '8px', color: '#155724' }}>{keyword.opportunity}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                아이템 이름과 카테고리를 입력한 후 통합 분석을 시작해주세요.
              </div>
            )}
          </div>
        )}
      </div>

      {error && <div className="error" style={{ marginTop: '20px' }}>{error}</div>}

      <style>{`
        .card.selected {
          box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
        }
        .btn-outline {
          background: white;
          border: 1px solid #ddd;
          color: #333;
        }
        .btn-outline:hover {
          background: #f8f9fa;
          border-color: #007bff;
          color: #007bff;
        }
      `}</style>
    </div>
  );
};

export default DomainSelector;