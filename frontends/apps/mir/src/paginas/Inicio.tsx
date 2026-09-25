import ArrowForward from '@mui/icons-material/ArrowForward';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  CardHeader,
  LinearProgress,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  mensajeDeError,
  useArmarDemo,
  useBorrarImportaciones,
  useCambiarEstadoDelPeriodo,
  useInicio,
  type ArchivoDelPeriodo,
  type Sesion,
} from '@mir/api';
import { EtiquetaDeEstado, useAvisar, useConfirmar, type Tono } from '@mir/ui';
import type { MouseEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { conFiltros } from '../comun/Selectores';

// Cómo se muestra el estado de un archivo. Neutral a propósito: un archivo
// válido no se pinta de verde, porque el verde es de marca.
const ESTADO_DEL_ARCHIVO: Record<string, { texto: string; tono: Tono }> = {
  SIN_CARGAR: { texto: 'Sin cargar', tono: 'pending' },
  VALIDA: { texto: 'Importado', tono: 'info' },
  FALLIDA: { texto: 'Con errores', tono: 'attention' },
  ANULADA: { texto: 'Reemplazado', tono: 'pending' },
};

const ESTADO_DEL_PERIODO: Record<string, { texto: string; tono: Tono }> = {
  PREPARACION: { texto: 'En preparación', tono: 'pending' },
  ABIERTO: { texto: 'Abierto', tono: 'info' },
  CERRADO: { texto: 'Cerrado', tono: 'pending' },
};

const fecha = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString('es-AR');

const estadoDe = (a: ArchivoDelPeriodo) => ESTADO_DEL_ARCHIVO[a.estado] ?? { texto: a.estado, tono: 'pending' as Tono };

/** En el teléfono, cada archivo es una ficha: una tabla de seis columnas no entra. */
function FichaDeArchivo({ a }: { a: ArchivoDelPeriodo }) {
  const e = estadoDe(a);
  return (
    <Box sx={{ py: 1.5, borderTop: 1, borderColor: 'divider' }}>
      <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'flex-start', gap: 1 }}>
        <Box>
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            {a.codigo}
          </Typography>
          {a.nombre && (
            <Typography variant="caption" color="text.secondary">
              {a.nombre}
            </Typography>
          )}
        </Box>
        <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
      </Stack>
      <Typography variant="caption" color="text.secondary" component="div" sx={{ mt: 0.5 }}>
        {a.obligatorio ? 'Obligatorio' : 'Opcional'} · {a.campos} campos · {a.reglas} reglas
      </Typography>
      {a.filas != null && (
        <Box sx={{ mt: 0.75 }}>
          <Filas a={a} alinear="flex-start" />
        </Box>
      )}
    </Box>
  );
}

function Filas({ a, alinear = 'flex-end' }: { a: ArchivoDelPeriodo; alinear?: 'flex-end' | 'flex-start' }) {
  if (a.filas == null) return <Typography color="text.secondary">—</Typography>;
  return (
    <Stack direction="row" spacing={1} sx={{ justifyContent: alinear, alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
      <span>{a.filas} filas</span>
      {a.bloqueantes > 0 && <EtiquetaDeEstado tono="attention" texto={`${a.bloqueantes} bloqueantes`} />}
      {a.advertencias > 0 && <EtiquetaDeEstado tono="info" texto={`${a.advertencias} advertencias`} />}
    </Stack>
  );
}

/**
 * El período se abre y se cierra para todas las jurisdicciones a la vez: lo
 * decide el nivel nacional. Al lado, las dos herramientas de prueba, que van
 * juntas porque son un par: una limpia para volver a probar y la otra deja algo
 * que mostrar.
 */
function HerramientasDelAdministrador({ periodo, estado }: { periodo: string; estado: string }) {
  const cambiarEstado = useCambiarEstadoDelPeriodo();
  const armar = useArmarDemo();
  const borrar = useBorrarImportaciones();
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  const alTerminar = {
    onSuccess: (r: { mensaje: string; aviso?: string }) => avisar({ texto: [r.mensaje, r.aviso].filter(Boolean).join(' ') }),
    onError: (e: unknown) => avisar({ texto: mensajeDeError(e), error: true }),
  };
  const pasarA = async (nuevo: string, titulo: string, texto: string) => {
    if ((await confirmar({ titulo, texto, confirmar: titulo })) === null) return;
    cambiarEstado.mutate({ codigo: periodo, estado: nuevo }, alTerminar);
  };
  const ocupado = cambiarEstado.isPending || armar.isPending || borrar.isPending;

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ alignItems: { md: 'center' } }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography sx={{ fontWeight: 500 }}>Administración del período</Typography>
            <Typography variant="body2" color="text.secondary">
              Las herramientas de prueba borran o arman datos de ejemplo y no forman parte del sistema definitivo.
            </Typography>
          </Box>
          <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1 }}>
            {estado !== 'ABIERTO' && (
              <Button
                variant="contained"
                disabled={ocupado}
                onClick={() => pasarA('ABIERTO', 'Abrir el período', 'Las jurisdicciones van a poder importar, y la estructura queda congelada.')}
              >
                Abrir el período
              </Button>
            )}
            {estado === 'ABIERTO' && (
              <>
                <Button
                  variant="outlined"
                  disabled={ocupado}
                  onClick={() => pasarA('CERRADO', 'Cerrar el período', 'Con el período cerrado ninguna jurisdicción puede importar.')}
                >
                  Cerrar el período
                </Button>
                <Button
                  variant="outlined"
                  disabled={ocupado}
                  onClick={() =>
                    pasarA(
                      'PREPARACION',
                      'Volver a preparación',
                      'Habilita a cambiar la definición. Es una herramienta de prueba: en el sistema real, con el período abierto, la definición no se toca.',
                    )
                  }
                >
                  Volver a preparación (prueba)
                </Button>
              </>
            )}
            <Button
              variant="outlined"
              disabled={ocupado}
              onClick={async () => {
                const ok = await confirmar({
                  titulo: 'Armar demostración',
                  texto: 'Se borrará lo que haya y se armará una presentación completa, con advertencias para corregir.',
                  confirmar: 'Armar',
                });
                if (ok !== null) armar.mutate(undefined, alTerminar);
              }}
            >
              Armar demostración
            </Button>
            <Button
              variant="outlined"
              color="warning"
              disabled={ocupado}
              onClick={async () => {
                const ok = await confirmar({
                  titulo: 'Borrar importaciones',
                  texto: 'Se borrarán TODAS las importaciones de TODAS las jurisdicciones. Existe únicamente para hacer pruebas.',
                  confirmar: 'Borrar todo',
                });
                if (ok !== null) borrar.mutate(undefined, alTerminar);
              }}
            >
              Borrar importaciones
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}

export function Inicio({ sesion }: { sesion: Sesion }) {
  const navegar = useNavigate();
  const [params, setParams] = useSearchParams();
  const chico = useMediaQuery(useTheme().breakpoints.down('sm'));
  const inicio = useInicio(params.get('periodo'), params.get('jurisdiccion'));

  const cambiar = (clave: string, valor: string) => {
    const nuevos = new URLSearchParams(params);
    if (valor) nuevos.set(clave, valor);
    else nuevos.delete(clave);
    setParams(nuevos);
  };

  if (inicio.isPending) return <LinearProgress aria-label="Cargando" />;
  if (inicio.isError) return <Alert severity="error">No se pudo cargar el inicio.</Alert>;

  const d = inicio.data;
  const periodo = d.periodo;
  const estadoPeriodo = periodo ? ESTADO_DEL_PERIODO[periodo.estado] : undefined;
  const accesos = sesion.menu.filter((m) => m.clave !== 'inicio');
  const destino = (ruta: string) => conFiltros(ruta.replace('/v2/mir', '') || '/', periodo?.codigo, d.jurisdiccion);
  const avance = d.avance.total ? Math.round((d.avance.cargados * 100) / d.avance.total) : 0;

  return (
    <Stack spacing={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ alignItems: { sm: 'center' } }}>
        <Typography variant="h5" component="h1" sx={{ fontWeight: 700, flexGrow: 1 }}>
          Inicio
        </Typography>
        {d.jurisdicciones.length > 0 && (
          <TextField
            select
            size="small"
            label="Jurisdicción"
            value={d.jurisdiccion ?? ''}
            onChange={(e) => cambiar('jurisdiccion', e.target.value)}
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">
              <em>Elegir…</em>
            </MenuItem>
            {d.jurisdicciones.map((j) => (
              <MenuItem key={j} value={j}>
                {j}
              </MenuItem>
            ))}
          </TextField>
        )}
        <TextField
          select
          size="small"
          label="Período"
          value={periodo?.codigo ?? ''}
          onChange={(e) => cambiar('periodo', e.target.value)}
          sx={{ minWidth: 160 }}
        >
          {d.periodos.map((p) => (
            <MenuItem key={p.codigo} value={p.codigo}>
              {p.codigo}
            </MenuItem>
          ))}
        </TextField>
      </Stack>

      {periodo && estadoPeriodo && (
        <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', flexWrap: 'wrap' }}>
          <EtiquetaDeEstado tono={estadoPeriodo.tono} texto={estadoPeriodo.texto} />
          <Typography variant="body2" color="text.secondary">
            Corte del {fecha(periodo.fecha_desde)} al {fecha(periodo.fecha_hasta)}
          </Typography>
        </Stack>
      )}

      {periodo && periodo.estado !== 'ABIERTO' && (
        <Alert severity="info">
          El período {periodo.codigo} está {estadoPeriodo?.texto.toLowerCase()}.{' '}
          {periodo.estado === 'PREPARACION'
            ? 'Todavía no está habilitado para cargar, y la estructura se puede modificar.'
            : 'No se admiten más cargas.'}
        </Alert>
      )}

      {sesion.permisos.administrar && periodo && <HerramientasDelAdministrador periodo={periodo.codigo} estado={periodo.estado} />}

      <Card variant="outlined">
        <CardHeader
          title={`Estado de la presentación — ${d.jurisdiccion ?? 'elegí una jurisdicción'}`}
          slotProps={{ title: { variant: 'subtitle1', sx: { fontWeight: 500 } } }}
          action={
            d.presentacion && (
              <Box sx={{ pt: 1, pr: 1 }}>
                <EtiquetaDeEstado tono="info" texto={d.presentacion.estado_legible} />
              </Box>
            )
          }
        />
        <CardContent sx={{ pt: 0 }}>
          {d.archivos.length === 0 ? (
            <Typography color="text.secondary">Todavía no hay archivos definidos para este período.</Typography>
          ) : (
            <Stack spacing={2}>
              <Box>
                <Stack direction="row" sx={{ justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2" color="text.secondary">
                    Archivos importados
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {d.avance.cargados} de {d.avance.total}
                  </Typography>
                </Stack>
                <LinearProgress
                  variant="determinate"
                  value={avance}
                  aria-label={`${d.avance.cargados} de ${d.avance.total} archivos importados`}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>
              {chico ? (
                <Box>
                  {d.archivos.map((a) => (
                    <FichaDeArchivo key={a.codigo} a={a} />
                  ))}
                </Box>
              ) : (
              <TableContainer>
                <Table size="small" aria-label="Archivos del período">
                  <TableHead>
                    <TableRow>
                      <TableCell>Archivo</TableCell>
                      <TableCell align="center">Obligatorio</TableCell>
                      <TableCell align="right">Campos</TableCell>
                      <TableCell align="right">Reglas</TableCell>
                      <TableCell>Estado</TableCell>
                      <TableCell align="right">Filas</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {d.archivos.map((a) => {
                      const e = estadoDe(a);
                      return (
                        <TableRow key={a.codigo} hover>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {a.codigo}
                            </Typography>
                            {a.nombre && (
                              <Typography variant="caption" color="text.secondary">
                                {a.nombre}
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell align="center">{a.obligatorio ? 'Sí' : '—'}</TableCell>
                          <TableCell align="right">{a.campos}</TableCell>
                          <TableCell align="right">{a.reglas}</TableCell>
                          <TableCell>
                            <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
                          </TableCell>
                          <TableCell align="right">
                            <Filas a={a} />
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
              )}
            </Stack>
          )}
        </CardContent>
      </Card>

      {accesos.length > 0 && (
        <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(3, 1fr)' } }}>
          {accesos.map((s) => (
            <Card key={s.clave} variant="outlined">
              {/* Se va con el mismo período y la misma jurisdicción. Lo que siga en la
                  versión actual se abre allá. */}
              <CardActionArea
                href={s.en_v2 ? `/v2/mir${destino(s.ruta)}` : `${s.ruta}?periodo=${periodo?.codigo ?? ''}`}
                onClick={(e: MouseEvent) => {
                  if (!s.en_v2 || e.ctrlKey || e.metaKey) return;
                  e.preventDefault();
                  navegar(destino(s.ruta));
                }}
                sx={{ height: '100%' }}
              >
                <CardContent>
                  <Stack direction="row" sx={{ alignItems: 'center', justifyContent: 'space-between' }}>
                    <Typography sx={{ fontWeight: 500 }}>{s.etiqueta}</Typography>
                    <ArrowForward fontSize="small" color="primary" />
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {s.detalle}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          ))}
        </Box>
      )}
    </Stack>
  );
}
