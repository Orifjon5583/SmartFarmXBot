/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        night: '#061014',
        panel: 'rgba(9, 24, 31, 0.68)',
        cyber: {
          green: '#38f2a1',
          blue: '#35c7ff',
          lime: '#b8ff5b',
          red: '#ff557a',
          amber: '#ffce55',
        },
      },
      boxShadow: {
        neon: '0 0 34px rgba(56, 242, 161, 0.18)',
        blue: '0 0 34px rgba(53, 199, 255, 0.16)',
      },
      backgroundImage: {
        grid:
          'linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.045) 1px, transparent 1px)',
      },
    },
  },
  plugins: [],
};
