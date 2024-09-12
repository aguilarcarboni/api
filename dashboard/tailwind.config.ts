import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
      },
    },
    extend: {
      rotate: {
        '30': '30deg',
        '60': '60deg',
        '90': '90deg',
        '120': '120deg'
      },
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: '#FA3232',
          dark:'#E12F2F'
        },
        secondary: {
          DEFAULT: '#38BAF2',
          dark:'#38BAF2'
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
        },
        subtitle: {
          DEFAULT: "hsl(var(--subtitle))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
        }
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "rotate-x-90": "rotate-x-90 0.1s linear",
      },
    },
  },
};
export default config;