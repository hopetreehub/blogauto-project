import { useEffect, useRef, useCallback, useState } from 'react';

export interface AutoSaveData<T> {
  data: T;
  timestamp: number;
  id: string;
}

export interface AutoSaveOptions {
  interval?: number; // 저장 간격 (ms)
  key: string; // 저장 키
  enabled?: boolean; // 자동저장 활성화 여부
  onSave?: (data: any) => void; // 저장 시 콜백
  onRestore?: (data: any) => void; // 복원 시 콜백
}

export function useAutoSave<T>(
  data: T,
  options: AutoSaveOptions
) {
  const {
    interval = 30000, // 30초마다 저장
    key,
    enabled = true,
    onSave,
    onRestore
  } = options;

  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const savedDataRef = useRef<T | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // 수동 저장 함수
  const saveNow = useCallback(() => {
    if (!data || !enabled) return;

    try {
      const saveData: AutoSaveData<T> = {
        data,
        timestamp: Date.now(),
        id: `autosave_${key}`
      };

      localStorage.setItem(`autosave_${key}`, JSON.stringify(saveData));
      savedDataRef.current = data;
      setHasUnsavedChanges(false);
      setLastSaved(new Date());
      onSave?.(data);

      console.log(`[AutoSave] Data saved for key: ${key}`);
    } catch (error) {
      console.error('[AutoSave] Failed to save data:', error);
    }
  }, [data, key, enabled, onSave]);

  // 저장된 데이터 복원
  const restoreData = useCallback((): AutoSaveData<T> | null => {
    try {
      const saved = localStorage.getItem(`autosave_${key}`);
      if (!saved) return null;

      const parsedData: AutoSaveData<T> = JSON.parse(saved);
      
      // 24시간 이상 된 데이터는 무효화
      const dayInMs = 24 * 60 * 60 * 1000;
      if (Date.now() - parsedData.timestamp > dayInMs) {
        clearSavedData();
        return null;
      }

      return parsedData;
    } catch (error) {
      console.error('[AutoSave] Failed to restore data:', error);
      return null;
    }
  }, [key]);

  // 저장된 데이터 삭제
  const clearSavedData = useCallback(() => {
    try {
      localStorage.removeItem(`autosave_${key}`);
      savedDataRef.current = null;
      setHasUnsavedChanges(false);
      setLastSaved(null);
      console.log(`[AutoSave] Cleared saved data for key: ${key}`);
    } catch (error) {
      console.error('[AutoSave] Failed to clear saved data:', error);
    }
  }, [key]);

  // 데이터 변경 감지
  useEffect(() => {
    if (!enabled) return;

    const hasChanged = JSON.stringify(data) !== JSON.stringify(savedDataRef.current);
    setHasUnsavedChanges(hasChanged);
  }, [data, enabled]);

  // 자동 저장 타이머
  useEffect(() => {
    if (!enabled || !hasUnsavedChanges) return;

    timerRef.current = setTimeout(() => {
      saveNow();
    }, interval);

    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, [hasUnsavedChanges, enabled, interval, saveNow]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    };
  }, []);

  return {
    saveNow,
    restoreData,
    clearSavedData,
    hasUnsavedChanges,
    lastSaved,
    isAutoSaveEnabled: enabled
  };
}

// 페이지 이탈 경고 훅
export function useBeforeUnload(hasUnsavedChanges: boolean, message?: string) {
  useEffect(() => {
    const defaultMessage = '저장하지 않은 변경사항이 있습니다. 정말 페이지를 벗어나시겠습니까?';
    
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = message || defaultMessage;
        return message || defaultMessage;
      }
    };

    if (hasUnsavedChanges) {
      window.addEventListener('beforeunload', handleBeforeUnload);
    }

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [hasUnsavedChanges, message]);
}

// 자동저장 상태 표시 컴포넌트 인터페이스
export interface AutoSaveStatusProps {
  hasUnsavedChanges: boolean;
  lastSaved: Date | null;
  onSaveNow?: () => void;
}

// AutoSaveStatus 컴포넌트는 별도 파일로 분리됨
// /components/AutoSaveStatus.tsx 참조