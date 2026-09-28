import { useSesion } from '@mir/api';

/**
 * Cómo se nombra un archivo en pantalla: «Dispositivos penales» y no
 * DISP_PENAL (pedido del responsable funcional, 27-09-2026). El nombre sale de
 * la definición (`mir_c1_archivo.nombre_corto`) y llega con la sesión; sin él,
 * queda el código, que sigue en los nombres de los Excel y en las direcciones.
 */
export function useNombreDeArchivo() {
  const nombres = useSesion().data?.nombres_de_archivo;
  return (codigo: string | null | undefined) => (codigo ? (nombres?.[codigo] ?? codigo) : '');
}
