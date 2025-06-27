import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/api';

interface PromptSummary {
  [key: string]: {
    total_count: number;
    active_count: number;
    default_prompt: {
      id: string | null;
      name: string;
      version: string;
    };
  };
}

interface Prompt {
  id: string;
  name: string;
  description: string;
  prompt_content: string;
  is_default: boolean;
  version: string;
  created_at: string;
  updated_at: string;
}

const AdminPanel: React.FC = () => {
  const { token } = useAuth();
  const [summary, setSummary] = useState<PromptSummary | null>(null);
  const [selectedType, setSelectedType] = useState<string>('keyword_analysis');
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [showEditor, setShowEditor] = useState(false);
  const [editMode, setEditMode] = useState<'create' | 'edit'>('create');

  const promptTypeLabels = {
    'keyword_analysis': '키워드 분석',
    'title_generation': '제목 생성',
    'blog_writing': '블로그 글쓰기'
  };

  useEffect(() => {
    loadSummary();
  }, []);

  useEffect(() => {
    if (selectedType) {
      loadPromptsByType(selectedType);
    }
  }, [selectedType]);

  const loadSummary = async () => {
    try {
      apiClient.setToken(token);
      const response = await apiClient.getPromptsSummary();
      setSummary(response.data);
    } catch (err) {
      setError('요약 정보를 불러오는데 실패했습니다.');
      console.error(err);
    }
  };

  const loadPromptsByType = async (type: string) => {
    setLoading(true);
    try {
      apiClient.setToken(token);
      const response = await apiClient.getPromptsByType(type);
      setPrompts(response.data.prompts);
    } catch (err) {
      setError('지침을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePrompt = () => {
    setSelectedPrompt({
      id: '',
      name: '',
      description: '',
      prompt_content: '',
      is_default: false,
      version: '1.0',
      created_at: '',
      updated_at: ''
    });
    setEditMode('create');
    setShowEditor(true);
  };

  const handleEditPrompt = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setEditMode('edit');
    setShowEditor(true);
  };

  const handleSavePrompt = async () => {
    if (!selectedPrompt) return;

    try {
      apiClient.setToken(token);
      
      const promptData = {
        name: selectedPrompt.name,
        description: selectedPrompt.description,
        prompt_content: selectedPrompt.prompt_content,
        prompt_type: selectedType,
        is_default: selectedPrompt.is_default,
        version: selectedPrompt.version
      };

      if (editMode === 'create') {
        await apiClient.createPrompt(promptData);
      } else {
        await apiClient.updatePrompt(selectedPrompt.id, promptData);
      }

      setShowEditor(false);
      loadPromptsByType(selectedType);
      loadSummary();
      alert(`지침이 성공적으로 ${editMode === 'create' ? '생성' : '수정'}되었습니다.`);
    } catch (err) {
      setError(`지침 ${editMode === 'create' ? '생성' : '수정'}에 실패했습니다.`);
      console.error(err);
    }
  };

  const handleDeletePrompt = async (promptId: string) => {
    if (!confirm('정말로 이 지침을 삭제하시겠습니까?')) return;

    try {
      apiClient.setToken(token);
      await apiClient.deletePrompt(promptId);
      loadPromptsByType(selectedType);
      loadSummary();
      alert('지침이 성공적으로 삭제되었습니다.');
    } catch (err) {
      setError('지침 삭제에 실패했습니다.');
      console.error(err);
    }
  };

  const handleExport = async () => {
    try {
      apiClient.setToken(token);
      const response = await apiClient.exportPrompts(selectedType);
      
      const dataStr = JSON.stringify(response.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `prompts_${selectedType}_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('내보내기에 실패했습니다.');
      console.error(err);
    }
  };

  const handleImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const importData = JSON.parse(text);
      
      apiClient.setToken(token);
      const response = await apiClient.importPrompts(importData);
      
      loadPromptsByType(selectedType);
      loadSummary();
      alert(`${response.data.imported_count}개의 지침이 성공적으로 가져왔습니다.`);
    } catch (err) {
      setError('가져오기에 실패했습니다.');
      console.error(err);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">⚙️ 관리자 패널 - 지침 관리</h1>
        <p className="page-description">키워드 분석, 제목 생성, 블로그 글쓰기 지침을 통합 관리합니다</p>
      </div>

      {/* 요약 정보 */}
      {summary && (
        <div className="card">
          <h3>📊 지침 현황 요약</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
            {Object.entries(summary).map(([type, data]) => (
              <div key={type} style={{
                padding: '20px',
                background: selectedType === type ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#f8f9fa',
                color: selectedType === type ? 'white' : '#333',
                borderRadius: '12px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }} onClick={() => setSelectedType(type)}>
                <h4 style={{ margin: '0 0 10px 0' }}>{promptTypeLabels[type as keyof typeof promptTypeLabels]}</h4>
                <div style={{ fontSize: '0.9rem', opacity: 0.9 }}>
                  <div>총 {data.total_count}개 지침</div>
                  <div>활성 {data.active_count}개</div>
                  <div>기본: {data.default_prompt.name}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 지침 관리 */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>📝 {promptTypeLabels[selectedType as keyof typeof promptTypeLabels]} 지침 관리</h3>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              className="btn btn-secondary"
              onClick={handleExport}
              style={{ padding: '8px 16px' }}
            >
              📤 내보내기
            </button>
            <label className="btn btn-secondary" style={{ padding: '8px 16px', margin: 0 }}>
              📥 가져오기
              <input
                type="file"
                accept=".json"
                onChange={handleImport}
                style={{ display: 'none' }}
              />
            </label>
            <button
              className="btn btn-primary"
              onClick={handleCreatePrompt}
              style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
            >
              ➕ 새 지침 생성
            </button>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>로딩 중...</div>
        ) : (
          <div style={{ display: 'grid', gap: '15px' }}>
            {prompts.map((prompt) => (
              <div key={prompt.id} style={{
                padding: '20px',
                border: prompt.is_default ? '3px solid #667eea' : '2px solid #e0e0e0',
                borderRadius: '12px',
                background: prompt.is_default ? 'linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%)' : 'white'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                      <h4 style={{ margin: 0, color: prompt.is_default ? '#667eea' : '#333' }}>
                        {prompt.is_default && '👑 '}{prompt.name}
                      </h4>
                      <span style={{
                        background: '#28a745',
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '0.7rem'
                      }}>
                        v{prompt.version}
                      </span>
                    </div>
                    <p style={{ margin: '0 0 10px 0', color: '#666', fontSize: '0.9rem' }}>
                      {prompt.description}
                    </p>
                    <div style={{
                      background: '#f8f9fa',
                      padding: '10px',
                      borderRadius: '6px',
                      fontSize: '0.8rem',
                      color: '#666',
                      maxHeight: '100px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis'
                    }}>
                      {prompt.prompt_content.substring(0, 200)}...
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', marginLeft: '20px' }}>
                    <button
                      onClick={() => handleEditPrompt(prompt)}
                      style={{
                        background: 'none',
                        border: '1px solid #007bff',
                        color: '#007bff',
                        padding: '6px 12px',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.8rem'
                      }}
                    >
                      ✏️ 수정
                    </button>
                    {!prompt.is_default && (
                      <button
                        onClick={() => handleDeletePrompt(prompt.id)}
                        style={{
                          background: 'none',
                          border: '1px solid #dc3545',
                          color: '#dc3545',
                          padding: '6px 12px',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.8rem'
                        }}
                      >
                        🗑️ 삭제
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 지침 편집 모달 */}
      {showEditor && selectedPrompt && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            padding: '30px',
            borderRadius: '12px',
            width: '90%',
            maxWidth: '800px',
            maxHeight: '90vh',
            overflow: 'auto'
          }}>
            <h3 style={{ marginTop: 0 }}>
              {editMode === 'create' ? '새 지침 생성' : '지침 수정'}
            </h3>

            <div className="form-group">
              <label className="form-label">지침 이름</label>
              <input
                type="text"
                className="form-input"
                value={selectedPrompt.name}
                onChange={(e) => setSelectedPrompt({
                  ...selectedPrompt,
                  name: e.target.value
                })}
                placeholder="지침의 이름을 입력하세요"
              />
            </div>

            <div className="form-group">
              <label className="form-label">설명</label>
              <input
                type="text"
                className="form-input"
                value={selectedPrompt.description}
                onChange={(e) => setSelectedPrompt({
                  ...selectedPrompt,
                  description: e.target.value
                })}
                placeholder="지침에 대한 간단한 설명을 입력하세요"
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div className="form-group">
                <label className="form-label">버전</label>
                <input
                  type="text"
                  className="form-input"
                  value={selectedPrompt.version}
                  onChange={(e) => setSelectedPrompt({
                    ...selectedPrompt,
                    version: e.target.value
                  })}
                  placeholder="1.0"
                />
              </div>

              <div className="form-group">
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <input
                    type="checkbox"
                    checked={selectedPrompt.is_default}
                    onChange={(e) => setSelectedPrompt({
                      ...selectedPrompt,
                      is_default: e.target.checked
                    })}
                  />
                  기본 지침으로 설정
                </label>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">지침 내용</label>
              <textarea
                className="form-input"
                rows={15}
                value={selectedPrompt.prompt_content}
                onChange={(e) => setSelectedPrompt({
                  ...selectedPrompt,
                  prompt_content: e.target.value
                })}
                placeholder="AI가 따라야 할 상세한 지침을 입력하세요..."
                style={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setShowEditor(false)}
                style={{
                  background: 'none',
                  border: '1px solid #ddd',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                취소
              </button>
              <button
                onClick={handleSavePrompt}
                style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                {editMode === 'create' ? '생성' : '저장'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;