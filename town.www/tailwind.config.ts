/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        primary: "hsl(var(--primary))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(215 16% 47%)",
        border: "hsl(var(--border))",
        danger: "#E74C3C",
        warning: "#F39C12",
        safe: "#27AE60",
      },
    },
  },
  plugins: [],
};
