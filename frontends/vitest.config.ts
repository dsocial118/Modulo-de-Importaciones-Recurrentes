import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

// Las pruebas del front: vitest + Testing Library sobre jsdom, un navegador
// simulado. Prueban lo que ve y hace la persona, no el HTML por dentro.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
    include: ['apps/**/src/**/*.test.{ts,tsx}', 'packages/**/src/**/*.test.{ts,tsx}'],
    css: false,
  },
});
