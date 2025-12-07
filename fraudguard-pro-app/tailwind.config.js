/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary-blue': '#4A90E2',
        'secondary-purple': '#A569BD',
        'fraud-red': '#E74C3C',
        'safe-green': '#2ECC71',
        'warning-orange': '#F39C12',
      },
      fontFamily: {
        'cairo': ['Cairo', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
