import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    // This forces the graph library to use YOUR React, fixing the "Invalid hook" error
    dedupe: ['react', 'react-dom'], 
  },
  optimizeDeps: {
    // This pre-bundles the library to fix the "useRef" null error
    include: ['react-force-graph-2d', 'three'], 
  },
});