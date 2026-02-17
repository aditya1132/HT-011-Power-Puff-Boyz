import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid';

// Icons
import {
  FaHeart,
  FaBrain,
  FaUsers,
  FaShieldAlt,
  FaChartLine,
  FaComments,
  FaTools,
  FaCalendarAlt
} from 'react-icons/fa';

// Hooks
import { useLocalStorage } from '../hooks/useLocalStorage';

// Services
import { apiService } from '../services/api';

// Types
import { User, NotificationPreferences, PrivacySettings } from '../types';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

const Welcome: React.FC = () => {
  const navigate = useNavigate();
  const [, setUser] = useLocalStorage<User | null>('mental_health_user', null);

  const [currentStep, setCurrentStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [preferences, setPreferences] = useState({
    copingTools: [] as string[],
    notifications: {
      daily_checkin_reminder: true,
      mood_trend_insights: true,
      coping_tool_suggestions: true,
      crisis_resources: true,
    } as NotificationPreferences,
    privacy: {
      store_chat_history: true,
      anonymous_analytics: false,
      share_mood_trends: false,
      data_retention_months: 12,
    } as PrivacySettings,
  });

  const onboardingSteps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to Your Mental Health Companion',
      description: 'A safe, supportive space for your emotional well-being journey.',
      icon: <FaHeart className="text-primary-500" />,
    },
    {
      id: 'features',
      title: 'How We Support You',
      description: 'Discover the tools and features designed to help you thrive.',
      icon: <FaBrain className="text-secondary-500" />,
    },
    {
      id: 'safety',
      title: 'Your Safety Comes First',
      description: 'Understanding our safety measures and professional boundaries.',
      icon: <FaShieldAlt className="text-accent-500" />,
    },
    {
      id: 'preferences',
      title: 'Personalize Your Experience',
      description: 'Choose your preferred coping tools and notification settings.',
      icon: <FaTools className="text-wellness-energetic" />,
    },
  ];

  const copingToolOptions = [
    { id: 'breathing', label: 'Breathing Exercises', description: 'Guided breathing techniques for calm' },
    { id: 'mindfulness', label: 'Mindfulness', description: 'Present-moment awareness practices' },
    { id: 'grounding', label: 'Grounding Techniques', description: '5-4-3-2-1 and other grounding methods' },
    { id: 'journaling', label: 'Journaling', description: 'Reflective writing prompts and exercises' },
    { id: 'physical', label: 'Physical Movement', description: 'Gentle stretches and movement' },
    { id: 'cognitive', label: 'Cognitive Tools', description: 'Thought challenging and reframing' },
  ];

  const features = [
    {
      icon: <FaComments className="text-primary-500" />,
      title: 'AI Chat Companion',
      description: 'Talk through your feelings with an understanding AI that detects emotions and provides supportive responses.',
    },
    {
      icon: <FaChartLine className="text-secondary-500" />,
      title: 'Mood Tracking',
      description: 'Log your daily moods and see patterns over time with beautiful visualizations and insights.',
    },
    {
      icon: <FaTools className="text-accent-500" />,
      title: 'Coping Tools',
      description: 'Access interactive breathing exercises, grounding techniques, and mindfulness practices.',
    },
    {
      icon: <FaCalendarAlt className="text-wellness-positive" />,
      title: 'Daily Check-ins',
      description: 'Build healthy habits with daily mood check-ins and maintain your wellness streak.',
    },
  ];

  const safetyPoints = [
    'This app is NOT a replacement for professional mental health care',
    'We never diagnose, treat, or provide medical advice',
    'Crisis situations are detected and appropriate resources are provided',
    'Your conversations are private and secure',
    'We encourage seeking professional help when appropriate',
  ];

  const handleCopingToolToggle = (toolId: string) => {
    setPreferences(prev => ({
      ...prev,
      copingTools: prev.copingTools.includes(toolId)
        ? prev.copingTools.filter(id => id !== toolId)
        : [...prev.copingTools, toolId]
    }));
  };

  const handleNotificationToggle = (key: keyof NotificationPreferences) => {
    setPreferences(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: !prev.notifications[key]
      }
    }));
  };

  const handlePrivacyToggle = (key: keyof PrivacySettings) => {
    if (key === 'data_retention_months') return; // Skip toggle for number field

    setPreferences(prev => ({
      ...prev,
      privacy: {
        ...prev.privacy,
        [key]: !prev.privacy[key]
      }
    }));
  };

  const handleNext = () => {
    if (currentStep < onboardingSteps.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleComplete = async () => {
    setIsLoading(true);

    try {
      // Create user with preferences
      const userData = {
        preferred_coping_tools: preferences.copingTools,
        notification_preferences: preferences.notifications,
        privacy_settings: preferences.privacy,
      };

      const newUser = await apiService.registerUser(userData);

      // Store user in local storage
      setUser(newUser);

      toast.success('Welcome! Your account has been created successfully.');

      // Navigate to dashboard
      navigate('/dashboard');

    } catch (error) {
      console.error('Registration failed:', error);
      toast.error('Failed to create account. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (onboardingSteps[currentStep].id) {
      case 'welcome':
        return (
          <div className="text-center">
            <div className="mb-8">
              <div className="w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <FaHeart className="text-4xl text-primary-500" />
              </div>
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Welcome to Your Mental Health Companion
              </h1>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                A safe, supportive, and private space designed to help you understand your emotions,
                practice coping skills, and track your mental wellness journey.
              </p>
            </div>

            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 mb-8 max-w-2xl mx-auto">
              <div className="flex items-start space-x-3">
                <FaShieldAlt className="text-amber-600 mt-1 flex-shrink-0" />
                <div className="text-left">
                  <h3 className="font-semibold text-amber-800 mb-2">Important Notice</h3>
                  <p className="text-amber-700 text-sm">
                    This tool is designed to support your mental health journey but is not a replacement for professional care.
                    If you're experiencing a mental health crisis, please contact emergency services or call the National
                    Suicide Prevention Lifeline at <strong>988</strong>.
                  </p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'features':
        return (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <div className="w-16 h-16 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FaBrain className="text-2xl text-secondary-500" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">How We Support You</h2>
              <p className="text-lg text-gray-600">
                Discover the features designed to help you build resilience and maintain emotional well-being.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-xl p-6 shadow-soft border border-gray-100"
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                        {feature.icon}
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        );

      case 'safety':
        return (
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-12">
              <div className="w-16 h-16 bg-accent-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FaShieldAlt className="text-2xl text-accent-500" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Your Safety Comes First</h2>
              <p className="text-lg text-gray-600">
                Understanding our safety measures and the boundaries of AI support.
              </p>
            </div>

            <div className="bg-white rounded-xl p-8 shadow-soft border border-gray-100">
              <div className="space-y-6">
                {safetyPoints.map((point, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start space-x-3"
                  >
                    <div className="flex-shrink-0 w-6 h-6 bg-accent-100 rounded-full flex items-center justify-center mt-0.5">
                      <div className="w-2 h-2 bg-accent-500 rounded-full"></div>
                    </div>
                    <p className="text-gray-700">{point}</p>
                  </motion.div>
                ))}
              </div>

              <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="font-semibold text-red-800 mb-3 flex items-center">
                  <FaShieldAlt className="mr-2" />
                  Crisis Resources
                </h3>
                <div className="space-y-2 text-sm text-red-700">
                  <p><strong>National Suicide Prevention Lifeline:</strong> 988</p>
                  <p><strong>Crisis Text Line:</strong> Text HOME to 741741</p>
                  <p><strong>Emergency Services:</strong> 911</p>
                </div>
              </div>
            </div>
          </div>
        );

      case 'preferences':
        return (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <div className="w-16 h-16 bg-wellness-energetic/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <FaTools className="text-2xl text-wellness-energetic" />
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Personalize Your Experience</h2>
              <p className="text-lg text-gray-600">
                Choose your preferred coping tools and customize your notification settings.
              </p>
            </div>

            <div className="space-y-8">
              {/* Coping Tools Preferences */}
              <div className="bg-white rounded-xl p-8 shadow-soft border border-gray-100">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">
                  Preferred Coping Tools
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {copingToolOptions.map((tool) => (
                    <div
                      key={tool.id}
                      onClick={() => handleCopingToolToggle(tool.id)}
                      className={`
                        p-4 rounded-lg border-2 cursor-pointer transition-all duration-200
                        ${preferences.copingTools.includes(tool.id)
                          ? 'border-primary-300 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                        }
                      `}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`
                          w-5 h-5 rounded-full border-2 flex items-center justify-center
                          ${preferences.copingTools.includes(tool.id)
                            ? 'border-primary-500 bg-primary-500'
                            : 'border-gray-300'
                          }
                        `}>
                          {preferences.copingTools.includes(tool.id) && (
                            <div className="w-2 h-2 bg-white rounded-full"></div>
                          )}
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{tool.label}</h4>
                          <p className="text-sm text-gray-500">{tool.description}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Notification Preferences */}
              <div className="bg-white rounded-xl p-8 shadow-soft border border-gray-100">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">
                  Notification Preferences
                </h3>
                <div className="space-y-4">
                  {Object.entries(preferences.notifications).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 capitalize">
                          {key.replace(/_/g, ' ')}
                        </h4>
                        <p className="text-sm text-gray-500">
                          {key === 'daily_checkin_reminder' && 'Gentle reminders for your daily mood check-in'}
                          {key === 'mood_trend_insights' && 'Weekly insights about your mood patterns'}
                          {key === 'coping_tool_suggestions' && 'Personalized coping tool recommendations'}
                          {key === 'crisis_resources' && 'Important safety resources and crisis support'}
                        </p>
                      </div>
                      <button
                        onClick={() => handleNotificationToggle(key as keyof NotificationPreferences)}
                        className={`
                          relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                          ${value ? 'bg-primary-500' : 'bg-gray-200'}
                        `}
                      >
                        <span className={`
                          inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                          ${value ? 'translate-x-6' : 'translate-x-1'}
                        `} />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Privacy Settings */}
              <div className="bg-white rounded-xl p-8 shadow-soft border border-gray-100">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">
                  Privacy Settings
                </h3>
                <div className="space-y-4">
                  {Object.entries(preferences.privacy).map(([key, value]) => {
                    if (key === 'data_retention_months') {
                      return (
                        <div key={key} className="flex items-center justify-between">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">Data Retention Period</h4>
                            <p className="text-sm text-gray-500">How long to keep your data (months)</p>
                          </div>
                          <select
                            value={value}
                            onChange={(e) => setPreferences(prev => ({
                              ...prev,
                              privacy: { ...prev.privacy, data_retention_months: parseInt(e.target.value) }
                            }))}
                            className="px-3 py-1 border border-gray-300 rounded-lg text-sm"
                          >
                            <option value={6}>6 months</option>
                            <option value={12}>1 year</option>
                            <option value={24}>2 years</option>
                            <option value={36}>3 years</option>
                          </select>
                        </div>
                      );
                    }

                    return (
                      <div key={key} className="flex items-center justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 capitalize">
                            {key.replace(/_/g, ' ')}
                          </h4>
                          <p className="text-sm text-gray-500">
                            {key === 'store_chat_history' && 'Save your conversations for pattern analysis'}
                            {key === 'anonymous_analytics' && 'Help improve the app with anonymous usage data'}
                            {key === 'share_mood_trends' && 'Share anonymized mood data for research'}
                          </p>
                        </div>
                        <button
                          onClick={() => handlePrivacyToggle(key as keyof PrivacySettings)}
                          className={`
                            relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                            ${value ? 'bg-primary-500' : 'bg-gray-200'}
                          `}
                        >
                          <span className={`
                            inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                            ${value ? 'translate-x-6' : 'translate-x-1'}
                          `} />
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      <div className="container mx-auto px-4 py-8">
        {/* Progress Bar */}
        <div className="max-w-2xl mx-auto mb-12">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-gray-500">
              Step {currentStep + 1} of {onboardingSteps.length}
            </span>
            <span className="text-sm font-medium text-gray-500">
              {Math.round(((currentStep + 1) / onboardingSteps.length) * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / onboardingSteps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Indicator */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="flex items-center justify-center space-x-8">
            {onboardingSteps.map((step, index) => (
              <div
                key={step.id}
                className={`
                  flex flex-col items-center space-y-2
                  ${index <= currentStep ? 'text-primary-600' : 'text-gray-400'}
                `}
              >
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center text-xl
                  ${index <= currentStep
                    ? 'bg-primary-100 text-primary-600'
                    : 'bg-gray-100 text-gray-400'
                  }
                  ${index === currentStep ? 'ring-4 ring-primary-100' : ''}
                `}>
                  {step.icon}
                </div>
                <span className="text-xs font-medium text-center max-w-20">
                  {step.title.split(' ').slice(0, 2).join(' ')}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="mb-12"
        >
          {renderStepContent()}
        </motion.div>

        {/* Navigation */}
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between">
            <button
              onClick={handleBack}
              disabled={currentStep === 0}
              className={`
                px-6 py-3 rounded-xl font-medium transition-colors
                ${currentStep === 0
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              Back
            </button>

            <button
              onClick={handleNext}
              disabled={isLoading}
              className="btn-primary min-w-32"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Setting up...</span>
                </div>
              ) : (
                currentStep === onboardingSteps.length - 1 ? 'Get Started' : 'Next'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Welcome;
