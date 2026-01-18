/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Midnight Void Palette
        void: {
          950: '#020617', // Deepest background
          900: '#0f172a', // Main background
          800: '#1e293b', // Card surface
        },
        // Neon Accents
        cyan: {
          400: '#22d3ee',
          500: '#06b6d4',
          glow: 'rgba(34, 211, 238, 0.5)',
        },
        indigo: {
          500: '#6366f1',
          glow: 'rgba(99, 102, 241, 0.5)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'monospace'],
      },
      boxShadow: {
        'neon': '0 0 20px -5px var(--tw-shadow-color)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
      backdropBlur: {
        'xs': '2px',
      }
    },
  },
  plugins: [],
}
