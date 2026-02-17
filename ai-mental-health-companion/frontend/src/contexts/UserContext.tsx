import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import toast from 'react-hot-toast';

// Types
import { User } from '../types';

// Services
import { apiService } from '../services/api';

// Hooks
import { useLocalStorage } from '../hooks/useLocalStorage';

interface UserContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (userData: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => Promise<void>;
  refreshUser: () => Promise<void>;
  checkIn: (moodScore?: number, notes?: string) => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

interface UserProviderProps {
  children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [user, setUser] = useLocalStorage<User | null>('mental_health_user', null);
  const [isLoading, setIsLoading] = useState(false);

  const isAuthenticated = !!user;

  // Login function
  const login = (userData: User) => {
    setUser(userData);
    toast.success(`Welcome back! Your current streak: ${userData.streak_count} days`);
  };

  // Logout function
  const logout = () => {
    setUser(null);
    toast.success('You have been logged out successfully');
  };

  // Update user function
  const updateUser = async (updates: Partial<User>) => {
    if (!user) {
      throw new Error('No user logged in');
    }

    setIsLoading(true);
    try {
      const updatedUser = await apiService.updateUserProfile(user.user_id, updates);
      setUser(updatedUser);
      toast.success('Profile updated successfully');
    } catch (error) {
      console.error('Failed to update user:', error);
      toast.error('Failed to update profile');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Refresh user data
  const refreshUser = async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      const refreshedUser = await apiService.getUserProfile(user.user_id);
      setUser(refreshedUser);
    } catch (error) {
      console.error('Failed to refresh user data:', error);
      // Don't show error toast for background refresh
    } finally {
      setIsLoading(false);
    }
  };

  // Daily check-in
  const checkIn = async (moodScore?: number, notes?: string) => {
    if (!user) {
      throw new Error('No user logged in');
    }

    setIsLoading(true);
    try {
      const checkInData = {
        user_id: user.user_id,
        mood_score: moodScore,
        quick_note: notes,
      };

      const result = await apiService.dailyCheckIn(checkInData);

      // Update user with new streak information
      const updatedUser = {
        ...user,
        streak_count: result.streak_count,
        total_check_ins: result.total_check_ins,
        last_check_in: new Date().toISOString(),
      };
      setUser(updatedUser);

      toast.success(result.message);
      return result;
    } catch (error) {
      console.error('Check-in failed:', error);
      toast.error('Failed to complete check-in');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-refresh user data periodically
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(() => {
      refreshUser();
    }, 5 * 60 * 1000); // Refresh every 5 minutes

    return () => clearInterval(interval);
  }, [user]);

  // Auto-refresh user data when tab becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && user) {
        refreshUser();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [user]);

  const value: UserContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    updateUser,
    refreshUser,
    checkIn,
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};

// Custom hook to use the UserContext
export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export default UserContext;
