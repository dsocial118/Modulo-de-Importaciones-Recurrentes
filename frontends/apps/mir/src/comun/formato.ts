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
