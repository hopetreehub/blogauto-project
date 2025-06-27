import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/api';

interface Guideline {
  id: string;
  type: 'keyword' | 'title' | 'blog';
  name: string;
  prompt: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const GuidelinesManager: React.FC = () => {
  const { user, token } = useAuth();
  const [guidelines, setGuidelines] = useState<Guideline[]>([]);
  const [selectedType, setSelectedType] = useState<'keyword' | 'title' | 'blog'>('keyword');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingGuideline, setEditingGuideline] = useState<Guideline | null>(null);
  const [newGuideline, setNewGuideline] = useState<{
    name: string;
    prompt: string;
    type: 'keyword' | 'title' | 'blog';
  }>({
    name: '',
    prompt: '',
    type: 'keyword'
  });

  // 지침 불러오기
  const fetchGuidelines = async () => {
    setLoading(true);
    try {
      if (!token) return;
      apiClient.setToken(token);
      const response = await apiClient.getPromptsByType(selectedType);
      setGuidelines(response.data || []);
    } catch (err) {
      setError('지침을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGuidelines();
  }, [selectedType, token]);

  // 새 지침 저장
  const handleSaveNew = async () => {
    if (!newGuideline.name || !newGuideline.prompt) {
      setError('이름과 프롬프트를 모두 입력해주세요.');
      return;
    }

    try {
      const response = await apiClient.createPrompt({
        prompt_name: newGuideline.name,
        prompt_type: selectedType,
        prompt_content: newGuideline.prompt,
        is_active: true
      });
      
      setNewGuideline({ name: '', prompt: '', type: selectedType as 'keyword' | 'title' | 'blog' });
      fetchGuidelines();
      setError('');
    } catch (err) {
      setError('지침 저장 중 오류가 발생했습니다.');
    }
  };

  // 지침 수정
  const handleUpdate = async (guideline: Guideline) => {
    try {
      await apiClient.updatePrompt(guideline.id, {
        prompt_name: guideline.name,
        prompt_content: guideline.prompt,
        is_active: guideline.is_active
      });
      
      setEditingGuideline(null);
      fetchGuidelines();
      setError('');
    } catch (err) {
      setError('지침 수정 중 오류가 발생했습니다.');
    }
  };

  // 지침 삭제
  const handleDelete = async (id: string) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    
    try {
      await apiClient.deletePrompt(id);
      fetchGuidelines();
    } catch (err) {
      setError('지침 삭제 중 오류가 발생했습니다.');
    }
  };

  // 기본 지침 템플릿
  const getDefaultTemplate = (type: string) => {
    switch (type) {
      case 'keyword':
        return `# SEO 키워드 분석 지침

당신은 전문 SEO 키워드 분석가입니다. 주어진 아이템과 카테고리를 분석하여 Google과 Naver에서 상위 노출될 수 있는 최적의 키워드를 제안해주세요.

## 분석 기준:
1. 검색량 (월 평균 검색 횟수)
2. 경쟁 강도 (낮음/보통/높음)  
3. 상업적 의도 (구매 의도가 있는 키워드 우선)
4. 계절성 (특정 시기에 검색량이 급증하는지)
5. 롱테일 키워드 포함

## 결과 형식:
각 키워드마다 다음 정보를 제공:
- 키워드
- 예상 월간 검색량
- 경쟁도 (낮음/보통/높음)
- 추천 이유
- SEO 점수 (1-100)

최대 15개의 키워드를 제안해주세요.`;

      case 'title':
        return `# 바이럴 블로그 제목 생성 지침

당신은 클릭률이 높은 바이럴 제목을 만드는 전문가입니다. 주어진 키워드로 사람들이 반드시 클릭하고 싶어하는 매력적인 제목을 생성해주세요.

## 제목 생성 원칙:
1. 호기심 유발: "몰랐던", "숨겨진", "의외의" 등 사용
2. 긴급성 표현: "지금", "당장", "마지막" 등 사용  
3. 감정 자극: "놀라운", "충격적인", "감동적인" 등 사용
4. 숫자 활용: "10가지", "3분만에", "100% 효과" 등
5. 개인화: "당신의", "나만의", "여러분의" 등 사용

## 형식 유형:
- 질문형: "~해야 할까?"
- 리스트형: "~가지 방법"
- How-to형: "~하는 법"
- 비교형: "~vs~"
- 결과형: "~한 결과"

## 최적화 요소:
- 제목 길이: 30-60자 권장
- SEO 키워드 자연스럽게 포함
- 클릭 유도 요소 포함
- 중복률 최소화

각 제목마다 SEO 점수, 클릭 점수, 바이럴 점수를 1-100으로 평가해주세요.`;

      case 'blog':
        return `# SEO+GEO 최적화 블로그 글쓰기 지침

당신은 SEO와 GEO(Generative Engine Optimization)를 완벽하게 이해하는 전문 블로거입니다. AI 시대에 맞는 최적화된 블로그 글을 작성해주세요.

## SEO 최적화 요소:
1. 키워드 밀도: 메인 키워드 1-2%, LSI 키워드 자연스럽게 배치
2. 제목 태그: H1, H2, H3 구조적 사용
3. 메타 설명: 검색 결과에 표시될 요약문 포함
4. 내부 링크: 관련 주제 연결 제안
5. 이미지 최적화: ALT 태그 활용 제안

## GEO 최적화 (AI 친화적 작성):
1. 명확한 정보 구조: AI가 인용하기 쉬운 형태
2. 팩트 기반 서술: "연구에 따르면", "통계에 의하면" 등
3. 단계별 설명: 번호나 순서를 활용한 구조화
4. 질문-답변 형식: 자주 묻는 질문에 대한 명확한 답변
5. 인용 가능한 문장: AI가 참조할 수 있는 독립적인 문장 구성

## 글 구조:
1. 도입부 (호기심 유발)
2. 본론 1 (문제 제기 및 분석)  
3. 본론 2 (해결책 제시)
4. 본론 3 (실제 사례 및 팁)
5. 결론 (요약 및 행동 유도)

## 글쓰기 스타일:
- 친근하고 이해하기 쉬운 톤
- 감정적 공감대 형성
- 실용적인 정보 제공
- 독자의 니즈 파악 및 해결

목표 길이: 800-1200자
SEO 키워드 자연스러운 배치, 가독성 점수 90점 이상 목표로 작성해주세요.`;

      default:
        return '';
    }
  };

  // 템플릿 적용
  const applyTemplate = () => {
    setNewGuideline({
      ...newGuideline,
      prompt: getDefaultTemplate(selectedType),
      name: `${selectedType === 'keyword' ? 'SEO 키워드 분석' : 
                selectedType === 'title' ? '바이럴 제목 생성' : 
                'SEO+GEO 블로그 글쓰기'} 기본 지침`
    });
  };

  if (!user?.is_admin) {
    return (
      <div className="card">
        <h2>접근 권한이 없습니다</h2>
        <p>관리자만 지침을 관리할 수 있습니다.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">📝 AI 지침 관리 시스템</h1>
        <p className="page-description">키워드 분석, 제목 생성, 블로그 글쓰기 AI 지침을 관리합니다</p>
      </div>

      {/* 탭 선택 */}
      <div className="card">
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          {[
            { key: 'keyword', label: '🔍 키워드 분석 지침', color: '#28a745' },
            { key: 'title', label: '✍️ 제목 생성 지침', color: '#007bff' },
            { key: 'blog', label: '📝 블로그 글쓰기 지침', color: '#fd7e14' }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setSelectedType(tab.key as any)}
              style={{
                padding: '12px 20px',
                border: 'none',
                borderRadius: '8px',
                background: selectedType === tab.key ? tab.color : '#f8f9fa',
                color: selectedType === tab.key ? 'white' : '#666',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {error && <div className="error" style={{ marginBottom: '20px' }}>{error}</div>}

        {/* 새 지침 작성 */}
        <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
          <h3>새 지침 작성</h3>
          
          <div className="form-group">
            <label className="form-label">지침 이름</label>
            <input
              type="text"
              className="form-input"
              value={newGuideline.name}
              onChange={(e) => setNewGuideline({...newGuideline, name: e.target.value})}
              placeholder="예: SEO 최적화 키워드 분석"
            />
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label className="form-label">AI 프롬프트 지침</label>
              <button 
                onClick={applyTemplate}
                style={{
                  padding: '6px 12px',
                  background: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '0.8rem'
                }}
              >
                📋 기본 템플릿 적용
              </button>
            </div>
            <textarea
              className="form-input"
              value={newGuideline.prompt}
              onChange={(e) => setNewGuideline({...newGuideline, prompt: e.target.value})}
              placeholder="AI가 수행할 작업에 대한 상세한 지침을 입력하세요..."
              rows={15}
              style={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
            />
          </div>

          <button 
            onClick={handleSaveNew}
            style={{
              background: '#28a745',
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            💾 지침 저장
          </button>
        </div>

        {/* 기존 지침 목록 */}
        <div>
          <h3>기존 지침 목록</h3>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              로딩 중...
            </div>
          ) : guidelines.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '20px', color: '#666' }}>
              등록된 지침이 없습니다. 새 지침을 작성해보세요.
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '15px' }}>
              {guidelines.map((guideline) => (
                <div 
                  key={guideline.id}
                  style={{
                    border: '1px solid #ddd',
                    borderRadius: '8px',
                    padding: '15px',
                    background: guideline.is_active ? '#f8fff8' : '#f8f8f8'
                  }}
                >
                  {editingGuideline?.id === guideline.id ? (
                    // 편집 모드
                    <div>
                      <input
                        type="text"
                        value={editingGuideline.name}
                        onChange={(e) => setEditingGuideline({...editingGuideline, name: e.target.value})}
                        style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
                      />
                      <textarea
                        value={editingGuideline.prompt}
                        onChange={(e) => setEditingGuideline({...editingGuideline, prompt: e.target.value})}
                        rows={10}
                        style={{ 
                          width: '100%', 
                          marginBottom: '10px', 
                          padding: '8px', 
                          fontFamily: 'monospace',
                          fontSize: '0.9rem'
                        }}
                      />
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <button 
                          onClick={() => handleUpdate(editingGuideline)}
                          style={{ background: '#28a745', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px' }}
                        >
                          저장
                        </button>
                        <button 
                          onClick={() => setEditingGuideline(null)}
                          style={{ background: '#6c757d', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px' }}
                        >
                          취소
                        </button>
                      </div>
                    </div>
                  ) : (
                    // 표시 모드
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                        <h4 style={{ margin: 0, color: guideline.is_active ? '#28a745' : '#6c757d' }}>
                          {guideline.is_active ? '✅' : '❌'} {guideline.name}
                        </h4>
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button 
                            onClick={() => setEditingGuideline(guideline)}
                            style={{ background: '#007bff', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', fontSize: '0.8rem' }}
                          >
                            ✏️ 편집
                          </button>
                          <button 
                            onClick={() => handleDelete(guideline.id)}
                            style={{ background: '#dc3545', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', fontSize: '0.8rem' }}
                          >
                            🗑️ 삭제
                          </button>
                        </div>
                      </div>
                      <div style={{ 
                        background: '#f8f9fa', 
                        padding: '10px', 
                        borderRadius: '4px', 
                        fontSize: '0.85rem',
                        fontFamily: 'monospace',
                        whiteSpace: 'pre-wrap',
                        maxHeight: '200px',
                        overflow: 'auto'
                      }}>
                        {guideline.prompt.length > 300 ? 
                          `${guideline.prompt.substring(0, 300)}...` : 
                          guideline.prompt
                        }
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '8px' }}>
                        생성일: {new Date(guideline.created_at).toLocaleDateString()}
                        {guideline.updated_at !== guideline.created_at && 
                          ` | 수정일: ${new Date(guideline.updated_at).toLocaleDateString()}`
                        }
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GuidelinesManager;