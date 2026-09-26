import { Link, MenuItem, TextField } from '@mui/material';
import type { Periodo } from '@mir/api';
import type { ReactNode } from 'react';
import { Link as RouterLink } from 'react-router-dom';

export function SelectorDePeriodo({
  periodos,
  valor,
  alCambiar,
}: {
  periodos: Periodo[];
  valor?: string | null;
  alCambiar: (codigo: string) => void;
}) {
  return (
    <TextField
      select
      size="small"
      label="Período"
      value={valor ?? ''}
      onChange={(e) => alCambiar(e.target.value)}
      sx={{ minWidth: 150 }}
    >
      {periodos.map((p) => (
        <MenuItem key={p.codigo} value={p.codigo}>
          {p.codigo}
        </MenuItem>
      ))}
    </TextField>
  );
}

/** Sólo aparece si hay entre qué elegir: al usuario provincial no se le ofrece. */
export function SelectorDeJurisdiccion({
  jurisdicciones,
  valor,
  alCambiar,
}: {
  jurisdicciones: string[];
  valor?: string | null;
  alCambiar: (jurisdiccion: string) => void;
}) {
  if (!jurisdicciones.length) return null;
  return (
    <TextField
      select
      size="small"
      label="Jurisdicción"
      value={valor ?? ''}
      onChange={(e) => alCambiar(e.target.value)}
      sx={{ minWidth: 200 }}
    >
      <MenuItem value="">
        <em>Elegir…</em>
      </MenuItem>
      {jurisdicciones.map((j) => (
        <MenuItem key={j} value={j}>
          {j}
        </MenuItem>
      ))}
    </TextField>
  );
}

/** Un enlace dentro de /v2/, sin recargar la página. */
export function Enlace({ a, children }: { a: string; children: ReactNode }) {
  return (
    <Link component={RouterLink} to={a} underline="hover">
      {children}
    </Link>
  );
}
