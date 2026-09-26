import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => cleanup());

// jsdom no trae matchMedia, y MUI lo usa para saber el ancho de pantalla.
// Se simula una pantalla de escritorio; los tests que necesiten teléfono lo
// pisan.
if (!window.matchMedia) {
  window.matchMedia = (consulta: string) =>
    ({
      matches: /min-width/.test(consulta),
      media: consulta,
      onchange: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList;
}
