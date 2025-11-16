/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Background colors
        background: {
          DEFAULT: '#0a0a0f',
          elevated: '#13131a',
        },
        // Primary color
        primary: {
          DEFAULT: '#6366f1',
          hover: '#5558e3',
        },
        // Secondary color
        secondary: {
          DEFAULT: '#8b5cf6',
          hover: '#7c3aed',
        },
        // Accent color
        accent: {
          DEFAULT: '#14b8a6',
          hover: '#0d9488',
        },
        // Text colors
        text: {
          primary: '#f8fafc',
          secondary: '#94a3b8',
          muted: '#64748b',
        },
        // Border color
        border: {
          DEFAULT: '#1e293b',
        },
        // Destructive/Error color
        destructive: {
          DEFAULT: '#ef4444',
          hover: '#dc2626',
        },
        // Muted state
        muted: {
          DEFAULT: '#1e293b',
          foreground: '#64748b',
        },
      },
    },
  },
  plugins: [],
}
