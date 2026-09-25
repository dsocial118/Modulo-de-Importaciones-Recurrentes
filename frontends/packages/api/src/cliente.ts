import axios from 'axios';

// Canal único con el back: /api/mir/. Mismo dominio que la página, así que la
// sesión de Django viaja sola en la galleta. No hay tokens en el navegador.
export const api = axios.create({
  baseURL: '/api/mir/',
  withCredentials: true,
  headers: { Accept: 'application/json' },
});

// El token de CSRF lo entrega /api/mir/sesion/. El nombre de la galleta cambia
// según la base, así que no se busca: se recibe y se guarda acá.
let csrf = '';
export function guardarCsrf(token: string) {
  csrf = token;
}

api.interceptors.request.use((config) => {
  const metodo = (config.method ?? 'get').toLowerCase();
  if (csrf && !['get', 'head', 'options'].includes(metodo)) {
    config.headers.set('X-CSRFToken', csrf);
  }
  return config;
});

// Si la sesión venció, al login actual, que vuelve a esta misma página.
api.interceptors.response.use(
  (r) => r,
  (error) => {
    const estado = error?.response?.status;
    const detalle: string = error?.response?.data?.detail ?? '';
    const sinSesion = estado === 401 || (estado === 403 && /credencial|authentication/i.test(detalle));
    if (sinSesion) {
      const volver = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.assign(`/entrar/?next=${volver}`);
    }
    return Promise.reject(error);
  },
);
