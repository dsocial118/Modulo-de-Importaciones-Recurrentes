import ArrowBack from '@mui/icons-material/ArrowBack';
import PrintOutlined from '@mui/icons-material/PrintOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useComprobante, useSesion } from '@mir/api';
import type { ReactNode } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { fecha, fechaHora, numero } from '../comun/formato';
import { conFiltros } from '../comun/filtros';

/** La constancia formal de la entrega. Se imprime sin el menú ni la barra. */
export function Comprobante() {
  const id = Number(useParams().id);
  const navegar = useNavigate();
  const consulta = useComprobante(id);
  const aviso = useSesion().data?.aviso;
  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="info">La presentación todavía no tiene comprobante.</Alert>;
  const c = consulta.data;
  const fila = (etiqueta: string, valor: ReactNode) => (
    <TableRow>
      <TableCell component="th" sx={{ width: { xs: '42%', sm: 220 }, fontWeight: 500 }}>
        {etiqueta}
      </TableCell>
      <TableCell>{valor}</TableCell>
    </TableRow>
  );

  return (
    <Box sx={{ maxWidth: 860 }}>
      <Box sx={{ display: 'flex', gap: 1, mb: 2, displayPrint: 'none' }}>
        <Button startIcon={<ArrowBack />} onClick={() => navegar(conFiltros('/resultado', c.periodo, c.jurisdiccion))}>
          Volver
        </Button>
        <Button variant="outlined" startIcon={<PrintOutlined />} onClick={() => window.print()} sx={{ ml: 'auto' }}>
          Imprimir
        </Button>
      </Box>
      <Card variant="outlined">
        <CardContent>
          <Typography variant="h5" component="h1" sx={{ fontWeight: 700 }} gutterBottom>
            Comprobante de presentación
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Deja constancia formal de que la jurisdicción cumplió con la entrega de la información del período.
            Constituye un resguardo para la provincia. Se remite por GDE, y el número de expediente obtenido se
            incorpora al sistema.
          </Typography>
          <Table size="small" sx={{ mb: 3 }}>
            <TableBody>
              {fila('Jurisdicción', c.jurisdiccion)}
              {fila('Período', `${c.periodo} (${fecha(c.fecha_desde)} al ${fecha(c.fecha_hasta)})`)}
              {fila('Versión presentada', c.version)}
              {fila('Fecha de presentación', fechaHora(c.presentada_el))}
              {fila('Presentó', c.usuario_presenta ?? '—')}
              {fila('Expediente GDE', c.expediente || 'pendiente de incorporar')}
            </TableBody>
          </Table>
          <Typography variant="subtitle1" sx={{ fontWeight: 500 }} gutterBottom>
            Archivos comprendidos
          </Typography>
          <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Archivo</TableCell>
                <TableCell>Nombre del archivo recibido</TableCell>
                <TableCell align="right">Filas incorporadas</TableCell>
                <TableCell>Importado</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {c.archivos.map((a) => (
                <TableRow key={a.codigo}>
                  <TableCell sx={{ fontWeight: 500 }}>{a.codigo}</TableCell>
                  <TableCell sx={{ fontFamily: 'monospace' }}>{a.nombre_archivo}</TableCell>
                  <TableCell align="right">{numero(a.filas_incorporadas)}</TableCell>
                  <TableCell>{fechaHora(a.iniciada_el)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          </TableContainer>
          {/* El aviso va dentro del comprobante y no sólo en la barra, que no se
              imprime: un comprobante con datos inventados no puede circular
              como si fuera real. */}
          {aviso && (
            <Typography variant="caption" component="p" sx={{ mt: 3, fontWeight: 700, textAlign: 'center' }}>
              {aviso}
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
