import DescriptionOutlined from '@mui/icons-material/DescriptionOutlined';
import EditOutlined from '@mui/icons-material/EditOutlined';
import FactCheckOutlined from '@mui/icons-material/FactCheckOutlined';
import GridOnOutlined from '@mui/icons-material/GridOnOutlined';
import UploadFileOutlined from '@mui/icons-material/UploadFileOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  Chip,
  LinearProgress,
  Stack,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  mensajeDeError,
  useAccion,
  useRegistrarExpediente,
  useResponder,
  useResultado,
  type Accion,
  type ArchivoDelResultado,
  type Observacion,
} from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar, useConfirmar } from '@mir/ui';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ESTADO_DEL_ARCHIVO, SEVERIDAD, formaDe, tonoDeLaPresentacion } from '../comun/estados';
import { fechaHora, numero, plural } from '../comun/formato';
import { SelectorDeJurisdiccion, SelectorDePeriodo } from '../comun/Selectores';
import { conFiltros, useFiltros } from '../comun/filtros';

// Las acciones que no tienen vuelta atrás se confirman; el resto, no.
const A_CONFIRMAR: Record<string, string> = {
  cerrar_carga: 'Declara terminada la carga del período y la envía a revisión nacional.',
  presentar:
    'Es el acto formal de presentación del período. Genera el comprobante para remitir por GDE, y después los datos ya no se modifican.',
  reabrir_carga: 'La revisión anterior queda sin efecto y la presentación vuelve a carga.',
};

function Archivo({ a, puedeEditar }: { a: ArchivoDelResultado; puedeEditar: boolean }) {
  const navegar = useNavigate();
  const imp = a.importacion;
  const e = formaDe(ESTADO_DEL_ARCHIVO, a.estado);
  const hayHallazgos = !!imp && (imp.bloqueantes > 0 || imp.advertencias > 0);
  return (
    <Box sx={{ py: 2, borderTop: 1, borderColor: 'divider' }}>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ alignItems: { md: 'flex-start' } }}>
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <Typography sx={{ fontWeight: 500 }}>{a.codigo}</Typography>
            <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {a.nombre}
          </Typography>
          {imp && (
            <Typography variant="body2" sx={{ mt: 0.5 }}>
              {numero(imp.filas_leidas)} leídas · {numero(imp.filas_incorporadas)} incorporadas
              {imp.bloqueantes > 0 && <> · <strong>{plural(imp.bloqueantes, 'bloqueante', 'bloqueantes')}</strong></>}
              {imp.advertencias > 0 && <> · {plural(imp.advertencias, 'advertencia', 'advertencias')}</>}
            </Typography>
          )}
          {a.resumen.length > 0 && (
            <Stack direction="row" sx={{ mt: 1, flexWrap: 'wrap', gap: 0.75 }}>
              {a.resumen.map((r) => (
                <Chip
                  key={`${r.codigo}-${r.severidad}`}
                  size="small"
                  variant="outlined"
                  label={`${r.casos} · ${r.ejemplo ?? r.codigo}`}
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
            {a.importada && puedeEditar && (
              <Button size="small" variant="outlined" startIcon={<EditOutlined />} onClick={() => navegar(`/resultado/${imp.id}/datos`)}>
                Corregir datos
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

function ObservacionDelRevisor({ o, puedeResponder }: { o: Observacion; puedeResponder: boolean }) {
  const [respuesta, setRespuesta] = useState('');
  const responder = useResponder();
  const avisar = useAvisar();
  const abierta = o.estado === 'ABIERTA';
  return (
    <Box sx={{ py: 2, borderTop: 1, borderColor: 'divider' }}>
      <Stack direction="row" spacing={1} sx={{ alignItems: 'center', mb: 0.5 }}>
        <EtiquetaDeEstado tono={abierta ? 'attention' : 'info'} texto={abierta ? 'Abierta' : 'Respondida'} />
        <Typography variant="caption" color="text.secondary">
          {o.usuario_observa} · {fechaHora(o.creada_el)}
          {o.archivo_codigo && ` · ${o.archivo_codigo}`}
          {o.numero_fila && ` · fila ${o.numero_fila}`}
        </Typography>
      </Stack>
      <Typography>{o.texto}</Typography>
      {o.respuesta ? (
        <Box sx={{ mt: 1, pl: 1.5, borderLeft: 3, borderColor: 'divider' }}>
          <Typography variant="body2">
            <strong>Respuesta:</strong> {o.respuesta}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {o.usuario_responde} · {fechaHora(o.respondida_el)}
          </Typography>
        </Box>
      ) : (
        puedeResponder && (
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }}>
            <TextField
              size="small"
              fullWidth
              label="Respuesta a la observación"
              value={respuesta}
              onChange={(e) => setRespuesta(e.target.value)}
            />
            <Button
              variant="outlined"
              disabled={!respuesta.trim() || responder.isPending}
              onClick={() =>
                responder.mutate(
                  { observacion: o.id, respuesta },
                  {
                    onSuccess: (r) => {
                      setRespuesta('');
                      avisar({ texto: r.mensaje });
                    },
                    onError: (e) => avisar({ texto: mensajeDeError(e), error: true }),
                  },
                )
              }
            >
              Responder
            </Button>
          </Stack>
        )
      )}
    </Box>
  );
}

export function Resultado() {
  const { periodo, jurisdiccion, cambiar } = useFiltros();
  const consulta = useResultado(periodo, jurisdiccion);
  const accion = useAccion();
  const expediente = useRegistrarExpediente();
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  const navegar = useNavigate();
  const vertical = useMediaQuery(useTheme().breakpoints.down('md'));
  const [numeroGde, setNumeroGde] = useState('');

  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar el resultado.</Alert>;
  const d = consulta.data;
  const p = d.presentacion;

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

  const paso = d.pasos.findIndex((x) => x.actual);

  return (
    <>
      <Titulo
        titulo={d.jurisdiccion ? `${d.jurisdiccion} · ${d.periodo?.codigo ?? ''}` : 'Resultado'}
        subtitulo={
          p ? (
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
              <EtiquetaDeEstado tono={tonoDeLaPresentacion(p.estado)} texto={p.estado_legible} />
              <span>versión {p.version}</span>
              {p.expediente && <span>· expediente {p.expediente}</span>}
              <span>· {p.estado_ayuda}</span>
            </Stack>
          ) : d.jurisdiccion ? (
            'La jurisdicción todavía no empezó a cargar este período.'
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
        <Stack spacing={3}>
          {p && (
            <Card variant="outlined">
              <CardContent>
                {vertical ? (
                  // En pantalla chica, ocho pasos uno debajo del otro tapan todo: se dice
                  // en qué paso está, y cuántos hay.
                  <Typography variant="body2">
                    Paso {paso + 1} de {d.pasos.length}:{' '}
                    <strong>{d.pasos.filter((x) => x.actual).map((x) => x.nombre).join(' · ')}</strong>
                  </Typography>
                ) : (
                  <Stepper activeStep={paso} alternativeLabel aria-label="Dónde está la presentación dentro del circuito">
                    {d.pasos.map((x) => (
                      // Carga, validación y corrección son el mismo estado: se marcan
                      // los tres, no sólo el primero.
                      <Step key={x.nombre} completed={false} active={x.actual}>
                        <StepLabel>{x.nombre}</StepLabel>
                      </Step>
                    ))}
                  </Stepper>
                )}
              </CardContent>
            </Card>
          )}

          {d.totales.bloqueantes > 0 ? (
            <Alert severity="warning">
              Hay <strong>{plural(d.totales.bloqueantes, 'error bloqueante', 'errores bloqueantes')}</strong>. La
              importación es restrictiva: <strong>no se incorporó ninguna fila</strong> de esos archivos. Se corrige el
              Excel y se vuelve a importar.
            </Alert>
          ) : d.totales.advertencias > 0 ? (
            <Alert severity="info">
              No hay errores bloqueantes. Quedan <strong>{plural(d.totales.advertencias, 'advertencia', 'advertencias')}</strong>:
              no impiden continuar, y se resuelven dentro del sistema editando el dato o justificándolo.
            </Alert>
          ) : d.totales.filas > 0 ? (
            <Alert severity="info">Todos los archivos se importaron sin errores.</Alert>
          ) : null}

          <Card variant="outlined">
            <CardHeader
              title="Archivos"
              subheader={
                d.totales.filas > 0 &&
                `${numero(d.totales.filas)} filas leídas · ${numero(d.totales.validas)} incorporadas`
              }
              slotProps={{ title: { variant: 'subtitle1', sx: { fontWeight: 500 } } }}
            />
            <CardContent sx={{ pt: 0, '&:last-child': { pb: 0 } }}>
              {d.archivos.map((a) => (
                <Archivo key={a.codigo} a={a} puedeEditar={d.puede_editar} />
              ))}
            </CardContent>
          </Card>

          {d.observaciones.length > 0 && (
            <Card variant="outlined">
              <CardHeader
                title="Observaciones del revisor técnico nacional"
                subheader="El revisor observa; no modifica datos provinciales."
                slotProps={{ title: { variant: 'subtitle1', sx: { fontWeight: 500 } } }}
              />
              <CardContent sx={{ pt: 0, '&:last-child': { pb: 0 } }}>
                {d.observaciones.map((o) => (
                  <ObservacionDelRevisor key={o.id} o={o} puedeResponder={d.puede_responder} />
                ))}
              </CardContent>
            </Card>
          )}

          <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
            <Button
              variant="outlined"
              startIcon={<UploadFileOutlined />}
              onClick={() => navegar(conFiltros('/cargar', d.periodo?.codigo, d.jurisdiccion))}
            >
              Cargar archivos
            </Button>
            {d.acciones.map((a) => (
              <Tooltip key={a.accion} title={a.ayuda}>
                <span>
                  <Button
                    variant={a.accion === 'reabrir_carga' ? 'outlined' : 'contained'}
                    disabled={accion.isPending}
                    onClick={() => ejecutar(a)}
                  >
                    {a.etiqueta}
                  </Button>
                </span>
              </Tooltip>
            ))}
            {p && (p.estado === 'PRESENTADA' || p.estado === 'CONSOLIDADA') && (
              <Button variant="outlined" onClick={() => navegar(`/presentacion/${p.id}/comprobante`)}>
                Ver comprobante
              </Button>
            )}
          </Stack>
          {!d.acciones.length && p?.estado === 'EN_CARGA' && !d.listo && (
            <Typography variant="body2" color="text.secondary">
              Faltan archivos obligatorios por importar. El responsable provincial podrá cerrar la carga cuando estén
              todos.
            </Typography>
          )}

          {p?.estado === 'PRESENTADA' && d.puede_presentar && !p.expediente && (
            <Card variant="outlined">
              <CardHeader title="Número de expediente" slotProps={{ title: { variant: 'subtitle1', sx: { fontWeight: 500 } } }} />
              <CardContent sx={{ pt: 0 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  El comprobante se remite por GDE. Obtenido el número de expediente, se incorpora acá. Su ausencia no
                  impide la consolidación: es un resguardo documental de la jurisdicción.
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
      )}
    </>
  );
}
