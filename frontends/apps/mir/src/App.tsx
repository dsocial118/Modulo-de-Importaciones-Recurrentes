import HomeOutlined from '@mui/icons-material/HomeOutlined';
import { Alert, Box, CircularProgress, GlobalStyles } from '@mui/material';
import { useSesion } from '@mir/api';
import { Avisos, Layout, type ItemDeMenu } from '@mir/ui';
import { useEffect, useRef } from 'react';
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { conFiltros } from './comun/filtros';
import { ICONOS } from './comun/iconos';
import { Cargar } from './paginas/Cargar';
import { Comprobante } from './paginas/Comprobante';
import { Datos } from './paginas/Datos';
import { Detalle } from './paginas/Detalle';
import { Inicio } from './paginas/Inicio';
import { Plantillas } from './paginas/Plantillas';
import { Reglas } from './paginas/Reglas';
import { Situacion } from './paginas/Situacion';
import { ObservacionesDelPeriodo } from './paginas/ObservacionesDelPeriodo';
import { Administracion } from './paginas/Administracion';
import { Resultado } from './paginas/Resultado';
import { Revision } from './paginas/Revision';
import { FranjaDelCircuito } from './comun/Franja';

// El ícono de cada sección. Las secciones y quién las ve las decide el back.
// Qué sección del menú queda marcada según la dirección: el detalle de una
// importación y el comprobante son parte del resultado.
const SECCION_DE: Record<string, string> = {
  '': 'inicio',
  plantillas: 'plantillas',
  cargar: 'cargar',
  resultado: 'resultado',
  presentacion: 'resultado',
  revision: 'revision',
  reglas: 'estructura',
  situacion: 'situacion',
  observaciones: 'observaciones',
  administracion: 'administracion',
};

const BASE = '/v2/mir';

export function App() {
  const sesion = useSesion();
  const navegar = useNavigate();
  const { pathname, search } = useLocation();
  // Al cambiar de pantalla, el recuadro arranca arriba: ya no es la ventana la
  // que se desplaza, y sin esto quedaba donde había quedado la anterior.
  const contenido = useRef<HTMLDivElement>(null);
  useEffect(() => {
    contenido.current?.scrollTo?.(0, 0);
  }, [pathname]);

  useEffect(() => {
    if (sesion.data) document.title = sesion.data.instancia;
  }, [sesion.data]);

  if (sesion.isPending) {
    return (
      <Box sx={{ display: 'grid', placeItems: 'center', minHeight: '100vh' }}>
        <CircularProgress aria-label="Cargando" />
      </Box>
    );
  }
  if (sesion.isError) {
    return (
      <Alert severity="error" sx={{ m: 3 }}>
        No se pudo obtener la sesión. Probá recargar la página.
      </Alert>
    );
  }

  const s = sesion.data;
  // Al pasar de una sección a otra se conservan el período y la jurisdicción.
  const actuales = new URLSearchParams(search);
  const menu: ItemDeMenu[] = s.menu.map((m) => {
    const ruta = m.en_v2 ? m.ruta.replace(BASE, '') || '/' : m.ruta;
    return {
      clave: m.clave,
      etiqueta: m.etiqueta,
      href: m.en_v2 ? `${BASE}${conFiltros(ruta, actuales.get('periodo'), actuales.get('jurisdiccion'))}` : m.ruta,
      ruta: conFiltros(ruta, actuales.get('periodo'), actuales.get('jurisdiccion')),
      icono: ICONOS[m.clave] ?? <HomeOutlined />,
      enV2: m.en_v2,
    };
  });
  // Si la sección no está en el menú de quien mira —el nivel nacional entra al
  // resultado de una provincia desde la bandeja de revisión—, se marca la
  // sección desde la que llegó: si no, el menú no marcaba nada (27-09-2026).
  const seccion = SECCION_DE[pathname.split('/')[1] ?? ''] ?? '';
  const enElMenu = s.menu.some((m) => m.clave === seccion);
  const desde = ['situacion', 'revision'].find((c) => s.menu.some((m) => m.clave === c));
  const activa = enElMenu ? seccion : seccion === 'resultado' && desde ? desde : seccion;

  return (
    <Avisos>
      <Layout
        instancia={s.instancia}
        usuario={s.usuario}
        rol={s.nombre_del_rol}
        entidad={s.jurisdiccion}
        aviso={s.aviso}
        menu={menu}
        activa={activa}
        salir={s.salir}
        alNavegar={(ruta) => navegar(ruta)}
      >
        {/* Los títulos de las tablas, en el verde de marca con su tinta de
            contraste (propuesta B, elegida el 27-09-2026). Color lleno: varios
            quedan fijos al desplazarse, y uno transparente dejaría ver debajo. */}
        <GlobalStyles
          styles={(t) => ({
            '#contenido .MuiTableHead-root .MuiTableCell-head': {
              backgroundColor: t.palette.primary.main,
              color: t.palette.primary.contrastText,
              fontWeight: 600,
            },
          })}
        />
        <FranjaDelCircuito />
        {/* El recuadro de cada pantalla: lo único que se desplaza (27-09-2026). */}
        <Box
          ref={contenido}
          id="contenido"
          sx={{
            flex: 1,
            minHeight: 0,
            overflow: 'auto',
            px: { xs: 2, md: 3 },
            pb: { xs: 2, md: 3 },
            '@media print': { overflow: 'visible' },
          }}
        >
        <Routes>
          <Route path="/" element={<Inicio sesion={s} />} />
          <Route path="/plantillas" element={<Plantillas />} />
          <Route path="/cargar" element={<Cargar />} />
          <Route path="/resultado" element={<Resultado />} />
          <Route path="/resultado/:id" element={<Detalle />} />
          <Route path="/resultado/:id/datos" element={<Datos />} />
          <Route path="/presentacion/:id/comprobante" element={<Comprobante />} />
          <Route path="/revision" element={<Revision />} />
          <Route path="/reglas" element={<Reglas />} />
          <Route path="/situacion" element={<Situacion />} />
          <Route path="/observaciones" element={<ObservacionesDelPeriodo />} />
          <Route path="/administracion" element={<Administracion />} />
          <Route path="*" element={<Alert severity="info">Esa página no existe.</Alert>} />
        </Routes>
        </Box>
      </Layout>
    </Avisos>
  );
}
