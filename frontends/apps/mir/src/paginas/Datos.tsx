import ArrowBack from '@mui/icons-material/ArrowBack';
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
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  LinearProgress,
  MenuItem,
  Pagination,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { mensajeDeError, useCorregir, useDatos, type Celda, type FilaDeDatos } from '@mir/api';
import { EtiquetaDeEstado, Titulo, useAvisar, useConfirmar } from '@mir/ui';
import { useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { tonoDeLaPresentacion } from '../comun/estados';
import { fechaHora, plural } from '../comun/formato';

type AlCorregir = (fila: number, celda: Celda, valor: string) => Promise<boolean>;

/** Un dato. Se guarda al salir del campo —o al elegir, en una lista—, y sólo si cambió. */
function CampoEditable({ fila, celda, editable, alCorregir }: { fila: number; celda: Celda; editable: boolean; alCorregir: AlCorregir }) {
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

function Fila({ f, editable, alCorregir }: { f: FilaDeDatos; editable: boolean; alCorregir: AlCorregir }) {
  return (
    <Accordion variant="outlined" disableGutters slotProps={{ transition: { unmountOnExit: true } }}>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Stack sx={{ width: '100%' }} spacing={0.5}>
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', rowGap: 0.5 }}>
            <Typography sx={{ fontWeight: 500 }}>Fila {f.numero_fila} del Excel</Typography>
            {f.estado === 'EDITADA' && <EtiquetaDeEstado tono="pending" texto="Editada" />}
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
            <CampoEditable key={c.nombre} fila={f.numero_fila} celda={c} editable={editable} alCorregir={alCorregir} />
          ))}
        </Box>
      </AccordionDetails>
    </Accordion>
  );
}

export function Datos() {
  const id = Number(useParams().id);
  const navegar = useNavigate();
  const [params, setParams] = useSearchParams();
  const [verHistorial, setVerHistorial] = useState(false);
  const avisar = useAvisar();
  const confirmar = useConfirmar();
  const filtros = { hoja: params.get('hoja'), pagina: params.get('pagina'), solo: params.get('solo') };
  const consulta = useDatos(id, filtros);
  const corregir = useCorregir(id);

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

  const alCorregir: AlCorregir = async (fila, celda, valor) => {
    const motivo = await confirmar({
      titulo: 'Confirmar el cambio',
      texto: (
        <>
          Fila {fila}, <strong>{celda.titulo}</strong>: de «{celda.valor || '—'}» a «{valor || '—'}». El cambio queda
          registrado con usuario, fecha y valor anterior.
        </>
      ),
      confirmar: 'Guardar',
      campo: { etiqueta: 'Motivo (opcional)' },
    });
    if (motivo === null) return false;
    try {
      const r = await corregir.mutateAsync({ hoja_id: d.hoja.id, numero_fila: fila, campo: celda.nombre, valor, motivo });
      // Guardar y quedar bien no son lo mismo: si el valor nuevo quedó
      // observado, se dice.
      if (r.sin_cambios) avisar({ texto: 'El valor era el mismo: no se registró un cambio.' });
      else if (r.observaciones.length) avisar({ texto: `Guardado, pero quedó observado: ${r.observaciones.join(' ')}` });
      else avisar({ texto: 'Dato corregido. Queda registrado en el historial.' });
      return true;
    } catch (e) {
      avisar({ texto: mensajeDeError(e), error: true });
      return false;
    }
  };

  return (
    <>
      <Titulo
        titulo={`${c.archivo_codigo} · corregir datos`}
        volver={
          <Button size="small" startIcon={<ArrowBack />} onClick={() => navegar(`/resultado/${id}`)} sx={{ mb: 1, ml: -1 }}>
            Volver al detalle de errores
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
        <Button
          variant="outlined"
          startIcon={<HistoryOutlined />}
          disabled={!d.historial.length}
          onClick={() => setVerHistorial(true)}
        >
          Historial de cambios ({d.historial.length})
        </Button>
      </Titulo>

      <Stack spacing={2}>
        {!c.editable ? (
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

        <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ alignItems: { md: 'center' } }}>
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
          <Typography variant="body2" color="text.secondary" sx={{ ml: { md: 'auto' } }}>
            {plural(d.total, 'fila', 'filas')} · página {d.pagina} de {d.paginas}
          </Typography>
        </Stack>

        {consulta.isFetching && <LinearProgress />}
        <Box>
          {d.filas.map((f) => (
            // La clave incluye la página: al cambiar de página, los campos arrancan de cero.
            <Fila key={`${d.hoja.id}-${f.numero_fila}`} f={f} editable={d.puede_editar} alCorregir={alCorregir} />
          ))}
          {d.filas.length === 0 && (
            <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
              {params.get('solo') === 'avisos' ? 'Ninguna fila de esta hoja tiene advertencias.' : 'Esta importación no incorporó filas.'}
            </Typography>
          )}
        </Box>
        {d.paginas > 1 && (
          <Pagination count={d.paginas} page={d.pagina} onChange={(_, n) => poner({ pagina: String(n) })} color="primary" />
        )}
      </Stack>

      <Dialog open={verHistorial} onClose={() => setVerHistorial(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Historial de cambios</DialogTitle>
        <DialogContent>
          <Table size="small">
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
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVerHistorial(false)}>Cerrar</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
