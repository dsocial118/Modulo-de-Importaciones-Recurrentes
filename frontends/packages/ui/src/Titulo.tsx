import { Box, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

type Props = { titulo: string; subtitulo?: ReactNode; volver?: ReactNode; children?: ReactNode };

/**
 * El encabezado de cada pantalla: título, una línea de contexto y sus controles.
 *
 * Queda fijo arriba del recuadro que se desplaza, y es más bajo que antes: el
 * responsable funcional marcó que obligaba a desplazarse para ver el contenido
 * (27-09-2026).
 */
export function Titulo({ titulo, subtitulo, volver, children }: Props) {
  return (
    <Box
      data-titulo
      sx={{
        position: 'sticky',
        top: 0,
        zIndex: 5,
        bgcolor: 'background.default',
        pt: { xs: 1.5, md: 2 },
        pb: 1.5,
        mb: 1,
        '@media print': { position: 'static' },
      }}
    >
      {volver}
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={{ xs: 1, md: 2 }} sx={{ alignItems: { md: 'center' } }}>
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          {/* Un nombre de archivo es una palabra larga sin espacios: sin esto,
              en un teléfono empuja la pantalla hacia el costado. */}
          {/* El filete ámbar es el acento de la marca, el mismo del borde de la barra. */}
          <Typography
            variant="h6"
            component="h1"
            sx={{ fontWeight: 700, overflowWrap: 'anywhere', lineHeight: 1.3, borderLeft: 4, borderColor: 'nav.accent', pl: 1.25 }}
          >
            {titulo}
          </Typography>
          {subtitulo && (
            <Typography variant="body2" color="text.secondary" component="div" sx={{ mt: 0.25 }}>
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
