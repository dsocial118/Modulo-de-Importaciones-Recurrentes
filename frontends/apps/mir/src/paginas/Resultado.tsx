import DescriptionOutlined from '@mui/icons-material/DescriptionOutlined';
import EditOutlined from '@mui/icons-material/EditOutlined';
import ExpandMore from '@mui/icons-material/ExpandMore';
import FactCheckOutlined from '@mui/icons-material/FactCheckOutlined';
import GridOnOutlined from '@mui/icons-material/GridOnOutlined';
import UploadFileOutlined from '@mui/icons-material/UploadFileOutlined';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  LinearProgress,
  MenuItem,
  Stack,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  mensajeDeError,
  useAccion,
  useHistorialDeLaPresentacion,
  useObservar,
  useRegistrarExpediente,
  useResultado,
  useSesion,
  type Accion,
  type ArchivoDelResultado,
  type Resultado as TResultado,
} from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar, useConfirmar } from '@mir/ui';
import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ESTADO_DEL_ARCHIVO, SEVERIDAD, formaDe, tonoDeLaPresentacion } from '../comun/estados';
import { fecha, fechaHora, filasEnPalabras, plural } from '../comun/formato';
import { SelectorDeJurisdiccion, SelectorDePeriodo } from '../comun/Selectores';
import { conFiltros, useFiltros } from '../comun/filtros';
import { TarjetaDeObservacion } from '../comun/Observaciones';
import { dondeEsta } from '../comun/ubicacion';
import { sinRepetir, useNombreDeArchivo } from '../comun/archivos';
import { Datos } from './Datos';

/**
 * La presentación de una provincia, en cuatro solapas: Resumen · Datos ·
 * Observaciones · Historial (maqueta aprobada el 27-09-2026). Reemplaza al
 * resultado con enlaces sueltos: la ven igual la provincia y el nivel
 * nacional, y los botones del circuito quedan siempre en el mismo lugar.
 */

// Las acciones que no tienen vuelta atrás se confirman; el resto, no.
const A_CONFIRMAR: Record<string, string> = {
  cerrar_carga: 'Declara terminada la carga del período y la envía a revisión nacional.',
  presentar:
    'Es el acto formal de presentación del período. Genera el comprobante para remitir por GDE, y después los datos ya no se modifican.',
  reabrir_carga: 'La revisión anterior queda sin efecto y la presentación vuelve a carga.',
  habilitar: 'Concluye la revisión y habilita a la jurisdicción a presentar formalmente.',
};

// Desde que la provincia cierra la carga hasta que se habilita: igual que el servidor.
const OBSERVABLES = ['CERRADA', 'EN_REVISION', 'OBSERVADA', 'SUBSANADA'];

const SOLAPAS = ['resumen', 'datos', 'observaciones', 'historial'] as const;
type Solapa = (typeof SOLAPAS)[number];

function Archivo({
  a,
  puedeEditar,
  alVerDatos,
}: {
  a: ArchivoDelResultado;
  puedeEditar: boolean;
  alVerDatos: (importacion: number) => void;
}) {
  const nombreDe = useNombreDeArchivo();
  const navegar = useNavigate();
  const imp = a.importacion;
  const e = formaDe(ESTADO_DEL_ARCHIVO, a.estado);
  const hayHallazgos = !!imp && (imp.bloqueantes > 0 || imp.advertencias > 0);
  const [conResumen, setConResumen] = useState(false);
  return (
    <Box sx={{ py: 2, borderTop: 1, borderColor: 'divider' }}>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ alignItems: { md: 'flex-start' } }}>
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <Typography sx={{ fontWeight: 700 }}>{nombreDe(a.codigo)}</Typography>
            <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
          </Stack>
          {/* Nombre y cifras en un solo renglón (27-09-2026). */}
          <Typography variant="body2" color="text.secondary">
            {sinRepetir(a.nombre, nombreDe(a.codigo))}
            {imp && (
              <Box component="span" sx={{ color: 'text.primary' }}>
                {sinRepetir(a.nombre, nombreDe(a.codigo)) ? ' · ' : ''}
                {filasEnPalabras(imp.filas_leidas, imp.filas_incorporadas)}
                {imp.bloqueantes > 0 && <> · <strong>{plural(imp.bloqueantes, 'bloqueante', 'bloqueantes')}</strong></>}
                {imp.advertencias > 0 && <> · {plural(imp.advertencias, 'advertencia', 'advertencias')}</>}
              </Box>
            )}
            {a.resumen.length > 0 && (
              <Button
                size="small"
                onClick={() => setConResumen((v) => !v)}
                aria-expanded={conResumen}
                sx={{ ml: 1, py: 0, minWidth: 0, verticalAlign: 'baseline' }}
              >
                {conResumen ? 'Ocultar reglas incumplidas' : 'Ver reglas incumplidas'}
              </Button>
            )}
          </Typography>
          {/* El resumen por tipo de problema, plegado: se abre si se pide. */}
          {conResumen && a.resumen.length > 0 && (
            <Stack direction="row" sx={{ mt: 1, flexWrap: 'wrap', gap: 0.75 }}>
              {a.resumen.map((r) => (
                <Chip
                  key={`${r.codigo}-${r.severidad}`}
                  size="small"
                  variant="outlined"
                  label={`${plural(r.casos, 'caso', 'casos')}: ${r.ejemplo ?? r.codigo}`}
                  title={`${formaDe(SEVERIDAD, r.severidad).texto}: ${r.ejemplo ?? ''}`}
                  sx={{ maxWidth: '100%' }}
                />
              ))}
            </Stack>
          )}
        </Box>
        {imp && (
          <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1, justifyContent: { md: 'flex-end' } }}>
            {/* El detalle sólo si hay algo que detallar: sobre un archivo que entró limpio, estaría vacío. */}
            {hayHallazgos && (
              <Button size="small" variant="outlined" startIcon={<FactCheckOutlined />} onClick={() => navegar(`/resultado/${imp.id}`)}>
                Ver detalle
              </Button>
            )}
            {/* Abre la solapa Datos en este archivo. */}
            {a.importada && (
              <Button size="small" variant="outlined" startIcon={<EditOutlined />} onClick={() => alVerDatos(imp.id)}>
                {puedeEditar ? 'Corregir datos' : 'Ver datos'}
              </Button>
            )}
            {/* Los informes se bajan cuantas veces haga falta, no sólo desde el aviso de la carga. */}
            {hayHallazgos && (
              <>
                <Tooltip title="La lista de errores y advertencias, en Excel">
                  <Button size="small" href={`/api/mir/importaciones/${imp.id}/errores.xlsx`} aria-label="Descargar la lista de errores">
                    <GridOnOutlined fontSize="small" />
                  </Button>
                </Tooltip>
                <Tooltip title="El archivo que se subió, con las celdas marcadas">
                  <Button size="small" href={`/api/mir/importaciones/${imp.id}/marcado.xlsx`} aria-label="Descargar el archivo marcado">
                    <DescriptionOutlined fontSize="small" />
                  </Button>
                </Tooltip>
              </>
            )}
          </Stack>
        )}
      </Stack>
    </Box>
  );
}

function SolapaResumen({ d, alVerDatos }: { d: TResultado; alVerDatos: (importacion: number) => void }) {
  const navegar = useNavigate();
  const expediente = useRegistrarExpediente();
  const avisar = useAvisar();
  const [numeroGde, setNumeroGde] = useState('');
  const p = d.presentacion;
  return (
    <Stack spacing={2}>
      {d.totales.bloqueantes > 0 && (
        <Alert severity="warning">
          Hay <strong>{plural(d.totales.bloqueantes, 'error bloqueante', 'errores bloqueantes')}</strong>. La importación
          es restrictiva: <strong>no se incorporó ninguna fila</strong> de esos archivos. Se corrige el Excel y se vuelve a
          importar.
        </Alert>
      )}
      <Card variant="outlined">
        <CardContent sx={{ pt: 0, '&:last-child': { pb: 0 }, '& > :first-of-type': { borderTop: 0 } }}>
          {d.archivos.map((a) => (
            <Archivo key={a.codigo} a={a} puedeEditar={d.puede_editar} alVerDatos={alVerDatos} />
          ))}
        </CardContent>
      </Card>
      <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
        {d.puede_editar && (
          <Button
            variant="outlined"
            startIcon={<UploadFileOutlined />}
            onClick={() => navegar(conFiltros('/cargar', d.periodo?.codigo, d.jurisdiccion))}
          >
            Cargar archivos
          </Button>
        )}
        {p && (p.estado === 'PRESENTADA' || p.estado === 'CONSOLIDADA') && (
          <Button variant="outlined" onClick={() => navegar(`/presentacion/${p.id}/comprobante`)}>
            Ver comprobante
          </Button>
        )}
        {!d.acciones.length && p?.estado === 'EN_CARGA' && !d.listo && (
          <Typography variant="body2" color="text.secondary">
            Faltan archivos obligatorios por importar. El responsable provincial podrá cerrar la carga cuando estén todos.
          </Typography>
        )}
      </Stack>
      {p?.estado === 'PRESENTADA' && d.puede_presentar && !p.expediente && (
        <Card variant="outlined">
          <CardHeader title="Número de expediente" slotProps={{ title: { variant: 'subtitle1', sx: { fontWeight: 500 } } }} />
          <CardContent sx={{ pt: 0 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              El comprobante se remite por GDE. Obtenido el número de expediente, se incorpora acá. Su ausencia no impide
              la consolidación: es un resguardo documental de la jurisdicción.
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }}>
              <TextField
                size="small"
                label="Número de expediente"
                placeholder="EX-2026-00000000-APN-..."
                value={numeroGde}
                onChange={(e) => setNumeroGde(e.target.value)}
                sx={{ maxWidth: 360 }}
                fullWidth
              />
              <Button
                variant="contained"
                disabled={!numeroGde.trim() || expediente.isPending}
                onClick={() =>
                  expediente.mutate(
                    { presentacion: p.id, expediente: numeroGde.trim() },
                    {
                      onSuccess: (r) => avisar({ texto: r.mensaje }),
                      onError: (e) => avisar({ texto: mensajeDeError(e), error: true }),
                    },
                  )
                }
              >
                Registrar
              </Button>
            </Stack>
          </CardContent>
        </Card>
      )}
    </Stack>
  );
}

function SolapaDatos({
  d,
  importacion,
  alElegir,
}: {
  d: TResultado;
  importacion: number | null;
  alElegir: (importacion: number) => void;
}) {
  const nombreDe = useNombreDeArchivo();
  const importados = d.archivos.filter((a) => a.importada && a.importacion);
  if (!importados.length)
    return (
      <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
        Todavía no hay archivos importados.
      </Typography>
    );
  const elegida = importados.some((a) => a.importacion!.id === importacion) ? importacion! : importados[0].importacion!.id;
  // El archivo se elige en la misma fila que los filtros de la grilla: arriba
  // ya están el título y las solapas, y todo junto empujaba la grilla.
  const selector = (
    <TextField
      select
      size="small"
      label="Archivo"
      value={elegida}
      onChange={(e) => alElegir(Number(e.target.value))}
      sx={{ minWidth: 240 }}
    >
        {importados.map((a) => (
          <MenuItem key={a.codigo} value={a.importacion!.id}>
            {nombreDe(a.codigo)}
          </MenuItem>
        ))}
    </TextField>
  );
  // La clave es la importación: al cambiar de archivo, la grilla arranca de cero.
  return <Datos key={elegida} importacion={elegida} incrustado selectorDeArchivo={selector} />;
}

function SolapaObservaciones({ d, puedeObservar }: { d: TResultado; puedeObservar: boolean }) {
  const observar = useObservar();
  const avisar = useAvisar();
  const [texto, setTexto] = useState('');
  const p = d.presentacion;
  const abiertas = d.observaciones.filter((o) => o.estado === 'ABIERTA');
  const resueltas = d.observaciones.filter((o) => o.estado !== 'ABIERTA');
  const permisos = { puedeObservar: false, puedeResponder: d.puede_responder };
  return (
    <Stack spacing={2}>
      {d.observaciones.length === 0 && (
        <Typography color="text.secondary" sx={{ py: 2 }}>
          No hay observaciones. El revisor observa cada dato desde la solapa Datos, una vez que la provincia cierra la
          carga.
        </Typography>
      )}
      {abiertas.length > 0 && (
        <Box>
          <Typography sx={{ fontWeight: 700, mb: 1, color: 'error.dark' }}>Sin resolver: {abiertas.length}</Typography>
          {abiertas.map((o) => (
            <TarjetaDeObservacion key={o.id} o={o} permisos={permisos} ubicacion={dondeEsta(o) || undefined} />
          ))}
        </Box>
      )}
      {resueltas.length > 0 && (
        <Accordion variant="outlined" disableGutters defaultExpanded={!abiertas.length}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="body2">Resueltas ({resueltas.length})</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {resueltas.map((o) => (
              <TarjetaDeObservacion key={o.id} o={o} permisos={permisos} ubicacion={dondeEsta(o) || undefined} />
            ))}
          </AccordionDetails>
        </Accordion>
      )}
      {/* Una observación sobre la presentación en general, no sobre un dato. */}
      {puedeObservar && p && (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ maxWidth: 760 }}>
          <TextField
            size="small"
            fullWidth
            label="Observación sobre la presentación en general"
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
          />
          <Button
            variant="outlined"
            disabled={!texto.trim() || observar.isPending}
            onClick={() =>
              observar.mutate(
                { presentacion: p.id, texto },
                {
                  onSuccess: (r) => {
                    setTexto('');
                    avisar({ texto: r.mensaje });
                  },
                  onError: (e) => avisar({ texto: mensajeDeError(e), error: true }),
                },
              )
            }
          >
            Observar
          </Button>
        </Stack>
      )}
    </Stack>
  );
}

function SolapaHistorial({ presentacion }: { presentacion: number | null }) {
  const consulta = useHistorialDeLaPresentacion(presentacion);
  if (!presentacion)
    return <Typography color="text.secondary">Todavía no hay una presentación para este período.</Typography>;
  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar el historial.</Alert>;
  const filas = consulta.data.filas;
  if (!filas.length)
    return <Typography color="text.secondary">Todavía no se corrigió ningún dato dentro del sistema.</Typography>;
  return (
    <Card variant="outlined">
      <TableContainer>
        <Table size="small" aria-label="Historial de cambios de la presentación">
          <TableHead>
            <TableRow>
              <TableCell>Cuándo</TableCell>
              <TableCell>Quién</TableCell>
              <TableCell>Archivo</TableCell>
              <TableCell>De quién</TableCell>
              <TableCell>Campo</TableCell>
              <TableCell>Antes</TableCell>
              <TableCell>Después</TableCell>
              <TableCell>Motivo</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filas.map((h, i) => (
              <TableRow key={i}>
                <TableCell>{fechaHora(h.fecha)}</TableCell>
                <TableCell>{h.usuario}</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>{h.archivo_nombre}</TableCell>
                <TableCell>{h.identificador_registro || `fila ${h.numero_fila}`}</TableCell>
                <TableCell>{h.campo ?? '—'}</TableCell>
                <TableCell>{h.valor_anterior || '—'}</TableCell>
                <TableCell>{h.valor_nuevo || '—'}</TableCell>
                <TableCell>{h.motivo || '—'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Card>
  );
}

export function Resultado() {
  const { periodo, jurisdiccion, cambiar } = useFiltros();
  const [params] = useSearchParams();
  const consulta = useResultado(periodo, jurisdiccion);
  const sesion = useSesion();
  const accion = useAccion();
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  const pedida = params.get('solapa') as Solapa | null;
  const solapa: Solapa = pedida && SOLAPAS.includes(pedida) ? pedida : 'resumen';
  const importacion = params.get('imp') ? Number(params.get('imp')) : null;

  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar el resultado.</Alert>;
  const d = consulta.data;
  const p = d.presentacion;
  const abiertas = d.observaciones.filter((o) => o.estado === 'ABIERTA').length;

  // Cambiar de solapa o de archivo limpia los filtros de la grilla anterior.
  const irA = (s: Solapa, imp?: number) =>
    cambiar({
      solapa: s === 'resumen' ? null : s,
      imp: imp ?? (s === 'datos' ? importacion : null),
      hoja: null,
      pagina: null,
      solo: null,
    });

  const ejecutar = async (a: Accion) => {
    if (!p) return;
    if (A_CONFIRMAR[a.accion]) {
      const ok = await confirmar({ titulo: a.etiqueta, texto: A_CONFIRMAR[a.accion], confirmar: a.etiqueta });
      if (ok === null) return;
    }
    accion.mutate(
      { presentacion: p.id, accion: a.accion },
      {
        onSuccess: (r) => avisar({ texto: r.mensaje }),
        onError: (e) => avisar({ texto: mensajeDeError(e), error: true }),
      },
    );
  };

  return (
    <>
      <Titulo
        titulo={d.jurisdiccion ?? 'Resultado'}
        subtitulo={
          p ? (
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
              {d.periodo && (
                <span>
                  {d.periodo.nombre} · del {fecha(d.periodo.fecha_desde)} al {fecha(d.periodo.fecha_hasta)} ·
                </span>
              )}
              <EtiquetaDeEstado tono={tonoDeLaPresentacion(p.estado)} texto={p.estado_legible} />
              <span>{p.estado_ayuda}</span>
              {p.expediente && <span>· expediente {p.expediente}</span>}
            </Stack>
          ) : d.jurisdiccion ? (
            `${d.periodo?.nombre ?? ''} · La jurisdicción todavía no empezó a cargar este período.`
          ) : undefined
        }
      >
        <SelectorDeJurisdiccion
          jurisdicciones={d.jurisdicciones}
          valor={d.jurisdiccion}
          alCambiar={(j) => cambiar({ jurisdiccion: j })}
        />
        {d.periodo && (
          <SelectorDePeriodo periodos={d.periodos} valor={d.periodo.codigo} alCambiar={(x) => cambiar({ periodo: x })} />
        )}
      </Titulo>

      {!d.jurisdiccion ? (
        <Alert severity="info">Elegí una jurisdicción para ver su resultado.</Alert>
      ) : (
        <>
          {/* Las solapas y, a la derecha, los botones del circuito: siempre en el mismo lugar. */}
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            spacing={1}
            sx={{ alignItems: { md: 'center' }, borderBottom: 1, borderColor: 'divider', mb: 2 }}
          >
            <Tabs
              value={solapa}
              onChange={(_, s: Solapa) => irA(s)}
              aria-label="Partes de la presentación"
              sx={{ flexGrow: 1, '& .MuiTabs-indicator': { bgcolor: 'nav.accent', height: 3 } }}
            >
              <Tab value="resumen" label="Resumen" />
              <Tab value="datos" label="Datos" />
              <Tab
                value="observaciones"
                label={
                  abiertas
                    ? `Observaciones (${abiertas} sin resolver)`
                    : `Observaciones${d.observaciones.length ? ` (${d.observaciones.length})` : ''}`
                }
                sx={abiertas ? { color: 'error.dark' } : undefined}
              />
              <Tab value="historial" label="Historial" />
            </Tabs>
            <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1, pb: { xs: 1, md: 0 } }}>
              {d.acciones.map((a) => (
                <Tooltip key={a.accion} describeChild title={a.ayuda}>
                  <span>
                    <Button
                      size="small"
                      variant={a.accion === 'reabrir_carga' || a.accion === 'devolver' ? 'outlined' : 'contained'}
                      color={a.accion === 'devolver' ? 'warning' : 'primary'}
                      disabled={accion.isPending}
                      onClick={() => ejecutar(a)}
                    >
                      {a.etiqueta}
                    </Button>
                  </span>
                </Tooltip>
              ))}
            </Stack>
          </Stack>

          {solapa === 'resumen' && <SolapaResumen d={d} alVerDatos={(i) => irA('datos', i)} />}
          {solapa === 'datos' && <SolapaDatos d={d} importacion={importacion} alElegir={(i) => irA('datos', i)} />}
          {solapa === 'observaciones' && (
            <SolapaObservaciones
              d={d}
              // Se observa desde que la provincia cierra la carga (28-09-2026).
              puedeObservar={!!sesion.data?.permisos.revisar && !!p && OBSERVABLES.includes(p.estado)}
            />
          )}
          {solapa === 'historial' && <SolapaHistorial presentacion={p?.id ?? null} />}
        </>
      )}
    </>
  );
}
