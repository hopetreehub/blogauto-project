import { useState, useEffect } from 'react';

/**
 * 세션 스토리지를 활용한 상태 관리 훅
 * 페이지 이동 후 돌아와도 입력 내용이 유지됨
 */
function useSessionStorage<T>(key: string, initialValue: T): [T, (value: T) => void] {
  // 세션 스토리지에서 값 읽기
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.sessionStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading sessionStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // 값 설정 및 세션 스토리지에 저장
  const setValue = (value: T) => {
    try {
      setStoredValue(value);
      window.sessionStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error(`Error setting sessionStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
}

export default useSessionStorage;