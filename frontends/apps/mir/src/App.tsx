import ChecklistOutlined from '@mui/icons-material/ChecklistOutlined';
import DownloadOutlined from '@mui/icons-material/DownloadOutlined';
import FactCheckOutlined from '@mui/icons-material/FactCheckOutlined';
import HomeOutlined from '@mui/icons-material/HomeOutlined';
import ManageSearchOutlined from '@mui/icons-material/ManageSearchOutlined';
import UploadFileOutlined from '@mui/icons-material/UploadFileOutlined';
import { Alert, Box, CircularProgress } from '@mui/material';
import { useSesion } from '@mir/api';
import { Layout, type ItemDeMenu } from '@mir/ui';
import { useEffect, type ReactNode } from 'react';
import { Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { Inicio } from './paginas/Inicio';

// El ícono de cada sección. Las secciones y quién las ve las decide el back.
const ICONOS: Record<string, ReactNode> = {
  inicio: <HomeOutlined />,
  plantillas: <DownloadOutlined />,
  cargar: <UploadFileOutlined />,
  resultado: <FactCheckOutlined />,
  revision: <ManageSearchOutlined />,
  estructura: <ChecklistOutlined />,
};

const BASE = '/v2/mir';

export function App() {
  const sesion = useSesion();
  const navegar = useNavigate();
  const { pathname } = useLocation();

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
  const menu: ItemDeMenu[] = s.menu.map((m) => ({
    clave: m.clave,
    etiqueta: m.etiqueta,
    href: m.ruta,
    // Las rutas del back para /v2/ son absolutas; el router trabaja sin la base.
    ruta: m.en_v2 ? m.ruta.replace(BASE, '') || '/' : m.ruta,
    icono: ICONOS[m.clave] ?? <HomeOutlined />,
    enV2: m.en_v2,
  }));
  const activa = pathname === '/' ? 'inicio' : pathname.split('/')[1];

  return (
    <Layout
      instancia={s.instancia}
      usuario={s.usuario}
      rol={s.nombre_del_rol}
      aviso={s.aviso}
      menu={menu}
      activa={activa}
      salir={s.salir}
      alNavegar={(ruta) => navegar(ruta)}
    >
      <Routes>
        <Route path="/" element={<Inicio sesion={s} />} />
        <Route path="*" element={<Alert severity="info">Esta sección todavía no está en la versión nueva.</Alert>} />
      </Routes>
    </Layout>
  );
}
