import ChecklistOutlined from '@mui/icons-material/ChecklistOutlined';
import DownloadOutlined from '@mui/icons-material/DownloadOutlined';
import FactCheckOutlined from '@mui/icons-material/FactCheckOutlined';
import HomeOutlined from '@mui/icons-material/HomeOutlined';
import ManageSearchOutlined from '@mui/icons-material/ManageSearchOutlined';
import UploadFileOutlined from '@mui/icons-material/UploadFileOutlined';
import type { ReactNode } from 'react';

/** El ícono de cada sección: el mismo en el menú y en los accesos de Inicio. */
export const ICONOS: Record<string, ReactNode> = {
  inicio: <HomeOutlined />,
  plantillas: <DownloadOutlined />,
  cargar: <UploadFileOutlined />,
  resultado: <FactCheckOutlined />,
  revision: <ManageSearchOutlined />,
  estructura: <ChecklistOutlined />,
};
