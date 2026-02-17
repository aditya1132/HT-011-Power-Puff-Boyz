import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

// Types
import { Notification, LoadingState, ErrorState, UIState } from '../types';

interface UIContextType {
  // Loading states
  loading: LoadingState;
  setLoading: (key: string, isLoading: boolean) => void;
  isLoading: (key?: string) => boolean;

  // Error states
  errors: ErrorState;
  setError: (key: string, error: string | null) => void;
  clearError: (key: string) => void;
  clearAllErrors: () => void;
  getError: (key: string) => string | null;

  // Notifications
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;

  // UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  modalOpen: string | null;
  setModalOpen: (modalId: string | null) => void;

  // Theme and preferences
  darkMode: boolean;
  setDarkMode: (enabled: boolean) => void;
  fontSize: 'small' | 'medium' | 'large';
  setFontSize: (size: 'small' | 'medium' | 'large') => void;

  // Accessibility
  reducedMotion: boolean;
  setReducedMotion: (enabled: boolean) => void;
  highContrast: boolean;
  setHighContrast: (enabled: boolean) => void;

  // Utility functions
  showSuccess: (message: string, duration?: number) => void;
  showError: (message: string, duration?: number) => void;
  showInfo: (message: string, duration?: number) => void;
  showWarning: (message: string, duration?: number) => void;
}

const UIContext = createContext<UIContextType | undefined>(undefined);

interface UIProviderProps {
  children: ReactNode;
}

export const UIProvider: React.FC<UIProviderProps> = ({ children }) => {
  // Loading states
  const [loading, setLoadingState] = useState<LoadingState>({});

  // Error states
  const [errors, setErrorsState] = useState<ErrorState>({});

  // Notifications
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // UI state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState<string | null>(null);

  // Theme and preferences
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('mental_health_dark_mode');
      if (saved) return JSON.parse(saved);
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  });

  const [fontSize, setFontSizeState] = useState<'small' | 'medium' | 'large'>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('mental_health_font_size');
      return (saved as 'small' | 'medium' | 'large') || 'medium';
    }
    return 'medium';
  });

  // Accessibility
  const [reducedMotion, setReducedMotion] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }
    return false;
  });

  const [highContrast, setHighContrast] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('mental_health_high_contrast');
      return saved ? JSON.parse(saved) : false;
    }
    return false;
  });

  // Loading functions
  const setLoading = useCallback((key: string, isLoading: boolean) => {
    setLoadingState(prev => ({
      ...prev,
      [key]: isLoading
    }));
  }, []);

  const isLoading = useCallback((key?: string) => {
    if (key) {
      return !!loading[key];
    }
    return Object.values(loading).some(Boolean);
  }, [loading]);

  // Error functions
  const setError = useCallback((key: string, error: string | null) => {
    setErrorsState(prev => ({
      ...prev,
      [key]: error
    }));
  }, []);

  const clearError = useCallback((key: string) => {
    setErrorsState(prev => {
      const { [key]: removed, ...rest } = prev;
      return rest;
    });
  }, []);

  const clearAllErrors = useCallback(() => {
    setErrorsState({});
  }, []);

  const getError = useCallback((key: string) => {
    return errors[key] || null;
  }, [errors]);

  // Notification functions
  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newNotification: Notification = {
      ...notification,
      id,
      duration: notification.duration || 4000
    };

    setNotifications(prev => [...prev, newNotification]);

    // Auto remove after duration
    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Utility notification functions
  const showSuccess = useCallback((message: string, duration?: number) => {
    addNotification({
      type: 'success',
      message,
      duration
    });
  }, [addNotification]);

  const showError = useCallback((message: string, duration?: number) => {
    addNotification({
      type: 'error',
      message,
      duration: duration || 6000 // Errors stay longer
    });
  }, [addNotification]);

  const showInfo = useCallback((message: string, duration?: number) => {
    addNotification({
      type: 'info',
      message,
      duration
    });
  }, [addNotification]);

  const showWarning = useCallback((message: string, duration?: number) => {
    addNotification({
      type: 'warning',
      message,
      duration: duration || 5000 // Warnings stay a bit longer
    });
  }, [addNotification]);

  // Theme functions with persistence
  const setDarkModeWithPersistence = useCallback((enabled: boolean) => {
    setDarkMode(enabled);
    localStorage.setItem('mental_health_dark_mode', JSON.stringify(enabled));

    // Apply theme class to document
    if (enabled) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const setFontSize = useCallback((size: 'small' | 'medium' | 'large') => {
    setFontSizeState(size);
    localStorage.setItem('mental_health_font_size', size);

    // Apply font size class to document
    document.documentElement.classList.remove('font-small', 'font-medium', 'font-large');
    document.documentElement.classList.add(`font-${size}`);
  }, []);

  const setHighContrastWithPersistence = useCallback((enabled: boolean) => {
    setHighContrast(enabled);
    localStorage.setItem('mental_health_high_contrast', JSON.stringify(enabled));

    // Apply high contrast class to document
    if (enabled) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }
  }, []);

  // Initialize theme on mount
  React.useEffect(() => {
    // Apply initial dark mode class
    if (darkMode) {
      document.documentElement.classList.add('dark');
    }

    // Apply initial font size class
    document.documentElement.classList.add(`font-${fontSize}`);

    // Apply initial high contrast class
    if (highContrast) {
      document.documentElement.classList.add('high-contrast');
    }

    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      // Only auto-switch if user hasn't manually set preference
      const savedPreference = localStorage.getItem('mental_health_dark_mode');
      if (!savedPreference) {
        setDarkMode(e.matches);
      }
    };

    mediaQuery.addEventListener('change', handleChange);

    // Listen for system motion preference changes
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handleMotionChange = (e: MediaQueryListEvent) => {
      setReducedMotion(e.matches);

      if (e.matches) {
        document.documentElement.classList.add('reduced-motion');
      } else {
        document.documentElement.classList.remove('reduced-motion');
      }
    };

    motionQuery.addEventListener('change', handleMotionChange);

    // Apply initial reduced motion class
    if (reducedMotion) {
      document.documentElement.classList.add('reduced-motion');
    }

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
      motionQuery.removeEventListener('change', handleMotionChange);
    };
  }, []);

  const value: UIContextType = {
    // Loading
    loading,
    setLoading,
    isLoading,

    // Errors
    errors,
    setError,
    clearError,
    clearAllErrors,
    getError,

    // Notifications
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,

    // UI state
    sidebarOpen,
    setSidebarOpen,
    modalOpen,
    setModalOpen,

    // Theme
    darkMode,
    setDarkMode: setDarkModeWithPersistence,
    fontSize,
    setFontSize,

    // Accessibility
    reducedMotion,
    setReducedMotion,
    highContrast,
    setHighContrast: setHighContrastWithPersistence,

    // Utilities
    showSuccess,
    showError,
    showInfo,
    showWarning,
  };

  return (
    <UIContext.Provider value={value}>
      {children}
    </UIContext.Provider>
  );
};

// Custom hook to use the UIContext
export const useUI = (): UIContextType => {
  const context = useContext(UIContext);
  if (context === undefined) {
    throw new Error('useUI must be used within a UIProvider');
  }
  return context;
};

export default UIContext;
