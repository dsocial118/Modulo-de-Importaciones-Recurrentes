import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, guardarCsrf } from './cliente';
import type { components } from './esquema';

// Los tipos salen del esquema OpenAPI del back (npm run tipos). No se escriben
// a mano: si el back cambia la forma de una respuesta, esto deja de compilar.
type E = components['schemas'];
export type Sesion = E['Sesion'];
export type Periodo = E['Periodo'];
export type Inicio = E['Inicio'];
export type ArchivoDelPeriodo = E['ArchivoDelPeriodo'];
export type Plantillas = E['Plantillas'];
export type Carga = E['Carga'];
export type ArchivoACargar = E['ArchivoACargar'];
export type ResultadoDeImportar = E['ResultadoDeImportar'];
export type Resultado = E['Resultado'];
export type ArchivoDelResultado = E['ArchivoDelResultado'];
export type Observacion = E['Observacion'];
export type Accion = E['Accion'];
export type AccionHecha = E['AccionHecha'];
export type Revision = E['Revision'];
export type PresentacionEnRevision = E['PresentacionEnRevision'];
export type Comprobante = E['Comprobante'];
export type Detalle = E['Detalle'];
export type PaginaDeHallazgos = E['PaginaDeHallazgos'];
export type Datos = E['Datos'];
export type FilaDeDatos = E['FilaDeDatos'];
export type Celda = E['Celda'];
export type Correccion = E['Correccion'];
export type CorreccionHecha = E['CorreccionHecha'];
export type Reglas = E['Reglas'];
export type CampoDeReglas = E['CampoDeReglas'];
export type CambiosDeReglas = E['CambiosDeReglas'];
export type ReglasGuardadas = E['ReglasGuardadas'];
export type PeriodoCambiado = E['PeriodoCambiado'];
export type Mensaje = E['Mensaje'];

type Parametros = Record<string, string | number | null | undefined>;

const limpios = (p: Parametros = {}) =>
  Object.fromEntries(Object.entries(p).filter(([, v]) => v !== null && v !== undefined && v !== ''));

/** Una consulta GET. La clave incluye los parámetros: cambiarlos vuelve a pedir. */
function useConsulta<T>(ruta: string | null, params: Parametros = {}) {
  return useQuery({
    queryKey: [ruta, limpios(params)],
    queryFn: async () => (await api.get<T>(ruta!, { params: limpios(params) })).data,
    enabled: ruta !== null,
    // Al cambiar un filtro, lo anterior queda a la vista hasta que llega lo
    // nuevo: la pantalla no parpadea.
    placeholderData: (anterior) => anterior,
  });
}

/**
 * Un envío: POST y, si sale bien, todo lo consultado se vuelve a pedir. Es más
 * simple que saber qué pantallas dependen de qué, y el costo es mínimo: sólo
 * se repiten las consultas que estén a la vista.
 */
function useEnvio<TDatos, TRespuesta>(ruta: (d: TDatos) => string, cuerpo?: (d: TDatos) => unknown) {
  const cliente = useQueryClient();
  return useMutation({
    mutationFn: async (d: TDatos) => (await api.post<TRespuesta>(ruta(d), cuerpo ? cuerpo(d) : d)).data,
    onSuccess: () => cliente.invalidateQueries(),
  });
}

/** El texto que ve la persona cuando algo no salió. */
export function mensajeDeError(error: unknown): string {
  const datos = (error as { response?: { data?: unknown } })?.response?.data;
  if (datos && typeof datos === 'object') {
    const d = datos as Record<string, unknown>;
    if (typeof d.detail === 'string') return d.detail;
    if (Array.isArray(d.errores) && d.errores.length) return (d.errores as string[]).join(' ');
    for (const valor of Object.values(d)) {
      if (Array.isArray(valor) && typeof valor[0] === 'string') return valor[0];
      if (typeof valor === 'string') return valor;
    }
  }
  return 'No se pudo completar la operación. Probá de nuevo.';
}

// --- Sesión e inicio --------------------------------------------------------

export function useSesion() {
  return useQuery({
    queryKey: ['sesion'],
    queryFn: async () => {
      const { data } = await api.get<Sesion>('sesion/');
      guardarCsrf(data.csrf_token);
      return data;
    },
    staleTime: 5 * 60 * 1000,
    // La sesión trae el menú, y el menú dice qué secciones están en /v2/. Una
    // pestaña abierta desde antes de una migración seguía llevando a la versión
    // actual, porque nunca volvía a pedirla. Al volver a la pestaña se renueva.
    refetchOnWindowFocus: true,
  });
}

export const useInicio = (periodo: string | null, jurisdiccion: string | null) =>
  useConsulta<Inicio>('inicio/', { periodo, jurisdiccion });

export const useCambiarEstadoDelPeriodo = () =>
  useEnvio<{ codigo: string; estado: string }, PeriodoCambiado>(
    (d) => `periodos/${d.codigo}/estado/`,
    (d) => ({ estado: d.estado }),
  );

export const useArmarDemo = () => useEnvio<void, Mensaje>(() => 'pruebas/armar-demo/', () => ({}));
export const useBorrarImportaciones = () =>
  useEnvio<void, Mensaje>(() => 'pruebas/borrar-importaciones/', () => ({}));

// --- Plantillas y carga -----------------------------------------------------

export const usePlantillas = (periodo: string | null) => useConsulta<Plantillas>('plantillas/', { periodo });

export const useCarga = (periodo: string | null, jurisdiccion: string | null) =>
  useConsulta<Carga>('carga/', { periodo, jurisdiccion });

export function useCargarArchivo() {
  const cliente = useQueryClient();
  return useMutation({
    mutationFn: async (d: {
      codigo: string;
      archivo: File;
      periodo: string;
      jurisdiccion?: string | null;
      // Cuánto del archivo ya viajó, de 0 a 100. Al llegar a 100 el archivo
      // está en el servidor y lo que falta es revisarlo.
      alAvanzar?: (porcentaje: number) => void;
    }) => {
      const formulario = new FormData();
      formulario.append('archivo', d.archivo);
      formulario.append('periodo', d.periodo);
      if (d.jurisdiccion) formulario.append('jurisdiccion', d.jurisdiccion);
      const { data } = await api.post<ResultadoDeImportar>(`carga/${d.codigo}/`, formulario, {
        onUploadProgress: (e) => d.alAvanzar?.(e.total ? Math.round((e.loaded * 100) / e.total) : 0),
      });
      return data;
    },
    onSuccess: () => cliente.invalidateQueries(),
  });
}

// --- Resultado, circuito y revisión -----------------------------------------

export const useResultado = (periodo: string | null, jurisdiccion: string | null) =>
  useConsulta<Resultado>('resultado/', { periodo, jurisdiccion });

export const useAccion = () =>
  useEnvio<{ presentacion: number; accion: string }, AccionHecha>(
    (d) => `presentaciones/${d.presentacion}/acciones/${d.accion}/`,
    () => ({}),
  );

export const useObservar = () =>
  useEnvio<{ presentacion: number; texto: string }, Mensaje>(
    (d) => `presentaciones/${d.presentacion}/observaciones/`,
    (d) => ({ texto: d.texto }),
  );

export const useResponder = () =>
  useEnvio<{ observacion: number; respuesta: string }, Mensaje>(
    (d) => `observaciones/${d.observacion}/respuesta/`,
    (d) => ({ respuesta: d.respuesta }),
  );

export const useRegistrarExpediente = () =>
  useEnvio<{ presentacion: number; expediente: string }, Mensaje>(
    (d) => `presentaciones/${d.presentacion}/expediente/`,
    (d) => ({ expediente: d.expediente }),
  );

export const useComprobante = (presentacion: number) =>
  useConsulta<Comprobante>(`presentaciones/${presentacion}/comprobante/`);

export const useRevision = (periodo: string | null) => useConsulta<Revision>('revision/', { periodo });

// --- Una importación ---------------------------------------------------------

export const useDetalle = (importacion: number) => useConsulta<Detalle>(`importaciones/${importacion}/`);

export const useHallazgos = (importacion: number, filtros: Parametros) =>
  useConsulta<PaginaDeHallazgos>(`importaciones/${importacion}/hallazgos/`, filtros);

export const useDatos = (importacion: number, filtros: Parametros) =>
  useConsulta<Datos>(`importaciones/${importacion}/datos/`, filtros);

export const useCorregir = (importacion: number) =>
  useEnvio<Correccion, CorreccionHecha>(() => `importaciones/${importacion}/datos/`);

// --- Reglas -----------------------------------------------------------------

export const useReglas = (hoja: string | null) => useConsulta<Reglas>('reglas/', { hoja });

export const useGuardarReglas = () => useEnvio<CambiosDeReglas, ReglasGuardadas>(() => 'reglas/');
