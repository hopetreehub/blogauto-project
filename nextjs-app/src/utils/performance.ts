/**
 * 프론트엔드 성능 최적화 유틸리티
 */

import React from 'react';

// 디바운스 함수
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      func(...args);
    };
    
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(later, wait);
  };
}

// 쓰로틀 함수
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}

// 레이지 로딩을 위한 Intersection Observer 훅
export function useLazyLoad(
  ref: React.RefObject<HTMLElement>,
  callback: () => void,
  options?: IntersectionObserverInit
) {
  React.useEffect(() => {
    if (!ref.current) return;
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          callback();
          observer.unobserve(entry.target);
        }
      });
    }, options);
    
    observer.observe(ref.current);
    
    return () => {
      observer.disconnect();
    };
  }, [ref, callback, options]);
}

// LazyImage 컴포넌트는 @/components/LazyImage로 이동됨

// 성능 측정 유틸리티
export class PerformanceMonitor {
  private marks: Map<string, number> = new Map();
  
  mark(name: string) {
    this.marks.set(name, performance.now());
  }
  
  measure(name: string, startMark: string, endMark?: string): number {
    const start = this.marks.get(startMark);
    const end = endMark ? this.marks.get(endMark) : performance.now();
    
    if (!start) {
      console.warn(`Start mark "${startMark}" not found`);
      return 0;
    }
    
    const duration = (end || performance.now()) - start;
    
    // 브라우저 Performance API에도 기록
    if ('performance' in window && 'measure' in window.performance) {
      try {
        performance.measure(name, startMark, endMark);
      } catch (e) {
        // 마크가 없을 수 있음
      }
    }
    
    return duration;
  }
  
  getMetrics() {
    const entries = performance.getEntriesByType('measure');
    return entries.map(entry => ({
      name: entry.name,
      duration: entry.duration,
      startTime: entry.startTime
    }));
  }
  
  clear() {
    this.marks.clear();
    performance.clearMeasures();
  }
}

// 메모이제이션 훅
export function useMemoizedCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList
): T {
  const ref = React.useRef<T>(callback);
  
  React.useLayoutEffect(() => {
    ref.current = callback;
  }, [callback]);
  
  return React.useCallback(
    ((...args) => ref.current(...args)) as T,
    deps
  );
}

// 가상 스크롤링을 위한 훅
export function useVirtualScroll<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan: number = 5
) {
  const [scrollTop, setScrollTop] = React.useState(0);
  
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );
  
  const visibleItems = items.slice(startIndex, endIndex + 1);
  const totalHeight = items.length * itemHeight;
  const offsetY = startIndex * itemHeight;
  
  const handleScroll = React.useCallback((e: React.UIEvent<HTMLElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);
  
  return {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll,
    startIndex,
    endIndex
  };
}

// 브라우저 아이들 콜백
export function requestIdleCallback(
  callback: IdleRequestCallback,
  options?: IdleRequestOptions
): number {
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    return (window as any).requestIdleCallback(callback, options);
  }
  
  // 폴백: setTimeout 사용
  const start = Date.now();
  return (typeof window !== 'undefined' ? (window as any).setTimeout(() => {
    callback({
      didTimeout: false,
      timeRemaining: () => Math.max(0, 50 - (Date.now() - start))
    });
  }, 1) : 0) as unknown as number;
}

// 이벤트 리스너 최적화
export function useOptimizedEventListener<K extends keyof WindowEventMap>(
  event: K,
  handler: (event: WindowEventMap[K]) => void,
  options?: AddEventListenerOptions & { throttle?: number; debounce?: number }
) {
  const savedHandler = React.useRef(handler);
  
  React.useEffect(() => {
    savedHandler.current = handler;
  }, [handler]);
  
  React.useEffect(() => {
    let eventHandler = (event: WindowEventMap[K]) => savedHandler.current(event);
    
    if (options?.throttle) {
      eventHandler = throttle(eventHandler, options.throttle);
    } else if (options?.debounce) {
      eventHandler = debounce(eventHandler, options.debounce);
    }
    
    window.addEventListener(event, eventHandler as any, options);
    
    return () => {
      window.removeEventListener(event, eventHandler as any, options);
    };
  }, [event, options]);
}