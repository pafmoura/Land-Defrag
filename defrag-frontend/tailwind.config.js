/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        'defrag-main': '#789521',
      },
      fontFamily: {
      'dm-sans': ['DM Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
