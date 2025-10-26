import { resolve } from 'node:path';

/** @type {import('vite').UserConfig} */
export default {
  root: '.',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'index.html'),
        try: resolve(__dirname, 'try.html')
      }
    }
  },
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  },
  preview: {
    port: 5173,
    strictPort: false
  }
};


