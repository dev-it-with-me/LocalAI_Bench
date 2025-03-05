import forms from '@tailwindcss/forms';
import typography from '@tailwindcss/typography';
import type { Config } from 'tailwindcss';

export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    colors: {
      background: {
        DEFAULT: '#2b3040', // Dark grey
        secondary: '#5A24A6', // Purple
      },
      text: {
        DEFAULT: '#FFFFFF', // White
        secondary: '#bddaaa', // Light green
      },
      border: {
        DEFAULT: '#9f96d9', // Light purple
      },
      accent: {
        DEFAULT: '#cbc5d9', // Very Light purple
        error: "#a62424", // Red
      },
      // Add new colors here when needed
    }
  },
  plugins: [typography, forms],
} satisfies Config;