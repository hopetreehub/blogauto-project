import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/api';

interface BatchContent {
  [title: string]: string;
}

interface Platform {
  id: string;
  name: string;
  platform: 'wordpress' | 'blogspot' | 'tistory';
  url: string;
  username?: string;
  password?: string;
  api_key?: string;
  blog_id?: string;
  access_token?: string;
}

const ContentGenerator: React.FC = () => {
  const { token } = useAuth();
  const [title, setTitle] = useState('');
  const [keywords, setKeywords] = useState('');
  const [guidelines, setGuidelines] = useState('');
  const [seoGuidelines, setSeoGuidelines] = useState('');
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState('');
  const [error, setError] = useState('');
  
  // 배치 콘텐츠 관련
  const [batchContent, setBatchContent] = useState<BatchContent>({});
  const [isBatchMode, setIsBatchMode] = useState(false);
  const [selectedContents, setSelectedContents] = useState<string[]>([]);
  
  // 자동 포스팅 관련
  const [showPostingPanel, setShowPostingPanel] = useState(false);
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [scheduleSettings, setScheduleSettings] = useState({
    immediate: true,
    start_delay_minutes: 0,
    interval_minutes: 30,
    platform_delay_minutes: 5
  });
  const [imageSettings, setImageSettings] = useState({
    auto_generate: false,
    generator: 'dall-e',
    style: 'blog-thumbnail',
    user_image: null
  });

  useEffect(() => {
    // URL에서 배치 모드 확인
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('batch') === 'true') {
      const savedBatchContent = localStorage.getItem('batch_content');
      if (savedBatchContent) {
        const parsedContent = JSON.parse(savedBatchContent);
        setBatchContent(parsedContent);
        setIsBatchMode(true);
        localStorage.removeItem('batch_content'); // 사용 후 삭제
      }
    }

    // 저장된 플랫폼 설정 로드
    const savedPlatforms = localStorage.getItem('posting_platforms');
    if (savedPlatforms) {
      setPlatforms(JSON.parse(savedPlatforms));
    }
  }, []);

  const handleGenerate = async () => {
    if (!title.trim()) {
      setError('제목을 입력해주세요.');
      return;
    }

    if (!token) {
      setError('로그인이 필요합니다.');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      apiClient.setToken(token);
      const data = await apiClient.generateContent(
        title,
        keywords || undefined,
        'medium'
      );
      setContent(data.content);
    } catch (err) {
      setError('콘텐츠 생성 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyContent = () => {
    navigator.clipboard.writeText(content);
    alert('콘텐츠가 클립보드에 복사되었습니다.');
  };

  const toggleContentSelection = (title: string) => {
    setSelectedContents(prev => 
      prev.includes(title) 
        ? prev.filter(t => t !== title)
        : [...prev, title]
    );
  };

  const addPlatform = () => {
    const newPlatform: Platform = {
      id: Date.now().toString(),
      name: '',
      platform: 'wordpress',
      url: ''
    };
    setPlatforms([...platforms, newPlatform]);
  };

  const updatePlatform = (id: string, updates: Partial<Platform>) => {
    setPlatforms(platforms.map(p => 
      p.id === id ? { ...p, ...updates } : p
    ));
  };

  const removePlatform = (id: string) => {
    setPlatforms(platforms.filter(p => p.id !== id));
    setSelectedPlatforms(selectedPlatforms.filter(pid => pid !== id));
  };

  const savePlatforms = () => {
    localStorage.setItem('posting_platforms', JSON.stringify(platforms));
    alert('플랫폼 설정이 저장되었습니다.');
  };

  const handleAutoPosting = async () => {
    if (selectedContents.length === 0) {
      setError('포스팅할 콘텐츠를 선택해주세요.');
      return;
    }

    if (selectedPlatforms.length === 0) {
      setError('포스팅할 플랫폼을 선택해주세요.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // 선택된 콘텐츠 데이터 준비
      const contentData: BatchContent = {};
      selectedContents.forEach(title => {
        contentData[title] = batchContent[title] || content;
      });

      // 선택된 플랫폼 설정 준비
      const selectedPlatformConfigs = platforms.filter(p => 
        selectedPlatforms.includes(p.id)
      );

      apiClient.setToken(token);
      const response = await apiClient.post('/api/posts/auto-publish', {
        titles: selectedContents,
        content_data: contentData,
        platforms: selectedPlatformConfigs,
        schedule_settings: scheduleSettings,
        image_settings: imageSettings
      }) as any;

      alert(`자동 포스팅이 완료되었습니다!\n성공: ${response.summary.successful}개\n실패: ${response.summary.failed}개\n예약: ${response.summary.scheduled}개`);
      
    } catch (err) {
      setError('자동 포스팅 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">콘텐츠 생성 {isBatchMode && '& 자동 포스팅'}</h1>
        <p className="page-description">
          {isBatchMode 
            ? 'AI 기반 배치 콘텐츠 생성 및 다중 플랫폼 자동 포스팅' 
            : 'AI 기반 고품질 블로그 콘텐츠 생성'
          }
        </p>
      </div>

      {/* 단일 콘텐츠 생성 모드 */}
      {!isBatchMode && (
        <>
          <div className="card">
            <div className="form-group">
              <label className="form-label">제목</label>
              <input
                type="text"
                className="form-input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="블로그 글 제목을 입력하세요"
              />
            </div>

            <div className="form-group">
              <label className="form-label">키워드 (선택사항)</label>
              <input
                type="text"
                className="form-input"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="콘텐츠에 포함할 키워드들을 쉼표로 구분하여 입력하세요"
              />
            </div>

            <div className="form-group">
              <label className="form-label">콘텐츠 작성 가이드라인</label>
              <textarea
                className="form-input"
                rows={3}
                value={guidelines}
                onChange={(e) => setGuidelines(e.target.value)}
                placeholder="콘텐츠 작성 시 고려할 가이드라인을 입력하세요"
              />
            </div>

            <div className="form-group">
              <label className="form-label">SEO & GEO 최적화 가이드라인</label>
              <textarea
                className="form-input"
                rows={3}
                value={seoGuidelines}
                onChange={(e) => setSeoGuidelines(e.target.value)}
                placeholder="SEO 최적화 및 지역 최적화 요구사항을 입력하세요"
              />
            </div>

            {error && <div className="error">{error}</div>}

            <button
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? '생성 중...' : '콘텐츠 생성'}
            </button>
          </div>

          {content && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3>생성된 콘텐츠</h3>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-secondary" onClick={copyContent}>
                    복사
                  </button>
                  <button 
                    className="btn btn-primary" 
                    onClick={() => setShowPostingPanel(true)}
                  >
                    자동 포스팅
                  </button>
                </div>
              </div>
              
              <div
                style={{
                  background: '#f8f9fa',
                  padding: '20px',
                  borderRadius: '6px',
                  border: '1px solid #ddd',
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.6',
                  maxHeight: '600px',
                  overflowY: 'auto'
                }}
              >
                {content}
              </div>
            </div>
          )}
        </>
      )}

      {/* 배치 콘텐츠 모드 */}
      {isBatchMode && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3>생성된 배치 콘텐츠 ({Object.keys(batchContent).length}개)</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button 
                className="btn btn-primary"
                onClick={() => setShowPostingPanel(true)}
                disabled={selectedContents.length === 0}
              >
                선택한 콘텐츠 자동 포스팅 ({selectedContents.length}개)
              </button>
            </div>
          </div>

          <div style={{ marginBottom: '15px', fontSize: '0.9rem', color: '#666' }}>
            💡 체크박스를 선택하여 원하는 콘텐츠를 자동 포스팅할 수 있습니다.
          </div>

          <div style={{ display: 'grid', gap: '15px' }}>
            {Object.entries(batchContent).map(([title, content]) => (
              <div 
                key={title}
                style={{
                  border: selectedContents.includes(title) ? '2px solid #007bff' : '1px solid #ddd',
                  borderRadius: '8px',
                  padding: '20px',
                  backgroundColor: selectedContents.includes(title) ? '#f8f9ff' : 'white'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '15px' }}>
                  <input
                    type="checkbox"
                    checked={selectedContents.includes(title)}
                    onChange={() => toggleContentSelection(title)}
                    style={{ marginRight: '15px', marginTop: '5px', transform: 'scale(1.2)' }}
                  />
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 10px 0', fontWeight: '600' }}>{title}</h4>
                    <div
                      style={{
                        background: '#f8f9fa',
                        padding: '15px',
                        borderRadius: '6px',
                        border: '1px solid #ddd',
                        whiteSpace: 'pre-wrap',
                        lineHeight: '1.6',
                        maxHeight: '300px',
                        overflowY: 'auto',
                        fontSize: '0.9rem'
                      }}
                    >
                      {content.substring(0, 500)}
                      {content.length > 500 && '...'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 자동 포스팅 패널 */}
      {showPostingPanel && (
        <div className="card" style={{ marginTop: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3>자동 포스팅 설정</h3>
            <button 
              className="btn btn-secondary"
              onClick={() => setShowPostingPanel(false)}
            >
              닫기
            </button>
          </div>

          {/* 플랫폼 설정 */}
          <div style={{ marginBottom: '30px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
              <h4>포스팅 플랫폼</h4>
              <div>
                <button className="btn btn-secondary" onClick={addPlatform} style={{ marginRight: '10px' }}>
                  + 플랫폼 추가
                </button>
                <button className="btn btn-primary" onClick={savePlatforms}>
                  설정 저장
                </button>
              </div>
            </div>

            {platforms.map(platform => (
              <div key={platform.id} style={{ 
                border: '1px solid #ddd', 
                borderRadius: '8px', 
                padding: '15px', 
                marginBottom: '15px',
                backgroundColor: selectedPlatforms.includes(platform.id) ? '#f8f9ff' : 'white'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '15px' }}>
                  <input
                    type="checkbox"
                    checked={selectedPlatforms.includes(platform.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedPlatforms([...selectedPlatforms, platform.id]);
                      } else {
                        setSelectedPlatforms(selectedPlatforms.filter(id => id !== platform.id));
                      }
                    }}
                    style={{ marginRight: '10px' }}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={platform.name}
                    onChange={(e) => updatePlatform(platform.id, { name: e.target.value })}
                    placeholder="플랫폼 이름"
                    style={{ marginRight: '10px', width: '200px' }}
                  />
                  <select
                    className="form-input"
                    value={platform.platform}
                    onChange={(e) => updatePlatform(platform.id, { platform: e.target.value as any })}
                    style={{ marginRight: '10px', width: '150px' }}
                  >
                    <option value="wordpress">WordPress</option>
                    <option value="blogspot">BlogSpot</option>
                    <option value="tistory">Tistory</option>
                  </select>
                  <button 
                    className="btn btn-danger"
                    onClick={() => removePlatform(platform.id)}
                  >
                    삭제
                  </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                  <input
                    type="text"
                    className="form-input"
                    value={platform.url}
                    onChange={(e) => updatePlatform(platform.id, { url: e.target.value })}
                    placeholder="블로그 URL"
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={platform.username || ''}
                    onChange={(e) => updatePlatform(platform.id, { username: e.target.value })}
                    placeholder="사용자명"
                  />
                  <input
                    type="password"
                    className="form-input"
                    value={platform.api_key || ''}
                    onChange={(e) => updatePlatform(platform.id, { api_key: e.target.value })}
                    placeholder="API 키 / 비밀번호"
                  />
                  {platform.platform === 'blogspot' && (
                    <input
                      type="text"
                      className="form-input"
                      value={platform.blog_id || ''}
                      onChange={(e) => updatePlatform(platform.id, { blog_id: e.target.value })}
                      placeholder="블로그 ID"
                    />
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* 스케줄 설정 */}
          <div style={{ marginBottom: '30px' }}>
            <h4 style={{ marginBottom: '15px' }}>예약 포스팅 설정</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
              <div>
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
                <>
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
                </>
              )}
            </div>
          </div>

          {/* 이미지 설정 */}
          <div style={{ marginBottom: '30px' }}>
            <h4 style={{ marginBottom: '15px' }}>이미지 설정</h4>
            <div>
              <label className="form-label">
                <input
                  type="checkbox"
                  checked={imageSettings.auto_generate}
                  onChange={(e) => setImageSettings({
                    ...imageSettings,
                    auto_generate: e.target.checked
                  })}
                  style={{ marginRight: '8px' }}
                />
                자동 이미지 생성
              </label>
            </div>
            
            {imageSettings.auto_generate && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px', marginTop: '15px' }}>
                <div className="form-group">
                  <label className="form-label">이미지 생성기</label>
                  <select
                    className="form-input"
                    value={imageSettings.generator}
                    onChange={(e) => setImageSettings({
                      ...imageSettings,
                      generator: e.target.value
                    })}
                  >
                    <option value="dall-e">DALL-E</option>
                    <option value="stable-diffusion">Stable Diffusion</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">이미지 스타일</label>
                  <select
                    className="form-input"
                    value={imageSettings.style}
                    onChange={(e) => setImageSettings({
                      ...imageSettings,
                      style: e.target.value
                    })}
                  >
                    <option value="blog-thumbnail">블로그 썸네일</option>
                    <option value="infographic">인포그래픽</option>
                    <option value="minimalist">미니멀</option>
                    <option value="vibrant">생동감</option>
                  </select>
                </div>
              </div>
            )}
          </div>

          {error && <div className="error" style={{ marginBottom: '20px' }}>{error}</div>}

          {/* 포스팅 실행 버튼 */}
          <div style={{ textAlign: 'center' }}>
            <button
              className="btn btn-primary btn-large"
              onClick={handleAutoPosting}
              disabled={loading || selectedPlatforms.length === 0}
            >
              {loading ? '포스팅 중...' : '자동 포스팅 시작'}
            </button>
          </div>
        </div>
      )}

      <style>{`
        .btn-large {
          padding: 12px 30px;
          font-size: 16px;
          font-weight: 600;
        }
        .btn-danger {
          background-color: #dc3545;
          color: white;
          border: 1px solid #dc3545;
        }
        .btn-danger:hover {
          background-color: #c82333;
          border-color: #bd2130;
        }
      `}</style>
    </div>
  );
};

export default ContentGenerator;