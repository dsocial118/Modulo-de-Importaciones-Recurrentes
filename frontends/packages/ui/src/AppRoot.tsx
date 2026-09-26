import { CssBaseline, ThemeProvider } from '@mui/material';
import { useMemo, useState, type ReactNode } from 'react';
import { ModoContext, type Modo } from './contextos';
import { buildTheme } from './theme';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

// La preferencia es común a todas las apps de /v2/, porque comparten origen.
const STORAGE_KEY = 'app.theme';

const leer = (): Modo => {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'dark' ? 'dark' : 'light';
  } catch {
    return 'light';
  }
};

/** Monta el tema y recuerda si el usuario eligió el modo oscuro. */
export function AppRoot({ children }: { children: ReactNode }) {
  const [modo, setModo] = useState<Modo>(leer);
  const theme = useMemo(() => buildTheme(modo), [modo]);
  const alternar = () =>
    setModo((m) => {
      const nuevo = m === 'light' ? 'dark' : 'light';
      try {
        localStorage.setItem(STORAGE_KEY, nuevo);
      } catch {
        // Sin almacenamiento se sigue igual: sólo no se recuerda.
      }
      return nuevo;
    });
  return (
    <ModoContext.Provider value={{ modo, alternar }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ModoContext.Provider>
  );
}
