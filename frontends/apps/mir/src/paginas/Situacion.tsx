import {
  Alert,
  Box,
  Card,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useSituacion, type FilaDeSituacion } from '@mir/api';
import { EtiquetaDeEstado, Titulo, type Tono } from '@mir/ui';
import { useNavigate } from 'react-router-dom';
import { conFiltros, useFiltros } from '../comun/filtros';
import { fecha, fechaHora, plural } from '../comun/formato';
import { SelectorDePeriodo } from '../comun/Selectores';
import { tonoDeLaPresentacion } from '../comun/estados';

/**
 * Estado de situación: cómo viene cada provincia del operativo en el período.
 *
 * Pantalla nueva del nivel nacional —revisor y administrador—, sobre la
 * maqueta que aprobó el responsable funcional el 27-09-2026. Arriba los
 * totales; abajo una fila por provincia, y un clic la abre.
 */

function Total({ n, texto, alerta = false }: { n: number; texto: string; alerta?: boolean }) {
  return (
    <Card
      variant="outlined"
      sx={{ p: 1.5, borderTop: 3, borderTopColor: alerta && n > 0 ? 'error.main' : 'primary.main' }}
    >
      <Typography
        sx={{ fontSize: 26, fontWeight: 700, lineHeight: 1.1, color: alerta && n > 0 ? 'error.dark' : 'primary.dark' }}
      >
        {n}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {texto}
      </Typography>
    </Card>
  );
}

function tonoDe(f: FilaDeSituacion): Tono {
  return f.estado === 'SIN_EMPEZAR' ? 'critical' : tonoDeLaPresentacion(f.estado);
}

function Barrita({ hechos, total }: { hechos: number; total: number }) {
  const parte = total ? Math.round((hechos / total) * 100) : 0;
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Box
        role="img"
        aria-label={`${hechos} de ${total} archivos`}
        sx={{ width: 90, height: 8, bgcolor: 'divider', borderRadius: 4, overflow: 'hidden' }}
      >
        <Box sx={{ width: `${parte}%`, height: '100%', bgcolor: 'primary.main' }} />
      </Box>
      <Typography variant="body2">
        {hechos} de {total}
      </Typography>
    </Box>
  );
}

function Observaciones({ f }: { f: FilaDeSituacion }) {
  const partes = [];
  if (f.observaciones_abiertas)
    partes.push(<EtiquetaDeEstado key="a" tono="critical" texto={plural(f.observaciones_abiertas, 'abierta', 'abiertas')} />);
  if (f.observaciones_respondidas)
    partes.push(<EtiquetaDeEstado key="r" tono="info" texto={plural(f.observaciones_respondidas, 'respondida', 'respondidas')} />);
  if (f.observaciones_subsanadas)
    partes.push(<EtiquetaDeEstado key="s" tono="pending" texto={plural(f.observaciones_subsanadas, 'subsanada', 'subsanadas')} />);
  return partes.length ? <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>{partes}</Box> : <>—</>;
}

export function Situacion() {
  const { periodo, cambiar } = useFiltros();
  const consulta = useSituacion(periodo);
  const navegar = useNavigate();
  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudo cargar el estado de situación.</Alert>;
  const d = consulta.data;
  const p = d.periodo;

  return (
    <>
      <Titulo
        titulo="Estado de situación"
        subtitulo={p ? `${p.nombre} · del ${fecha(p.fecha_desde)} al ${fecha(p.fecha_hasta)}` : undefined}
      >
        {p && <SelectorDePeriodo periodos={d.periodos} valor={p.codigo} alCambiar={(x) => cambiar({ periodo: x })} />}
      </Titulo>

      <Box
        sx={{
          display: 'grid',
          gap: 1.5,
          mb: 2,
          gridTemplateColumns: { xs: '1fr 1fr', md: 'repeat(5, minmax(0, 1fr))' },
        }}
      >
        <Total n={d.operativo} texto="provincias del operativo" />
        <Total n={d.totales.presentaron} texto="presentaron o están habilitadas" />
        <Total n={d.totales.en_revision} texto="en revisión nacional" />
        <Total n={d.totales.cargando} texto="cargando" />
        <Total n={d.totales.sin_empezar} texto="sin empezar" alerta />
      </Box>

      <Card variant="outlined">
        <TableContainer>
          <Table size="small" aria-label="Cómo viene cada provincia">
            <TableHead>
              <TableRow>
                <TableCell>Provincia</TableCell>
                <TableCell>Dónde está</TableCell>
                <TableCell>Archivos</TableCell>
                <TableCell align="right">Advertencias</TableCell>
                <TableCell>Observaciones</TableCell>
                <TableCell>Última actividad</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {d.filas.map((f) => (
                  <TableRow
                    key={f.jurisdiccion}
                    aria-label={`Abrir la presentación de ${f.jurisdiccion}`}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => navegar(conFiltros('/resultado', p?.codigo, f.jurisdiccion))}
                  >
                    <TableCell sx={{ fontWeight: 700 }}>{f.jurisdiccion}</TableCell>
                    <TableCell>
                      <EtiquetaDeEstado tono={tonoDe(f)} texto={f.estado_legible} />
                    </TableCell>
                    <TableCell>
                      <Barrita hechos={f.archivos_importados} total={f.archivos_esperados} />
                    </TableCell>
                    <TableCell align="right">{f.archivos_importados ? f.advertencias : '—'}</TableCell>
                    <TableCell>
                      <Observaciones f={f} />
                    </TableCell>
                    <TableCell>{f.ultima_actividad ? fechaHora(f.ultima_actividad) : '—'}</TableCell>
                  </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
      {d.filas.length === 0 && (
        <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
          No hay provincias en el operativo. Se definen en Administración.
        </Typography>
      )}
    </>
  );
}
