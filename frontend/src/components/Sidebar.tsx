import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const mainMenuItems = [
    { path: '/', label: '블로그 자동화 허브', icon: '🚀' },
    { path: '/site-manager.html', label: '사이트 관리', icon: '🏗️' },
    { path: '/dashboard.html', label: '통계 대시보드', icon: '📊' },
  ];

  const legacyMenuItems = [
    { path: '/titles.html', label: '제목 생성', icon: '✍️' },
    { path: '/content.html', label: '콘텐츠 생성', icon: '📝' },
  ];

  const adminMenuItems = [
    { path: '/admin.html', label: '관리자 패널', icon: '⚙️' },
    { path: '/guidelines.html', label: 'AI 지침 관리', icon: '📝' },
  ];

  const settingsMenuItems = [
    { path: '/settings.html', label: '설정', icon: '🔧' },
  ];

  // 사용자 권한에 따라 메뉴 구성
  const menuItems = [
    ...mainMenuItems,
    ...(user?.is_admin ? adminMenuItems : []),
    ...legacyMenuItems,
    ...settingsMenuItems
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Blog Auto</h2>
        {user && (
          <div className="user-info">
            <span>안녕하세요, {user.username}님</span>
          </div>
        )}
      </div>
      <nav className="sidebar-nav">
        {/* 메인 자동화 메뉴 */}
        <div className="menu-section">
          <h4 className="menu-section-title">🤖 자동화 시스템</h4>
          {mainMenuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </div>

        {/* 관리자 메뉴 */}
        {user?.is_admin && (
          <div className="menu-section">
            <h4 className="menu-section-title">⚙️ 관리</h4>
            {adminMenuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </Link>
            ))}
          </div>
        )}

        {/* 레거시 도구 */}
        <div className="menu-section">
          <h4 className="menu-section-title">🔧 개별 도구</h4>
          {legacyMenuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </div>

        {/* 설정 메뉴 */}
        <div className="menu-section">
          {settingsMenuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>
      <div className="sidebar-footer">
        <button className="logout-btn" onClick={logout}>
          <span className="nav-icon">🚪</span>
          <span className="nav-label">로그아웃</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;