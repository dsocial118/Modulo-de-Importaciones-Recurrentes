import ArrowBack from '@mui/icons-material/ArrowBack';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  MenuItem,
  Pagination,
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
import { useDetalle, useHallazgos } from '@mir/api';
import { EtiquetaDeEstado, Titulo } from '@mir/ui';
import { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ESTADO_DEL_ARCHIVO, SEVERIDAD, formaDe } from '../comun/estados';
import { numero, plural } from '../comun/formato';
import { conFiltros } from '../comun/filtros';

const POR_PAGINA = 50;

export function Detalle() {
  const id = Number(useParams().id);
  const navegar = useNavigate();
  const [params, setParams] = useSearchParams();
  const chico = useMediaQuery(useTheme().breakpoints.down('md'));
  const severidad = params.get('severidad') ?? '';
  const hoja = params.get('hoja') ?? '';
  const pagina = Number(params.get('page') ?? 1);
  // Se busca al dejar de escribir, no con cada letra.
  const [buscar, setBuscar] = useState(params.get('buscar') ?? '');
  useEffect(() => {
    const t = setTimeout(() => {
      if ((params.get('buscar') ?? '') !== buscar) poner({ buscar, page: '' });
    }, 400);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [buscar]);

  const detalle = useDetalle(id);
  const hallazgos = useHallazgos(id, {
    severidad,
    hoja,
    buscar: params.get('buscar'),
    page: pagina,
    page_size: POR_PAGINA,
  });

  function poner(cambios: Record<string, string>) {
    const nuevos = new URLSearchParams(params);
    for (const [k, v] of Object.entries(cambios)) {
      if (v) nuevos.set(k, v);
      else nuevos.delete(k);
    }
    setParams(nuevos, { replace: true });
  }

  if (detalle.isPending) return <LinearProgress aria-label="Cargando" />;
  if (detalle.isError) return <Alert severity="error">No existe esa importación, o no es de tu jurisdicción.</Alert>;
  const d = detalle.data;
  const imp = d.importacion;
  const e = formaDe(ESTADO_DEL_ARCHIVO, imp.estado);
  const volver = conFiltros('/resultado', imp.periodo, imp.jurisdiccion);
  const hayHallazgos = (imp.bloqueantes ?? 0) > 0 || (imp.advertencias ?? 0) > 0;
  const paginas = hallazgos.data ? Math.max(1, Math.ceil(hallazgos.data.count / POR_PAGINA)) : 1;

  return (
    <>
      <Titulo
        titulo={`${imp.archivo_codigo} · ${imp.nombre_archivo ?? ''}`}
        volver={
          <Button size="small" startIcon={<ArrowBack />} onClick={() => navegar(volver)} sx={{ mb: 1, ml: -1 }}>
            Volver al resultado
          </Button>
        }
        subtitulo={
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
            <span>
              {numero(imp.filas_leidas)} filas · {numero(imp.filas_incorporadas)} incorporadas ·{' '}
              {numero(imp.bloqueantes)} bloqueantes · {numero(imp.advertencias)} advertencias
            </span>
          </Stack>
        }
      />

      <Stack spacing={3}>
        {hayHallazgos && (
          <Stack direction={{ xs: 'column', sm: 'row' }} sx={{ gap: 1, flexWrap: 'wrap', alignItems: { sm: 'center' } }}>
            <Button variant="contained" href={d.descargas.marcado}>
              Descargar mi archivo con los errores marcados
            </Button>
            {d.puede_editar && (
              <Button variant="outlined" onClick={() => navegar(`/resultado/${id}/datos`)}>
                Corregir datos en el sistema
              </Button>
            )}
            <Button variant="outlined" href={d.descargas.errores}>
              Descargar la lista de errores y advertencias
            </Button>
          </Stack>
        )}
        {hayHallazgos && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: -1.5 }}>
            El primero es el mismo Excel que subiste, con las celdas señaladas y la explicación en cada una. Es el que
            conviene para corregir.
          </Typography>
        )}

        {imp.estado === 'FALLIDA' && (
          <Alert severity="error">
            <strong>El archivo no se importó.</strong> La importación es restrictiva: no se incorporó ninguna de sus
            filas.
          </Alert>
        )}

        {d.errores_archivo.length > 0 && (
          <Card variant="outlined">
            <CardHeader
              title="Problemas del archivo"
              subheader="No corresponden a un campo: impiden interpretar el archivo o su estructura."
              slotProps={{ title: { variant: 'subtitle1', sx: { fontWeight: 500 } } }}
            />
            <CardContent sx={{ pt: 0 }}>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Hoja</TableCell>
                      <TableCell align="right">Fila</TableCell>
                      <TableCell>Se esperaba</TableCell>
                      <TableCell>Se encontró</TableCell>
                      <TableCell>Detalle</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {d.errores_archivo.map((x, i) => (
                      <TableRow key={i}>
                        <TableCell sx={{ fontFamily: 'monospace' }}>{x.tipo}</TableCell>
                        <TableCell>{x.hoja ?? '—'}</TableCell>
                        <TableCell align="right">{x.numero_fila ?? '—'}</TableCell>
                        <TableCell sx={{ fontFamily: 'monospace' }}>{x.esperado ?? '—'}</TableCell>
                        <TableCell sx={{ fontFamily: 'monospace' }}>{x.encontrado ?? '—'}</TableCell>
                        <TableCell>{x.descripcion}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 2, alignItems: { sm: 'center' } }}>
                <Button variant="outlined" size="small" onClick={() => navegar(conFiltros('/plantillas', imp.periodo))}>
                  Descargar la plantilla vigente
                </Button>
                <Typography variant="body2" color="text.secondary">
                  Suele pasar cuando se usa una plantilla de un período anterior, o cuando se agregaron o renombraron
                  columnas.
                </Typography>
              </Stack>
            </CardContent>
          </Card>
        )}

        {d.resumen.length > 0 && (
          <Card variant="outlined">
            <CardHeader title="Reglas incumplidas, por tipo" slotProps={{ title: { variant: 'subtitle1', sx: { fontWeight: 500 } } }} />
            <CardContent sx={{ pt: 0 }}>
              {d.resumen.map((r) => (
                <Stack key={`${r.codigo}-${r.severidad}`} direction="row" spacing={2} sx={{ py: 0.5, alignItems: 'baseline' }}>
                  <Typography sx={{ fontWeight: 700, minWidth: 40, textAlign: 'right' }}>{r.casos}</Typography>
                  <EtiquetaDeEstado tono={formaDe(SEVERIDAD, r.severidad).tono} texto={formaDe(SEVERIDAD, r.severidad).texto} />
                  <Typography variant="body2" color="text.secondary" sx={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {r.ejemplo}
                  </Typography>
                </Stack>
              ))}
            </CardContent>
          </Card>
        )}

        {d.resumen.length > 0 && (
          <Card variant="outlined">
            <CardContent>
              <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ mb: 2 }}>
                {/* Ofrecer un filtro por algo que no varía no filtra nada. */}
                {!d.severidad_unica && (
                  <TextField
                    select
                    size="small"
                    label="Severidad"
                    value={severidad}
                    onChange={(ev) => poner({ severidad: ev.target.value, page: '' })}
                    sx={{ minWidth: 160 }}
                  >
                    <MenuItem value="">Todas</MenuItem>
                    <MenuItem value="BLOQUEANTE">Bloqueantes</MenuItem>
                    <MenuItem value="ADVERTENCIA">Advertencias</MenuItem>
                  </TextField>
                )}
                {d.hojas.length > 1 && (
                  <TextField
                    select
                    size="small"
                    label="Hoja"
                    value={hoja}
                    onChange={(ev) => poner({ hoja: ev.target.value, page: '' })}
                    sx={{ minWidth: 160 }}
                  >
                    <MenuItem value="">Todas</MenuItem>
                    {d.hojas.map((h) => (
                      <MenuItem key={h} value={h}>
                        {h}
                      </MenuItem>
                    ))}
                  </TextField>
                )}
                <TextField
                  size="small"
                  label="Buscar"
                  placeholder="campo o texto del error"
                  value={buscar}
                  onChange={(ev) => setBuscar(ev.target.value)}
                  sx={{ flexGrow: 1, maxWidth: 360 }}
                />
              </Stack>

              <Typography variant="body2" color="text.secondary" gutterBottom>
                {hallazgos.data ? plural(hallazgos.data.count, 'resultado', 'resultados') : '…'}
                {d.severidad_unica && ` · todos de severidad ${formaDe(SEVERIDAD, d.severidad_unica).texto.toLowerCase()}`}
              </Typography>
              {hallazgos.isFetching && <LinearProgress sx={{ mb: 1 }} />}

              {chico ? (
                <Box>
                  {hallazgos.data?.results.map((h, i) => (
                    <Box key={i} sx={{ py: 1.5, borderTop: 1, borderColor: 'divider' }}>
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        Fila {h.numero_fila ?? '—'} · {h.nombre_campo ?? '—'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" component="div">
                        {h.identificador_registro ?? ''} {h.nombre_hoja ? `· ${h.nombre_hoja}` : ''}
                      </Typography>
                      <Typography variant="body2">{h.descripcion}</Typography>
                      {h.valor_encontrado && (
                        <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                          Valor: {h.valor_encontrado}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              ) : (
                <TableContainer>
                  <Table size="small" aria-label="Hallazgos">
                    <TableHead>
                      <TableRow>
                        <TableCell align="right">Fila</TableCell>
                        <TableCell>De quién</TableCell>
                        <TableCell>Hoja</TableCell>
                        <TableCell>Campo</TableCell>
                        {!d.severidad_unica && <TableCell>Severidad</TableCell>}
                        <TableCell>Valor</TableCell>
                        <TableCell>Qué pasa</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {hallazgos.data?.results.map((h, i) => (
                        <TableRow key={i} hover>
                          <TableCell align="right" sx={{ fontWeight: 500 }}>
                            {h.numero_fila ?? '—'}
                          </TableCell>
                          <TableCell>{h.identificador_registro ?? '—'}</TableCell>
                          <TableCell>{h.nombre_hoja ?? '—'}</TableCell>
                          <TableCell>{h.nombre_campo ?? '—'}</TableCell>
                          {!d.severidad_unica && <TableCell>{formaDe(SEVERIDAD, h.severidad).texto}</TableCell>}
                          <TableCell sx={{ fontFamily: 'monospace', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {h.valor_encontrado ?? '—'}
                          </TableCell>
                          <TableCell>{h.descripcion}</TableCell>
                        </TableRow>
                      ))}
                      {hallazgos.data?.count === 0 && (
                        <TableRow>
                          <TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                            No hay problemas con esos filtros.
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
              {paginas > 1 && (
                <Pagination
                  sx={{ mt: 2 }}
                  count={paginas}
                  page={pagina}
                  onChange={(_, n) => poner({ page: String(n) })}
                  color="primary"
                />
              )}
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                El número de fila es el del Excel, tal como lo ves al abrirlo.
              </Typography>
            </CardContent>
          </Card>
        )}
      </Stack>
    </>
  );
}
