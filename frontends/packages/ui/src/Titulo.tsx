import { Box, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

type Props = { titulo: string; subtitulo?: ReactNode; volver?: ReactNode; children?: ReactNode };

/** El encabezado de cada pantalla: título, una línea de contexto y sus controles. */
export function Titulo({ titulo, subtitulo, volver, children }: Props) {
  return (
    <Box sx={{ mb: 3 }}>
      {volver}
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ alignItems: { md: 'center' } }}>
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          {/* Un nombre de archivo es una palabra larga sin espacios: sin esto,
              en un teléfono empuja la pantalla hacia el costado. */}
          <Typography variant="h5" component="h1" sx={{ fontWeight: 700, overflowWrap: 'anywhere' }}>
            {titulo}
          </Typography>
          {subtitulo && (
            <Typography variant="body2" color="text.secondary" component="div" sx={{ mt: 0.5 }}>
              {subtitulo}
            </Typography>
          )}
        </Box>
        {children && (
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ alignItems: { sm: 'center' } }}>
            {children}
          </Stack>
        )}
      </Stack>
    </Box>
  );
}
