import { resolve } from 'node:path';

/** @type {import('vite').UserConfig} */
export default {
  root: './web',
  build: {
    outDir: './dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        index: resolve(__dirname, 'web/index.html'),
        try: resolve(__dirname, 'web/try.html')
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

