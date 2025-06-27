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
  is_active: boolean;
  auto_posting_enabled: boolean;
  posting_interval_hours: number;
  total_keywords_generated: number;
  total_titles_generated: number;
  total_posts_generated: number;
  total_posts_published: number;
  created_at: string;
  updated_at?: string;
}

interface DashboardStats {
  total_sites: number;
  active_sites: number;
  total_keywords: number;
  total_titles: number;
  total_posts: number;
  total_published: number;
  success_rate: number;
}

const BlogAutomationHub: React.FC = () => {
  const { user, token } = useAuth();
  const [sites, setSites] = useState<Site[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    total_sites: 0,
    active_sites: 0,
    total_keywords: 0,
    total_titles: 0,
    total_posts: 0,
    total_published: 0,
    success_rate: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (token) {
      loadSites();
    }
  }, [token]);

  const loadSites = async () => {
    try {
      setLoading(true);
      apiClient.setToken(token);
      
      const response = await apiClient.request<{success: boolean, data: Site[]}>('/api/sites');
      
      if (response.success) {
        setSites(response.data);
        calculateStats(response.data);
      }
    } catch (err) {
      setError('사이트 목록을 불러오는 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = (sitesData: Site[]) => {
    const stats: DashboardStats = {
      total_sites: sitesData.length,
      active_sites: sitesData.filter(s => s.is_active).length,
      total_keywords: sitesData.reduce((sum, s) => sum + s.total_keywords_generated, 0),
      total_titles: sitesData.reduce((sum, s) => sum + s.total_titles_generated, 0),
      total_posts: sitesData.reduce((sum, s) => sum + s.total_posts_generated, 0),
      total_published: sitesData.reduce((sum, s) => sum + s.total_posts_published, 0),
      success_rate: 0
    };
    
    if (stats.total_posts > 0) {
      stats.success_rate = (stats.total_published / stats.total_posts) * 100;
    }
    
    setStats(stats);
  };

  const startAutomation = (siteId: string, category: string) => {
    // AutomationWorkflow 페이지로 이동
    window.location.href = `/automation-workflow.html?site_id=${siteId}&category=${category}`;
  };

  const goToSiteManager = () => {
    window.location.href = '/site-manager.html';
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '1.5rem', marginBottom: '10px' }}>🔄</div>
          <div>사이트 정보를 불러오는 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🚀 블로그 자동화 허브</h1>
        <p className="page-description">
          AI 기반 완전 자동화 블로그 운영 시스템 - 키워드부터 포스팅까지 5분만에!
        </p>
      </div>

      {/* 통계 대시보드 */}
      <div className="card">
        <h3 style={{ marginBottom: '20px', color: '#667eea' }}>📊 오늘의 통계</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', 
          gap: '20px' 
        }}>
          <div style={{ 
            textAlign: 'center', 
            padding: '20px', 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
            borderRadius: '12px',
            color: 'white'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total_sites}</div>
            <div style={{ opacity: 0.9 }}>등록된 사이트</div>
          </div>
          <div style={{ 
            textAlign: 'center', 
            padding: '20px', 
            background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)', 
            borderRadius: '12px',
            color: 'white'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total_keywords}</div>
            <div style={{ opacity: 0.9 }}>생성된 키워드</div>
          </div>
          <div style={{ 
            textAlign: 'center', 
            padding: '20px', 
            background: 'linear-gradient(135deg, #007bff 0%, #6610f2 100%)', 
            borderRadius: '12px',
            color: 'white'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total_titles}</div>
            <div style={{ opacity: 0.9 }}>생성된 제목</div>
          </div>
          <div style={{ 
            textAlign: 'center', 
            padding: '20px', 
            background: 'linear-gradient(135deg, #fd7e14 0%, #e83e8c 100%)', 
            borderRadius: '12px',
            color: 'white'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total_posts}</div>
            <div style={{ opacity: 0.9 }}>생성된 블로그 글</div>
          </div>
          <div style={{ 
            textAlign: 'center', 
            padding: '20px', 
            background: 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)', 
            borderRadius: '12px',
            color: 'white'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.total_published}</div>
            <div style={{ opacity: 0.9 }}>자동 포스팅</div>
          </div>
          <div style={{ 
            textAlign: 'center', 
            padding: '20px', 
            background: 'linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%)', 
            borderRadius: '12px',
            color: 'white'
          }}>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>{stats.success_rate.toFixed(1)}%</div>
            <div style={{ opacity: 0.9 }}>성공률</div>
          </div>
        </div>
      </div>

      {/* 빠른 실행 버튼 */}
      <div className="card">
        <h3 style={{ marginBottom: '20px', color: '#667eea' }}>⚡ 빠른 실행</h3>
        <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
          <button 
            onClick={goToSiteManager}
            style={{
              background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
              color: 'white',
              border: 'none',
              padding: '15px 25px',
              borderRadius: '10px',
              fontSize: '1rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            🏗️ 새 사이트 등록
          </button>
          
          <button 
            onClick={() => window.location.href = '/guidelines.html'}
            style={{
              background: 'linear-gradient(135deg, #007bff 0%, #6610f2 100%)',
              color: 'white',
              border: 'none',
              padding: '15px 25px',
              borderRadius: '10px',
              fontSize: '1rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            📝 AI 지침 관리
          </button>
          
          <button 
            onClick={() => window.location.href = '/dashboard.html'}
            style={{
              background: 'linear-gradient(135deg, #fd7e14 0%, #e83e8c 100%)',
              color: 'white',
              border: 'none',
              padding: '15px 25px',
              borderRadius: '10px',
              fontSize: '1rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            📊 상세 통계
          </button>
        </div>
      </div>

      {/* 사이트 목록 */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3 style={{ color: '#667eea' }}>🌐 등록된 사이트</h3>
          <button 
            onClick={goToSiteManager}
            style={{
              background: '#667eea',
              color: 'white',
              border: 'none',
              padding: '8px 15px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.9rem'
            }}
          >
            + 사이트 추가
          </button>
        </div>

        {error && (
          <div style={{ 
            background: '#f8d7da', 
            color: '#721c24', 
            padding: '10px', 
            borderRadius: '6px', 
            marginBottom: '20px' 
          }}>
            {error}
          </div>
        )}

        {sites.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px', 
            color: '#666',
            background: '#f8f9fa',
            borderRadius: '10px',
            border: '2px dashed #ddd'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '15px' }}>🌟</div>
            <h4>첫 번째 사이트를 등록해보세요!</h4>
            <p style={{ marginBottom: '20px' }}>
              AI 자동화로 블로그 운영을 시작하려면 먼저 사이트를 등록해야 합니다.
            </p>
            <button 
              onClick={goToSiteManager}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                padding: '12px 24px',
                borderRadius: '8px',
                fontSize: '1rem',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              🚀 첫 사이트 등록하기
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '20px' }}>
            {sites.map((site) => (
              <div 
                key={site.id}
                style={{
                  border: site.is_active ? '2px solid #28a745' : '2px solid #ddd',
                  borderRadius: '12px',
                  padding: '20px',
                  background: site.is_active ? '#f8fff8' : '#f8f9fa',
                  position: 'relative'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                      <h4 style={{ margin: '0 10px 0 0', color: '#333' }}>
                        {site.is_active ? '✅' : '⏸️'} {site.name}
                      </h4>
                      <span style={{
                        background: site.category === '여행' ? '#007bff' : 
                                   site.category === '맛집' ? '#28a745' :
                                   site.category === 'IT' ? '#6f42c1' : '#fd7e14',
                        color: 'white',
                        padding: '3px 8px',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: 'bold'
                      }}>
                        {site.category}
                      </span>
                    </div>
                    
                    <div style={{ color: '#666', fontSize: '0.9rem', marginBottom: '10px' }}>
                      <div>{site.description}</div>
                      <div style={{ marginTop: '5px' }}>
                        🌐 <a href={site.url} target="_blank" rel="noopener noreferrer" style={{ color: '#667eea' }}>
                          {site.url}
                        </a>
                      </div>
                      {site.wordpress_url && (
                        <div style={{ marginTop: '5px' }}>
                          📝 WordPress: {site.wordpress_url}
                        </div>
                      )}
                    </div>

                    {/* 사이트 통계 */}
                    <div style={{ 
                      display: 'flex', 
                      gap: '20px', 
                      fontSize: '0.85rem',
                      color: '#666',
                      marginBottom: '15px'
                    }}>
                      <span>🎯 키워드: <strong>{site.total_keywords_generated}</strong></span>
                      <span>📝 제목: <strong>{site.total_titles_generated}</strong></span>
                      <span>📄 블로그: <strong>{site.total_posts_generated}</strong></span>
                      <span>📤 포스팅: <strong>{site.total_posts_published}</strong></span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '10px', flexDirection: 'column' }}>
                    {site.is_active && (
                      <button
                        onClick={() => startAutomation(site.id, site.category)}
                        style={{
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          border: 'none',
                          padding: '10px 20px',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontWeight: 'bold',
                          fontSize: '0.9rem',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        🚀 자동화 시작
                      </button>
                    )}
                    
                    <button
                      onClick={() => window.location.href = `/site-manager.html?edit=${site.id}`}
                      style={{
                        background: '#6c757d',
                        color: 'white',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      ⚙️ 설정
                    </button>
                  </div>
                </div>

                {/* 자동 포스팅 상태 */}
                {site.auto_posting_enabled && (
                  <div style={{
                    position: 'absolute',
                    top: '10px',
                    right: '10px',
                    background: '#28a745',
                    color: 'white',
                    padding: '4px 8px',
                    borderRadius: '12px',
                    fontSize: '0.7rem',
                    fontWeight: 'bold'
                  }}>
                    🤖 자동포스팅 ON
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BlogAutomationHub;