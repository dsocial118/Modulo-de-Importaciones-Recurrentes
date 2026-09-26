import LockOutlined from '@mui/icons-material/LockOutlined';
import SwapHorizOutlined from '@mui/icons-material/SwapHorizOutlined';
import UploadFileOutlined from '@mui/icons-material/UploadFileOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  Stack,
  Typography,
  useTheme,
} from '@mui/material';
import {
  mensajeDeError,
  useCarga,
  useCargarArchivo,
  type ArchivoACargar,
  type ResultadoDeImportar,
} from '@mir/api';
import { EtiquetaDeEstado, Titulo, coloresDe, useAvisar, useConfirmar, type Tono } from '@mir/ui';
import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ESTADO_DEL_ARCHIVO, formaDe } from '../comun/estados';
import { plural } from '../comun/formato';
import { SelectorDeJurisdiccion, SelectorDePeriodo } from '../comun/Selectores';
import { conFiltros, useFiltros } from '../comun/filtros';

type Recien = ResultadoDeImportar & { codigo: string };

/**
 * Mientras se importa, la fila lo dice y dice en qué va: primero sube el
 * archivo, con porcentaje, y después el sistema lo revisa, que con un archivo
 * grande es lo que más tarda. Antes el botón desaparecía al apretarlo y la
 * fila quedaba como si nada, con el archivo subiendo por detrás.
 */
function Avance({ porcentaje }: { porcentaje: number }) {
  const revisando = porcentaje >= 100;
  return (
    <Box sx={{ width: '100%' }} role="status" aria-live="polite">
      <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
        {revisando ? 'Revisando el archivo…' : `Subiendo el archivo… ${porcentaje} %`}
      </Typography>
      <LinearProgress
        variant={revisando ? 'indeterminate' : 'determinate'}
        value={porcentaje}
        aria-label={revisando ? 'Revisando el archivo' : 'Subiendo el archivo'}
      />
      {revisando && (
        <Typography variant="caption" color="text.secondary">
          Se controlan la estructura y cada fila. Con archivos grandes puede tardar.
        </Typography>
      )}
    </Box>
  );
}

function FilaDeCarga({
  a,
  habilitada,
  progreso,
  ocupado,
  alImportar,
}: {
  a: ArchivoACargar;
  habilitada: boolean;
  // null: esta fila no está importando. De 0 a 100, cuánto subió.
  progreso: number | null;
  // Otra fila está importando: una por vez.
  ocupado: boolean;
  alImportar: (a: ArchivoACargar, archivo: File) => Promise<void>;
}) {
  const campo = useRef<HTMLInputElement>(null);
  const e = formaDe(ESTADO_DEL_ARCHIVO, a.estado);
  const atencion = coloresDe('attention', useTheme().palette.mode);

  return (
    <Box sx={{ py: 2, borderTop: 1, borderColor: 'divider' }}>
      {/* El texto no se estira: con flexGrow empujaba los botones a la otra
          punta y dejaba el medio en blanco. Con el mismo ancho base en todas
          las filas, los botones quedan cerca y encolumnados. */}
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} sx={{ alignItems: { md: 'center' } }}>
        <Box sx={{ flex: { md: '0 1 720px' }, minWidth: 0 }}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <Typography sx={{ fontWeight: 500 }}>{a.codigo}</Typography>
            <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
            {a.filas != null && (
              <Typography variant="body2" color="text.secondary">
                {plural(a.filas, 'fila', 'filas')}
              </Typography>
            )}
          </Stack>
          {/* En un renglón mientras entre; si no entra, el nombre requerido baja. */}
          <Stack direction="row" sx={{ flexWrap: 'wrap', alignItems: 'baseline', columnGap: 1.5 }}>
            <Typography variant="body2" color="text.secondary">
              {a.nombre}
              {a.obligatorio ? ' · obligatorio' : ''}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Nombre requerido: <Box component="span" sx={{ fontFamily: 'monospace' }}>{a.nombre_sugerido}</Box>
            </Typography>
          </Stack>
          {/* Se dice SIEMPRE, no sólo cuando traba: así se sabe antes de intentar. */}
          {a.necesita.length > 0 && (
            <Typography variant="caption" color="text.secondary" component="div">
              Necesita: <strong>{a.necesita.join(', ')}</strong>
            </Typography>
          )}
        </Box>

        <Box sx={{ minWidth: { md: 280 }, flexShrink: 0 }}>
          {progreso !== null ? (
            <Avance porcentaje={progreso} />
          ) : a.bloqueado_por.length > 0 ? (
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
              <LockOutlined fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                Primero hay que importar <strong>{a.bloqueado_por.join(', ')}</strong>.
              </Typography>
            </Stack>
          ) : habilitada ? (
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 1 }}>
              <input
                ref={campo}
                type="file"
                accept=".xlsx,.xlsm"
                hidden
                onChange={async (ev) => {
                  const archivo = ev.target.files?.[0];
                  // Se vacía ya: así elegir el mismo archivo otra vez vuelve a disparar.
                  ev.target.value = '';
                  if (archivo) await alImportar(a, archivo);
                }}
              />
              {/* El botón dice lo que va a pasar. Antes decía «Seleccionar
                  archivo» también en lo ya importado, y parecía que faltaba
                  hacer algo. Reemplazar va en ámbar: pisa lo que ya estaba. */}
              {a.importada ? (
                <Button
                  variant="outlined"
                  color="warning"
                  size="small"
                  disabled={ocupado}
                  startIcon={<SwapHorizOutlined />}
                  // El texto va en el tono oscuro de «atención»: el ámbar
                  // sobre blanco no llega al contraste AA.
                  sx={{ color: atencion.text, borderColor: atencion.border, '&:hover': { bgcolor: atencion.surface } }}
                  onClick={() => campo.current?.click()}
                >
                  Reemplazar
                </Button>
              ) : (
                <Button
                  variant="contained"
                  size="small"
                  disabled={ocupado}
                  startIcon={<UploadFileOutlined />}
                  onClick={() => campo.current?.click()}
                >
                  Importar
                </Button>
              )}
            </Stack>
          ) : (
            <Typography color="text.secondary">—</Typography>
          )}
        </Box>
      </Stack>
    </Box>
  );
}

function ResultadoDelArchivo({ r, alCerrar, alVer }: { r: Recien | null; alCerrar: () => void; alVer: () => void }) {
  const { palette } = useTheme();
  if (!r) return null;
  const entro = !r.rechazado && r.estado === 'VALIDA';
  const hayQueCorregir = !!r.importacion_id && (r.bloqueantes > 0 || r.advertencias > 0);
  // El color dice cómo le fue antes de leer: rojo si no entró, ámbar si entró
  // con advertencias, azul si entró limpio.
  const tono: Tono = !entro ? 'critical' : r.advertencias > 0 ? 'attention' : 'info';
  const c = coloresDe(tono, palette.mode);
  return (
    <Dialog open onClose={alCerrar} maxWidth="sm" fullWidth>
      <DialogTitle>
        {!entro ? 'No se pudo importar' : r.advertencias > 0 ? 'Importado, con advertencias' : 'Importación correcta'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ bgcolor: c.surface, color: c.text, borderLeft: `4px solid ${c.border}`, borderRadius: 1, p: 2 }}>
        <Typography gutterBottom>
          Archivo <strong>{r.codigo}</strong>.
        </Typography>
        {r.rechazado ? (
          <Typography>{r.mensaje}</Typography>
        ) : entro ? (
          <Typography>
            {r.advertencias > 0 ? (
              <>
                Los registros se incorporaron. Quedan <strong>{plural(r.advertencias, 'advertencia', 'advertencias')}</strong>:
                pueden corregirse dentro del sistema, o volver a importarse el archivo corregido.
              </>
            ) : (
              'Los registros se incorporaron sin observaciones.'
            )}
          </Typography>
        ) : (
          <>
            <Typography gutterBottom>
              {r.bloqueantes > 0
                ? `${plural(r.bloqueantes, 'error bloqueante', 'errores bloqueantes')}.`
                : 'El archivo no se corresponde con la estructura esperada.'}
            </Typography>
            <Typography>No se incorporó ningún registro de este archivo.</Typography>
          </>
        )}
        </Box>
        {hayQueCorregir && (
          <Stack spacing={1} sx={{ mt: 2 }}>
            <Button variant="contained" href={`/api/mir/importaciones/${r.importacion_id}/marcado.xlsx`}>
              Descargar el archivo con las celdas marcadas
            </Button>
            <Button variant="outlined" href={`/api/mir/importaciones/${r.importacion_id}/errores.xlsx`}>
              Descargar la lista de errores
            </Button>
          </Stack>
        )}
      </DialogContent>
      <DialogActions>
        {r.importacion_id && hayQueCorregir && <Button onClick={alVer}>Ver el detalle</Button>}
        <Button onClick={alCerrar}>Cerrar</Button>
      </DialogActions>
    </Dialog>
  );
}

export function Cargar() {
  const { periodo, jurisdiccion, cambiar } = useFiltros();
  const consulta = useCarga(periodo, jurisdiccion);
  const cargar = useCargarArchivo();
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  const navegar = useNavigate();
  const [recien, setRecien] = useState<Recien | null>(null);
  // Qué archivo se está importando y cuánto subió. Uno por vez.
  const [enCurso, setEnCurso] = useState<{ codigo: string; porcentaje: number } | null>(null);

  // Cerrar la pestaña en medio de una importación la corta sin avisar: el
  // navegador pregunta antes.
  useEffect(() => {
    if (!enCurso) return;
    const avisarAlSalir = (e: BeforeUnloadEvent) => e.preventDefault();
    window.addEventListener('beforeunload', avisarAlSalir);
    return () => window.removeEventListener('beforeunload', avisarAlSalir);
  }, [enCurso]);

  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar la pantalla.</Alert>;
  const d = consulta.data;
  const habilitada = d.carga_abierta && d.puede_cargar && d.periodo?.estado === 'ABIERTO';

  const importar = async (a: ArchivoACargar, archivo: File) => {
    // Sólo se pregunta al reemplazar: es lo único que pisa algo. Importar por
    // primera vez no necesita confirmación, porque un archivo con errores se
    // rechaza entero y no deja nada a medias.
    if (a.importada) {
      const hoy = [
        a.filas != null ? plural(a.filas, 'fila', 'filas') : null,
        a.advertencias ? plural(a.advertencias, 'advertencia', 'advertencias') : null,
        a.correcciones ? plural(a.correcciones, 'corrección hecha', 'correcciones hechas') : null,
      ].filter(Boolean);
      const ok = await confirmar({
        titulo: `Reemplazar ${a.codigo}`,
        texto: (
          <>
            <Typography gutterBottom>
              Ya hay una importación de <strong>{a.codigo}</strong>
              {hoy.length > 0 && <> ({hoy.join(', ')})</>}. Vas a subir{' '}
              <Box component="span" sx={{ fontFamily: 'monospace' }}>
                {archivo.name}
              </Box>
              .
            </Typography>
            <Typography>
              Si el archivo nuevo entra, reemplaza al anterior
              {a.correcciones ? (
                <>
                  {' '}
                  y{' '}
                  <strong>
                    {a.correcciones === 1
                      ? 'se pierde la corrección hecha'
                      : `se pierden las ${a.correcciones} correcciones hechas`}
                  </strong>{' '}
                  dentro del sistema
                </>
              ) : null}
              . Si tiene errores bloqueantes, no se incorpora y el anterior queda como estaba.
            </Typography>
          </>
        ),
        confirmar: 'Reemplazar',
        color: 'warning',
      });
      if (ok === null) return;
    }
    setEnCurso({ codigo: a.codigo, porcentaje: 0 });
    try {
      const r = await cargar.mutateAsync({
        codigo: a.codigo,
        archivo,
        periodo: d.periodo!.codigo,
        jurisdiccion: d.jurisdiccion,
        alAvanzar: (porcentaje) => setEnCurso({ codigo: a.codigo, porcentaje }),
      });
      setRecien({ ...r, codigo: a.codigo });
    } catch (e) {
      avisar({ texto: mensajeDeError(e), error: true });
    } finally {
      setEnCurso(null);
    }
  };

  return (
    <>
      <Titulo
        titulo={d.jurisdiccion ? `Cargar archivos · ${d.jurisdiccion}` : "Cargar archivos"}
        subtitulo="Los archivos se cargan de a uno y deben tener el nombre y la estructura indicada en la plantilla modelo."
      >
        <SelectorDeJurisdiccion
          jurisdicciones={d.jurisdicciones}
          valor={d.jurisdiccion}
          alCambiar={(j) => cambiar({ jurisdiccion: j })}
        />
        {d.periodo && (
          <SelectorDePeriodo periodos={d.periodos} valor={d.periodo.codigo} alCambiar={(p) => cambiar({ periodo: p })} />
        )}
      </Titulo>

      {!d.jurisdiccion && <Alert severity="info">Elegí una jurisdicción para ver su carga.</Alert>}
      {d.jurisdiccion && d.periodo?.estado !== 'ABIERTO' && (
        <Alert severity="info" sx={{ mb: 2 }}>
          El período {d.periodo?.codigo} no está abierto: no se reciben archivos.
        </Alert>
      )}
      {d.jurisdiccion && !d.carga_abierta && (
        <Alert severity="info" sx={{ mb: 2 }}>
          La carga de este período está en «{d.estado_legible}». Para volver a importar un archivo, el responsable
          provincial tiene que <strong>reabrir la carga</strong> desde el resultado. Así el revisor no queda
          trabajando sobre datos que cambiaron abajo.
        </Alert>
      )}
      {d.jurisdiccion && d.carga_abierta && !d.puede_cargar && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Este rol no importa archivos. La importación la realiza el operador provincial.
        </Alert>
      )}

      {d.jurisdiccion && (
        <Card variant="outlined">
          <CardContent sx={{ pt: 0, '&:last-child': { pb: 0 } }}>
            {d.archivos.length === 0 ? (
              <Typography color="text.secondary" sx={{ py: 3, textAlign: 'center' }}>
                El período no tiene archivos definidos.
              </Typography>
            ) : (
              d.archivos.map((a) => (
                <FilaDeCarga
                  key={a.codigo}
                  a={a}
                  habilitada={habilitada}
                  progreso={enCurso?.codigo === a.codigo ? enCurso.porcentaje : null}
                  ocupado={!!enCurso}
                  alImportar={importar}
                />
              ))
            )}
          </CardContent>
        </Card>
      )}

      <Stack direction="row" spacing={2} sx={{ mt: 3, alignItems: 'center', flexWrap: 'wrap', rowGap: 1 }}>
        <Button variant="outlined" onClick={() => navegar(conFiltros('/resultado', periodo, jurisdiccion))}>
          Ver el estado del período
        </Button>
        {d.listo && (
          <Typography variant="body2" color="text.secondary">
            Todos los archivos obligatorios están importados.
          </Typography>
        )}
      </Stack>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
        La importación es <strong>restrictiva</strong>: si un archivo tiene errores bloqueantes, no se incorpora
        ninguna de sus filas. Los bloqueantes se corrigen en el Excel y el archivo se vuelve a importar; las
        advertencias se resuelven dentro del sistema.
      </Typography>

      <ResultadoDelArchivo
        r={recien}
        alCerrar={() => setRecien(null)}
        alVer={() => {
          const id = recien?.importacion_id;
          setRecien(null);
          if (id) navegar(`/resultado/${id}`);
        }}
      />
    </>
  );
}
