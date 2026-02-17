import { useState, useEffect, useCallback } from 'react';

// Type for the hook return value
type UseLocalStorageReturn<T> = [
  T,
  (value: T | ((prevValue: T) => T)) => void,
  () => void
];

/**
 * Custom hook for managing localStorage with TypeScript support
 *
 * @param key - The localStorage key
 * @param initialValue - Initial value to use if key doesn't exist
 * @returns [value, setValue, removeValue]
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T
): UseLocalStorageReturn<T> {
  // Get value from localStorage or use initial value
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);

      if (item === null) {
        return initialValue;
      }

      return JSON.parse(item);
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Set value to localStorage
  const setValue = useCallback((value: T | ((prevValue: T) => T)) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;

      // Save state
      setStoredValue(valueToStore);

      // Save to localStorage
      window.localStorage.setItem(key, JSON.stringify(valueToStore));

      // Dispatch custom event for cross-tab synchronization
      window.dispatchEvent(
        new CustomEvent('local-storage-change', {
          detail: { key, value: valueToStore }
        })
      );
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  // Remove value from localStorage
  const removeValue = useCallback(() => {
    try {
      // Remove from localStorage
      window.localStorage.removeItem(key);

      // Reset state to initial value
      setStoredValue(initialValue);

      // Dispatch custom event for cross-tab synchronization
      window.dispatchEvent(
        new CustomEvent('local-storage-change', {
          detail: { key, value: undefined }
        })
      );
    } catch (error) {
      console.error(`Error removing localStorage key "${key}":`, error);
    }
  }, [key, initialValue]);

  // Listen for changes in localStorage from other tabs
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === key) {
        try {
          const newValue = e.newValue ? JSON.parse(e.newValue) : initialValue;
          setStoredValue(newValue);
        } catch (error) {
          console.warn(`Error parsing localStorage change for key "${key}":`, error);
        }
      }
    };

    const handleCustomStorageChange = (e: CustomEvent) => {
      if (e.detail.key === key) {
        setStoredValue(e.detail.value ?? initialValue);
      }
    };

    // Listen for storage events from other tabs
    window.addEventListener('storage', handleStorageChange);

    // Listen for custom events from same tab
    window.addEventListener('local-storage-change', handleCustomStorageChange as EventListener);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('local-storage-change', handleCustomStorageChange as EventListener);
    };
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}

/**
 * Hook for managing arrays in localStorage with additional array methods
 */
export function useLocalStorageArray<T>(
  key: string,
  initialValue: T[] = []
): [
  T[],
  {
    setValue: (value: T[] | ((prevValue: T[]) => T[])) => void;
    addItem: (item: T) => void;
    removeItem: (predicate: (item: T) => boolean) => void;
    updateItem: (predicate: (item: T) => boolean, updater: (item: T) => T) => void;
    clear: () => void;
    removeValue: () => void;
  }
] {
  const [array, setArray, removeValue] = useLocalStorage<T[]>(key, initialValue);

  const addItem = useCallback((item: T) => {
    setArray(prev => [...prev, item]);
  }, [setArray]);

  const removeItem = useCallback((predicate: (item: T) => boolean) => {
    setArray(prev => prev.filter(item => !predicate(item)));
  }, [setArray]);

  const updateItem = useCallback((
    predicate: (item: T) => boolean,
    updater: (item: T) => T
  ) => {
    setArray(prev => prev.map(item => predicate(item) ? updater(item) : item));
  }, [setArray]);

  const clear = useCallback(() => {
    setArray([]);
  }, [setArray]);

  return [
    array,
    {
      setValue: setArray,
      addItem,
      removeItem,
      updateItem,
      clear,
      removeValue,
    }
  ];
}

/**
 * Hook for managing objects in localStorage with merge functionality
 */
export function useLocalStorageObject<T extends Record<string, any>>(
  key: string,
  initialValue: T
): [
  T,
  {
    setValue: (value: T | ((prevValue: T) => T)) => void;
    updateProperty: <K extends keyof T>(property: K, value: T[K]) => void;
    mergeObject: (partial: Partial<T>) => void;
    removeProperty: <K extends keyof T>(property: K) => void;
    reset: () => void;
    removeValue: () => void;
  }
] {
  const [object, setObject, removeValue] = useLocalStorage<T>(key, initialValue);

  const updateProperty = useCallback(<K extends keyof T>(property: K, value: T[K]) => {
    setObject(prev => ({ ...prev, [property]: value }));
  }, [setObject]);

  const mergeObject = useCallback((partial: Partial<T>) => {
    setObject(prev => ({ ...prev, ...partial }));
  }, [setObject]);

  const removeProperty = useCallback(<K extends keyof T>(property: K) => {
    setObject(prev => {
      const { [property]: removed, ...rest } = prev;
      return rest as T;
    });
  }, [setObject]);

  const reset = useCallback(() => {
    setObject(initialValue);
  }, [setObject, initialValue]);

  return [
    object,
    {
      setValue: setObject,
      updateProperty,
      mergeObject,
      removeProperty,
      reset,
      removeValue,
    }
  ];
}

/**
 * Utility function to check if localStorage is available
 */
export function isLocalStorageAvailable(): boolean {
  try {
    const testKey = '__localStorage_test__';
    window.localStorage.setItem(testKey, 'test');
    window.localStorage.removeItem(testKey);
    return true;
  } catch {
    return false;
  }
}

/**
 * Utility function to get localStorage usage info
 */
export function getLocalStorageInfo() {
  if (!isLocalStorageAvailable()) {
    return { available: false, used: 0, remaining: 0 };
  }

  let used = 0;
  for (const key in localStorage) {
    if (localStorage.hasOwnProperty(key)) {
      used += localStorage.getItem(key)?.length || 0;
      used += key.length;
    }
  }

  // Most browsers have a 5-10MB limit, we'll assume 5MB
  const limit = 5 * 1024 * 1024; // 5MB in bytes

  return {
    available: true,
    used,
    remaining: limit - used,
    usedFormatted: formatBytes(used),
    remainingFormatted: formatBytes(limit - used),
    percentUsed: Math.round((used / limit) * 100)
  };
}

/**
 * Helper function to format bytes
 */
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
