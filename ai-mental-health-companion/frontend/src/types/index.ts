// Type definitions for AI Mental Health Companion Frontend

export interface User {
  user_id: string;
  created_at: string;
  updated_at?: string;
  streak_count: number;
  last_check_in?: string;
  total_check_ins: number;
  is_active: boolean;
  first_login?: string;
  last_activity?: string;
  preferred_coping_tools?: string[];
  notification_preferences?: NotificationPreferences;
  privacy_settings?: PrivacySettings;
}

export interface NotificationPreferences {
  daily_checkin_reminder: boolean;
  mood_trend_insights: boolean;
  coping_tool_suggestions: boolean;
  crisis_resources: boolean;
}

export interface PrivacySettings {
  store_chat_history: boolean;
  anonymous_analytics: boolean;
  share_mood_trends: boolean;
  data_retention_months: number;
}

// Mood and Emotion Types
export type EmotionCategory =
  | 'stressed'
  | 'anxious'
  | 'sad'
  | 'overwhelmed'
  | 'neutral'
  | 'positive'
  | 'angry'
  | 'excited'
  | 'confused'
  | 'grateful';

export type MoodScore = 1 | 2 | 3 | 4 | 5;

export type TimeOfDay = 'morning' | 'afternoon' | 'evening' | 'night';

export interface MoodLog {
  log_id: string;
  user_id: string;
  mood_score: MoodScore;
  emotion_category: EmotionCategory;
  secondary_emotions?: string[];
  notes?: string;
  triggers?: string[];
  timestamp: string;
  date_only: string;
  ai_confidence?: number;
  suggested_activities?: string[];
  time_of_day?: TimeOfDay;
  social_context?: string;
  weather_impact?: string;
}

export interface MoodTrend {
  user_id: string;
  date_range: {
    start: string;
    end: string;
  };
  average_mood: number;
  mood_trend: 'improving' | 'declining' | 'stable';
  most_common_emotion: EmotionCategory;
  mood_logs: MoodLog[];
  insights: MoodInsights;
  recommendations: string[];
}

export interface MoodInsights {
  best_day: {
    date: string;
    mood_score: MoodScore;
    emotion: EmotionCategory;
  };
  worst_day: {
    date: string;
    mood_score: MoodScore;
    emotion: EmotionCategory;
  };
  common_triggers: Array<{
    trigger: string;
    count: number;
  }>;
  mood_by_time: Record<TimeOfDay, number>;
  total_entries: number;
  days_with_notes: number;
}

// Chat Types
export interface ChatMessage {
  chat_id: string;
  message: string;
  response_type: 'supportive' | 'crisis_intervention' | 'general';
  emotion_detected: EmotionResponse;
  coping_suggestions: CopingToolSuggestion[];
  follow_up_questions: string[];
  resources: Resource[];
  safety_info: SafetyInfo;
  processing_time_ms: number;
  session_id: string;
  timestamp: string;
}

export interface EmotionResponse {
  primary_emotion: EmotionCategory;
  confidence: number;
  secondary_emotions: Array<Record<string, number>>;
  sentiment_score: number;
  intensity: 'low' | 'medium' | 'high' | 'extreme';
  keywords_matched: string[];
  processing_time_ms: number;
}

export interface SafetyInfo {
  intervention_triggered: boolean;
  safety_level: 'normal' | 'high' | 'crisis';
  crisis_resources: Resource[];
  professional_help_suggested: boolean;
}

export interface Resource {
  name: string;
  contact: string;
  description: string;
}

// Coping Tools Types
export type CopingToolType =
  | 'breathing'
  | 'grounding'
  | 'mindfulness'
  | 'journaling'
  | 'physical'
  | 'cognitive'
  | 'relaxation'
  | 'creativity'
  | 'social';

export type DifficultyLevel = 'easy' | 'medium' | 'hard';

export interface CopingTool {
  id: string;
  name: string;
  type: CopingToolType;
  description: string;
  target_emotions: EmotionCategory[];
  duration_minutes: number;
  difficulty: DifficultyLevel;
  instructions: string[];
  benefits: string[];
  requirements: string[];
  interactive: boolean;
  guided_steps?: GuidedStep[];
}

export interface GuidedStep {
  step: number;
  action: 'inhale' | 'exhale' | 'hold' | 'pause' | 'prepare' | 'focus' | 'observe';
  duration: number;
  instruction: string;
}

export interface CopingToolSuggestion {
  id: string;
  name: string;
  type: CopingToolType;
  description: string;
  duration_minutes: number;
  difficulty: DifficultyLevel;
  interactive: boolean;
}

export interface CopingSession {
  session_id: string;
  user_id: string;
  tool_id: string;
  tool_name: string;
  tool_type: CopingToolType;
  started_at: string;
  completed_at?: string;
  completed: boolean;
  duration_seconds?: number;
  trigger_emotion?: EmotionCategory;
  pre_mood_score?: MoodScore;
  post_mood_score?: MoodScore;
  helpfulness_rating?: number;
  user_notes?: string;
  completion_percentage?: number;
  guided_session_data?: GuidedSessionData;
}

export interface GuidedSessionData {
  session_id: string;
  tool_id: string;
  tool_name: string;
  total_steps: number;
  estimated_duration: number;
  steps: GuidedStep[];
  created_at: string;
}

// Dashboard Types
export interface DashboardData {
  user_id: string;
  generated_at: string;
  summary: DashboardSummary;
  mood_trends: MoodTrendData[];
  weekly_insights: WeeklyInsight[];
  emotion_patterns: EmotionPattern[];
  coping_tools_analysis: CopingToolInsight[];
  streak_analysis: StreakAnalysis;
  recommendations: string[];
  achievements: Achievement[];
}

export interface DashboardSummary {
  total_days: number;
  mood_logs: number;
  coping_sessions: number;
  average_mood?: number;
  improvement_trend: 'improving' | 'declining' | 'stable';
  most_common_emotion?: EmotionCategory;
  completion_rate?: number;
}

export interface MoodTrendData {
  date: string;
  mood_score?: MoodScore;
  emotion?: EmotionCategory;
}

export interface WeeklyInsight {
  week_start: string;
  average_mood: number;
  most_common_emotion: EmotionCategory;
  total_logs: number;
  mood_trend: 'improving' | 'declining' | 'stable';
}

export interface EmotionPattern {
  emotion: EmotionCategory;
  frequency: number;
  percentage: number;
  average_mood_score: number;
  common_triggers: string[];
  time_patterns: Record<TimeOfDay, number>;
}

export interface CopingToolInsight {
  tool_name: string;
  tool_type: CopingToolType;
  usage_count: number;
  completion_rate: number;
  average_helpfulness?: number;
  mood_improvement_rate?: number;
}

export interface StreakAnalysis {
  current_streak: number;
  longest_streak: number;
  total_check_ins: number;
  consistency_rate: number;
  streak_history: StreakPeriod[];
}

export interface StreakPeriod {
  start_date: string;
  end_date: string;
  length: number;
}

export interface Achievement {
  name: string;
  description: string;
  icon: string;
  earned_date: string;
}

export interface QuickStats {
  current_mood?: MoodScore;
  streak_count: number;
  this_week_average?: number;
  total_coping_sessions: number;
  mood_trend: 'improving' | 'declining' | 'stable';
  next_milestone: Milestone;
}

export interface Milestone {
  type: 'streak' | 'coping_sessions' | 'mood_logs';
  target: number;
  progress: number;
  description: string;
}

// API Response Types
export interface APIResponse<T> {
  data?: T;
  error?: boolean;
  message?: string;
  timestamp?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total_count: number;
  has_more: boolean;
  limit: number;
  offset: number;
}

// Form Types
export interface MoodLogForm {
  mood_score: MoodScore;
  emotion_category: EmotionCategory;
  notes?: string;
  triggers?: string[];
  time_of_day?: TimeOfDay;
  social_context?: string;
  weather_impact?: string;
}

export interface ChatForm {
  message: string;
  session_id?: string;
  context?: Record<string, any>;
}

export interface CheckInForm {
  mood_score?: MoodScore;
  quick_note?: string;
}

export interface UserProfileForm {
  preferred_coping_tools?: string[];
  notification_preferences?: Partial<NotificationPreferences>;
  privacy_settings?: Partial<PrivacySettings>;
}

// UI State Types
export interface LoadingState {
  [key: string]: boolean;
}

export interface ErrorState {
  [key: string]: string | null;
}

export interface UIState {
  loading: LoadingState;
  errors: ErrorState;
  notifications: Notification[];
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// Navigation Types
export interface NavItem {
  label: string;
  path: string;
  icon?: string;
  badge?: string | number;
  children?: NavItem[];
}

// Component Props Types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
  testId?: string;
}

export interface ModalProps extends BaseComponentProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export interface InputProps extends BaseComponentProps {
  label?: string;
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  type?: 'text' | 'email' | 'password' | 'number' | 'textarea';
}

// Chart Types
export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartDataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
  borderColor?: string | string[];
  borderWidth?: number;
  fill?: boolean;
  tension?: number;
}

export interface ChartOptions {
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  scales?: any;
  plugins?: any;
  elements?: any;
}

// Local Storage Types
export interface StoredUser {
  user: User;
  timestamp: number;
}

export interface StoredSession {
  session_id: string;
  user_id: string;
  started_at: string;
  messages: StoredChatMessage[];
}

export interface StoredChatMessage {
  user_message: string;
  ai_response: string;
  timestamp: string;
  emotion_detected?: EmotionCategory;
}

// Calendar Types
export interface CalendarDay {
  date: string;
  mood_score?: MoodScore;
  emotion?: EmotionCategory;
  has_notes: boolean;
  triggers_count: number;
  is_today?: boolean;
  is_selected?: boolean;
}

export interface CalendarData {
  year: number;
  month: number;
  calendar_data: Record<string, CalendarDay>;
  summary: {
    total_logs: number;
    average_mood?: number;
    best_day?: string;
    challenging_day?: string;
  };
}

// Breathing Exercise Types
export interface BreathingExercise {
  name: string;
  pattern: BreathingPattern;
  duration_minutes: number;
  instructions: string[];
}

export interface BreathingPattern {
  inhale_count: number;
  hold_count: number;
  exhale_count: number;
  pause_count?: number;
  cycles: number;
}

// Theme Types
export interface Theme {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: {
    primary: string;
    secondary: string;
    muted: string;
  };
  mood: Record<MoodScore, string>;
  emotion: Record<EmotionCategory, string>;
}

// Accessibility Types
export interface A11yProps {
  'aria-label'?: string;
  'aria-describedby'?: string;
  'aria-expanded'?: boolean;
  'aria-hidden'?: boolean;
  role?: string;
  tabIndex?: number;
}

// Hook Return Types
export interface UseMoodLogReturn {
  moodLogs: MoodLog[];
  loading: boolean;
  error: string | null;
  createMoodLog: (data: MoodLogForm) => Promise<void>;
  updateMoodLog: (id: string, data: Partial<MoodLogForm>) => Promise<void>;
  deleteMoodLog: (id: string) => Promise<void>;
  refetch: () => void;
}

export interface UseCopingToolsReturn {
  tools: CopingTool[];
  loading: boolean;
  error: string | null;
  getToolsForEmotion: (emotion: EmotionCategory) => CopingTool[];
  startSession: (toolId: string) => Promise<CopingSession>;
  completeSession: (sessionId: string, data: any) => Promise<void>;
}

export interface UseUserReturn {
  user: User | null;
  loading: boolean;
  error: string | null;
  updateUser: (data: Partial<UserProfileForm>) => Promise<void>;
  checkIn: (data: CheckInForm) => Promise<void>;
  logout: () => void;
}

// Utility Types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};
