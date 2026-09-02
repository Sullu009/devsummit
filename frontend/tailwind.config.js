/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#14171C",
        paper: "#F7F5F0",
        surface: "#FFFFFF",
        line: "#DCD7C9",
        muted: "#6B6558",
        forest: "#1F5E45",
        "forest-dark": "#153F2F",
        gold: "#B8862B",
        rust: "#A23E2A",
      },
      fontFamily: {
        display: ["Fraunces", "Georgia", "ui-serif", "serif"],
        sans: ["Inter", "-apple-system", "Segoe UI", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      borderRadius: {
        none: "0px",
        sm: "2px",
        DEFAULT: "3px",
        md: "4px",
      },
      boxShadow: {
        none: "none",
      },
    },
  },
  plugins: [],
};
