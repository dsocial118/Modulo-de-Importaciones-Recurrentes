// Los tres estados neutrales del skill `tema-verde-institucional`: info,
// attention y pending. Están en la paleta del skill pero no en su
// createTheme, así que viven acá y no en theme.ts, que se deja sin tocar.
//
// NO son un semáforo: el verde es de marca y no quiere decir «bien». Por eso
// un archivo válido se muestra como `info`, no en verde.

export type Tono = 'info' | 'attention' | 'pending';

type Colores = { surface: string; border: string; text: string };

const CLARO: Record<Tono, Colores> = {
  info: { surface: '#E3F2FB', border: '#0288D1', text: '#01466E' },
  attention: { surface: '#FBEEE1', border: '#E86A00', text: '#7A3B00' },
  pending: { surface: '#EFEFEE', border: '#78716C', text: '#44403C' },
};

const OSCURO: Record<Tono, Colores> = {
  info: { surface: '#0E2F3F', border: '#3DC1FD', text: '#9FDDFB' },
  attention: { surface: '#3A2A1A', border: '#FFB74D', text: '#FFCF99' },
  pending: { surface: '#2B2725', border: '#78716C', text: '#D6D3D1' },
};

export function coloresDe(tono: Tono, modo: 'light' | 'dark'): Colores {
  return (modo === 'dark' ? OSCURO : CLARO)[tono];
}
