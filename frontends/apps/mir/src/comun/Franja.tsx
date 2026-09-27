import CheckCircle from '@mui/icons-material/CheckCircle';
import ChevronRight from '@mui/icons-material/ChevronRight';
import RadioButtonChecked from '@mui/icons-material/RadioButtonChecked';
import RadioButtonUnchecked from '@mui/icons-material/RadioButtonUnchecked';
import { Box, Link, Stack, Tooltip, Typography, useMediaQuery, useTheme } from '@mui/material';
import { useFranja } from '@mir/api';
import { EtiquetaDeEstado } from '@mir/ui';
import { Fragment, useLayoutEffect, useState } from 'react';
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
  const chico = useMediaQuery(theme.breakpoints.down('md'));
  // Queda fija al bajar por la página, justo debajo de la barra (27-09-2026).
  // La barra cambia de alto con el ancho y con el aviso de la instancia: se mide.
  const [arriba, setArriba] = useState(64);
  useLayoutEffect(() => {
    const medir = () => setArriba(document.querySelector('header')?.getBoundingClientRect().height ?? 64);
    medir();
    window.addEventListener('resize', medir);
    return () => window.removeEventListener('resize', medir);
  }, []);
  const f = consulta.data;
  if (!f || !f.estado || !f.pasos.length) return null;

  const actual = f.pasos.findIndex((p) => p.actual);
  const irAlResultado = () => navegar(conFiltros('/resultado', f.periodo, f.jurisdiccion));

  return (
    <Box
      component="nav"
      aria-label="Avance del circuito"
      sx={{
        // De borde a borde del contenido y pegada a la barra: se come el margen
        // del contenido, que está antes del espaciador de la barra fija.
        mx: { xs: -2, md: -3 },
        // Dos píxeles menos: no tapa la franja ámbar del borde de la barra.
        mt: { xs: '-14px', md: '-22px' },
        mb: 2,
        position: 'sticky',
        top: arriba,
        zIndex: theme.zIndex.appBar - 1,
        px: { xs: 2, md: 3 },
        py: 0.75,
        borderBottom: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
          {f.jurisdiccion} · {f.periodo_nombre || f.periodo}
        </Typography>

        {chico ? (
          // En el teléfono, seis pasos no entran: se dice en cuál está.
          <Tooltip describeChild title={f.que_pasa}>
            <Typography variant="caption">
              Paso {actual + 1} de {f.pasos.length}: <strong>{f.pasos[actual]?.nombre}</strong>
            </Typography>
          </Tooltip>
        ) : (
          <Stack direction="row" spacing={0.25} sx={{ alignItems: 'center' }} component="ol" role="list">
            {f.pasos.map((p, i) => (
              <Fragment key={p.nombre}>
                {i > 0 && <ChevronRight fontSize="inherit" sx={{ color: 'text.disabled' }} aria-hidden />}
                <Tooltip describeChild title={p.actual ? `${f.estado_legible}: ${f.que_pasa}` : p.hecho ? 'Hecho' : 'Todavía no'}>
                  <Stack
                    component="li"
                    direction="row"
                    spacing={0.5}
                    aria-current={p.actual ? 'step' : undefined}
                    sx={{
                      alignItems: 'center',
                      listStyle: 'none',
                      px: 0.75,
                      py: 0.25,
                      borderRadius: 1,
                      bgcolor: p.actual ? 'primary.main' : 'transparent',
                      color: p.actual ? 'primary.contrastText' : p.hecho ? 'text.secondary' : 'text.disabled',
                    }}
                  >
                    {p.hecho ? (
                      <CheckCircle sx={{ fontSize: 14 }} />
                    ) : p.actual ? (
                      <RadioButtonChecked sx={{ fontSize: 14 }} />
                    ) : (
                      <RadioButtonUnchecked sx={{ fontSize: 14 }} />
                    )}
                    <Typography variant="caption" sx={{ fontWeight: p.actual ? 600 : 400, whiteSpace: 'nowrap' }}>
                      {p.nombre}
                    </Typography>
                  </Stack>
                </Tooltip>
              </Fragment>
            ))}
          </Stack>
        )}

        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', ml: { md: 'auto' }, flexWrap: 'wrap', rowGap: 0.5 }}>
          <Typography variant="caption" color="text.secondary">
            {archivosEnPalabras(f.estado, f.archivos_importados, f.archivos_esperados)}
          </Typography>
          {f.observaciones_abiertas > 0 && (
            <EtiquetaDeEstado
              tono="critical"
              texto={plural(f.observaciones_abiertas, 'observación sin resolver', 'observaciones sin resolver')}
            />
          )}
          {f.te_toca.length > 0 && (
            <Typography variant="caption">
              Te toca:{' '}
              <Link component="button" variant="caption" onClick={irAlResultado} sx={{ fontWeight: 600, verticalAlign: 'baseline' }}>
                {f.te_toca.join(' o ').toLowerCase()}
              </Link>
            </Typography>
          )}
        </Stack>
      </Stack>
    </Box>
  );
}
