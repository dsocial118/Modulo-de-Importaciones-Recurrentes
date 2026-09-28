import CheckCircle from '@mui/icons-material/CheckCircle';
import ChevronRight from '@mui/icons-material/ChevronRight';
import RadioButtonChecked from '@mui/icons-material/RadioButtonChecked';
import RadioButtonUnchecked from '@mui/icons-material/RadioButtonUnchecked';
import { Box, Link, Stack, Tooltip, Typography, useMediaQuery, useTheme } from '@mui/material';
import { useFranja } from '@mir/api';
import { EtiquetaDeEstado } from '@mir/ui';
import { Fragment } from 'react';
import { useNavigate } from 'react-router-dom';
import { conFiltros, useFiltros } from './filtros';
import { plural } from './formato';

// Los archivos dicen en qué están (27-09-2026). En la carga importa cuántos
// faltan; después ya están todos, y lo que cambia es qué pasa con ellos.
const QUE_PASA_CON_LOS_ARCHIVOS: Record<string, string> = {
  CERRADA: 'en revisión',
  EN_REVISION: 'en revisión',
  OBSERVADA: 'observados',
  SUBSANADA: 'subsanados',
  HABILITADA: 'listos para presentar',
  PRESENTADA: 'presentados',
  CONSOLIDADA: 'consolidados',
};

function archivosEnPalabras(estado: string | null | undefined, importados: number, esperados: number) {
  const que = estado ? QUE_PASA_CON_LOS_ARCHIVOS[estado] : undefined;
  if (!que) return `${importados} de ${esperados} archivos importados`;
  return `${importados} ${importados === 1 ? 'archivo' : 'archivos'} ${que}`;
}

/**
 * El avance del circuito, en un renglón fino arriba de todas las pantallas.
 *
 * A la contraparte le encantó el avance y estaba escondido dentro de Resultado
 * (27-09-2026). Acá está siempre a la vista, sin ocupar lugar: los pasos con el
 * actual resaltado, los archivos cargados, las observaciones sin resolver y,
 * si le toca a quien mira, qué tiene que hacer. El detalle, al pasar el mouse.
 * Sin jurisdicción elegida —el nivel nacional en su bandeja— no se muestra.
 */
export function FranjaDelCircuito() {
  const { periodo, jurisdiccion } = useFiltros();
  const consulta = useFranja(periodo, jurisdiccion);
  const navegar = useNavigate();
  const theme = useTheme();
  // Un solo renglón siempre: por debajo de 1200 px los cinco pasos no entran
  // junto con lo demás y la franja se partía en tres; ahí se dice en cuál está.
  const chico = useMediaQuery(theme.breakpoints.down('lg'));
  const f = consulta.data;
  if (!f || !f.estado || !f.pasos.length) return null;

  const actual = f.pasos.findIndex((p) => p.actual);
  const irAlResultado = () => navegar(conFiltros('/resultado', f.periodo, f.jurisdiccion));

  return (
    <Box
      component="nav"
      aria-label="Avance del circuito"
      sx={{
        // Fuera del recuadro que se desplaza: queda siempre a la vista.
        flexShrink: 0,
        px: { xs: 2, md: 3 },
        // Con los colores de la navegación y el paso actual en ámbar, como la
        // sección activa del menú (propuesta C, elegida el 27-09-2026).
        py: 1,
        borderBottom: 3,
        borderColor: 'nav.accent',
        bgcolor: 'nav.activeBg',
        color: 'nav.text',
      }}
    >
      <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', flexWrap: 'nowrap', overflow: 'hidden' }}>
        {/* Si no entra todo, lo primero que se achica es esto: está también en el título. */}
        <Typography variant="body2" noWrap sx={{ color: 'nav.textMuted', fontWeight: 500, minWidth: 40, flexShrink: 1 }}>
          {f.jurisdiccion} · {f.periodo_nombre || f.periodo}
        </Typography>

        {chico ? (
          // En pantallas angostas los pasos no entran: se dice en cuál está.
          <Tooltip describeChild title={f.que_pasa}>
            <Typography variant="body2">
              Paso {actual + 1} de {f.pasos.length}: <strong>{f.pasos[actual]?.nombre}</strong>
            </Typography>
          </Tooltip>
        ) : (
          <Stack direction="row" spacing={0.25} sx={{ alignItems: 'center', flexShrink: 0, m: 0, p: 0 }} component="ol" role="list">
            {f.pasos.map((p, i) => (
              <Fragment key={p.nombre}>
                {i > 0 && <ChevronRight fontSize="inherit" sx={{ color: 'nav.textMuted' }} aria-hidden />}
                <Tooltip describeChild title={p.actual ? `${f.estado_legible}: ${f.que_pasa}` : p.hecho ? 'Hecho' : 'Todavía no'}>
                  <Stack
                    component="li"
                    direction="row"
                    spacing={0.5}
                    aria-current={p.actual ? 'step' : undefined}
                    sx={{
                      alignItems: 'center',
                      listStyle: 'none',
                      px: 1,
                      py: 0.4,
                      borderRadius: 1,
                      bgcolor: p.actual ? 'nav.accent' : 'transparent',
                      // Sobre el ámbar, la tinta que le da contraste (la oscura, en los dos modos).
                      color: (t) =>
                        p.actual ? t.palette.getContrastText(t.palette.nav.accent) : p.hecho ? t.palette.nav.text : t.palette.nav.textMuted,
                    }}
                  >
                    {p.hecho ? (
                      <CheckCircle sx={{ fontSize: 18 }} />
                    ) : p.actual ? (
                      <RadioButtonChecked sx={{ fontSize: 18 }} />
                    ) : (
                      <RadioButtonUnchecked sx={{ fontSize: 18 }} />
                    )}
                    <Typography variant="body2" sx={{ fontWeight: p.actual ? 600 : 400, whiteSpace: 'nowrap' }}>
                      {p.nombre}
                    </Typography>
                  </Stack>
                </Tooltip>
              </Fragment>
            ))}
          </Stack>
        )}

        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', ml: 'auto', flexWrap: 'nowrap', flexShrink: 0, '& > *': { whiteSpace: 'nowrap' } }}>
          <Typography variant="body2" sx={{ color: 'nav.textMuted' }}>
            {archivosEnPalabras(f.estado, f.archivos_importados, f.archivos_esperados)}
          </Typography>
          {f.observaciones_abiertas > 0 && (
            <EtiquetaDeEstado
              tono="critical"
              texto={plural(f.observaciones_abiertas, 'observación sin resolver', 'observaciones sin resolver')}
            />
          )}
          {f.te_toca.length > 0 && (
            <Typography variant="body2">
              Te toca:{' '}
              <Link component="button" variant="body2" onClick={irAlResultado} sx={{ fontWeight: 600, verticalAlign: 'baseline', color: 'nav.accent' }}>
                {f.te_toca.join(' o ').toLowerCase()}
              </Link>
            </Typography>
          )}
        </Stack>
      </Stack>
    </Box>
  );
}
