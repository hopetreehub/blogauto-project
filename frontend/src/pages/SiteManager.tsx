import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/api';

interface Site {
  id: string;
  name: string;
  url: string;
  description: string;
  category: string;
  wordpress_url?: string;
  wordpress_username?: string;
  keyword_guideline_id?: string;
  title_guideline_id?: string;
  blog_guideline_id?: string;
  is_active: boolean;
  auto_posting_enabled: boolean;
  posting_interval_hours: number;
  created_at: string;
  updated_at?: string;
}

interface Guideline {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  is_default: boolean;
}

interface Guidelines {
  keyword_analysis: Guideline[];
  title_generation: Guideline[];
  blog_writing: Guideline[];
}

const SiteManager: React.FC = () => {
  const { token } = useAuth();
  const [sites, setSites] = useState<Site[]>([]);
  const [guidelines, setGuidelines] = useState<Guidelines>({
    keyword_analysis: [],
    title_generation: [],
    blog_writing: []
  });
  const [editingSite, setEditingSite] = useState<Site | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [testingConnection, setTestingConnection] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    description: '',
    category: '여행',
    wordpress_url: '',
    wordpress_username: '',
    wordpress_password: '',
    keyword_guideline_id: '',
    title_guideline_id: '',
    blog_guideline_id: '',
    auto_posting_enabled: false,
    posting_interval_hours: 24
  });

  const categories = [
    '여행', '맛집', '패션', 'IT', '건강', '라이프스타일', '금융', '교육'
  ];

  useEffect(() => {
    if (token) {
      loadData();
    }
    
    // URL에서 편집할 사이트 ID 확인
    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get('edit');
    if (editId) {
      // 사이트 목록이 로드된 후 편집 모드로 전환
      setTimeout(() => {
        const site = sites.find(s => s.id === editId);
        if (site) {
          handleEdit(site);
        }
      }, 1000);
    }
  }, [token]);

  const loadData = async () => {
    try {
      setLoading(true);
      apiClient.setToken(token);
      
      // 사이트 목록과 지침 목록을 병렬로 로드
      const [sitesResponse, guidelinesResponse] = await Promise.all([
        apiClient.request<{success: boolean, data: Site[]}>('/api/sites'),
        apiClient.request<{success: boolean, data: Guidelines}>('/api/sites/guidelines/available')
      ]);
      
      if (sitesResponse.success) {
        setSites(sitesResponse.data);
      }
      
      if (guidelinesResponse.success) {
        setGuidelines(guidelinesResponse.data);
      }
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      apiClient.setToken(token);
      
      if (editingSite) {
        // 사이트 수정
        const response = await apiClient.request(`/api/sites/${editingSite.id}`, {
          method: 'PUT',
          body: JSON.stringify(formData)
        });
        
        setSuccess('사이트가 성공적으로 수정되었습니다.');
        setEditingSite(null);
      } else {
        // 새 사이트 생성
        const response = await apiClient.request('/api/sites', {
          method: 'POST',
          body: JSON.stringify(formData)
        });
        
        setSuccess('사이트가 성공적으로 등록되었습니다.');
        setIsCreating(false);
      }
      
      // 폼 초기화
      setFormData({
        name: '',
        url: '',
        description: '',
        category: '여행',
        wordpress_url: '',
        wordpress_username: '',
        wordpress_password: '',
        keyword_guideline_id: '',
        title_guideline_id: '',
        blog_guideline_id: '',
        auto_posting_enabled: false,
        posting_interval_hours: 24
      });
      
      // 목록 새로고침
      loadData();
      
    } catch (err) {
      setError('저장 중 오류가 발생했습니다.');
      console.error(err);
    }
  };

  const handleEdit = (site: Site) => {
    setEditingSite(site);
    setIsCreating(false);
    setFormData({
      name: site.name,
      url: site.url,
      description: site.description || '',
      category: site.category,
      wordpress_url: site.wordpress_url || '',
      wordpress_username: site.wordpress_username || '',
      wordpress_password: '', // 보안상 비밀번호는 비워둠
      keyword_guideline_id: site.keyword_guideline_id || '',
      title_guideline_id: site.title_guideline_id || '',
      blog_guideline_id: site.blog_guideline_id || '',
      auto_posting_enabled: site.auto_posting_enabled,
      posting_interval_hours: site.posting_interval_hours
    });
  };

  const handleDelete = async (siteId: string, siteName: string) => {
    if (!confirm(`정말로 "${siteName}" 사이트를 삭제하시겠습니까?`)) {
      return;
    }

    try {
      apiClient.setToken(token);
      await apiClient.request(`/api/sites/${siteId}`, {
        method: 'DELETE'
      });
      
      setSuccess('사이트가 성공적으로 삭제되었습니다.');
      loadData();
    } catch (err) {
      setError('사이트 삭제 중 오류가 발생했습니다.');
      console.error(err);
    }
  };

  const testWordPressConnection = async () => {
    if (!formData.wordpress_url || !formData.wordpress_username || !formData.wordpress_password) {
      setError('WordPress URL, 사용자명, 비밀번호를 모두 입력해주세요.');
      return;
    }

    setTestingConnection(true);
    setError('');

    try {
      apiClient.setToken(token);
      const response = await apiClient.request('/api/sites/test-wordpress', {
        method: 'POST',
        body: JSON.stringify({
          wordpress_url: formData.wordpress_url,
          username: formData.wordpress_username,
          password: formData.wordpress_password
        })
      }) as any;

      if (response.success) {
        setSuccess(`WordPress 연결 성공! 사용자: ${response.user_info?.name || 'Unknown'}`);
      } else {
        setError(`WordPress 연결 실패: ${response.message}`);
      }
    } catch (err) {
      setError('WordPress 연결 테스트 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setTestingConnection(false);
    }
  };

  const startCreate = () => {
    setIsCreating(true);
    setEditingSite(null);
    setFormData({
      name: '',
      url: '',
      description: '',
      category: '여행',
      wordpress_url: '',
      wordpress_username: '',
      wordpress_password: '',
      keyword_guideline_id: '',
      title_guideline_id: '',
      blog_guideline_id: '',
      auto_posting_enabled: false,
      posting_interval_hours: 24
    });
  };

  const cancelEdit = () => {
    setIsCreating(false);
    setEditingSite(null);
    setFormData({
      name: '',
      url: '',
      description: '',
      category: '여행',
      wordpress_url: '',
      wordpress_username: '',
      wordpress_password: '',
      keyword_guideline_id: '',
      title_guideline_id: '',
      blog_guideline_id: '',
      auto_posting_enabled: false,
      posting_interval_hours: 24
    });
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '10px' }}>🔄</div>
          <div>데이터를 불러오는 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🏗️ 사이트 관리</h1>
        <p className="page-description">
          블로그 사이트 등록 및 WordPress 연동 설정
        </p>
      </div>

      {/* 알림 메시지 */}
      {error && (
        <div style={{ 
          background: '#f8d7da', 
          color: '#721c24', 
          padding: '12px', 
          borderRadius: '6px', 
          marginBottom: '20px',
          border: '1px solid #f5c6cb'
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
          marginBottom: '20px',
          border: '1px solid #c3e6cb'
        }}>
          ✅ {success}
        </div>
      )}

      {/* 사이트 생성/편집 폼 */}
      {(isCreating || editingSite) && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3>{editingSite ? '사이트 편집' : '새 사이트 등록'}</h3>
            <button 
              onClick={cancelEdit}
              style={{
                background: '#6c757d',
                color: 'white',
                border: 'none',
                padding: '8px 15px',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              취소
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
              {/* 기본 정보 */}
              <div>
                <h4>📋 기본 정보</h4>
                
                <div className="form-group">
                  <label className="form-label">사이트 이름 *</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="예: 제주도 여행 블로그"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">사이트 URL *</label>
                  <input
                    type="url"
                    className="form-input"
                    value={formData.url}
                    onChange={(e) => setFormData({...formData, url: e.target.value})}
                    placeholder="https://my-blog.com"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">카테고리 *</label>
                  <select
                    className="form-input"
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    required
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">설명</label>
                  <textarea
                    className="form-input"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    placeholder="사이트에 대한 간단한 설명"
                    rows={3}
                  />
                </div>
              </div>

              {/* WordPress 연동 */}
              <div>
                <h4>📝 WordPress 연동</h4>
                
                <div className="form-group">
                  <label className="form-label">WordPress URL</label>
                  <input
                    type="url"
                    className="form-input"
                    value={formData.wordpress_url}
                    onChange={(e) => setFormData({...formData, wordpress_url: e.target.value})}
                    placeholder="https://my-blog.com"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">WordPress 사용자명</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.wordpress_username}
                    onChange={(e) => setFormData({...formData, wordpress_username: e.target.value})}
                    placeholder="admin"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">WordPress 비밀번호</label>
                  <input
                    type="password"
                    className="form-input"
                    value={formData.wordpress_password}
                    onChange={(e) => setFormData({...formData, wordpress_password: e.target.value})}
                    placeholder={editingSite ? "변경하려면 입력하세요" : "비밀번호"}
                  />
                </div>

                <button
                  type="button"
                  onClick={testWordPressConnection}
                  disabled={testingConnection}
                  style={{
                    background: testingConnection ? '#6c757d' : '#007bff',
                    color: 'white',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    cursor: testingConnection ? 'not-allowed' : 'pointer',
                    width: '100%'
                  }}
                >
                  {testingConnection ? '🔄 연결 테스트 중...' : '🔗 WordPress 연결 테스트'}
                </button>
              </div>

              {/* AI 지침 설정 */}
              <div>
                <h4>🤖 AI 지침 설정</h4>
                
                <div className="form-group">
                  <label className="form-label">키워드 분석 지침</label>
                  <select
                    className="form-input"
                    value={formData.keyword_guideline_id}
                    onChange={(e) => setFormData({...formData, keyword_guideline_id: e.target.value})}
                  >
                    <option value="">기본 지침 사용</option>
                    {guidelines.keyword_analysis.map(g => (
                      <option key={g.id} value={g.id}>
                        {g.name} {g.is_default ? '(기본)' : ''}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">제목 생성 지침</label>
                  <select
                    className="form-input"
                    value={formData.title_guideline_id}
                    onChange={(e) => setFormData({...formData, title_guideline_id: e.target.value})}
                  >
                    <option value="">기본 지침 사용</option>
                    {guidelines.title_generation.map(g => (
                      <option key={g.id} value={g.id}>
                        {g.name} {g.is_default ? '(기본)' : ''}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">블로그 글쓰기 지침</label>
                  <select
                    className="form-input"
                    value={formData.blog_guideline_id}
                    onChange={(e) => setFormData({...formData, blog_guideline_id: e.target.value})}
                  >
                    <option value="">기본 지침 사용</option>
                    {guidelines.blog_writing.map(g => (
                      <option key={g.id} value={g.id}>
                        {g.name} {g.is_default ? '(기본)' : ''}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* 자동화 설정 */}
              <div>
                <h4>⚙️ 자동화 설정</h4>
                
                <div className="form-group">
                  <label className="form-label">
                    <input
                      type="checkbox"
                      checked={formData.auto_posting_enabled}
                      onChange={(e) => setFormData({...formData, auto_posting_enabled: e.target.checked})}
                      style={{ marginRight: '8px' }}
                    />
                    자동 포스팅 활성화
                  </label>
                </div>

                {formData.auto_posting_enabled && (
                  <div className="form-group">
                    <label className="form-label">포스팅 간격 (시간)</label>
                    <select
                      className="form-input"
                      value={formData.posting_interval_hours}
                      onChange={(e) => setFormData({...formData, posting_interval_hours: parseInt(e.target.value)})}
                    >
                      <option value={1}>1시간</option>
                      <option value={6}>6시간</option>
                      <option value={12}>12시간</option>
                      <option value={24}>24시간</option>
                      <option value={48}>48시간</option>
                      <option value={72}>72시간</option>
                    </select>
                  </div>
                )}
              </div>
            </div>

            <div style={{ marginTop: '30px', textAlign: 'center' }}>
              <button
                type="submit"
                style={{
                  background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '15px 30px',
                  borderRadius: '8px',
                  fontSize: '1.1rem',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                {editingSite ? '💾 변경사항 저장' : '🚀 사이트 등록'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 사이트 목록 */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>등록된 사이트 ({sites.length}개)</h3>
          {!isCreating && !editingSite && (
            <button 
              onClick={startCreate}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              + 새 사이트 등록
            </button>
          )}
        </div>

        {sites.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px', 
            color: '#666',
            background: '#f8f9fa',
            borderRadius: '10px',
            border: '2px dashed #ddd'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📝</div>
            <h4>등록된 사이트가 없습니다</h4>
            <p>첫 번째 사이트를 등록하여 자동화를 시작해보세요!</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '15px' }}>
            {sites.map((site) => (
              <div 
                key={site.id}
                style={{
                  border: site.is_active ? '2px solid #28a745' : '2px solid #ddd',
                  borderRadius: '12px',
                  padding: '20px',
                  background: site.is_active ? '#f8fff8' : '#f8f9fa'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 8px 0', color: '#333' }}>
                      {site.is_active ? '✅' : '⏸️'} {site.name}
                    </h4>
                    
                    <div style={{ color: '#666', fontSize: '0.9rem', marginBottom: '10px' }}>
                      <div><strong>카테고리:</strong> {site.category}</div>
                      <div><strong>URL:</strong> 
                        <a href={site.url} target="_blank" rel="noopener noreferrer" style={{ color: '#667eea', marginLeft: '5px' }}>
                          {site.url}
                        </a>
                      </div>
                      {site.wordpress_url && (
                        <div><strong>WordPress:</strong> {site.wordpress_url}</div>
                      )}
                      <div><strong>등록일:</strong> {new Date(site.created_at).toLocaleDateString()}</div>
                    </div>

                    {site.description && (
                      <div style={{ color: '#555', fontSize: '0.9rem', fontStyle: 'italic' }}>
                        {site.description}
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={() => handleEdit(site)}
                      style={{
                        background: '#007bff',
                        color: 'white',
                        border: 'none',
                        padding: '8px 15px',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.9rem'
                      }}
                    >
                      ✏️ 편집
                    </button>
                    
                    <button
                      onClick={() => handleDelete(site.id, site.name)}
                      style={{
                        background: '#dc3545',
                        color: 'white',
                        border: 'none',
                        padding: '8px 15px',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.9rem'
                      }}
                    >
                      🗑️ 삭제
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SiteManager;