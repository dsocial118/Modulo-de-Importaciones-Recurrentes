// Los contextos del paquete, aparte de los componentes que los proveen: así
// la recarga en caliente puede actualizar un componente sin reiniciar la app.
import { createContext, useContext, type ReactNode } from 'react';

export type Modo = 'light' | 'dark';

export const ModoContext = createContext<{ modo: Modo; alternar: () => void }>({
  modo: 'light',
  alternar: () => {},
});

/** El modo de color y cómo cambiarlo. */
export const useModo = () => useContext(ModoContext);

export type Aviso = { texto: string; error?: boolean };

export const AvisoContext = createContext<(a: Aviso) => void>(() => {});

/** Para avisar el resultado de una acción: `avisar({ texto, error })`. */
export const useAvisar = () => useContext(AvisoContext);

export type Pregunta = {
  titulo: string;
  texto: ReactNode;
  confirmar?: string;
  // `warning` para lo que pisa algo que ya estaba, como reemplazar una
  // importación: el botón sale en ámbar y no en el verde de marca.
  color?: 'primary' | 'warning';
  // Si se pide, la confirmación trae un campo de texto —por ejemplo, el motivo
  // de una corrección— y su valor es lo que devuelve.
  campo?: { etiqueta: string; obligatorio?: boolean };
};

export const ConfirmarContext = createContext<(p: Pregunta) => Promise<string | null>>(async () => null);

/**
 * `await confirmar({...})`: devuelve el texto del campo (o '' si no hay), o
 * null si se canceló.
 */
export const useConfirmar = () => useContext(ConfirmarContext);
