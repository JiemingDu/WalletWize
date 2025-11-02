/** @type {import('tailwindcss').Config} */
import forms from '@tailwindcss/forms'
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        jersey: ['"Jersey 10"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};