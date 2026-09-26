import DarkModeOutlined from '@mui/icons-material/DarkModeOutlined';
import LightModeOutlined from '@mui/icons-material/LightModeOutlined';
import LogoutOutlined from '@mui/icons-material/LogoutOutlined';
import MenuIcon from '@mui/icons-material/Menu';
import OpenInNew from '@mui/icons-material/OpenInNew';
import {
  AppBar,
  Box,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { useState, type MouseEvent, type ReactNode } from 'react';
import { useModo } from './contextos';
import { coloresDe } from './estados';

export type ItemDeMenu = {
  clave: string;
  etiqueta: string;
  // La dirección completa, para que funcione abrir en otra pestaña.
  href: string;
  // Dentro de /v2/, la ruta que entiende el router de la app.
  ruta: string;
  icono: ReactNode;
  // false: la sección todavía está en la versión actual. Se abre con una
  // navegación completa y se marca, para que se sepa que se sale de /v2/.
  enV2: boolean;
};

type Props = {
  instancia: string;
  usuario: string;
  rol: string;
  // La entidad sobre la que trabaja, si es de una. Siempre a la vista: desde
  // que el usuario de una entidad no elige, no había otro lugar que la dijera.
  entidad?: string | null;
  aviso: string;
  menu: ItemDeMenu[];
  activa: string;
  salir: string;
  alNavegar: (ruta: string) => void;
  children: ReactNode;
};

const ANCHO = 264;

/** AppBar + Drawer del front v2. Propio de /v2/: no reusa el menú viejo. */
export function Layout({ instancia, usuario, rol, entidad, aviso, menu, activa, salir, alNavegar, children }: Props) {
  const theme = useTheme();
  const { modo, alternar } = useModo();
  const ancho = useMediaQuery(theme.breakpoints.up('md'));
  const [abierto, setAbierto] = useState(false);
  const atencion = coloresDe('attention', theme.palette.mode);

  const lista = (
    <Box component="nav" aria-label="Secciones" sx={{ overflow: 'auto' }}>
      <List>
        {menu.map((item) => (
          <ListItemButton
            key={item.clave}
            selected={item.clave === activa}
            href={item.href}
            onClick={(e: MouseEvent) => {
              // Dentro de /v2/ navega el router, sin recargar. Con Ctrl o el
              // botón del medio se deja al navegador: abre otra pestaña.
              if (!item.enV2 || e.ctrlKey || e.metaKey || e.button !== 0) return;
              e.preventDefault();
              alNavegar(item.ruta);
              setAbierto(false);
            }}
            sx={{
              color: 'nav.text',
              '&.Mui-selected': {
                bgcolor: 'nav.activeBg',
                borderLeft: `3px solid ${theme.palette.nav.accent}`,
              },
              '&.Mui-selected:hover': { bgcolor: 'nav.activeBg' },
            }}
          >
            <ListItemIcon sx={{ color: item.clave === activa ? 'nav.accent' : 'nav.textMuted', minWidth: 40 }}>
              {item.icono}
            </ListItemIcon>
            <ListItemText primary={item.etiqueta} />
            {!item.enV2 && (
              <Tooltip title="Todavía en la versión actual">
                <OpenInNew fontSize="small" sx={{ color: 'nav.textMuted' }} />
              </Tooltip>
            )}
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Al imprimir —un comprobante, por ejemplo— no van ni la barra ni el menú. */}
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1, displayPrint: 'none' }}>
        <Toolbar>
          {!ancho && (
            <IconButton color="inherit" edge="start" aria-label="Abrir el menú" onClick={() => setAbierto(true)} sx={{ mr: 1 }}>
              <MenuIcon />
            </IconButton>
          )}
          <Box sx={{ flexGrow: 1, minWidth: 0, display: 'flex', alignItems: 'baseline', gap: 1 }}>
            <Typography variant="h6" component="div" sx={{ fontWeight: 700 }}>
              {instancia}
            </Typography>
            {/* En el teléfono no entra el bloque de usuario: la entidad va acá. */}
            {entidad && (
              <Typography
                variant="body2"
                component="div"
                sx={{ display: { xs: 'block', sm: 'none' }, color: 'nav.accent', fontWeight: 500 }}
              >
                {entidad}
              </Typography>
            )}
          </Box>
          <Box sx={{ textAlign: 'right', mr: 1, display: { xs: 'none', sm: 'block' } }}>
            <Typography variant="body2" sx={{ lineHeight: 1.2 }}>{usuario}</Typography>
            <Typography variant="caption" sx={{ color: 'nav.textMuted' }}>
              {rol}
              {entidad && (
                <Box component="span" sx={{ color: 'nav.accent', fontWeight: 500 }}>
                  {' '}
                  · {entidad}
                </Box>
              )}
            </Typography>
          </Box>
          <Tooltip title={modo === 'light' ? 'Modo oscuro' : 'Modo claro'}>
            <IconButton color="inherit" onClick={alternar} aria-label="Cambiar el modo de color">
              {modo === 'light' ? <DarkModeOutlined /> : <LightModeOutlined />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Salir">
            <IconButton color="inherit" href={salir} aria-label="Salir">
              <LogoutOutlined />
            </IconButton>
          </Tooltip>
        </Toolbar>
        {aviso && (
          // Etiqueta de seguridad: que nadie confunda esto con un sistema con
          // datos reales, ni en persona ni en una captura que circule.
          <Box
            role="note"
            sx={{ bgcolor: atencion.surface, color: atencion.text, px: 2, py: 0.5, fontSize: 13, fontWeight: 500, textAlign: 'center' }}
          >
            {aviso}
          </Box>
        )}
      </AppBar>

      <Drawer
        variant={ancho ? 'permanent' : 'temporary'}
        open={ancho || abierto}
        onClose={() => setAbierto(false)}
        sx={{ width: ANCHO, flexShrink: 0, displayPrint: 'none', '& .MuiDrawer-paper': { width: ANCHO, boxSizing: 'border-box' } }}
      >
        <Toolbar />
        {aviso && <Box sx={{ height: 28 }} />}
        {lista}
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, minWidth: 0, p: { xs: 2, md: 3 } }}>
        <Toolbar sx={{ displayPrint: 'none' }} />
        {aviso && <Box sx={{ height: 28, displayPrint: 'none' }} />}
        {children}
      </Box>
    </Box>
  );
}
