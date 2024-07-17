import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'data/www/scss/')
    }
  },
  build: {
    rollupOptions: {
      input: {
        'main-dark-mode': path.resolve(__dirname, 'data/www/scss/main-dark-mode.scss'),
        'main-light-mode': path.resolve(__dirname, 'data/www/scss/main-light-mode.scss'),
      },
      output: {
        dir: path.resolve(__dirname, 'data/www/css/compiled'),
        assetFileNames: '[name].css',
        entryFileNames: '[name]_entry.css',
        chunkFileNames: '[name]_chunk[extname]'
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {}
    }
  }
});
