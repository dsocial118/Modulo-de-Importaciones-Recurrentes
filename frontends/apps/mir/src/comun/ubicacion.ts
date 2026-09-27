import type { Observacion } from '@mir/api';

/** Dónde está una observación: la hoja, de quién es la fila y el campo. */
export const dondeEsta = (o: Observacion) =>
  [o.archivo_codigo, o.hoja !== o.archivo_codigo ? o.hoja : null, o.identificador_registro || (o.numero_fila ? `fila ${o.numero_fila}` : null), o.campo_titulo]
    .filter(Boolean)
    .join(' · ');
