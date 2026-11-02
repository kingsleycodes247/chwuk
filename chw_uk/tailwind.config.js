/** @type {import('tailwindcss').Config} */
module.exports = {
  // Every class used in the Django templates is picked up from these files.
  content: ["./core/templates/**/*.html"],
  theme: {
    extend: {
      colors: {
        navy: { 950: "#071428", 900: "#0b1f3a", 800: "#12305a", 700: "#1b447d" },
        gold: { 400: "#d8b866", 500: "#c9a24a", 600: "#a8832f" },
        cream: "#faf7f0",
      },
      fontFamily: {
        serif: ['"Cormorant Garamond"', "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
