import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence } from 'framer-motion';

// Layout Components
import Layout from './components/layout/Layout';
import LoadingScreen from './components/common/LoadingScreen';
import ErrorBoundary from './components/common/ErrorBoundary';

// Page Components
import Welcome from './pages/Welcome';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import MoodLog from './pages/MoodLog';
import CopingTools from './pages/CopingTools';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';

// Context Providers
import { UserProvider } from './contexts/UserContext';
import { UIProvider } from './contexts/UIContext';

// Hooks
import { useLocalStorage } from './hooks/useLocalStorage';

// Types
import { User } from './types';

// Styles
import './index.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
    mutations: {
      retry: 1,
    },
  },
});

const App: React.FC = () => {
  const [user] = useLocalStorage<User | null>('mental_health_user', null);
  const isAuthenticated = !!user;

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <UserProvider>
          <UIProvider>
            <Router>
              <div className="App min-h-screen bg-gray-50">
                {/* Safety Notice */}
                <div className="safety-notice">
                  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
                    <p className="safety-notice-text text-center">
                      <strong>Important:</strong> This tool supports your mental health journey but is not a replacement for professional care.
                      If you're experiencing a crisis, please call <strong>988</strong> (Suicide & Crisis Lifeline) or text <strong>HOME to 741741</strong> (Crisis Text Line).
                    </p>
                  </div>
                </div>

                <AnimatePresence mode="wait">
                  <Routes>
                    {/* Public Routes */}
                    <Route
                      path="/welcome"
                      element={
                        isAuthenticated ? <Navigate to="/dashboard" replace /> : <Welcome />
                      }
                    />

                    {/* Protected Routes */}
                    <Route
                      path="/"
                      element={
                        isAuthenticated ? (
                          <Layout>
                            <Navigate to="/dashboard" replace />
                          </Layout>
                        ) : (
                          <Navigate to="/welcome" replace />
                        )
                      }
                    />

                    <Route
                      path="/dashboard"
                      element={
                        isAuthenticated ? (
                          <Layout>
                            <Dashboard />
                          </Layout>
                        ) : (
                          <Navigate to="/welcome" replace />
                        )
                      }
                    />

                    <Route
                      path="/chat"
                      element={
                        isAuthenticated ? (
                          <Layout>
                            <Chat />
                          </Layout>
                        ) : (
                          <Navigate to="/welcome" replace />
                        )
                      }
                    />

                    <Route
                      path="/mood"
                      element={
                        isAuthenticated ? (
                          <Layout>
                            <MoodLog />
                          </Layout>
                        ) : (
                          <Navigate to="/welcome" replace />
                        )
                      }
                    />

                    <Route
                      path="/coping-tools"
                      element={
                        isAuthenticated ? (
                          <Layout>
                            <CopingTools />
                          </Layout>
                        ) : (
                          <Navigate to="/welcome" replace />
                        )
                      }
                    />

                    <Route
                      path="/profile"
                      element={
                        isAuthenticated ? (
                          <Layout>
                            <Profile />
                          </Layout>
                        ) : (
                          <Navigate to="/welcome" replace />
                        )
                      }
                    />

                    {/* 404 Route */}
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </AnimatePresence>

                {/* Global Toast Notifications */}
                <Toaster
                  position="top-right"
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: '#ffffff',
                      color: '#1a202c',
                      border: '1px solid #e2e8f0',
                      borderRadius: '0.75rem',
                      padding: '12px 16px',
                      fontSize: '14px',
                      maxWidth: '400px',
                    },
                    success: {
                      iconTheme: {
                        primary: '#10b981',
                        secondary: '#ffffff',
                      },
                    },
                    error: {
                      iconTheme: {
                        primary: '#ef4444',
                        secondary: '#ffffff',
                      },
                      duration: 6000,
                    },
                    loading: {
                      iconTheme: {
                        primary: '#6b7280',
                        secondary: '#ffffff',
                      },
                    },
                  }}
                />

                {/* React Query Devtools (Development only) */}
                {process.env.NODE_ENV === 'development' && (
                  <ReactQueryDevtools initialIsOpen={false} />
                )}
              </div>
            </Router>
          </UIProvider>
        </UserProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
};

export default App;
