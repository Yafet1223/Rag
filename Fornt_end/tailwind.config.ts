import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './hooks/**/*.{js,ts,jsx,tsx}',
    './lib/**/*.{js,ts,jsx,tsx}',
    './types/**/*.{js,ts,jsx,tsx}',
    './services/**/*.{js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        surface: '#0f172a',
        panel: '#111827',
        accent: '#7c3aed',
        muted: '#94a3b8',
        ring: '#1d4ed8'
      },
      boxShadow: {
        soft: '0 18px 50px rgba(15, 23, 42, 0.28)'
      },
      borderRadius: {
        xl: '1.5rem'
      }
    }
  },
  plugins: []
};

export default config;
