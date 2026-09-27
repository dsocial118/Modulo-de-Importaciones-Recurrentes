import { Box, MenuItem, Table, TableCell, TableHead, TableRow, TextField, useTheme } from '@mui/material';
import type { Celda, FilaDeDatos } from '@mir/api';
import { coloresDe } from '@mir/ui';
import {
  memo,
  useCallback,
  useLayoutEffect,
  useRef,
  useState,
  type KeyboardEvent,
  type MouseEvent,
  type ReactNode,
} from 'react';

/**
 * Los datos como en el Excel: una fila por registro, los títulos fijos arriba
 * y la identificación fija a la izquierda, para no perder de quién es la fila
 * al moverse de costado (pedido del responsable funcional, 27-09-2026).
 *
 * La grilla vive en un contenedor que entra entero en la pantalla, con sus
 * barras de desplazamiento a la vista; al pie, el renglón del dato elegido y
 * la paginación (27-09-2026).
 *
 * Un clic elige el dato; doble clic —o Enter— lo edita en el lugar, con la
 * misma confirmación que en las fichas. Quien no corrige la ve de sólo lectura.
 *
 * Rendimiento: el MPI son 25 filas por 65 columnas, unas 1.600 celdas. Cada
 * celda es un `<td>` simple con clases —sin componentes ni estilos propios— y
 * los eventos se atienden una sola vez, en el cuerpo de la tabla. Elegir un
 * dato vuelve a dibujar sólo las filas que cambian (`memo`). Antes cada celda
 * traía su texto emergente y cada clic redibujaba todo: se trababa.
 */

export type Elegida = { fila: number; campo: string } | null;

type Props = {
  filas: FilaDeDatos[];
  editable: boolean;
  alCorregir: (fila: FilaDeDatos, celda: Celda, valor: string) => Promise<boolean>;
  elegida: Elegida;
  alElegir: (e: Elegida) => void;
  /** Lo que va al pie del contenedor: el dato elegido y la paginación. */
  pie?: ReactNode;
};

const ANCHO_IDENTIFICACION = 220;
// Lo mínimo para que la grilla sirva; si arriba no queda tanto, ocupa la
// pantalla entera debajo de la barra y la página se corre hasta ella.
const ALTO_MINIMO = 360;

function Editor({ celda, alTerminar }: { celda: Celda; alTerminar: (valor: string | null) => void }) {
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

function textoEmergente(c: Celda): string | undefined {
  if (c.observacion?.estado === 'ABIERTA') return `Observado: ${c.observacion.texto}`;
  if (c.tiene_aviso) return 'Tiene una advertencia: elegí el dato para verla.';
  return undefined;
}

const FilaDeLaGrilla = memo(function FilaDeLaGrilla({
  f,
  campoElegido,
  campoEditando,
  alTerminar,
}: {
  f: FilaDeDatos;
  campoElegido: string | null;
  campoEditando: string | null;
  alTerminar: (f: FilaDeDatos, c: Celda, valor: string | null) => void;
}) {
  return (
    <tr data-fila={f.numero_fila}>
      <th scope="row" className="id">
        <div className="quien" title={f.identificacion}>
          {f.identificacion || '—'}
        </div>
        <div className="nro">fila {f.numero_fila}</div>
      </th>
      {f.celdas.map((c) => {
        const clases = ['c'];
        if (c.tiene_aviso) clases.push('aviso');
        if (c.observacion?.estado === 'ABIERTA') clases.push('obs');
        if (campoElegido === c.nombre) clases.push('elegida');
        return (
          <td key={c.nombre} data-campo={c.nombre} tabIndex={0} className={clases.join(' ')} title={textoEmergente(c)}>
            {campoEditando === c.nombre ? (
              <Editor celda={c} alTerminar={(v) => alTerminar(f, c, v)} />
            ) : (
              c.valor || '—'
            )}
          </td>
        );
      })}
    </tr>
  );
});

const Encabezado = memo(function Encabezado({ campos }: { campos: Celda[] }) {
  return (
    <TableHead>
      <TableRow>
        <TableCell
          sx={{
            fontWeight: 500,
            verticalAlign: 'bottom',
            bgcolor: 'background.paper',
            position: 'sticky',
            left: 0,
            zIndex: 3,
            minWidth: ANCHO_IDENTIFICACION,
            maxWidth: ANCHO_IDENTIFICACION,
          }}
        >
          Fila
        </TableCell>
        {campos.map((c) => (
          <TableCell
            key={c.nombre}
            sx={{
              fontWeight: 500,
              whiteSpace: 'normal',
              minWidth: 150,
              maxWidth: 220,
              verticalAlign: 'bottom',
              bgcolor: 'background.paper',
            }}
          >
            {c.titulo}
            {c.obligatorio && ' *'}
          </TableCell>
        ))}
      </TableRow>
    </TableHead>
  );
});

/** El alto que le queda a la grilla en la ventana, y se recalcula al cambiarla. */
function useAltoDisponible() {
  const ref = useRef<HTMLDivElement>(null);
  const [alto, setAlto] = useState(ALTO_MINIMO);
  useLayoutEffect(() => {
    const medir = () => {
      const el = ref.current;
      if (!el) return;
      const arriba = el.getBoundingClientRect().top + window.scrollY;
      const barra = document.querySelector('header')?.getBoundingClientRect().bottom ?? 64;
      const queda = window.innerHeight - arriba - 16;
      setAlto(Math.round(queda >= ALTO_MINIMO ? queda : Math.max(ALTO_MINIMO, window.innerHeight - barra - 16)));
    };
    medir();
    window.addEventListener('resize', medir);
    // Lo de arriba (avisos, observaciones) puede crecer o achicarse.
    const observador = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(medir);
    observador?.observe(document.body);
    return () => {
      window.removeEventListener('resize', medir);
      observador?.disconnect();
    };
  }, []);
  return { ref, alto };
}

export function Grilla({ filas, editable, alCorregir, elegida, alElegir, pie }: Props) {
  const { palette, typography } = useTheme();
  const aviso = coloresDe('attention', palette.mode);
  const observado = coloresDe('critical', palette.mode);
  const [editando, setEditando] = useState<{ fila: number; campo: string } | null>(null);
  const campos = filas[0]?.celdas ?? [];
  const { ref, alto } = useAltoDisponible();

  // La función de corregir cambia en cada dibujo de la página; se guarda
  // aparte para que las filas no se redibujen por eso.
  const corregir = useRef(alCorregir);
  useLayoutEffect(() => {
    corregir.current = alCorregir;
  });
  const alTerminar = useCallback((f: FilaDeDatos, c: Celda, valor: string | null) => {
    setEditando(null);
    if (valor === null || valor === c.valor) return;
    void corregir.current(f, c, valor);
  }, []);

  // Dónde cayó el evento: la celda y su fila. Lo que viene del editor o de su
  // lista desplegable no es la celda, y se ignora.
  const ubicar = (e: MouseEvent | KeyboardEvent) => {
    const td = (e.target as HTMLElement).closest?.('td[data-campo]') as HTMLElement | null;
    const tr = td?.closest('tr[data-fila]') as HTMLElement | null;
    if (!td || !tr) return null;
    return { td, fila: Number(tr.dataset.fila), campo: td.dataset.campo as string };
  };

  const alClic = (e: MouseEvent) => {
    const u = ubicar(e);
    if (u && !(editando?.fila === u.fila && editando.campo === u.campo)) alElegir({ fila: u.fila, campo: u.campo });
  };
  const alDobleClic = (e: MouseEvent) => {
    const u = ubicar(e);
    if (u && editable) setEditando({ fila: u.fila, campo: u.campo });
  };
  const alTeclear = (e: KeyboardEvent) => {
    const u = ubicar(e);
    // Sólo sobre la celda misma: el Enter del editor lo atiende el editor.
    if (!u || e.target !== u.td || e.key !== 'Enter') return;
    alElegir({ fila: u.fila, campo: u.campo });
    if (editable) setEditando({ fila: u.fila, campo: u.campo });
  };

  const celda = {
    px: 1.5,
    py: 0.75,
    borderBottom: `1px solid ${palette.divider}`,
    fontSize: typography.body2.fontSize,
    lineHeight: 1.43,
    textAlign: 'left',
  } as const;

  return (
    <Box
      ref={ref}
      sx={{
        height: alto,
        display: 'flex',
        flexDirection: 'column',
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        bgcolor: 'background.paper',
        overflow: 'hidden',
      }}
    >
      <Box
        // Las barras siempre a la vista, aunque el sistema las esconda.
        sx={{ flex: 1, minHeight: 0, overflow: 'scroll' }}
        aria-label="Datos en grilla: los títulos quedan fijos al desplazarse"
        role="region"
        tabIndex={-1}
      >
        <Table
          size="small"
          stickyHeader
          sx={{
            borderCollapse: 'separate',
            '& td.c': {
              ...celda,
              minWidth: 150,
              maxWidth: 220,
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              cursor: 'pointer',
            },
            '& tbody tr:hover td.c': { bgcolor: palette.action.hover },
            '& td.aviso, & tbody tr:hover td.aviso': { bgcolor: aviso.surface },
            '& td.obs': { boxShadow: `inset 3px 0 0 ${observado.border}` },
            '& td.elegida': { outline: `2px solid ${palette.primary.main}`, outlineOffset: '-2px' },
            '& td.c:focus-visible': { outline: `2px solid ${palette.primary.main}`, outlineOffset: '-2px' },
            '& th.id': {
              ...celda,
              position: 'sticky',
              left: 0,
              zIndex: 1,
              bgcolor: 'background.paper',
              minWidth: ANCHO_IDENTIFICACION,
              maxWidth: ANCHO_IDENTIFICACION,
              borderRight: `1px solid ${palette.divider}`,
              fontWeight: 400,
            },
            '& th.id .quien': { fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' },
            '& th.id .nro': { fontSize: typography.caption.fontSize, color: 'text.secondary' },
          }}
        >
          <Encabezado campos={campos} />
          <tbody onClick={alClic} onDoubleClick={alDobleClic} onKeyDown={alTeclear}>
            {filas.map((f) => (
              <FilaDeLaGrilla
                key={f.numero_fila}
                f={f}
                campoElegido={elegida?.fila === f.numero_fila ? elegida.campo : null}
                campoEditando={editando?.fila === f.numero_fila ? editando.campo : null}
                alTerminar={alTerminar}
              />
            ))}
          </tbody>
        </Table>
      </Box>
      {pie && (
        <Box sx={{ borderTop: 1, borderColor: 'divider', px: 1.5, py: 1, maxHeight: '45%', overflowY: 'auto' }}>
          {pie}
        </Box>
      )}
    </Box>
  );
}
