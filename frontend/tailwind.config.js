/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0a", 
        surface: "#111111",    
        primary: "#00ff41",    
        secondary: "#008F11",  
        accent: "#003B00",     
        text: "#e0e0e0",       
        danger: "#ff3333",     
        warning: "#ffaa00",    
      },
      fontFamily: {
        mono: ['"Fira Code"', 'monospace'], 
      }
    },
  },
  plugins: [],
}