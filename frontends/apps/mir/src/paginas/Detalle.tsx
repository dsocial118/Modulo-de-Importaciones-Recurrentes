import ArrowBack from '@mui/icons-material/ArrowBack';
import DescriptionOutlined from '@mui/icons-material/DescriptionOutlined';
import DownloadOutlined from '@mui/icons-material/DownloadOutlined';
import EditOutlined from '@mui/icons-material/EditOutlined';
import ExpandMore from '@mui/icons-material/ExpandMore';
import TableChartOutlined from '@mui/icons-material/TableChartOutlined';
import VisibilityOutlined from '@mui/icons-material/VisibilityOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  ListItemIcon,
  ListItemText,
  Menu,
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
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { useDetalle, useHallazgos } from '@mir/api';
import { EtiquetaDeEstado, Titulo } from '@mir/ui';
import { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ESTADO_DEL_ARCHIVO, SEVERIDAD, formaDe } from '../comun/estados';
import { filasEnPalabras, numero, plural } from '../comun/formato';
import { conFiltros } from '../comun/filtros';
import { useNombreDeArchivo } from '../comun/archivos';

const POR_PAGINA = 50;

/**
 * Las dos descargas de una importación, juntas en un botón «Descargar». Cada
 * una dice en dos renglones para qué sirve: no hace falta leer un párrafo
 * antes de elegir.
 */
function MenuDeDescargas({ marcado, informe }: { marcado: string; informe: string }) {
  const [ancla, setAncla] = useState<HTMLElement | null>(null);
  return (
    <>
      <Tooltip describeChild title="El archivo para corregir o el informe de la importación">
        <Button
          variant="outlined"
          startIcon={<DownloadOutlined />}
          endIcon={<ExpandMore />}
          onClick={(e) => setAncla(e.currentTarget)}
          aria-haspopup="menu"
          aria-expanded={!!ancla}
        >
          Descargar
        </Button>
      </Tooltip>
      <Menu anchorEl={ancla} open={!!ancla} onClose={() => setAncla(null)}>
        <MenuItem component="a" href={marcado} onClick={() => setAncla(null)}>
          <ListItemIcon>
            <TableChartOutlined fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Archivo para corregir"
            secondary="El Excel que subiste, con cada problema marcado. Se corrige ahí y se vuelve a subir."
            slotProps={{ secondary: { sx: { whiteSpace: 'normal', maxWidth: 320 } } }}
          />
        </MenuItem>
        <MenuItem component="a" href={informe} onClick={() => setAncla(null)}>
          <ListItemIcon>
            <DescriptionOutlined fontSize="small" />
          </ListItemIcon>
          <ListItemText
            primary="Informe de la importación"
            secondary="Cada problema con su estado, para seguirlo y contarlo."
            slotProps={{ secondary: { sx: { whiteSpace: 'normal', maxWidth: 320 } } }}
          />
        </MenuItem>
      </Menu>
    </>
  );
}

export function Detalle() {
  const nombreDe = useNombreDeArchivo();
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
        titulo={`${nombreDe(imp.archivo_codigo)} · ${imp.nombre_archivo ?? ''}`}
        volver={
          <Button size="small" startIcon={<ArrowBack />} onClick={() => navegar(volver)} sx={{ mb: 1, ml: -1 }}>
            Volver al resultado
          </Button>
        }
        subtitulo={
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
            <span>
              {filasEnPalabras(imp.filas_leidas, imp.filas_incorporadas)} ·{' '}
              {numero(imp.bloqueantes)} bloqueantes · {numero(imp.advertencias)} advertencias
            </span>
          </Stack>
        }
      />

      <Stack spacing={3}>
        {/* Textos cortos y el detalle al pasar el mouse: los botones largos
            ensuciaban la pantalla (26-09-2026). Primero lo que se hace en el
            sistema; las dos descargas, juntas en un solo botón. */}
        {hayHallazgos && (
          <Stack direction="row" sx={{ gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
            {imp.estado === 'VALIDA' && (
              <Tooltip
                describeChild
                title={
                  d.puede_corregir
                    ? 'Los datos que entraron, fila por fila: corregí las advertencias sin volver a subir el archivo.'
                    : 'Los datos que entraron, fila por fila. Tu rol los ve pero no los cambia.'
                }
              >
                <Button
                  variant="contained"
                  startIcon={d.puede_corregir ? <EditOutlined /> : <VisibilityOutlined />}
                  onClick={() => navegar(`/resultado/${id}/datos`)}
                >
                  {d.puede_corregir ? 'Ver y corregir datos' : 'Ver datos'}
                </Button>
              </Tooltip>
            )}
            <MenuDeDescargas marcado={d.descargas.marcado} informe={d.descargas.errores} />
            {/* Las observaciones sin resolver se ven desde acá, sin entrar. */}
            {d.observaciones_abiertas > 0 && (
              <EtiquetaDeEstado
                tono="critical"
                texto={plural(d.observaciones_abiertas, 'observación sin resolver', 'observaciones sin resolver')}
              />
            )}
          </Stack>
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
                        <TableCell>{x.tipo}</TableCell>
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
                  <Typography sx={{ fontWeight: 700, minWidth: 72, textAlign: 'right' }}>{plural(r.casos, 'caso', 'casos')}</Typography>
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
                        {/* Según el archivo, no «De quién»: lo que es una fila de este archivo. */}
                        <TableCell>{imp.que_es_una_fila ?? 'Registro'}</TableCell>
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
