import type { Tono } from '@mir/ui';

// Cómo se muestra cada estado. Neutral a propósito: un archivo válido no se
// pinta de verde, porque el verde es de marca y no quiere decir «bien».
type Forma = { texto: string; tono: Tono };

export const ESTADO_DEL_ARCHIVO: Record<string, Forma> = {
  SIN_CARGAR: { texto: 'Sin cargar', tono: 'pending' },
  VALIDA: { texto: 'Importado', tono: 'info' },
  FALLIDA: { texto: 'Con errores', tono: 'critical' },
  ANULADA: { texto: 'Reemplazado', tono: 'pending' },
};

export const ESTADO_DEL_PERIODO: Record<string, Forma> = {
  PREPARACION: { texto: 'En preparación', tono: 'pending' },
  ABIERTO: { texto: 'Abierto', tono: 'info' },
  CERRADO: { texto: 'Cerrado', tono: 'pending' },
};

// La presentación: lo que espera respuesta de la jurisdicción va en atención.
const A_LA_JURISDICCION = new Set(['OBSERVADA', 'SUBSANADA']);
export const tonoDeLaPresentacion = (estado: string): Tono =>
  A_LA_JURISDICCION.has(estado) ? 'attention' : estado === 'EN_CARGA' ? 'pending' : 'info';

export const SEVERIDAD: Record<string, Forma> = {
  BLOQUEANTE: { texto: 'Bloqueante', tono: 'critical' },
  ADVERTENCIA: { texto: 'Advertencia', tono: 'attention' },
};

export const formaDe = (tabla: Record<string, Forma>, codigo: string): Forma =>
  tabla[codigo] ?? { texto: codigo, tono: 'pending' };
