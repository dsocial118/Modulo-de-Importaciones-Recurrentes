import ArrowBack from '@mui/icons-material/ArrowBack';
import ChatBubbleOutline from '@mui/icons-material/ChatBubbleOutlineOutlined';
import GridOnOutlined from '@mui/icons-material/GridOnOutlined';
import ViewAgendaOutlined from '@mui/icons-material/ViewAgendaOutlined';
import DownloadOutlined from '@mui/icons-material/DownloadOutlined';
import ExpandMore from '@mui/icons-material/ExpandMore';
import HistoryOutlined from '@mui/icons-material/HistoryOutlined';
import WarningAmberOutlined from '@mui/icons-material/WarningAmberOutlined';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  FormControlLabel,
  LinearProgress,
  MenuItem,
  Pagination,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  mensajeDeError,
  useCorregir,
  useDatos,
  type Celda,
  type FilaDeDatos,
  type HaceFaltaConfirmar,
} from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar, useConfirmar } from '@mir/ui';
import { useState, type ReactNode } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { ObservacionDelDato } from '../comun/Observaciones';
import { Grilla } from '../comun/Grilla';
import { tonoDeLaPresentacion } from '../comun/estados';
import { fechaHora, plural } from '../comun/formato';
import { useNombreDeArchivo } from '../comun/archivos';

// La fila entera, no sólo su número: la confirmación dice de quién es.
type AlCorregir = (fila: FilaDeDatos, celda: Celda, valor: string) => Promise<boolean>;

/** De quién es la fila y dónde está: «9 · Paz · Ana · fila 12 del Excel». */
const quien = (f: FilaDeDatos) =>
  f.identificacion ? `${f.identificacion} · fila ${f.numero_fila} del Excel` : `Fila ${f.numero_fila} del Excel`;

/** Un dato. Se guarda al salir del campo —o al elegir, en una lista—, y sólo si cambió. */
function CampoEditable({
  fila,
  celda,
  editable,
  alCorregir,
}: {
  fila: FilaDeDatos;
  celda: Celda;
  editable: boolean;
  alCorregir: AlCorregir;
}) {
  const [valor, setValor] = useState(celda.valor);
  const [original, setOriginal] = useState(celda.valor);
  const etiqueta = (
    <>
      {celda.titulo}
      {celda.obligatorio && ' *'}
    </>
  );
  const guardar = async (nuevo: string) => {
    if (nuevo === original) return;
    const ok = await alCorregir(fila, celda, nuevo);
    if (ok) setOriginal(nuevo);
    else setValor(original);
  };
  const aviso = celda.tiene_aviso && (
    <WarningAmberOutlined fontSize="small" color="warning" titleAccess="Este dato tiene una advertencia" />
  );

  if (!editable) {
    return (
      <TextField
        size="small"
        fullWidth
        label={etiqueta}
        value={celda.valor || '—'}
        slotProps={{ input: { readOnly: true, endAdornment: aviso } }}
      />
    );
  }
  // Con lista cerrada se elige, no se escribe.
  if (celda.opciones.length) {
    return (
      <TextField
        select
        size="small"
        fullWidth
        label={etiqueta}
        value={celda.opciones.includes(valor) || valor === '' ? valor : ''}
        onChange={(e) => {
          setValor(e.target.value);
          void guardar(e.target.value);
        }}
        helperText={!celda.opciones.includes(valor) && valor ? `Valor actual fuera de la lista: «${valor}»` : undefined}
        slotProps={{ input: { endAdornment: aviso } }}
      >
        <MenuItem value="">—</MenuItem>
        {celda.opciones.map((o) => (
          <MenuItem key={o} value={o}>
            {o}
          </MenuItem>
        ))}
      </TextField>
    );
  }
  // Las fechas vienen como 27/10/2014 y el campo de fecha del navegador sólo
  // entiende 2014-10-27: lo mostraba vacío, y pasar por el campo podía
  // guardarlo vacío. Van como texto, igual que en la pantalla actual. La hora,
  // con selector sólo si ya viene como HH:MM.
  const tipo = celda.tipo_dato === 'HORA' && (!valor || /^\d{2}:\d{2}/.test(valor)) ? 'time' : 'text';
  return (
    <TextField
      size="small"
      fullWidth
      label={etiqueta}
      type={tipo}
      value={valor}
      onChange={(e) => setValor(e.target.value)}
      onBlur={() => void guardar(valor.trim())}
      onKeyDown={(e) => e.key === 'Enter' && (e.target as HTMLInputElement).blur()}
      placeholder={celda.tipo_dato === 'FECHA' ? 'dd/mm/aaaa' : undefined}
      slotProps={{
        inputLabel: tipo !== 'text' || celda.tipo_dato === 'FECHA' ? { shrink: true } : undefined,
        htmlInput: celda.tipo_dato === 'ENTERO' || celda.tipo_dato === 'DECIMAL' ? { inputMode: 'decimal' } : undefined,
        input: { endAdornment: aviso },
      }}
    />
  );
}

type ParaObservar = {
  permisos: { puedeObservar: boolean; puedeResponder: boolean };
  presentacion: number;
  importacion: number;
};

function Fila({
  f,
  editable,
  alCorregir,
  obs,
}: {
  f: FilaDeDatos;
  editable: boolean;
  alCorregir: AlCorregir;
  obs: ParaObservar;
}) {
  const abiertas = f.celdas.filter((c) => c.observacion?.estado === 'ABIERTA').length;
  return (
    // Una fila con observaciones sin resolver arranca abierta: es lo que hay que mirar.
    <Accordion
      variant="outlined"
      disableGutters
      defaultExpanded={abiertas > 0}
      slotProps={{ transition: { unmountOnExit: true } }}
    >
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Stack sx={{ width: '100%' }} spacing={0.5}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            {/* De quién es la fila, no sólo su número: pedido de la DNPYPI (#67). */}
            <Typography sx={{ fontWeight: 500 }}>{quien(f)}</Typography>
            {f.estado === 'EDITADA' && <EtiquetaDeEstado tono="pending" texto="Editada" />}
            {abiertas > 0 && (
              <EtiquetaDeEstado tono="critical" texto={plural(abiertas, 'observación', 'observaciones')} />
            )}
            {f.avisos.length > 0 && (
              <EtiquetaDeEstado tono="attention" texto={plural(f.avisos.length, 'advertencia', 'advertencias')} />
            )}
          </Stack>
          {f.avisos.map((a, i) => (
            <Typography key={i} variant="body2" color="text.secondary">
              <strong>{a.nombre_campo}</strong>: {a.descripcion}
            </Typography>
          ))}
        </Stack>
      </AccordionSummary>
      <AccordionDetails>
        <Box sx={{ display: 'grid', gap: 2, gridTemplateColumns: { xs: 'minmax(0, 1fr)', md: 'repeat(2, minmax(0, 1fr))', xl: 'repeat(3, minmax(0, 1fr))' } }}>
          {f.celdas.map((c) => (
            <Box key={c.nombre}>
              <CampoEditable fila={f} celda={c} editable={editable} alCorregir={alCorregir} />
              <ObservacionDelDato
                observacion={c.observacion}
                permisos={obs.permisos}
                ubicacion={{
                  presentacion: obs.presentacion,
                  importacion: obs.importacion,
                  numero_fila: f.numero_fila,
                  campo_id: c.campo_id,
                }}
              />
            </Box>
          ))}
        </Box>
      </AccordionDetails>
    </Accordion>
  );
}

/**
 * Al pie de la grilla, en un renglón: el dato elegido, si tiene algo que
 * mostrar —advertencia u observación— o si quien mira puede observarlo. Si no,
 * cómo se usa la grilla. Reemplaza al panel «Dato elegido» (27-09-2026).
 */
function RenglonDelDato({
  fila,
  celda,
  obs,
  editable,
}: {
  fila?: FilaDeDatos;
  celda?: Celda;
  obs: ParaObservar;
  editable: boolean;
}) {
  const avisos = fila && celda ? fila.avisos.filter((a) => a.nombre_campo === celda.titulo) : [];
  const hayQueMostrar = !!celda && (avisos.length > 0 || !!celda.observacion || obs.permisos.puedeObservar);
  if (!fila || !celda || !hayQueMostrar) {
    return (
      <Typography variant="caption" color="text.secondary">
        Un clic elige el dato.{editable ? ' Doble clic, o Enter, para corregirlo.' : ''} Las celdas en ámbar tienen
        advertencias; las marcadas en rojo, observaciones sin resolver.
      </Typography>
    );
  }
  return (
    <Box>
      <Typography variant="body2">
        <strong>{celda.titulo}</strong> · {quien(fila)}: «{celda.valor || '—'}»
        {avisos.map((a, i) => (
          <Box component="span" key={i} sx={{ ml: 1.5, color: 'text.secondary' }}>
            <WarningAmberOutlined fontSize="inherit" color="warning" sx={{ mr: 0.5, verticalAlign: 'text-bottom' }} />
            {a.descripcion}
          </Box>
        ))}
      </Typography>
      <ObservacionDelDato
        observacion={celda.observacion}
        permisos={obs.permisos}
        ubicacion={{
          presentacion: obs.presentacion,
          importacion: obs.importacion,
          numero_fila: fila.numero_fila,
          campo_id: celda.campo_id,
        }}
      />
    </Box>
  );
}

/**
 * Ver y corregir los datos de una importación. Va dentro de la solapa «Datos»
 * de la presentación (`incrustado`), sin título propio, sin historial —tiene
 * su solapa— y sin la lista de observaciones arriba, que empujaba la grilla
 * hacia abajo (27-09-2026). Por su dirección propia sigue andando sola.
 */
export function Datos({
  importacion,
  incrustado = false,
  selectorDeArchivo,
}: { importacion?: number; incrustado?: boolean; selectorDeArchivo?: ReactNode } = {}) {
  const nombreDe = useNombreDeArchivo();
  const parametro = Number(useParams().id);
  const id = importacion ?? parametro;
  const navegar = useNavigate();
  const [params, setParams] = useSearchParams();
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  const filtros = { hoja: params.get('hoja'), pagina: params.get('pagina'), solo: params.get('solo') };
  const consulta = useDatos(id, filtros);
  const corregir = useCorregir(id);
  // El dato elegido en la grilla: por fila y campo, así sigue elegido cuando
  // los datos se vuelven a leer después de corregir.
  const [elegida, setElegida] = useState<{ fila: number; campo: string } | null>(null);
  // Fichas o grilla: queda en la dirección, así se puede compartir o volver.
  // La grilla es la de entrada (27-09-2026), salvo en el teléfono: una tabla
  // de 65 columnas no entra, y ahí las fichas se leen mejor.
  const chico = useMediaQuery(useTheme().breakpoints.down('md'));
  const vista = params.get('vista') ?? (chico ? 'fichas' : 'grilla');
  const enGrilla = vista === 'grilla';

  const poner = (cambios: Record<string, string>) => {
    const nuevos = new URLSearchParams(params);
    for (const [k, v] of Object.entries(cambios)) {
      if (v) nuevos.set(k, v);
      else nuevos.delete(k);
    }
    setParams(nuevos, { replace: true });
  };

  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No existe esa importación, o no es de tu jurisdicción.</Alert>;
  const d = consulta.data;
  const c = d.contexto;
  const abiertas = d.observaciones.filter((o) => o.estado === 'ABIERTA');
  const filaElegida = elegida ? d.filas.find((f) => f.numero_fila === elegida.fila) : undefined;
  const celdaElegida = filaElegida?.celdas.find((x) => x.nombre === elegida?.campo);
  // Observa el nivel nacional; responde la jurisdicción, y sólo si la carga admite cambios.
  const paraObservar: ParaObservar = {
    permisos: { puedeObservar: d.puede_observar, puedeResponder: d.puede_responder && c.editable },
    presentacion: c.presentacion_id,
    importacion: id,
  };

  const alCorregir: AlCorregir = async (fila, celda, valor) => {
    const motivo = await confirmar({
      titulo: 'Confirmar el cambio',
      texto: (
        <>
          {quien(fila)}, <strong>{celda.titulo}</strong>: de «{celda.valor || '—'}» a «{valor || '—'}». El cambio
          queda registrado con usuario, fecha y valor anterior.
        </>
      ),
      confirmar: 'Guardar',
      campo: { etiqueta: 'Motivo (opcional)' },
    });
    if (motivo === null) return false;
    const pedido = { hoja_id: d.hoja.id, numero_fila: fila.numero_fila, campo: celda.nombre, valor, motivo, en_cascada: false };
    try {
      let r;
      try {
        r = await corregir.mutateAsync(pedido);
      } catch (e) {
        // Como en una base relacional (27-09-2026): si el dato lo usan filas de
        // otros archivos, se pregunta si se actualizan también. Si no, el dato
        // queda como estaba y no cambia nada.
        const aviso = (e as { response?: { status?: number; data?: HaceFaltaConfirmar } })?.response;
        if (aviso?.status !== 409 || !aviso.data?.usos) throw e;
        const usos = aviso.data.usos;
        const cuantas = usos.reduce((n, g) => n + g.filas.length, 0);
        const seguir = await confirmar({
          titulo: 'Ese dato se usa en otros archivos',
          texto: (
            <>
              Pasar <strong>{celda.titulo}</strong> de «{celda.valor || '—'}» a «{valor || '—'}» deja sin su referencia a{' '}
              <strong>{plural(cuantas, 'fila', 'filas')}</strong> que lo usan:
              <Box component="ul" sx={{ my: 1, pl: 3, maxHeight: 220, overflowY: 'auto' }}>
                {usos.map((g) => (
                  <li key={`${g.importacion_id}-${g.hoja}-${g.campo_titulo}`}>
                    <strong>{g.archivo_nombre}</strong>
                    {g.hoja && g.hoja !== g.archivo_nombre && g.hoja !== g.archivo ? ` (hoja ${g.hoja})` : ''} · {g.campo_titulo}:{' '}
                    {g.filas.map((f) => f.identificacion || `fila ${f.numero_fila}`).join('; ')}
                  </li>
                ))}
              </Box>
              ¿Se actualizan también? Si no, el dato queda como estaba.
            </>
          ),
          confirmar: 'Sí, actualizar todas',
        });
        if (seguir === null) {
          avisar({ texto: 'No se cambió nada: el dato quedó como estaba.' });
          return false;
        }
        r = await corregir.mutateAsync({ ...pedido, en_cascada: true });
      }
      // Guardar y quedar bien no son lo mismo: si el valor nuevo quedó
      // observado, se dice.
      const junto = r.en_cascada ? ` También se actualizaron ${plural(r.en_cascada, 'fila', 'filas')} de otros archivos.` : '';
      if (r.sin_cambios) avisar({ texto: 'El valor era el mismo: no se registró un cambio.' });
      else if (r.observaciones.length) avisar({ texto: `Guardado, pero quedó observado: ${r.observaciones.join(' ')}${junto}` });
      else avisar({ texto: `Dato corregido. Queda registrado en el historial.${junto}` });
      return true;
    } catch (e) {
      avisar({ texto: mensajeDeError(e), error: true });
      return false;
    }
  };

  return (
    <>
      {!incrustado && (
      <Titulo
        titulo={`${nombreDe(c.archivo_codigo)} · ${d.puede_editar && c.editable ? 'ver y corregir datos' : 'ver datos'}`}
        volver={
          <Button size="small" startIcon={<ArrowBack />} onClick={() => navegar(`/resultado/${id}`)} sx={{ mb: 1, ml: -1 }}>
            Volver al detalle
          </Button>
        }
        subtitulo={
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <EtiquetaDeEstado tono={tonoDeLaPresentacion(c.estado_presentacion)} texto={c.estado_legible} />
            <span>
              {c.jurisdiccion} · {c.periodo} · estructura v{c.version}
            </span>
          </Stack>
        }
      >
        <Tooltip describeChild title="Un Excel con cada corrección: quién, cuándo, antes, después y el motivo.">
          <span>
            <Button
              variant="outlined"
              startIcon={<DownloadOutlined />}
              disabled={!d.historial.length}
              href={d.descarga_historial}
            >
              Historial
            </Button>
          </span>
        </Tooltip>
      </Titulo>
      )}

      <Stack spacing={2}>
        {/* Dentro de la solapa, sin avisos: el estado ya está en el título de la
            presentación, y cada dato dice si se puede tocar. */}
        {incrustado ? null : !c.editable ? (
          <Alert severity="info">
            La presentación está en «{c.estado_legible}» y los datos no se pueden modificar. Para corregir, el
            responsable provincial tiene que <strong>reabrir la carga</strong>.
          </Alert>
        ) : !d.puede_editar ? (
          <Alert severity="info">
            El nivel nacional <strong>no modifica datos provinciales</strong>: formula observaciones. La corrección la
            hace la jurisdicción.
          </Alert>
        ) : (
          <Alert severity="info" icon={false}>
            Cada cambio se confirma y queda registrado con usuario, fecha, valor anterior y valor nuevo. Los errores{' '}
            <strong>bloqueantes</strong> no se corrigen acá: se arreglan en el Excel y el archivo se vuelve a importar.
          </Alert>
        )}

        {/* Las observaciones no van arriba de la grilla: tienen su solapa en
            la presentación, y acá quedan marcadas en rojo en cada dato. */}
        {!incrustado && abiertas.length > 0 && (
          <Alert severity="error" icon={<ChatBubbleOutline fontSize="inherit" />}>
            {plural(abiertas.length, 'observación sin resolver', 'observaciones sin resolver')}: están marcadas en rojo en cada
            dato y en la solapa Observaciones de la presentación.
          </Alert>
        )}

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ alignItems: { md: 'center' } }}>
          {selectorDeArchivo}
          {d.hojas.length > 1 && (
            <TextField
              select
              size="small"
              label="Hoja"
              value={d.hoja.id}
              onChange={(e) => poner({ hoja: String(e.target.value), pagina: '' })}
              sx={{ minWidth: 200 }}
            >
              {d.hojas.map((h) => (
                <MenuItem key={h.id} value={h.id}>
                  {h.nombre}
                </MenuItem>
              ))}
            </TextField>
          )}
          <FormControlLabel
            control={
              <Switch checked={params.get('solo') === 'avisos'} onChange={(e) => poner({ solo: e.target.checked ? 'avisos' : '', pagina: '' })} />
            }
            label={`Sólo las filas con advertencia (${d.con_advertencia})`}
          />
          {abiertas.length > 0 && (
            <FormControlLabel
              control={
                <Switch
                  checked={params.get('solo') === 'observadas'}
                  onChange={(e) => poner({ solo: e.target.checked ? 'observadas' : '', pagina: '' })}
                />
              }
              label="Sólo las filas con observaciones sin resolver"
            />
          )}
          <Typography variant="body2" color="text.secondary" sx={{ ml: { md: 'auto' } }}>
            {plural(d.total, 'fila', 'filas')} · página {d.pagina} de {d.paginas}
          </Typography>
          <ToggleButtonGroup
            size="small"
            exclusive
            value={enGrilla ? 'grilla' : 'fichas'}
            onChange={(_, v) => v && poner({ vista: v })}
            aria-label="Cómo ver los datos"
          >
            <Tooltip describeChild title="Una ficha por fila, con todos sus datos">
              <ToggleButton value="fichas">
                <ViewAgendaOutlined fontSize="small" sx={{ mr: 0.5 }} />
                Fichas
              </ToggleButton>
            </Tooltip>
            <Tooltip describeChild title="Como en el Excel: una fila por registro, con los títulos fijos">
              <ToggleButton value="grilla">
                <GridOnOutlined fontSize="small" sx={{ mr: 0.5 }} />
                Grilla
              </ToggleButton>
            </Tooltip>
          </ToggleButtonGroup>
        </Stack>

        {consulta.isFetching && <LinearProgress />}
        {d.filas.length > 0 && enGrilla ? (
          <Grilla
            filas={d.filas}
            editable={d.puede_editar}
            alCorregir={alCorregir}
            elegida={filaElegida && celdaElegida ? elegida : null}
            alElegir={setElegida}
            pie={
              <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <RenglonDelDato
                    fila={filaElegida}
                    celda={celdaElegida}
                    obs={paraObservar}
                    editable={d.puede_editar}
                  />
                </Box>
                {d.paginas > 1 && (
                  <Pagination
                    size="small"
                    count={d.paginas}
                    page={d.pagina}
                    onChange={(_, n) => poner({ pagina: String(n) })}
                    color="primary"
                  />
                )}
              </Stack>
            }
          />
        ) : (
          <Box>
            {d.filas.map((f) => (
              // La clave incluye la página: al cambiar de página, los campos arrancan de cero.
              <Fila
                key={`${d.hoja.id}-${f.numero_fila}`}
                f={f}
                editable={d.puede_editar}
                alCorregir={alCorregir}
                obs={paraObservar}
              />
            ))}
          </Box>
        )}
        {d.filas.length === 0 && (
          <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
            {params.get('solo') === 'avisos' ? 'Ninguna fila de esta hoja tiene advertencias.' : 'Esta importación no incorporó filas.'}
          </Typography>
        )}
        {d.paginas > 1 && !(enGrilla && d.filas.length > 0) && (
          <Pagination count={d.paginas} page={d.pagina} onChange={(_, n) => poner({ pagina: String(n) })} color="primary" />
        )}

        {/* En la página, no en una ventana: los modales quedan para confirmar
            lo que pisa algo (26-09-2026). Cerrado de entrada, para no empujar
            los datos hacia abajo. */}
        {!incrustado && (
        <Accordion variant="outlined" disableGutters id="historial">
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
              <HistoryOutlined fontSize="small" color="action" />
              <Typography sx={{ fontWeight: 500 }}>Historial de cambios ({d.historial.length})</Typography>
            </Stack>
          </AccordionSummary>
          <AccordionDetails>
            {d.historial.length === 0 ? (
              <Typography color="text.secondary">Todavía no se corrigió ningún dato de esta importación.</Typography>
            ) : (
              <TableContainer>
                <Table size="small" aria-label="Historial de cambios">
                  <TableHead>
                    <TableRow>
                      <TableCell>Cuándo</TableCell>
                      <TableCell>Quién</TableCell>
                      <TableCell align="right">Fila</TableCell>
                      <TableCell>Campo</TableCell>
                      <TableCell>Antes</TableCell>
                      <TableCell>Después</TableCell>
                      <TableCell>Motivo</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {d.historial.map((h, i) => (
                      <TableRow key={i}>
                        <TableCell>{fechaHora(h.fecha)}</TableCell>
                        <TableCell>{h.usuario}</TableCell>
                        <TableCell align="right">{h.numero_fila}</TableCell>
                        <TableCell>{h.campo}</TableCell>
                        <TableCell>{h.valor_anterior || '—'}</TableCell>
                        <TableCell>{h.valor_nuevo || '—'}</TableCell>
                        <TableCell>{h.motivo || '—'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </AccordionDetails>
        </Accordion>
        )}
      </Stack>
    </>
  );
}
