import { Chip, useTheme } from '@mui/material';
import { coloresDe, type Tono } from './estados';

type Props = { texto: string; tono: Tono; titulo?: string };

/** Una etiqueta de estado con los colores neutrales del skill. */
export function EtiquetaDeEstado({ texto, tono, titulo }: Props) {
  const { palette } = useTheme();
  const c = coloresDe(tono, palette.mode);
  return (
    <Chip
      size="small"
      label={texto}
      title={titulo}
      sx={{ bgcolor: c.surface, color: c.text, border: `1px solid ${c.border}`, fontWeight: 500 }}
    />
  );
}
