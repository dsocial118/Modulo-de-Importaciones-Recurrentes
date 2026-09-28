import EventNote from '@mui/icons-material/EventNote';
import { Alert, AlertTitle } from '@mui/material';
import { useSesion } from '@mir/api';

/**
 * Un período en preparación no se muestra a las provincias, y sin un período
 * abierto no hay nada que cargar: sin explicación parecería una falla
 * (28-09-2026). Este aviso dice cuál se está preparando y que no es un error.
 * Para el administrador, o con un período abierto, no se muestra.
 */
export function AvisoDePreparacion() {
  const nombre = useSesion().data?.periodo_en_preparacion;
  if (!nombre) return null;
  return (
    <Alert severity="info" icon={<EventNote />} sx={{ borderLeft: 4, borderLeftColor: 'info.main' }}>
      <AlertTitle sx={{ fontWeight: 700 }}>La importación del período {nombre} todavía no está habilitada</AlertTitle>
      El nivel nacional está preparando el período: los archivos, sus columnas y sus reglas. La carga se habilitará
      cuando el período se abra; hasta entonces no es posible importar archivos. <strong>No se trata de un error del
      sistema.</strong>
    </Alert>
  );
}
