import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./providers/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#FACC15",
          hover: "#EAB308",
        },
        background: {
          DEFAULT: "#FFFFFF",
          soft: "#F8FAFC",
        },
        ai: {
          light: "#E0F2FE",
          blue: "#38BDF8",
        },
        foreground: "#111827",
        muted: {
          DEFAULT: "#64748B",
          text: "#94A3B8",
        },
        line: "#E2E8F0",
        ink: "#111827",
        brand: "#FACC15",
        success: "#22C55E",
        warning: "#F59E0B",
        error: "#EF4444",
      },
      borderRadius: {
        button: "12px",
        card: "18px",
        section: "24px",
      },
      boxShadow: {
        card: "0 8px 24px rgba(15, 23, 42, 0.04)",
        soft: "0 12px 40px rgba(15, 23, 42, 0.06)",
      },
    },
  },
  plugins: [],
};

export default config;
