import ChecklistOutlined from '@mui/icons-material/ChecklistOutlined';
import DownloadOutlined from '@mui/icons-material/DownloadOutlined';
import FactCheckOutlined from '@mui/icons-material/FactCheckOutlined';
import HomeOutlined from '@mui/icons-material/HomeOutlined';
import ManageSearchOutlined from '@mui/icons-material/ManageSearchOutlined';
import UploadFileOutlined from '@mui/icons-material/UploadFileOutlined';
import { Alert, Box, CircularProgress } from '@mui/material';
import { useSesion } from '@mir/api';
import { Avisos, Layout, type ItemDeMenu } from '@mir/ui';
import { useEffect, type ReactNode } from 'react';
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { conFiltros } from './comun/filtros';
import { Cargar } from './paginas/Cargar';
import { Comprobante } from './paginas/Comprobante';
import { Datos } from './paginas/Datos';
import { Detalle } from './paginas/Detalle';
import { Inicio } from './paginas/Inicio';
import { Plantillas } from './paginas/Plantillas';
import { Reglas } from './paginas/Reglas';
import { Resultado } from './paginas/Resultado';
import { Revision } from './paginas/Revision';

// El ícono de cada sección. Las secciones y quién las ve las decide el back.
const ICONOS: Record<string, ReactNode> = {
  inicio: <HomeOutlined />,
  plantillas: <DownloadOutlined />,
  cargar: <UploadFileOutlined />,
  resultado: <FactCheckOutlined />,
  revision: <ManageSearchOutlined />,
  estructura: <ChecklistOutlined />,
};

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
};

const BASE = '/v2/mir';

export function App() {
  const sesion = useSesion();
  const navegar = useNavigate();
  const { pathname, search } = useLocation();

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
  const activa = SECCION_DE[pathname.split('/')[1] ?? ''] ?? '';

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
          <Route path="*" element={<Alert severity="info">Esa página no existe.</Alert>} />
        </Routes>
      </Layout>
    </Avisos>
  );
}
