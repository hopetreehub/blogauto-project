import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/api';
import useSessionStorage from '../hooks/useSessionStorage';

interface TitleOption {
  length: 'short' | 'medium' | 'long';
  language: 'ko' | 'en';
  tone: 'professional' | 'casual' | 'exciting';
}

interface GeneratedTitle {
  title: string;
  duplicateRate: number;
  selected?: boolean;
}

interface AdvancedTitle {
  title: string;
  format_type: string;
  emotion_trigger: string;
  scores: {
    seo_score: number;
    click_score: number;
    viral_score: number;
    timely_score: number;
    total_score: number;
  };
  length: number;
  reason: string;
  selected?: boolean;
}

const TitleGenerator: React.FC = () => {
  const { token } = useAuth();
  const [keyword, setKeyword] = useSessionStorage('titleGenerator_keyword', '');
  const [guidelines, setGuidelines] = useSessionStorage('titleGenerator_guidelines', '');
  const [seoGuidelines, setSeoGuidelines] = useSessionStorage('titleGenerator_seoGuidelines', '');
  const [options, setOptions] = useSessionStorage<TitleOption>('titleGenerator_options', {
    length: 'medium',
    language: 'ko',
    tone: 'professional'
  });
  const [titles, setTitles] = useState<GeneratedTitle[]>([]);
  const [advancedTitles, setAdvancedTitles] = useState<AdvancedTitle[]>([]);
  const [loading, setLoading] = useState(false);
  const [advancedLoading, setAdvancedLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedMode, setSelectedMode] = useState<'basic' | 'advanced'>('advanced');

  const handleGenerate = async () => {
    if (!keyword.trim()) {
      setError('키워드를 입력해주세요.');
      return;
    }

    if (!token) {
      setError('로그인이 필요합니다.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Ensure API client has the latest token
      apiClient.setToken(token);
      const data = await apiClient.generateTitles(
        keyword,
        options.length,
        options.language,
        options.tone,
        5
      );
      
      const titles: GeneratedTitle[] = data.map((item: any) => ({
        title: item.title,
        duplicateRate: item.duplicate_rate,
        selected: false
      }));
      
      setTitles(titles);
    } catch (err) {
      setError('제목 생성 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvancedGenerate = async () => {
    if (!keyword.trim()) {
      setError('키워드를 입력해주세요.');
      return;
    }

    if (!token) {
      setError('로그인이 필요합니다.');
      return;
    }

    setAdvancedLoading(true);
    setError('');
    
    try {
      apiClient.setToken(token);
      const response = await apiClient.generateAdvancedTitles(keyword, 5) as any;
      
      const generatedTitles: AdvancedTitle[] = response.data.generated_titles.map((item: any) => ({
        title: item.title,
        format_type: item.format_type,
        emotion_trigger: item.emotion_trigger,
        scores: item.scores,
        length: item.length,
        reason: item.reason,
        selected: false
      }));
      
      setAdvancedTitles(generatedTitles);
    } catch (err) {
      setError('고급 제목 생성 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setAdvancedLoading(false);
    }
  };

  const toggleAdvancedTitleSelection = (index: number) => {
    const updatedTitles = advancedTitles.map((title, i) => 
      i === index ? { ...title, selected: !title.selected } : title
    );
    setAdvancedTitles(updatedTitles);
  };

  const toggleTitleSelection = (index: number) => {
    const updatedTitles = titles.map((title, i) => 
      i === index ? { ...title, selected: !title.selected } : title
    );
    setTitles(updatedTitles);
  };

  const copyTitle = (title: string) => {
    navigator.clipboard.writeText(title);
    alert('제목이 클립보드에 복사되었습니다.');
  };

  const generateBatchContent = async (selectedTitles: string[]) => {
    if (selectedTitles.length === 0) {
      setError('콘텐츠를 생성할 제목을 선택해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      apiClient.setToken(token);
      const response = await apiClient.post('/api/content/batch-generate', {
        titles: selectedTitles,
        guidelines: guidelines,
        seo_guidelines: seoGuidelines,
        geo_guidelines: 'GEO 최적화를 고려한 콘텐츠 작성'
      }) as any;

      const contentData = response.content_data;
      localStorage.setItem('batch_content', JSON.stringify(contentData));
      window.location.href = '/content?batch=true';
      
    } catch (err) {
      setError('콘텐츠 생성 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchContent = () => {
    const selectedTitles = selectedMode === 'basic' 
      ? titles.filter(t => t.selected).map(t => t.title)
      : advancedTitles.filter(t => t.selected).map(t => t.title);
    
    generateBatchContent(selectedTitles);
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🎯 블로그 제목 생성기</h1>
        <p className="page-description">AI 기반 매력적이고 클릭률 높은 블로그 제목을 생성합니다</p>
      </div>

      {/* 모드 선택 탭 */}
      <div className="card">
        <div style={{ display: 'flex', borderBottom: '2px solid #f0f0f0', marginBottom: '20px' }}>
          <button
            className={`tab-button ${selectedMode === 'basic' ? 'active' : ''}`}
            onClick={() => setSelectedMode('basic')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: selectedMode === 'basic' ? '#007bff' : 'transparent',
              color: selectedMode === 'basic' ? 'white' : '#666',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0'
            }}
          >
            📝 기본 제목 생성
          </button>
          <button
            className={`tab-button ${selectedMode === 'advanced' ? 'active' : ''}`}
            onClick={() => setSelectedMode('advanced')}
            style={{
              padding: '12px 24px',
              border: 'none',
              background: selectedMode === 'advanced' ? '#007bff' : 'transparent',
              color: selectedMode === 'advanced' ? 'white' : '#666',
              cursor: 'pointer',
              borderRadius: '8px 8px 0 0',
              marginLeft: '8px'
            }}
          >
            🚀 고급 제목 생성 (시의성+SEO+바이럴)
          </button>
        </div>

        {/* 기본 키워드 입력 */}
        <div className="form-group">
          <label className="form-label">키워드</label>
          <input
            type="text"
            className="form-input"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="예: 장마철 건강관리, 스탠딩책상"
          />
        </div>

        {selectedMode === 'basic' && (
          <>
            {/* 기본 모드 옵션 */}

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '20px' }}>
              <div className="form-group">
                <label className="form-label">길이</label>
                <select
                  className="form-input"
                  value={options.length}
                  onChange={(e) => setOptions({...options, length: e.target.value as any})}
                >
                  <option value="short">짧음</option>
                  <option value="medium">보통</option>
                  <option value="long">길음</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">언어</label>
                <select
                  className="form-input"
                  value={options.language}
                  onChange={(e) => setOptions({...options, language: e.target.value as any})}
                >
                  <option value="ko">한국어</option>
                  <option value="en">영어</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">톤</label>
                <select
                  className="form-input"
                  value={options.tone}
                  onChange={(e) => setOptions({...options, tone: e.target.value as any})}
                >
                  <option value="professional">전문적</option>
                  <option value="casual">캐주얼</option>
                  <option value="exciting">흥미진진</option>
                </select>
              </div>
            </div>

            <button 
              className="btn btn-primary" 
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? '생성 중...' : '📝 기본 제목 생성'}
            </button>
          </>
        )}

        {selectedMode === 'advanced' && (
          <>
            <div style={{ background: '#f8f9fa', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
              <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>
                💡 고급 제목 생성기는 <strong>시의성, SEO, 바이럴성, 클릭 유도</strong>를 모두 고려하여 
                현재 시기에 최적화된 매력적인 제목을 생성합니다.
              </p>
            </div>
            
            <button 
              className="btn btn-primary" 
              onClick={handleAdvancedGenerate}
              disabled={advancedLoading}
              style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
            >
              {advancedLoading ? '🔍 고급 분석 중...' : '🚀 고급 제목 생성 시작'}
            </button>
          </>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {/* 기본 제목 결과 */}
      {selectedMode === 'basic' && titles.length > 0 && (
        <div className="card">
          <h3>생성된 제목</h3>
          <div style={{ display: 'grid', gap: '15px' }}>
            {titles.map((title, index) => (
              <div key={index} style={{ 
                padding: '15px', 
                border: `2px solid ${title.selected ? '#007bff' : '#e0e0e0'}`,
                borderRadius: '8px',
                background: title.selected ? '#f0f8ff' : 'white'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', flex: 1 }}>
                    <input
                      type="checkbox"
                      checked={title.selected || false}
                      onChange={() => toggleTitleSelection(index)}
                      style={{ marginRight: '10px' }}
                    />
                    <span style={{ fontSize: '1.1rem', fontWeight: '500' }}>{title.title}</span>
                  </label>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <span style={{ 
                      background: title.duplicateRate < 30 ? '#28a745' : title.duplicateRate < 60 ? '#ffc107' : '#dc3545',
                      color: 'white',
                      padding: '4px 8px',
                      borderRadius: '12px',
                      fontSize: '0.8rem'
                    }}>
                      중복률: {title.duplicateRate.toFixed(1)}%
                    </span>
                    <button 
                      onClick={() => copyTitle(title.title)}
                      style={{ 
                        background: 'none', 
                        border: '1px solid #ddd', 
                        padding: '6px 12px', 
                        borderRadius: '4px',
                        cursor: 'pointer' 
                      }}
                    >
                      📋 복사
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {titles.some(t => t.selected) && (
            <div style={{ marginTop: '20px' }}>
              <button 
                className="btn btn-secondary" 
                onClick={handleBatchContent}
                disabled={loading}
              >
                {loading ? '생성 중...' : '선택된 제목으로 콘텐츠 생성'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* 고급 제목 결과 */}
      {selectedMode === 'advanced' && advancedTitles.length > 0 && (
        <div className="card">
          <h3>🎯 고급 제목 분석 결과</h3>
          <div style={{ display: 'grid', gap: '20px' }}>
            {advancedTitles.map((title, index) => (
              <div key={index} style={{ 
                padding: '20px', 
                border: `2px solid ${title.selected ? '#667eea' : '#e0e0e0'}`,
                borderRadius: '12px',
                background: title.selected ? 'linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%)' : 'white'
              }}>
                {/* 제목 헤더 */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', flex: 1 }}>
                    <input
                      type="checkbox"
                      checked={title.selected || false}
                      onChange={() => toggleAdvancedTitleSelection(index)}
                      style={{ marginRight: '12px' }}
                    />
                    <span style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#333' }}>
                      {title.title}
                    </span>
                  </label>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <span style={{
                      background: title.scores.total_score > 80 ? '#28a745' : 
                                 title.scores.total_score > 60 ? '#ffc107' : '#6c757d',
                      color: 'white',
                      padding: '6px 12px',
                      borderRadius: '20px',
                      fontSize: '0.9rem',
                      fontWeight: 'bold'
                    }}>
                      총점: {title.scores.total_score.toFixed(1)}
                    </span>
                    <button 
                      onClick={() => copyTitle(title.title)}
                      style={{ 
                        background: 'none', 
                        border: '1px solid #ddd', 
                        padding: '6px 12px', 
                        borderRadius: '4px',
                        cursor: 'pointer' 
                      }}
                    >
                      📋 복사
                    </button>
                  </div>
                </div>

                {/* 제목 타입 및 감정 */}
                <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                  <span style={{
                    background: '#667eea',
                    color: 'white',
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '0.8rem'
                  }}>
                    {title.format_type}
                  </span>
                  <span style={{
                    background: '#764ba2',
                    color: 'white',
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '0.8rem'
                  }}>
                    {title.emotion_trigger}
                  </span>
                  <span style={{
                    background: '#f093fb',
                    color: 'white',
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '0.8rem'
                  }}>
                    {title.length}자
                  </span>
                </div>

                {/* 점수 상세 */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '15px' }}>
                  <div style={{ textAlign: 'center', padding: '10px', background: '#f8f9fa', borderRadius: '6px' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#007bff' }}>
                      {title.scores.seo_score.toFixed(0)}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#666' }}>SEO</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '10px', background: '#f8f9fa', borderRadius: '6px' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#28a745' }}>
                      {title.scores.click_score.toFixed(0)}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#666' }}>클릭</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '10px', background: '#f8f9fa', borderRadius: '6px' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#dc3545' }}>
                      {title.scores.viral_score.toFixed(0)}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#666' }}>바이럴</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '10px', background: '#f8f9fa', borderRadius: '6px' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ffc107' }}>
                      {title.scores.timely_score.toFixed(0)}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#666' }}>시의성</div>
                  </div>
                </div>

                {/* 추천 이유 */}
                <div style={{ 
                  background: '#e8f5e8', 
                  padding: '12px', 
                  borderRadius: '8px',
                  fontSize: '0.9rem',
                  border: '1px solid #28a745'
                }}>
                  <strong style={{ color: '#28a745' }}>💡 추천 이유:</strong> 
                  <span style={{ marginLeft: '8px', color: '#155724' }}>{title.reason}</span>
                </div>
              </div>
            ))}
          </div>
          
          {advancedTitles.some(t => t.selected) && (
            <div style={{ marginTop: '20px' }}>
              <button 
                className="btn btn-secondary" 
                onClick={handleBatchContent}
                disabled={loading}
                style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}
              >
                {loading ? '생성 중...' : '선택된 제목으로 콘텐츠 생성'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* 가이드라인 입력 (선택된 제목이 있을 때만 표시) */}
      {((selectedMode === 'basic' && titles.some(t => t.selected)) || 
        (selectedMode === 'advanced' && advancedTitles.some(t => t.selected))) && (
        <div className="card">
          <h3>콘텐츠 생성 가이드라인</h3>
          
          <div className="form-group">
            <label className="form-label">제목 생성 가이드라인</label>
            <textarea
              className="form-input"
              rows={3}
              value={guidelines}
              onChange={(e) => setGuidelines(e.target.value)}
              placeholder="제목 생성 시 고려할 가이드라인을 입력하세요 (예: 브랜드 톤앤매너, 타겟 독자층 등)"
            />
          </div>

          <div className="form-group">
            <label className="form-label">SEO & GEO 최적화 가이드라인</label>
            <textarea
              className="form-input"
              rows={3}
              value={seoGuidelines}
              onChange={(e) => setSeoGuidelines(e.target.value)}
              placeholder="SEO 최적화 및 지역 최적화 요구사항을 입력하세요 (예: 지역명 포함, 특정 키워드 포함 등)"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default TitleGenerator;