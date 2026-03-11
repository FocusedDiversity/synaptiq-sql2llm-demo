/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        accent: "#3B82F6",
        "accent-hover": "#2563EB",
        "dark-bg": "#0F1117",
        "dark-surface": "#1A1D27",
        "dark-border": "#2A2D3A",
        "dark-text": "#E2E8F0",
        "dark-muted": "#94A3B8",
      },
    },
  },
  plugins: [],
};
