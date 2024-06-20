import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        section: 'var(--color-section)',
        secondary: 'var(--color-secondary)',
        tertiary: 'var(--color-tertiary)',
        quarternary: 'var(--color-quarternary)',
        grayish: 'var(--color-grayish)',
        info: 'var(--color-info)',
        infohover: 'var(--color-infohover)',
        accent: 'var(--color-accent)',
        reddish: 'var(--color-reddish)'
      },
      height: {
        'calc-100percent-5rem': 'calc(100% - 5rem)',
        'calc-100vh-5rem': 'calc(100vh - 5rem)'
      }
    },
  },
  plugins: [],
};
export default config;
