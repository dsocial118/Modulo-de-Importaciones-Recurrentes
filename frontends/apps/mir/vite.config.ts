import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// La app vive bajo /v2/mir/: Django recibe esa ruta y la reenvía acá.
export default defineConfig({
  base: '/v2/mir/',
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    // Django pide las páginas con el nombre del servicio en el compose. Vite
    // rechaza cualquier nombre que no conozca: se habilita ése y nada más.
    allowedHosts: ['front_mir'],
    // Django reenvía las páginas, pero no el websocket de la recarga en
    // caliente: el navegador lo abre directo contra este puerto.
    hmr: { clientPort: Number(process.env.VITE_HMR_PUERTO ?? 5173) },
    // En Docker Desktop sobre Windows los cambios de archivo no llegan al
    // contenedor como eventos: hay que mirarlos cada tanto.
    watch: process.env.VITE_SONDEO ? { usePolling: true, interval: 300 } : undefined,
    // Los paquetes compartidos están fuera de la carpeta de la app.
    fs: { allow: ['../..'] },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Las librerías, aparte de lo nuestro: casi nunca cambian, y con su propia
    // huella el navegador las conserva de un despliegue al otro.
    rollupOptions: {
      output: {
        manualChunks: {
          react: ['react', 'react-dom', 'react-router-dom', '@tanstack/react-query'],
          mui: ['@mui/material', '@emotion/react', '@emotion/styled'],
        },
      },
    },
  },
});
