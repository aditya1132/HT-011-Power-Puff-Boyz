// AI Mental Health Companion - API Service
// Centralized API client for backend communication

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';

// Types
import {
  User,
  MoodLog,
  MoodTrend,
  ChatMessage,
  CopingTool,
  CopingSession,
  DashboardData,
  QuickStats,
  APIResponse,
  PaginatedResponse,
  MoodLogForm,
  ChatForm,
  CheckInForm,
  UserProfileForm,
  CalendarData
} from '../types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = '/api/v1';

// Request timeout (10 seconds)
const REQUEST_TIMEOUT = 10000;

// Create axios instance with default configuration
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: `${API_BASE_URL}${API_VERSION}`,
    timeout: REQUEST_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  // Request interceptor
  client.interceptors.request.use(
    (config) => {
      // Add timestamp to prevent caching
      config.params = {
        ...config.params,
        _t: Date.now(),
      };

      // Add user agent for tracking
      config.headers = {
        ...config.headers,
        'X-Client-Version': '1.0.0',
        'X-Client-Platform': 'web',
      };

      return config;
    },
    (error) => {
      console.error('Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor
  client.interceptors.response.use(
    (response: AxiosResponse) => {
      // Log successful responses in development
      if (process.env.NODE_ENV === 'development') {
        console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data);
      }
      return response;
    },
    (error) => {
      // Enhanced error handling
      if (error.response) {
        // Server responded with error status
        const { status, data } = error.response;
        const message = data?.message || data?.detail || 'An error occurred';

        console.error(`❌ API Error ${status}:`, message);

        // Handle specific error cases
        switch (status) {
          case 400:
            toast.error('Invalid request. Please check your input.');
            break;
          case 404:
            toast.error('Resource not found.');
            break;
          case 429:
            toast.error('Too many requests. Please wait a moment.');
            break;
          case 500:
            toast.error('Server error. Please try again later.');
            break;
          default:
            toast.error(message);
        }
      } else if (error.request) {
        // Network error
        console.error('❌ Network Error:', error.message);
        toast.error('Connection failed. Please check your internet connection.');
      } else {
        // Request setup error
        console.error('❌ Request Error:', error.message);
        toast.error('Request failed. Please try again.');
      }

      return Promise.reject(error);
    }
  );

  return client;
};

// Create the API client instance
const apiClient = createApiClient();

// Generic API request wrapper
const apiRequest = async <T>(
  method: 'get' | 'post' | 'put' | 'delete' | 'patch',
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    const response = await apiClient.request<T>({
      method,
      url,
      data,
      ...config,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// API Service Class
class ApiService {
  // Health Check
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    return apiRequest('get', '/health');
  }

  // User Management
  async registerUser(userData: Partial<User>): Promise<User> {
    return apiRequest('post', '/users/register', userData);
  }

  async getUserProfile(userId: string): Promise<User> {
    return apiRequest('get', `/users/profile/${userId}`);
  }

  async updateUserProfile(userId: string, updates: UserProfileForm): Promise<User> {
    return apiRequest('put', `/users/profile/${userId}`, updates);
  }

  async dailyCheckIn(checkInData: CheckInForm & { user_id: string }): Promise<{
    message: string;
    streak_count: number;
    total_check_ins: number;
    encouragement: string;
    suggested_activities: string[];
  }> {
    return apiRequest('post', '/users/check-in', checkInData);
  }

  async getUserStats(userId: string): Promise<{
    user_id: string;
    account_age_days: number;
    total_check_ins: number;
    current_streak: number;
    longest_streak: number;
    total_mood_logs: number;
    total_chat_sessions: number;
    total_coping_sessions: number;
    completed_coping_sessions: number;
    average_mood_last_30_days?: number;
    most_used_coping_tool?: string;
    favorite_emotions: Array<{ emotion: string; count: number }>;
    activity_summary: Record<string, any>;
  }> {
    return apiRequest('get', `/users/stats/${userId}`);
  }

  async deleteUserAccount(userId: string, confirm: boolean): Promise<{
    message: string;
    deleted_data: Record<string, number>;
  }> {
    return apiRequest('delete', `/users/account/${userId}`, null, {
      params: { confirm }
    });
  }

  // Chat Interface
  async sendChatMessage(messageData: ChatForm & { user_id: string }): Promise<ChatMessage> {
    return apiRequest('post', '/chat/message', messageData);
  }

  async getChatHistory(
    userId: string,
    limit: number = 20,
    offset: number = 0,
    sessionId?: string
  ): Promise<{
    conversations: Array<{
      chat_id: string;
      session_id: string;
      emotion_detected: string;
      emotion_confidence: number;
      sentiment_score: number;
      safety_intervention: boolean;
      timestamp: string;
      response_time_ms: number;
      coping_tools_suggested: string[];
    }>;
    total_count: number;
    has_more: boolean;
  }> {
    return apiRequest('get', `/chat/history/${userId}`, null, {
      params: { limit, offset, session_id: sessionId }
    });
  }

  async deleteChatHistory(userId: string, sessionId?: string): Promise<{
    message: string;
    deleted_count: number;
  }> {
    return apiRequest('delete', `/chat/history/${userId}`, null, {
      params: { session_id: sessionId }
    });
  }

  async analyzeEmotion(text: string): Promise<{
    primary_emotion: string;
    confidence: number;
    secondary_emotions: Array<Record<string, number>>;
    sentiment_score: number;
    intensity: string;
    keywords_matched: string[];
    processing_time_ms: number;
  }> {
    return apiRequest('post', '/chat/analyze-emotion', { text });
  }

  // Mood Tracking
  async logMood(moodData: MoodLogForm & { user_id: string }): Promise<MoodLog> {
    return apiRequest('post', '/mood/log', moodData);
  }

  async getMoodHistory(userId: string, days: number = 30): Promise<MoodLog[]> {
    return apiRequest('get', `/mood/history/${userId}`, null, {
      params: { days }
    });
  }

  async getMoodTrends(userId: string, days: number = 30): Promise<MoodTrend> {
    return apiRequest('get', `/mood/trends/${userId}`, null, {
      params: { days }
    });
  }

  async getMoodStats(userId: string): Promise<{
    user_id: string;
    total_logs: number;
    logging_streak: number;
    average_mood_last_30_days: number;
    emotion_distribution: Record<string, number>;
    mood_by_time_of_day: Record<string, number>;
    common_triggers: Array<{ trigger: string; count: number }>;
    daily_summaries: Array<{
      date: string;
      mood_score?: number;
      emotion_category?: string;
      notes_count: number;
      triggers_count: number;
    }>;
  }> {
    return apiRequest('get', `/mood/stats/${userId}`);
  }

  async updateMoodLog(logId: string, updates: Partial<MoodLogForm> & { user_id: string }): Promise<MoodLog> {
    return apiRequest('put', `/mood/log/${logId}`, updates);
  }

  async deleteMoodLog(logId: string, userId: string): Promise<{ message: string }> {
    return apiRequest('delete', `/mood/log/${logId}`, null, {
      params: { user_id: userId }
    });
  }

  // Coping Tools
  async getCopingTools(filters?: {
    emotion?: string;
    tool_type?: string;
    difficulty?: string;
    max_duration?: number;
    interactive_only?: boolean;
  }): Promise<CopingTool[]> {
    return apiRequest('get', '/coping/tools', null, { params: filters });
  }

  async getCopingTool(toolId: string): Promise<CopingTool> {
    return apiRequest('get', `/coping/tools/${toolId}`);
  }

  async getPersonalizedRecommendations(recommendationData: {
    user_id: string;
    current_emotion: string;
    available_time?: number;
    preferred_types?: string[];
  }): Promise<CopingTool[]> {
    return apiRequest('post', '/coping/recommendations', recommendationData);
  }

  async startCopingSession(sessionData: {
    user_id: string;
    tool_id: string;
    trigger_emotion?: string;
    pre_mood_score?: number;
  }): Promise<{
    session_id: string;
    user_id: string;
    tool_id: string;
    tool_name: string;
    started_at: string;
    completed: boolean;
    guided_session_data?: any;
  }> {
    return apiRequest('post', '/coping/session/start', sessionData);
  }

  async completeCopingSession(completionData: {
    session_id: string;
    completed: boolean;
    completion_percentage?: number;
    post_mood_score?: number;
    helpfulness_rating?: number;
    user_notes?: string;
  }): Promise<{
    message: string;
    session_id: string;
    mood_improvement?: number;
  }> {
    return apiRequest('put', '/coping/session/complete', completionData);
  }

  async getCopingSessionHistory(userId: string, limit: number = 50): Promise<{
    sessions: Array<{
      session_id: string;
      tool_type: string;
      tool_name: string;
      started_at: string;
      completed: boolean;
      duration_seconds?: number;
      trigger_emotion?: string;
      pre_mood_score?: number;
      post_mood_score?: number;
      helpfulness_rating?: number;
      completion_percentage?: number;
    }>;
    total_sessions: number;
    favorite_tools: Array<{
      tool_name: string;
      usage_count: number;
      average_rating?: number;
      total_ratings: number;
    }>;
    effectiveness_stats: {
      completion_rate: number;
      average_helpfulness: number;
      mood_improvement_rate: number;
      most_effective_time?: string;
    };
  }> {
    return apiRequest('get', `/coping/session/history/${userId}`, null, {
      params: { limit }
    });
  }

  async getQuickCopingTools(maxDuration: number = 5): Promise<CopingTool[]> {
    return apiRequest('get', '/coping/quick-tools', null, {
      params: { max_duration: maxDuration }
    });
  }

  async getCopingStats(): Promise<{
    total_tools: number;
    by_type: Record<string, number>;
    by_difficulty: Record<string, number>;
    interactive_tools: number;
    average_duration: number;
    duration_range: { min: number; max: number };
  }> {
    return apiRequest('get', '/coping/stats');
  }

  // Dashboard
  async getDashboardOverview(userId: string, days: number = 30): Promise<DashboardData> {
    return apiRequest('get', `/dashboard/overview/${userId}`, null, {
      params: { days }
    });
  }

  async getQuickStats(userId: string): Promise<QuickStats> {
    return apiRequest('get', `/dashboard/quick-stats/${userId}`);
  }

  async getMoodCalendar(userId: string, year?: number, month?: number): Promise<CalendarData> {
    return apiRequest('get', `/dashboard/mood-calendar/${userId}`, null, {
      params: { year, month }
    });
  }

  async getPersonalizedInsights(userId: string, insightType?: string): Promise<{
    user_id: string;
    insights: Array<{
      type: string;
      title: string;
      description: string;
      actionable: string;
    }>;
    generated_at: string;
  }> {
    return apiRequest('get', `/dashboard/insights/${userId}`, null, {
      params: { insight_type: insightType }
    });
  }

  // System Operations
  async getSystemHealth(): Promise<{
    status: string;
    services: Record<string, any>;
    database: any;
    ai_system: any;
  }> {
    return apiRequest('get', '/system/health');
  }
}

// Create and export the API service instance
export const apiService = new ApiService();

// Export individual methods for convenience
export const {
  healthCheck,
  registerUser,
  getUserProfile,
  updateUserProfile,
  dailyCheckIn,
  getUserStats,
  deleteUserAccount,
  sendChatMessage,
  getChatHistory,
  deleteChatHistory,
  analyzeEmotion,
  logMood,
  getMoodHistory,
  getMoodTrends,
  getMoodStats,
  updateMoodLog,
  deleteMoodLog,
  getCopingTools,
  getCopingTool,
  getPersonalizedRecommendations,
  startCopingSession,
  completeCopingSession,
  getCopingSessionHistory,
  getQuickCopingTools,
  getCopingStats,
  getDashboardOverview,
  getQuickStats,
  getMoodCalendar,
  getPersonalizedInsights,
  getSystemHealth,
} = apiService;

export default apiService;
