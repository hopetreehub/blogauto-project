import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">대시보드</h1>
        <p className="page-description">블로그 자동화 프로세스 개요</p>
      </div>

      <div className="card">
        <h3>프로젝트 상태</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '20px' }}>
          <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>🔍</div>
            <h4>키워드 분석</h4>
            <p>0개 처리됨</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>✍️</div>
            <h4>제목 생성</h4>
            <p>0개 생성됨</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>📝</div>
            <h4>콘텐츠 생성</h4>
            <p>0개 생성됨</p>
          </div>
          <div style={{ textAlign: 'center', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>📊</div>
            <h4>포스팅 완료</h4>
            <p>0개 발행됨</p>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>최근 활동</h3>
        <p>아직 활동 기록이 없습니다.</p>
      </div>
    </div>
  );
};

export default Dashboard;