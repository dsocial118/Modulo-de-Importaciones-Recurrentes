import {
  Alert,
  Card,
  LinearProgress,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useObservacionesDelPeriodo } from '@mir/api';
import { EtiquetaDeEstado, Titulo, type Tono } from '@mir/ui';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { conFiltros, useFiltros } from '../comun/filtros';
import { fechaHora } from '../comun/formato';
import { SelectorDePeriodo } from '../comun/Selectores';

/**
 * Todas las observaciones del período, para el seguimiento del nivel nacional
 * (maqueta aprobada el 27-09-2026). La provincia ve las suyas en la solapa
 * «Observaciones» de su presentación.
 */

const ESTADOS: Record<string, { texto: string; tono: Tono }> = {
  ABIERTA: { texto: 'Abierta', tono: 'critical' },
  RESPONDIDA: { texto: 'Respondida', tono: 'info' },
  SUBSANADA: { texto: 'Subsanada', tono: 'pending' },
  DESESTIMADA: { texto: 'Desestimada', tono: 'pending' },
};

export function ObservacionesDelPeriodo() {
  const { periodo, cambiar } = useFiltros();
  const [params, setParams] = useSearchParams();
  const provincia = params.get('provincia');
  // De entrada, todas: provincia y estado (28-09-2026).
  const estado = params.get('estado') ?? 'TODAS';
  const consulta = useObservacionesDelPeriodo(periodo, provincia, estado === 'TODAS' ? null : estado);
  const navegar = useNavigate();
  const poner = (clave: string, valor: string) => {
    const nuevos = new URLSearchParams(params);
    if (valor) nuevos.set(clave, valor);
    else nuevos.delete(clave);
    setParams(nuevos, { replace: true });
  };
  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudieron cargar las observaciones.</Alert>;
  const d = consulta.data;

  return (
    <>
      <Titulo
        titulo="Observaciones"
        subtitulo="Las observaciones que hizo la revisión nacional sobre los datos que importaron las provincias."
      >
        <TextField
          select
          size="small"
          label="Provincia"
          value={provincia ?? ''}
          onChange={(e) => poner('provincia', e.target.value)}
          sx={{ minWidth: 180 }}
          // Que diga «Todas» cuando no hay una elegida: vacío no se entendía.
          slotProps={{ select: { displayEmpty: true }, inputLabel: { shrink: true } }}
        >
          <MenuItem value="">Todas</MenuItem>
          {d.jurisdicciones.map((j) => (
            <MenuItem key={j} value={j}>
              {j}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          select
          size="small"
          label="Estado"
          value={estado}
          onChange={(e) => poner('estado', e.target.value)}
          sx={{ minWidth: 160 }}
        >
          <MenuItem value="TODAS">Todas</MenuItem>
          <MenuItem value="ABIERTA">Sin resolver</MenuItem>
          <MenuItem value="RESPONDIDA">Respondidas</MenuItem>
          <MenuItem value="SUBSANADA">Subsanadas</MenuItem>
        </TextField>
        {d.periodo && (
          <SelectorDePeriodo periodos={d.periodos} valor={d.periodo.codigo} alCambiar={(x) => cambiar({ periodo: x })} />
        )}
      </Titulo>
      <Card variant="outlined">
        <TableContainer>
          <Table size="small" aria-label="Observaciones del período">
            <TableHead>
              <TableRow>
                <TableCell>Provincia</TableCell>
                <TableCell>Archivo · dato</TableCell>
                <TableCell>Registro</TableCell>
                <TableCell>Observación</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Observó</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {d.filas.map((o) => {
                const e = ESTADOS[o.estado] ?? { texto: o.estado, tono: 'pending' as Tono };
                return (
                  <TableRow
                    key={o.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    aria-label={`Abrir la presentación de ${o.jurisdiccion}`}
                    // Abre la provincia en la solapa de sus observaciones.
                    onClick={() =>
                      navegar(conFiltros('/resultado', d.periodo?.codigo, o.jurisdiccion, { solapa: 'observaciones' }))
                    }
                  >
                    <TableCell sx={{ fontWeight: 700 }}>{o.jurisdiccion}</TableCell>
                    <TableCell>
                      {o.archivo_nombre ? (
                        <>
                          <strong>{o.archivo_nombre}</strong>
                          {o.campo_titulo && ` · ${o.campo_titulo}`}
                        </>
                      ) : (
                        'Sobre la presentación'
                      )}
                    </TableCell>
                    <TableCell>{o.identificador_registro || (o.numero_fila ? `fila ${o.numero_fila}` : '—')}</TableCell>
                    <TableCell>
                      {o.texto}
                      {o.respuesta && (
                        <Typography variant="body2" color="text.secondary">
                          Respuesta: {o.respuesta}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <EtiquetaDeEstado tono={e.tono} texto={e.texto} />
                    </TableCell>
                    <TableCell>
                      {o.usuario_observa ?? '—'}
                      <Typography variant="body2" color="text.secondary">
                        {fechaHora(o.creada_el)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
        {d.filas.length === 0 && (
          <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
            No hay observaciones con ese filtro.
          </Typography>
        )}
      </Card>
    </>
  );
}
