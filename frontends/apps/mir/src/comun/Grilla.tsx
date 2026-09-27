import {
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
  useTheme,
} from '@mui/material';
import type { Celda, FilaDeDatos } from '@mir/api';
import { coloresDe } from '@mir/ui';
import { useState, type ReactNode } from 'react';

/**
 * Los datos como en el Excel: una fila por registro, los títulos fijos arriba
 * y la identificación fija a la izquierda, para no perder de quién es la fila
 * al moverse de costado (pedido del responsable funcional, 27-09-2026).
 *
 * Un clic elige el dato y muestra abajo sus advertencias y su observación;
 * doble clic —o Enter— lo edita en el lugar, con la misma confirmación que en
 * las fichas. Quien no corrige ve la grilla de sólo lectura.
 */

export type Elegido = { fila: FilaDeDatos; celda: Celda } | null;

type Props = {
  filas: FilaDeDatos[];
  editable: boolean;
  alCorregir: (fila: FilaDeDatos, celda: Celda, valor: string) => Promise<boolean>;
  elegido: Elegido;
  alElegir: (e: Elegido) => void;
};

const ANCHO_IDENTIFICACION = 220;

function Editor({
  celda,
  alTerminar,
}: {
  celda: Celda;
  alTerminar: (valor: string | null) => void;
}) {
  const [valor, setValor] = useState(celda.valor);
  if (celda.opciones.length) {
    return (
      <TextField
        select
        size="small"
        fullWidth
        autoFocus
        value={celda.opciones.includes(valor) || valor === '' ? valor : ''}
        onChange={(e) => alTerminar(e.target.value)}
        onBlur={() => alTerminar(null)}
        slotProps={{ select: { defaultOpen: true } }}
        aria-label={celda.titulo}
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
  return (
    <TextField
      size="small"
      fullWidth
      autoFocus
      value={valor}
      onChange={(e) => setValor(e.target.value)}
      onBlur={() => alTerminar(valor)}
      onKeyDown={(e) => {
        if (e.key === 'Enter') alTerminar(valor);
        if (e.key === 'Escape') alTerminar(null);
      }}
      slotProps={{ htmlInput: { 'aria-label': celda.titulo } }}
    />
  );
}

export function Grilla({ filas, editable, alCorregir, elegido, alElegir }: Props) {
  const { palette } = useTheme();
  const aviso = coloresDe('attention', palette.mode);
  const observado = coloresDe('critical', palette.mode);
  const [editando, setEditando] = useState<{ fila: number; campo: string } | null>(null);
  const campos = filas[0]?.celdas ?? [];

  const terminar = async (f: FilaDeDatos, c: Celda, valor: string | null) => {
    setEditando(null);
    if (valor === null || valor === c.valor) return;
    await alCorregir(f, c, valor);
  };

  const encabezado = (clave: string, texto: ReactNode, obligatorio: boolean, fijo = false) => (
    <TableCell
      key={clave}
      sx={{
        fontWeight: 500,
        whiteSpace: 'normal',
        minWidth: fijo ? ANCHO_IDENTIFICACION : 150,
        maxWidth: fijo ? ANCHO_IDENTIFICACION : 220,
        verticalAlign: 'bottom',
        bgcolor: 'background.paper',
        ...(fijo && { position: 'sticky', left: 0, zIndex: 3 }),
      }}
    >
      {texto}
      {obligatorio && ' *'}
    </TableCell>
  );

  return (
    <TableContainer
      sx={{ maxHeight: '70vh', border: 1, borderColor: 'divider', borderRadius: 1 }}
      aria-label="Datos en grilla: los títulos quedan fijos al desplazarse"
    >
      <Table size="small" stickyHeader>
        <TableHead>
          <TableRow>
            {encabezado('__fila', 'Fila', false, true)}
            {campos.map((c) => encabezado(c.nombre, c.titulo, c.obligatorio))}
          </TableRow>
        </TableHead>
        <TableBody>
          {filas.map((f) => (
            <TableRow key={f.numero_fila} hover>
              <TableCell
                component="th"
                scope="row"
                sx={{
                  position: 'sticky',
                  left: 0,
                  zIndex: 1,
                  bgcolor: 'background.paper',
                  minWidth: ANCHO_IDENTIFICACION,
                  maxWidth: ANCHO_IDENTIFICACION,
                  borderRight: 1,
                  borderColor: 'divider',
                }}
              >
                <Typography variant="body2" sx={{ fontWeight: 500 }} noWrap title={f.identificacion}>
                  {f.identificacion || '—'}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  fila {f.numero_fila}
                </Typography>
              </TableCell>
              {f.celdas.map((c) => {
                const esEste = elegido?.fila.numero_fila === f.numero_fila && elegido.celda.nombre === c.nombre;
                const enEdicion = editando?.fila === f.numero_fila && editando.campo === c.nombre;
                const abierta = c.observacion?.estado === 'ABIERTA';
                return (
                  <TableCell
                    key={c.nombre}
                    tabIndex={0}
                    onClick={() => alElegir({ fila: f, celda: c })}
                    onDoubleClick={() => editable && setEditando({ fila: f.numero_fila, campo: c.nombre })}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && editable && !enEdicion) setEditando({ fila: f.numero_fila, campo: c.nombre });
                    }}
                    sx={{
                      cursor: 'pointer',
                      minWidth: 150,
                      maxWidth: 220,
                      bgcolor: c.tiene_aviso ? aviso.surface : undefined,
                      boxShadow: abierta ? `inset 3px 0 0 ${observado.border}` : undefined,
                      outline: esEste ? `2px solid ${palette.primary.main}` : undefined,
                      outlineOffset: -2,
                    }}
                  >
                    {enEdicion ? (
                      <Editor celda={c} alTerminar={(v) => void terminar(f, c, v)} />
                    ) : (
                      <Tooltip
                        describeChild
                        title={
                          abierta
                            ? `Observado: ${c.observacion?.texto}`
                            : c.tiene_aviso
                              ? 'Tiene una advertencia: elegí el dato para verla.'
                              : ''
                        }
                      >
                        <Stack direction="row" spacing={0.5} sx={{ alignItems: 'center' }}>
                          <Typography variant="body2" noWrap>
                            {c.valor || '—'}
                          </Typography>
                        </Stack>
                      </Tooltip>
                    )}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
