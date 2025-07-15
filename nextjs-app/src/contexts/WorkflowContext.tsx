'use client';

import { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';

// 워크플로우 단계 정의
export type WorkflowStep = 'keyword' | 'title' | 'content' | 'publish';

// 워크플로우 상태 인터페이스
export interface WorkflowState {
  currentStep: WorkflowStep;
  selectedKeyword: string;
  keywordResults: any[];
  selectedTitle: string;
  generatedTitles: string[];
  generatedContent: string;
  settings: {
    tone: string;
    length: string;
    language: string;
  };
  history: Array<{
    step: WorkflowStep;
    timestamp: Date;
    data: any;
  }>;
}

// 워크플로우 액션 타입
export type WorkflowAction =
  | { type: 'SET_STEP'; payload: WorkflowStep }
  | { type: 'SET_KEYWORD'; payload: string }
  | { type: 'SET_KEYWORD_RESULTS'; payload: any[] }
  | { type: 'SET_TITLE'; payload: string }
  | { type: 'SET_TITLES'; payload: string[] }
  | { type: 'SET_CONTENT'; payload: string }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<WorkflowState['settings']> }
  | { type: 'RESET_WORKFLOW' }
  | { type: 'RESTORE_STATE'; payload: WorkflowState }
  | { type: 'GO_TO_PREVIOUS_STEP' }
  | { type: 'GO_TO_NEXT_STEP' };

// 초기 상태
const initialState: WorkflowState = {
  currentStep: 'keyword',
  selectedKeyword: '',
  keywordResults: [],
  selectedTitle: '',
  generatedTitles: [],
  generatedContent: '',
  settings: {
    tone: 'professional',
    length: 'medium',
    language: 'ko'
  },
  history: []
};

// 워크플로우 단계 순서
const stepOrder: WorkflowStep[] = ['keyword', 'title', 'content', 'publish'];

// 워크플로우 리듀서
function workflowReducer(state: WorkflowState, action: WorkflowAction): WorkflowState {
  const addToHistory = (step: WorkflowStep, data: any) => ({
    ...state,
    history: [
      ...state.history,
      { step, timestamp: new Date(), data }
    ].slice(-10) // 최대 10개 히스토리 유지
  });

  switch (action.type) {
    case 'SET_STEP':
      return { ...state, currentStep: action.payload };

    case 'SET_KEYWORD':
      return addToHistory('keyword', action.payload) && {
        ...state,
        selectedKeyword: action.payload,
        currentStep: state.selectedKeyword ? state.currentStep : 'keyword'
      };

    case 'SET_KEYWORD_RESULTS':
      return {
        ...state,
        keywordResults: action.payload
      };

    case 'SET_TITLE':
      return addToHistory('title', action.payload) && {
        ...state,
        selectedTitle: action.payload
      };

    case 'SET_TITLES':
      return {
        ...state,
        generatedTitles: action.payload
      };

    case 'SET_CONTENT':
      return addToHistory('content', action.payload) && {
        ...state,
        generatedContent: action.payload
      };

    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
      };

    case 'GO_TO_NEXT_STEP':
      const currentIndex = stepOrder.indexOf(state.currentStep);
      const nextIndex = Math.min(currentIndex + 1, stepOrder.length - 1);
      return {
        ...state,
        currentStep: stepOrder[nextIndex]
      };

    case 'GO_TO_PREVIOUS_STEP':
      const prevCurrentIndex = stepOrder.indexOf(state.currentStep);
      const prevIndex = Math.max(prevCurrentIndex - 1, 0);
      return {
        ...state,
        currentStep: stepOrder[prevIndex]
      };

    case 'RESET_WORKFLOW':
      return { ...initialState };

    case 'RESTORE_STATE':
      return { ...action.payload };

    default:
      return state;
  }
}

// 워크플로우 컨텍스트
const WorkflowContext = createContext<{
  state: WorkflowState;
  dispatch: React.Dispatch<WorkflowAction>;
  actions: {
    setStep: (step: WorkflowStep) => void;
    setKeyword: (keyword: string) => void;
    setKeywordResults: (results: any[]) => void;
    setTitle: (title: string) => void;
    setTitles: (titles: string[]) => void;
    setContent: (content: string) => void;
    updateSettings: (settings: Partial<WorkflowState['settings']>) => void;
    goToNextStep: () => void;
    goToPreviousStep: () => void;
    resetWorkflow: () => void;
    canGoToStep: (step: WorkflowStep) => boolean;
    getStepProgress: () => number;
  };
} | null>(null);

// 워크플로우 프로바이더
export function WorkflowProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(workflowReducer, initialState);

  // 로컬 스토리지에서 상태 복원
  useEffect(() => {
    try {
      const saved = localStorage.getItem('workflow_state');
      if (saved) {
        const parsedState = JSON.parse(saved);
        // 24시간 이내의 데이터만 복원
        const dayInMs = 24 * 60 * 60 * 1000;
        const lastActivity = parsedState.history?.[parsedState.history.length - 1]?.timestamp;
        
        if (lastActivity && Date.now() - new Date(lastActivity).getTime() < dayInMs) {
          dispatch({ type: 'RESTORE_STATE', payload: parsedState });
        }
      }
    } catch (error) {
      console.error('Failed to restore workflow state:', error);
    }
  }, []);

  // 상태 변경 시 로컬 스토리지에 저장
  useEffect(() => {
    try {
      localStorage.setItem('workflow_state', JSON.stringify(state));
    } catch (error) {
      console.error('Failed to save workflow state:', error);
    }
  }, [state]);

  // 액션 함수들
  const actions = {
    setStep: (step: WorkflowStep) => dispatch({ type: 'SET_STEP', payload: step }),
    setKeyword: (keyword: string) => dispatch({ type: 'SET_KEYWORD', payload: keyword }),
    setKeywordResults: (results: any[]) => dispatch({ type: 'SET_KEYWORD_RESULTS', payload: results }),
    setTitle: (title: string) => dispatch({ type: 'SET_TITLE', payload: title }),
    setTitles: (titles: string[]) => dispatch({ type: 'SET_TITLES', payload: titles }),
    setContent: (content: string) => dispatch({ type: 'SET_CONTENT', payload: content }),
    updateSettings: (settings: Partial<WorkflowState['settings']>) => 
      dispatch({ type: 'UPDATE_SETTINGS', payload: settings }),
    goToNextStep: () => dispatch({ type: 'GO_TO_NEXT_STEP' }),
    goToPreviousStep: () => dispatch({ type: 'GO_TO_PREVIOUS_STEP' }),
    resetWorkflow: () => dispatch({ type: 'RESET_WORKFLOW' }),

    // 특정 단계로 이동 가능한지 확인
    canGoToStep: (step: WorkflowStep): boolean => {
      switch (step) {
        case 'keyword':
          return true;
        case 'title':
          return !!state.selectedKeyword;
        case 'content':
          return !!state.selectedKeyword && !!state.selectedTitle;
        case 'publish':
          return !!state.selectedKeyword && !!state.selectedTitle && !!state.generatedContent;
        default:
          return false;
      }
    },

    // 진행률 계산
    getStepProgress: (): number => {
      let completed = 0;
      if (state.selectedKeyword) completed++;
      if (state.selectedTitle) completed++;
      if (state.generatedContent) completed++;
      return Math.round((completed / 3) * 100);
    }
  };

  return (
    <WorkflowContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </WorkflowContext.Provider>
  );
}

// 워크플로우 훅
export function useWorkflow() {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflow must be used within a WorkflowProvider');
  }
  return context;
}

// 워크플로우 단계 메타데이터
export const stepMetadata = {
  keyword: {
    title: '키워드 분석',
    description: '관련 키워드를 분석하고 선택하세요',
    icon: '🔍',
    path: '/keywords'
  },
  title: {
    title: '제목 생성',
    description: '매력적인 블로그 제목을 생성하세요',
    icon: '✍️',
    path: '/titles'
  },
  content: {
    title: '콘텐츠 생성',
    description: '고품질 블로그 콘텐츠를 생성하세요',
    icon: '📝',
    path: '/content'
  },
  publish: {
    title: '발행',
    description: '완성된 콘텐츠를 발행하세요',
    icon: '🚀',
    path: '/wordpress'
  }
};