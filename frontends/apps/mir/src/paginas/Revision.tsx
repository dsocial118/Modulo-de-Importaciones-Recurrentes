import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  LinearProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import { mensajeDeError, useAccion, useRevision, type PresentacionEnRevision } from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar, useConfirmar } from '@mir/ui';
import { useNavigate } from 'react-router-dom';
import { tonoDeLaPresentacion } from '../comun/estados';
import { fechaHora, plural } from '../comun/formato';
import { SelectorDePeriodo } from '../comun/Selectores';
import { conFiltros, useFiltros } from '../comun/filtros';

/**
 * Revisión nacional: la bandeja de trabajo del revisor. Sólo lo que requiere
 * una acción suya (maqueta aprobada el 27-09-2026); el panorama completo está
 * en «Estado de situación». Un clic en la fila abre la provincia.
 */

// Lo que espera al revisor: tomarla, seguir revisando o ver las respuestas.
const LE_TOCA = ['CERRADA', 'EN_REVISION', 'SUBSANADA'];

function Fila({ p, periodo }: { p: PresentacionEnRevision; periodo?: string }) {
  const navegar = useNavigate();
  const accion = useAccion();
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  // Abre la provincia en la solapa que corresponde: con respuestas, sus observaciones.
  const abrir = () =>
    navegar(
      conFiltros('/resultado', periodo, p.jurisdiccion, { solapa: p.estado === 'SUBSANADA' ? 'observaciones' : 'resumen' }),
    );

  return (
    <TableRow hover sx={{ cursor: 'pointer' }} onClick={abrir} aria-label={`Abrir la presentación de ${p.jurisdiccion}`}>
      <TableCell sx={{ fontWeight: 700 }}>{p.jurisdiccion}</TableCell>
      <TableCell>
        <EtiquetaDeEstado tono={tonoDeLaPresentacion(p.estado)} texto={p.estado_legible} />
      </TableCell>
      <TableCell>{p.cerrada_el ? fechaHora(p.cerrada_el) : '—'}</TableCell>
      <TableCell>
        {p.observaciones > 0 ? (
          <EtiquetaDeEstado tono="critical" texto={plural(p.observaciones, 'abierta', 'abiertas')} />
        ) : (
          '—'
        )}
      </TableCell>
      <TableCell align="right" onClick={(e) => e.stopPropagation()}>
        <Stack direction="row" spacing={1} sx={{ justifyContent: 'flex-end', flexWrap: 'wrap', rowGap: 1 }}>
          {p.acciones.map((a) => (
            <Tooltip key={a.accion} describeChild title={a.ayuda}>
              <span>
                <Button
                  size="small"
                  variant={a.accion === 'devolver' ? 'outlined' : 'contained'}
                  color={a.accion === 'devolver' ? 'warning' : 'primary'}
                  disabled={accion.isPending}
                  onClick={async () => {
                    if (a.accion === 'habilitar') {
                      const ok = await confirmar({
                        titulo: a.etiqueta,
                        texto:
                          p.estado === 'CERRADA'
                            ? `La revisión de ${p.jurisdiccion} todavía no se inició. ¿Se habilita igualmente para que realice la presentación formal?`
                            : `Concluye la revisión de ${p.jurisdiccion} y la habilita a presentar formalmente.`,
                        confirmar: a.etiqueta,
                      });
                      if (ok === null) return;
                    }
                    accion.mutate(
                      { presentacion: p.id, accion: a.accion },
                      {
                        onSuccess: (r) => avisar({ texto: r.mensaje }),
                        onError: (e) => avisar({ texto: mensajeDeError(e), error: true }),
                      },
                    );
                  }}
                >
                  {a.etiqueta}
                </Button>
              </span>
            </Tooltip>
          ))}
        </Stack>
      </TableCell>
    </TableRow>
  );
}

export function Revision() {
  const { periodo, cambiar } = useFiltros();
  const consulta = useRevision(periodo);
  const navegar = useNavigate();
  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar la revisión.</Alert>;
  const d = consulta.data;
  const pendientes = d.presentaciones.filter((p) => LE_TOCA.includes(p.estado));
  const otras = d.presentaciones.filter((p) => !LE_TOCA.includes(p.estado));

  return (
    <>
      <Titulo
        titulo="Revisión nacional"
        subtitulo={
          <>
            Presentaciones pendientes de revisión{d.periodo ? ` · ${d.periodo.nombre}` : ''}. El revisor observa; <strong>no modifica
            datos provinciales.</strong>
          </>
        }
      >
        {d.periodo && (
          <SelectorDePeriodo periodos={d.periodos} valor={d.periodo.codigo} alCambiar={(x) => cambiar({ periodo: x })} />
        )}
      </Titulo>
      {!d.es_revisor && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Este rol permite consultar la bandeja, pero no ejecutar acciones de revisión.
        </Alert>
      )}
      <Card variant="outlined">
        <TableContainer>
          <Table size="small" aria-label="Presentaciones para revisar">
            <TableHead>
              <TableRow>
                <TableCell>Provincia</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Cerró la carga</TableCell>
                <TableCell>Observaciones</TableCell>
                <TableCell align="right" />
              </TableRow>
            </TableHead>
            <TableBody>
              {pendientes.map((p) => (
                <Fila key={p.id} p={p} periodo={d.periodo?.codigo} />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {pendientes.length === 0 && (
          <Box sx={{ py: 3, px: 2, textAlign: 'center' }}>
            <Typography sx={{ fontWeight: 700 }}>No hay presentaciones pendientes de revisión.</Typography>
            <Typography variant="body2" color="text.secondary">
              Una provincia se incorpora a este listado al cerrar la carga y enviarla a revisión nacional, y vuelve a
              incorporarse al responder las observaciones formuladas.
            </Typography>
          </Box>
        )}
      </Card>
      {/* Las demás, para que se entienda por qué no están arriba (28-09-2026). */}
      {otras.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" sx={{ fontWeight: 700, mb: 0.75 }}>
            Otras provincias del operativo, sin revisión pendiente (en carga, habilitadas o presentadas)
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.75 }}>
            {otras.map((p) => (
              <Chip
                key={p.id}
                size="small"
                variant="outlined"
                label={`${p.jurisdiccion} · ${p.estado_legible}`}
                onClick={() => navegar(conFiltros('/resultado', d.periodo?.codigo, p.jurisdiccion))}
              />
            ))}
          </Box>
        </Box>
      )}
      <Button size="small" sx={{ mt: 1.5 }} onClick={() => navegar(conFiltros('/situacion', d.periodo?.codigo))}>
        Ver cómo viene cada provincia en el Estado de situación
      </Button>
    </>
  );
}
