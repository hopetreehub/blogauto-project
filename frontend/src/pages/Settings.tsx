import React, { useState } from 'react';

const Settings: React.FC = () => {
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    gemini: '',
    semrush: '',
    ahrefs: ''
  });
  
  const [preferences, setPreferences] = useState({
    language: 'ko',
    defaultTone: 'professional',
    autoSave: true
  });

  const handleSave = () => {
    // TODO: 설정 저장 API 호출
    alert('설정이 저장되었습니다.');
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">설정</h1>
        <p className="page-description">API 키 및 기본 설정 관리</p>
      </div>

      <div className="card">
        <h3>API 키 설정</h3>
        <div className="form-group">
          <label className="form-label">OpenAI API Key</label>
          <input
            type="password"
            className="form-input"
            value={apiKeys.openai}
            onChange={(e) => setApiKeys({...apiKeys, openai: e.target.value})}
            placeholder="OpenAI API 키를 입력하세요"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Gemini API Key</label>
          <input
            type="password"
            className="form-input"
            value={apiKeys.gemini}
            onChange={(e) => setApiKeys({...apiKeys, gemini: e.target.value})}
            placeholder="Gemini API 키를 입력하세요"
          />
        </div>

        <div className="form-group">
          <label className="form-label">SEMrush API Key</label>
          <input
            type="password"
            className="form-input"
            value={apiKeys.semrush}
            onChange={(e) => setApiKeys({...apiKeys, semrush: e.target.value})}
            placeholder="SEMrush API 키를 입력하세요"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Ahrefs API Key</label>
          <input
            type="password"
            className="form-input"
            value={apiKeys.ahrefs}
            onChange={(e) => setApiKeys({...apiKeys, ahrefs: e.target.value})}
            placeholder="Ahrefs API 키를 입력하세요"
          />
        </div>
      </div>

      <div className="card">
        <h3>기본 설정</h3>
        <div className="form-group">
          <label className="form-label">기본 언어</label>
          <select
            className="form-input"
            value={preferences.language}
            onChange={(e) => setPreferences({...preferences, language: e.target.value})}
          >
            <option value="ko">한국어</option>
            <option value="en">English</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">기본 톤</label>
          <select
            className="form-input"
            value={preferences.defaultTone}
            onChange={(e) => setPreferences({...preferences, defaultTone: e.target.value})}
          >
            <option value="professional">전문적</option>
            <option value="casual">캐주얼</option>
            <option value="exciting">흥미진진</option>
          </select>
        </div>

        <div className="form-group">
          <label style={{ display: 'flex', alignItems: 'center' }}>
            <input
              type="checkbox"
              checked={preferences.autoSave}
              onChange={(e) => setPreferences({...preferences, autoSave: e.target.checked})}
              style={{ marginRight: '8px' }}
            />
            자동 저장
          </label>
        </div>
      </div>

      <button className="btn btn-primary" onClick={handleSave}>
        설정 저장
      </button>
    </div>
  );
};

export default Settings;