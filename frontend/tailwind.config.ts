export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0f',
        elevated: '#13131a',
        primary: '#6366f1',
        secondary: '#8b5cf6',
        accent: '#14b8a6',
        text: {
          DEFAULT: '#f8fafc',
          muted: '#94a3b8',
        },
        border: '#1e293b',
        destructive: '#ef4444',
        muted: {
          DEFAULT: '#1e293b',
          foreground: '#64748b',
        },
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px 10px rgba(99, 102, 241, 0.3)' },
          '50%': { boxShadow: '0 0 30px 15px rgba(99, 102, 241, 0.5)' },
        }
      }
    },
  },
  plugins: [],
}