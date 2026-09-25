import DownloadOutlined from '@mui/icons-material/DownloadOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { usePlantillas } from '@mir/api';
import { Titulo } from '@mir/ui';
import { SelectorDePeriodo, useFiltros } from '../comun/Selectores';

export function Plantillas() {
  const { periodo, cambiar } = useFiltros();
  const consulta = usePlantillas(periodo);
  const chico = useMediaQuery(useTheme().breakpoints.down('sm'));

  if (consulta.isPending) return <LinearProgress aria-label="Cargando" />;
  if (consulta.isError) return <Alert severity="error">No se pudieron cargar las plantillas.</Alert>;
  const d = consulta.data;

  return (
    <>
      <Titulo
        titulo="Plantillas"
        subtitulo={`Modelos para completar y adjuntar — período ${d.periodo?.codigo ?? ''}`}
      >
        <SelectorDePeriodo periodos={d.periodos} valor={d.periodo?.codigo} alCambiar={(p) => cambiar({ periodo: p })} />
      </Titulo>

      {/* Registro impersonal y en dos oraciones: es un texto oficial. */}
      <Alert severity="info" sx={{ mb: 3 }}>
        Las plantillas se generan desde la misma definición que el sistema verifica al importar.{' '}
        <strong>No deben utilizarse las de períodos anteriores.</strong>
      </Alert>

      <Card variant="outlined">
        <CardHeader
          title="Archivos a presentar"
          slotProps={{ title: { variant: 'subtitle1', sx: { fontWeight: 500 } } }}
          action={
            d.descarga_todas && (
              <Button variant="contained" startIcon={<DownloadOutlined />} href={d.descarga_todas} sx={{ mt: 0.5, mr: 1 }}>
                Descargar todas (.zip)
              </Button>
            )
          }
        />
        <CardContent sx={{ pt: 0 }}>
          {chico ? (
            <Stack divider={<Box sx={{ borderTop: 1, borderColor: 'divider' }} />}>
              {d.archivos.map((a) => (
                <Stack key={a.codigo} direction="row" spacing={1} sx={{ py: 1.5, alignItems: 'center' }}>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {a.codigo}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" component="div">
                      {a.nombre}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {a.hojas} hojas · {a.campos} campos{a.obligatorio ? ' · obligatorio' : ''}
                    </Typography>
                  </Box>
                  <Button size="small" variant="outlined" href={a.descarga} aria-label={`Descargar ${a.codigo}`}>
                    <DownloadOutlined fontSize="small" />
                  </Button>
                </Stack>
              ))}
            </Stack>
          ) : (
            <TableContainer>
              <Table size="small" aria-label="Plantillas del período">
                <TableHead>
                  <TableRow>
                    <TableCell>Archivo</TableCell>
                    <TableCell align="right">Hojas</TableCell>
                    <TableCell align="right">Campos</TableCell>
                    <TableCell align="center">Obligatorio</TableCell>
                    <TableCell align="right">Plantilla</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {d.archivos.map((a) => (
                    <TableRow key={a.codigo} hover>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {a.codigo}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {a.nombre}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">{a.hojas}</TableCell>
                      <TableCell align="right">{a.campos}</TableCell>
                      <TableCell align="center">{a.obligatorio ? 'Sí' : '—'}</TableCell>
                      <TableCell align="right">
                        <Button size="small" variant="outlined" startIcon={<DownloadOutlined />} href={a.descarga}>
                          Descargar
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
        Cada plantilla trae el título, los grupos de campos, las listas desplegables con los valores vigentes, los
        campos obligatorios marcados con <strong>*</strong> y una hoja de instrucciones.{' '}
        <strong>Se arma en el momento de descargarla</strong>, así que siempre corresponde a la definición vigente.
      </Typography>
    </>
  );
}
