/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],

  theme: {
    extend: {

      colors: {
        background: "#09090b",
        card: "#18181b",
        border: "#27272a",

        primary: "#06b6d4",
        success: "#22c55e",
        warning: "#eab308",
        danger: "#ef4444"
      },

      fontFamily: {
        sans: ["Inter", "sans-serif"]
      },

      borderRadius: {
        "3xl": "1.5rem"
      },

      boxShadow: {
        card: "0 8px 32px rgba(0,0,0,0.35)"
      },

      animation: {
        pulseSlow: "pulse 2s infinite",
        fadeIn: "fadeIn 0.6s ease-in-out"
      },

      keyframes: {
        fadeIn: {
          "0%": {
            opacity: "0",
            transform: "translateY(10px)"
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0px)"
          }
        }
      }

    }
  },

  plugins: []
};