/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        neon: {
          pink: '#ff47a3',
          blue: '#6ac1ff',
          purple: '#9d7bff',
          amber: '#ffb347',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'Inter', 'system-ui', 'sans-serif'],
        body: ['"Space Grotesk"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'neon-strong':
          '0 0 15px rgba(157, 123, 255, 0.6), 0 0 30px rgba(255, 71, 163, 0.4)',
        'neon-soft':
          '0 0 10px rgba(106, 193, 255, 0.4), 0 0 20px rgba(255, 179, 71, 0.3)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};
