/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary colors - Calming blues
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },

        // Secondary colors - Warm greens for positivity
        secondary: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },

        // Accent colors - Gentle purples
        accent: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7c3aed',
          800: '#6b21a8',
          900: '#581c87',
        },

        // Mental health specific colors
        wellness: {
          calm: '#87ceeb',      // Sky blue
          peaceful: '#b0e0e6',   // Powder blue
          energetic: '#98fb98',  // Pale green
          positive: '#f0e68c',   // Khaki
          neutral: '#d3d3d3',    // Light gray
          concerned: '#dda0dd',  // Plum
          stressed: '#f4a460',   // Sandy brown
        },

        // Emotion colors for mood tracking
        emotion: {
          stressed: '#ff6b6b',
          anxious: '#feca57',
          sad: '#74b9ff',
          overwhelmed: '#fd79a8',
          neutral: '#636e72',
          positive: '#00b894',
          excited: '#e17055',
          grateful: '#a29bfe',
          angry: '#d63031',
          confused: '#fdcb6e',
        },

        // Mood scale colors (1-5)
        mood: {
          1: '#ff4757', // Very low - red
          2: '#ff6b6b', // Low - light red
          3: '#ffa502', // Neutral - orange
          4: '#2ed573', // Good - light green
          5: '#1dd1a1', // Excellent - green
        },

        // Background variations
        background: {
          primary: '#ffffff',
          secondary: '#f8fafc',
          tertiary: '#f1f5f9',
          card: '#ffffff',
          modal: 'rgba(0, 0, 0, 0.5)',
        },

        // Text colors
        text: {
          primary: '#1a202c',
          secondary: '#4a5568',
          tertiary: '#718096',
          muted: '#a0aec0',
          inverse: '#ffffff',
        },

        // Status colors
        status: {
          success: '#10b981',
          warning: '#f59e0b',
          error: '#ef4444',
          info: '#3b82f6',
        },
      },

      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Cal Sans', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },

      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },

      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },

      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },

      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'bounce-gentle': 'bounceGentle 2s infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'breathing': 'breathing 4s ease-in-out infinite',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
        breathing: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
      },

      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'strong': '0 10px 40px -10px rgba(0, 0, 0, 0.15), 0 2px 5px 0px rgba(0, 0, 0, 0.05)',
        'inner-soft': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
      },

      backdropBlur: {
        xs: '2px',
      },

      screens: {
        'xs': '475px',
        '3xl': '1600px',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),

    // Custom plugin for mental health specific utilities
    function({ addUtilities, theme }) {
      const newUtilities = {
        // Calm focus states
        '.focus-calm': {
          '&:focus': {
            outline: 'none',
            boxShadow: `0 0 0 3px ${theme('colors.wellness.calm')}40`,
          },
        },

        // Gentle hover transitions
        '.hover-gentle': {
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-1px)',
          },
        },

        // Breathing animation for interactive elements
        '.animate-breathe': {
          animation: 'breathing 4s ease-in-out infinite',
        },

        // Gradient backgrounds for mood states
        '.bg-mood-gradient': {
          background: `linear-gradient(135deg, ${theme('colors.wellness.calm')}, ${theme('colors.wellness.peaceful')})`,
        },

        '.bg-positive-gradient': {
          background: `linear-gradient(135deg, ${theme('colors.secondary.400')}, ${theme('colors.secondary.300')})`,
        },

        '.bg-neutral-gradient': {
          background: `linear-gradient(135deg, ${theme('colors.gray.100')}, ${theme('colors.gray.50')})`,
        },

        // Safe space styling
        '.safe-space': {
          backgroundColor: theme('colors.background.card'),
          borderRadius: theme('borderRadius.2xl'),
          padding: theme('spacing.6'),
          boxShadow: theme('boxShadow.soft'),
          border: `1px solid ${theme('colors.gray.100')}`,
        },
      }

      addUtilities(newUtilities, ['responsive', 'hover'])
    },
  ],
}
