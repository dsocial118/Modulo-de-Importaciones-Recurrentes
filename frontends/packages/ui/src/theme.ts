// Tema del skill `tema-verde-institucional`, SIN MODIFICAR. Es la regla de
// SISOC para el front v2: el tema vive una sola vez, en este paquete, y las
// apps no redefinen colores. Si hay que cambiar algo, se cambia en el skill.
import { createTheme, type Theme } from '@mui/material/styles';

const FONT = "'Roboto','Segoe UI',system-ui,-apple-system,sans-serif";

// El nav (AppBar/Drawer) es una superficie propia; lo exponemos en theme para consumirlo con sx.
declare module '@mui/material/styles' {
  interface Palette { nav: { surface: string; activeBg: string; accent: string; text: string; textMuted: string } }
  interface PaletteOptions { nav?: Palette['nav'] }
}

export function buildTheme(mode: 'light' | 'dark'): Theme {
  const light = mode === 'light';
  return createTheme({
    palette: {
      mode,
      primary: light
        ? { main: '#04756F', light: '#9DCECB', dark: '#045F5B', contrastText: '#FFFFFF' }
        : { main: '#379F9B', light: '#54C4C0', dark: '#6FD0CC', contrastText: '#1C1917' },
      background: light
        ? { default: '#F5F5F4', paper: '#FFFFFF' }
        : { default: '#1C1917', paper: '#292524' },
      text: light
        ? { primary: '#1C1917', secondary: '#57534E' }
        : { primary: '#FAFAF9', secondary: '#D6D3D1' },
      divider: light ? '#E7E5E4' : '#44403C',
      info: { main: light ? '#0288D1' : '#3DC1FD' },
      warning: { main: light ? '#E86A00' : '#FFB74D' }, // "attention" (no semáforo)
      nav: light
        ? { surface: '#045F5B', activeBg: '#045049', accent: '#FFC000', text: '#FAFAF9', textMuted: '#D6D3D1' }
        : { surface: '#073B38', activeBg: '#0A2E2B', accent: '#FFCD33', text: '#FAFAF9', textMuted: '#D6D3D1' },
    },
    shape: { borderRadius: 8 },
    typography: {
      fontFamily: FONT,
      h1: { fontWeight: 700 }, h2: { fontWeight: 700 }, h3: { fontWeight: 500 },
      button: { textTransform: 'none', fontWeight: 500 }, // sin MAYÚSCULAS forzadas
    },
    components: {
      MuiCssBaseline: { styleOverrides: { body: { fontFamily: FONT } } },
      MuiButton: { defaultProps: { disableElevation: true } },
      // Chrome de marca: AppBar y Drawer usan la superficie de navegación (verde oscuro) en ambos modos.
      MuiAppBar: {
        styleOverrides: {
          colorPrimary: ({ theme }) => ({
            backgroundColor: theme.palette.nav.surface,
            color: theme.palette.nav.text,
            borderBottom: `3px solid ${theme.palette.nav.accent}`, // franja ámbar de marca
          }),
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: ({ theme }) => ({ backgroundColor: theme.palette.nav.surface, color: theme.palette.nav.text }),
        },
      },
    },
  });
}
