/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        cyber: {
          900: '#030712', // Deep space
          800: '#0b132b',
          700: '#1c2541',
          primary: '#00f7ff', // Neon Cyan
          secondary: '#7b2cbf', // Neon Purple
          accent: '#e0aaff',
          danger: '#ff003c',
          success: '#00ff66',
          warning: '#ffb703',
        }
      },
      backgroundImage: {
        'glass-gradient': 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)',
        'glass-glow': 'radial-gradient(circle at var(--x, 50%) var(--y, 50%), rgba(0, 247, 255, 0.15) 0%, transparent 50%)',
        'glass-glow-purple': 'radial-gradient(circle at var(--x, 50%) var(--y, 50%), rgba(123, 44, 191, 0.25) 0%, transparent 60%)',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glass-hover': '0 8px 32px 0 rgba(0, 247, 255, 0.2)',
        'neon-primary': '0 0 10px rgba(0, 247, 255, 0.5), 0 0 20px rgba(0, 247, 255, 0.3)',
        'neon-secondary': '0 0 10px rgba(123, 44, 191, 0.5), 0 0 20px rgba(123, 44, 191, 0.3)',
      }
    },
  },
  plugins: [],
}
