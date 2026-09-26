import LockOutlined from '@mui/icons-material/LockOutlined';
import UploadFileOutlined from '@mui/icons-material/UploadFileOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  LinearProgress,
  Stack,
  Typography,
} from '@mui/material';
import {
  mensajeDeError,
  useCarga,
  useCargarArchivo,
  type ArchivoACargar,
  type ResultadoDeImportar,
} from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar, useConfirmar } from '@mir/ui';
import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ESTADO_DEL_ARCHIVO, formaDe } from '../comun/estados';
import { plural } from '../comun/formato';
import { SelectorDeJurisdiccion, SelectorDePeriodo, conFiltros, useFiltros } from '../comun/Selectores';

type Recien = ResultadoDeImportar & { codigo: string };

/**
 * Una fila por archivo. Un solo botón que cambia en el mismo lugar: primero
 * «Seleccionar archivo», y con el archivo elegido pasa a ser «Importar».
 */
function FilaDeCarga({
  a,
  habilitada,
  subiendo,
  alImportar,
}: {
  a: ArchivoACargar;
  habilitada: boolean;
  subiendo: boolean;
  alImportar: (a: ArchivoACargar, archivo: File) => void;
}) {
  const campo = useRef<HTMLInputElement>(null);
  const [elegido, setElegido] = useState<File | null>(null);
  const e = formaDe(ESTADO_DEL_ARCHIVO, a.estado);

  return (
    <Box sx={{ py: 2, borderTop: 1, borderColor: 'divider' }}>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ alignItems: { md: 'center' } }}>
        <Box sx={{ flexGrow: 1, minWidth: 0 }}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <Typography sx={{ fontWeight: 500 }}>{a.codigo}</Typography>
            <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
            {a.filas != null && (
              <Typography variant="body2" color="text.secondary">
                {plural(a.filas, 'fila', 'filas')}
              </Typography>
            )}
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {a.nombre}
            {a.obligatorio ? ' · obligatorio' : ''}
          </Typography>
          <Typography variant="caption" color="text.secondary" component="div">
            Nombre requerido: <Box component="span" sx={{ fontFamily: 'monospace' }}>{a.nombre_sugerido}</Box>
          </Typography>
          {/* Se dice SIEMPRE, no sólo cuando traba: así se sabe antes de intentar. */}
          {a.necesita.length > 0 && (
            <Typography variant="caption" color="text.secondary" component="div">
              Necesita: <strong>{a.necesita.join(', ')}</strong>
            </Typography>
          )}
        </Box>

        <Box sx={{ minWidth: { md: 280 } }}>
          {a.bloqueado_por.length > 0 ? (
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
                onChange={(ev) => setElegido(ev.target.files?.[0] ?? null)}
              />
              {elegido ? (
                <>
                  {/* El nombre vuelve a abrir el selector: así se cambia de archivo sin otro botón. */}
                  <Button
                    size="small"
                    onClick={() => campo.current?.click()}
                    sx={{ fontFamily: 'monospace', textTransform: 'none', maxWidth: 220 }}
                    title="Elegir otro archivo"
                  >
                    <Box component="span" sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {elegido.name}
                    </Box>
                  </Button>
                  <Button
                    variant="contained"
                    size="small"
                    disabled={subiendo}
                    startIcon={subiendo ? <CircularProgress size={16} color="inherit" /> : <UploadFileOutlined />}
                    onClick={() => {
                      alImportar(a, elegido);
                      setElegido(null);
                      if (campo.current) campo.current.value = '';
                    }}
                  >
                    {a.importada ? 'Reemplazar' : 'Importar'}
                  </Button>
                </>
              ) : (
                <Button variant="outlined" size="small" onClick={() => campo.current?.click()}>
                  Seleccionar archivo
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
  if (!r) return null;
  const entro = !r.rechazado && r.estado === 'VALIDA';
  const hayQueCorregir = !!r.importacion_id && (r.bloqueantes > 0 || r.advertencias > 0);
  return (
    <Dialog open onClose={alCerrar} maxWidth="sm" fullWidth>
      <DialogTitle>{entro ? 'Importación correcta' : 'No se pudo importar'}</DialogTitle>
      <DialogContent>
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

  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar la pantalla.</Alert>;
  const d = consulta.data;
  const habilitada = d.carga_abierta && d.puede_cargar && d.periodo?.estado === 'ABIERTO';

  const importar = async (a: ArchivoACargar, archivo: File) => {
    if (a.importada) {
      const ok = await confirmar({
        titulo: `Reemplazar ${a.codigo}`,
        texto:
          'Si la nueva importación entra, reemplaza a la anterior y se pierden las correcciones hechas sobre ella.',
        confirmar: 'Reemplazar',
      });
      if (ok === null) return;
    }
    cargar.mutate(
      { codigo: a.codigo, archivo, periodo: d.periodo!.codigo, jurisdiccion: d.jurisdiccion },
      {
        onSuccess: (r) => setRecien({ ...r, codigo: a.codigo }),
        onError: (e) => avisar({ texto: mensajeDeError(e), error: true }),
      },
    );
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
                  subiendo={cargar.isPending && cargar.variables?.codigo === a.codigo}
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
