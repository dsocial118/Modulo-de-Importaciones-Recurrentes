// Fechas como se leen acá. Las fechas solas vienen como AAAA-MM-DD, sin hora:
// se arma a mediodía para que ningún huso horario las corra un día.
export const fecha = (iso?: string | null) =>
  iso ? new Date(iso.length === 10 ? `${iso}T12:00:00` : iso).toLocaleDateString('es-AR') : '—';

export const fechaHora = (iso?: string | null) =>
  iso
    ? new Date(iso).toLocaleString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '—';

export const numero = (n?: number | null) => (n == null ? '—' : n.toLocaleString('es-AR'));

export const plural = (n: number, uno: string, varios: string) => `${n.toLocaleString('es-AR')} ${n === 1 ? uno : varios}`;

// Las filas de una importación. Es todo o nada: si se incorporó, entraron todas
// y alcanza con decir cuántas; leídas e incorporadas se separan sólo cuando
// difieren, es decir, cuando se rechazó (27-09-2026).
export const filasEnPalabras = (leidas?: number | null, incorporadas?: number | null) =>
  (incorporadas ?? 0) === (leidas ?? 0)
    ? plural(leidas ?? 0, 'fila', 'filas')
    : `${numero(leidas)} leídas · ${incorporadas ? `${numero(incorporadas)} incorporadas` : 'ninguna incorporada'}`;
