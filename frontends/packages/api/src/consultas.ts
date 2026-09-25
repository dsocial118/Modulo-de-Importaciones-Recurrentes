import { useQuery } from '@tanstack/react-query';
import { api, guardarCsrf } from './cliente';
import type { components } from './esquema';

// Los tipos salen del esquema OpenAPI del back (npm run tipos). No se escriben
// a mano: si el back cambia la forma de una respuesta, esto deja de compilar.
export type Sesion = components['schemas']['Sesion'];
export type Inicio = components['schemas']['Inicio'];
export type ArchivoDelPeriodo = components['schemas']['ArchivoDelPeriodo'];

export function useSesion() {
  return useQuery({
    queryKey: ['sesion'],
    queryFn: async () => {
      const { data } = await api.get<Sesion>('sesion/');
      guardarCsrf(data.csrf_token);
      return data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useInicio(periodo: string | null, jurisdiccion: string | null) {
  return useQuery({
    queryKey: ['inicio', periodo, jurisdiccion],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (periodo) params.periodo = periodo;
      if (jurisdiccion) params.jurisdiccion = jurisdiccion;
      const { data } = await api.get<Inicio>('inicio/', { params });
      return data;
    },
    // Al cambiar de período o de jurisdicción, lo anterior queda a la vista
    // hasta que llega lo nuevo: la pantalla no parpadea.
    placeholderData: (anterior) => anterior,
  });
}
