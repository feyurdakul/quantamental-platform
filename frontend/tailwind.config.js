/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0B0E14',
          800: '#111722',
          700: '#182232',
          600: '#223046'
        },
        brand: {
          500: '#3B82F6',
          600: '#2563EB',
          accent: '#10B981'
        },
        signal: {
          strongBuy: '#10B981',
          buy: '#34D399',
          hold: '#FBBF24',
          watch: '#60A5FA',
          sell: '#F87171',
          strongSell: '#EF4444'
        }
      }
    },
  },
  plugins: [],
}
