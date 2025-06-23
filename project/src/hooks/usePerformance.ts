import { useRef, useCallback } from 'react';

/**
 * Custom hook for performance monitoring
 * Tracks API response times and user interactions
 */
export function usePerformance() {
  const timers = useRef<Record<string, number>>({});

  const startTimer = useCallback((label: string) => {
    timers.current[label] = performance.now();
  }, []);

  const endTimer = useCallback((label: string) => {
    const startTime = timers.current[label];
    if (startTime) {
      const duration = performance.now() - startTime;
      console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
      delete timers.current[label];
      return duration;
    }
    return 0;
  }, []);

  const measureApiCall = useCallback(async <T>(
    label: string, 
    apiCall: () => Promise<T>
  ): Promise<T> => {
    startTimer(label);
    try {
      const result = await apiCall();
      endTimer(label);
      return result;
    } catch (error) {
      endTimer(label);
      throw error;
    }
  }, [startTimer, endTimer]);

  return { startTimer, endTimer, measureApiCall };
} 