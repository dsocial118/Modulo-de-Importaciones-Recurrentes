import { Link, MenuItem, TextField } from '@mui/material';
import type { Periodo } from '@mir/api';
import type { ReactNode } from 'react';
import { Link as RouterLink, useSearchParams } from 'react-router-dom';

/**
 * El período y la jurisdicción viven en la dirección: recargar, compartir el
 * enlace o volver atrás deja la pantalla como estaba. Y se conservan al pasar
 * de una sección a otra, porque el menú los arrastra.
 */
export function useFiltros() {
  const [params, setParams] = useSearchParams();
  const cambiar = (cambios: Record<string, string | number | null | undefined>) => {
    const nuevos = new URLSearchParams(params);
    for (const [clave, valor] of Object.entries(cambios)) {
      if (valor === null || valor === undefined || valor === '') nuevos.delete(clave);
      else nuevos.set(clave, String(valor));
    }
    setParams(nuevos);
  };
  return {
    params,
    periodo: params.get('periodo'),
    jurisdiccion: params.get('jurisdiccion'),
    cambiar,
  };
}

/** Los filtros de siempre, para agregarlos a un enlace interno. */
export function conFiltros(ruta: string, periodo?: string | null, jurisdiccion?: string | null) {
  const q = new URLSearchParams();
  if (periodo) q.set('periodo', periodo);
  if (jurisdiccion) q.set('jurisdiccion', jurisdiccion);
  const s = q.toString();
  return s ? `${ruta}?${s}` : ruta;
}

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
