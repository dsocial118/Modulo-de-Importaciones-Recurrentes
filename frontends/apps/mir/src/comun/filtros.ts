import { useSearchParams } from 'react-router-dom';

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
