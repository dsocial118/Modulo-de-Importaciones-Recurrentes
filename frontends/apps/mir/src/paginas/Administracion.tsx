import AddOutlined from '@mui/icons-material/AddOutlined';
import LockOutlined from '@mui/icons-material/LockOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
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
  Tooltip,
  Typography,
} from '@mui/material';
import {
  api,
  mensajeDeError,
  useAdministracion,
  useArmarDemo,
  useBorrarImportaciones,
  useCambiarEstadoDelPeriodo,
  useCambiarOperativo,
  type ResumenDeCierre,
} from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar, useConfirmar } from '@mir/ui';
import { useState, type ReactNode } from 'react';
import { ESTADO_DEL_PERIODO, formaDe } from '../comun/estados';
import { fecha } from '../comun/formato';

/**
 * Administración: los períodos, las provincias del operativo y las
 * herramientas de prueba. Sólo el administrador nacional. Sale de Inicio y
 * tiene su propio menú (maqueta aprobada el 27-09-2026). Cada botón dice qué
 * hace al pasar el mouse.
 */

function ConAyuda({ ayuda, children }: { ayuda: string; children: ReactNode }) {
  return (
    <Tooltip describeChild title={ayuda}>
      <span>{children}</span>
    </Tooltip>
  );
}

/** Antes de cerrar el período para todas: lo que hay y lo que falta. */
function TextoDelCierre({ r }: { r: ResumenDeCierre }) {
  const sinCerrar = r.grupos
    .filter((g) => g.grupo === 'EN_CARGA' || g.grupo === 'SIN_EMPEZAR')
    .reduce((n, g) => n + g.cantidad, 0);
  return (
    <>
      <Typography gutterBottom>
        Después de cerrarlo, <strong>ninguna provincia puede importar más archivos</strong> para {r.periodo.nombre}.
      </Typography>
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Situación</TableCell>
              <TableCell align="right">Provincias</TableCell>
              <TableCell>Cuáles</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {r.grupos.map((g) => (
              <TableRow key={g.grupo}>
                <TableCell sx={g.grupo === 'SIN_EMPEZAR' && g.cantidad ? { color: 'error.dark', fontWeight: 700 } : {}}>
                  {g.titulo}
                </TableCell>
                <TableCell align="right">{g.cantidad}</TableCell>
                <TableCell>
                  {g.provincias
                    .map((p) => (p.faltan.length ? `${p.jurisdiccion} (faltan ${p.faltan.length})` : p.jurisdiccion))
                    .join(', ') || '—'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {sinCerrar > 0 && (
        <Alert severity="error" sx={{ mt: 1.5 }}>
          <strong>
            {sinCerrar === 1 ? '1 provincia no llegó a cerrar la carga.' : `${sinCerrar} provincias no llegaron a cerrar la carga.`}
          </strong>{' '}
          Si cerrás el período, quedan con lo que cargaron hasta ahora.
        </Alert>
      )}
    </>
  );
}

export function Administracion() {
  const consulta = useAdministracion();
  const cambiarEstado = useCambiarEstadoDelPeriodo();
  const cambiarOperativo = useCambiarOperativo();
  const armar = useArmarDemo();
  const borrar = useBorrarImportaciones();
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  const [agregar, setAgregar] = useState('');
  const alTerminar = {
    onSuccess: (r: { mensaje: string; aviso?: string }) => avisar({ texto: [r.mensaje, r.aviso].filter(Boolean).join(' ') }),
    onError: (e: unknown) => avisar({ texto: mensajeDeError(e), error: true }),
  };
  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar la administración.</Alert>;
  const d = consulta.data;
  const ocupado = cambiarEstado.isPending || armar.isPending || borrar.isPending || cambiarOperativo.isPending;
  const enElOperativo = d.jurisdicciones.filter((j) => j.en_el_operativo).map((j) => j.nombre);
  const yaCargo = new Set(d.jurisdicciones.filter((j) => j.ya_cargo).map((j) => j.nombre));
  const paraAgregar = d.todas.filter((j) => !enElOperativo.includes(j));

  const pasarA = async (codigo: string, nuevo: string, titulo: string, texto: ReactNode) => {
    if ((await confirmar({ titulo, texto, confirmar: titulo, color: 'warning' })) === null) return;
    cambiarEstado.mutate({ codigo, estado: nuevo }, alTerminar);
  };

  const cerrar = async (codigo: string, nombre: string) => {
    try {
      const r = (await api.get<ResumenDeCierre>(`periodos/${codigo}/resumen-de-cierre/`)).data;
      await pasarA(codigo, 'CERRADO', `Cerrar ${nombre} para todas las provincias`, <TextoDelCierre r={r} />);
    } catch (e) {
      avisar({ texto: mensajeDeError(e), error: true });
    }
  };

  const operativo = (nombre: string, en_el_operativo: boolean) =>
    cambiarOperativo.mutate({ nombre, en_el_operativo }, alTerminar);

  return (
    <>
      <Titulo titulo="Administración" subtitulo="Sólo el administrador nacional." />
      <Stack spacing={2}>
        <Card variant="outlined">
          <TableContainer>
            <Table size="small" aria-label="Períodos">
              <TableHead>
                <TableRow>
                  <TableCell>Período</TableCell>
                  <TableCell>Desde</TableCell>
                  <TableCell>Hasta</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Presentaron</TableCell>
                  <TableCell align="right" />
                </TableRow>
              </TableHead>
              <TableBody>
                {d.periodos.map((p) => {
                  const e = formaDe(ESTADO_DEL_PERIODO, p.estado);
                  return (
                    <TableRow key={p.codigo}>
                      <TableCell sx={{ fontWeight: 700 }}>{p.nombre}</TableCell>
                      <TableCell>{fecha(p.fecha_desde)}</TableCell>
                      <TableCell>{fecha(p.fecha_hasta)}</TableCell>
                      <TableCell>
                        <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
                      </TableCell>
                      <TableCell>
                        {p.presentaron} de {d.operativo}
                      </TableCell>
                      <TableCell align="right">
                        <Stack direction="row" spacing={1} sx={{ justifyContent: 'flex-end', flexWrap: 'wrap', rowGap: 1 }}>
                          {p.estado !== 'ABIERTO' && (
                            <ConAyuda ayuda="Habilita a las provincias a importar los archivos del período. Desde ese momento la definición (reglas y columnas) queda congelada.">
                              <Button
                                size="small"
                                variant="contained"
                                disabled={ocupado}
                                onClick={() =>
                                  pasarA(p.codigo, 'ABIERTO', `Abrir ${p.nombre}`, 'Las provincias van a poder importar, y la definición queda congelada.')
                                }
                              >
                                Abrir
                              </Button>
                            </ConAyuda>
                          )}
                          {p.estado === 'ABIERTO' && (
                            <>
                              <ConAyuda ayuda="Cierra el período para TODAS las provincias: ninguna puede importar más. Antes muestra qué hay y qué falta.">
                                <Button size="small" variant="outlined" disabled={ocupado} onClick={() => cerrar(p.codigo, p.nombre)}>
                                  Cerrar
                                </Button>
                              </ConAyuda>
                              <ConAyuda ayuda="Herramienta de prueba: vuelve el período a preparación para poder cambiar la definición. En el sistema real no existe.">
                                <Button
                                  size="small"
                                  variant="outlined"
                                  disabled={ocupado}
                                  onClick={() =>
                                    pasarA(
                                      p.codigo,
                                      'PREPARACION',
                                      'Volver a preparación',
                                      'Habilita a cambiar la definición. Es una herramienta de prueba: en el sistema real, con el período abierto, la definición no se toca.',
                                    )
                                  }
                                >
                                  Volver a preparación
                                </Button>
                              </ConAyuda>
                            </>
                          )}
                        </Stack>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Typography sx={{ fontWeight: 700 }}>Provincias del operativo ({enElOperativo.length})</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
              Las que tienen que presentar. Las demás no aparecen en el Estado de situación. Las que ya cargaron
              llevan un candado: no se pueden sacar.
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
              {enElOperativo.map((j) =>
                // La que ya cargó no se saca: lo presentado quedaría fuera del
                // estado de situación (28-09-2026). Lleva un candado.
                yaCargo.has(j) ? (
                  <Tooltip key={j} describeChild title={`${j} ya cargó archivos: no se puede sacar del operativo.`}>
                    <Chip label={j} color="primary" icon={<LockOutlined />} />
                  </Tooltip>
                ) : (
                  <Chip
                    key={j}
                    label={j}
                    color="primary"
                    variant="outlined"
                    disabled={ocupado}
                    onDelete={() => operativo(j, false)}
                    aria-label={`Sacar a ${j} del operativo`}
                  />
                ),
              )}
              <TextField
                select
                size="small"
                label="Agregar"
                value={agregar}
                onChange={(e) => setAgregar(e.target.value)}
                sx={{ minWidth: 180 }}
              >
                {paraAgregar.map((j) => (
                  <MenuItem key={j} value={j}>
                    {j}
                  </MenuItem>
                ))}
              </TextField>
              <Button
                size="small"
                startIcon={<AddOutlined />}
                disabled={!agregar || ocupado}
                onClick={() => {
                  operativo(agregar, true);
                  setAgregar('');
                }}
              >
                Agregar
              </Button>
            </Box>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center', mb: 1.5 }}>
              <Typography sx={{ fontWeight: 700 }}>Herramientas de prueba</Typography>
              <EtiquetaDeEstado tono="attention" texto="no forman parte del sistema definitivo" />
            </Stack>
            <Stack direction="row" sx={{ flexWrap: 'wrap', gap: 1 }}>
              <ConAyuda ayuda="Borra lo cargado y arma una presentación completa de Chubut, con advertencias para corregir.">
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
              </ConAyuda>
              <ConAyuda ayuda="Borra todas las importaciones de todas las provincias.">
                <Button
                  variant="outlined"
                  color="warning"
                  disabled={ocupado}
                  onClick={async () => {
                    const ok = await confirmar({
                      titulo: 'Borrar importaciones',
                      texto: 'Se borrarán TODAS las importaciones de TODAS las jurisdicciones. Existe únicamente para hacer pruebas.',
                      confirmar: 'Borrar todo',
                      color: 'warning',
                    });
                    if (ok !== null) borrar.mutate(undefined, alTerminar);
                  }}
                >
                  Borrar importaciones
                </Button>
              </ConAyuda>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </>
  );
}
