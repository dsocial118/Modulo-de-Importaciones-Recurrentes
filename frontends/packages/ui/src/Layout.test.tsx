import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AppRoot } from './AppRoot';
import { Layout, type ItemDeMenu } from './Layout';

const MENU: ItemDeMenu[] = [
  { clave: 'inicio', etiqueta: 'Inicio', href: '/v2/mir/', ruta: '/', icono: null, enV2: true },
  { clave: 'cargar', etiqueta: 'Cargar archivos', href: '/v2/mir/cargar', ruta: '/cargar', icono: null, enV2: true },
  { clave: 'vieja', etiqueta: 'Sección vieja', href: '/vieja/', ruta: '/vieja/', icono: null, enV2: false },
];

function armar(props: Partial<Parameters<typeof Layout>[0]> = {}) {
  const alNavegar = vi.fn();
  render(
    <AppRoot>
      <Layout
        instancia="RUNAC"
        usuario="operador"
        rol="Operador provincial"
        entidad="Chubut"
        aviso="datos de prueba"
        menu={MENU}
        activa="inicio"
        salir="/salir/"
        alNavegar={alNavegar}
        {...props}
      >
        <p>contenido</p>
      </Layout>
    </AppRoot>,
  );
  return { alNavegar };
}

describe('Layout', () => {
  it('dice sobre qué jurisdicción se trabaja', () => {
    armar();
    // Desde que el usuario provincial no elige, es el único lugar que lo dice.
    expect(screen.getAllByText(/Chubut/).length).toBeGreaterThan(0);
  });

  it('muestra siempre el aviso de datos de prueba', () => {
    armar();
    expect(screen.getByRole('note')).toHaveTextContent('datos de prueba');
  });

  it('marca la sección activa', () => {
    armar({ activa: 'cargar' });
    expect(screen.getByRole('link', { name: /Cargar archivos/ })).toHaveClass('Mui-selected');
  });

  it('dentro de /v2/ navega sin recargar la página', () => {
    const { alNavegar } = armar();
    fireEvent.click(screen.getByRole('link', { name: /Cargar archivos/ }));
    expect(alNavegar).toHaveBeenCalledWith('/cargar');
  });

  it('una sección que sigue en la versión actual lleva allá', () => {
    const { alNavegar } = armar();
    const enlace = screen.getByRole('link', { name: /Sección vieja/ });
    expect(enlace).toHaveAttribute('href', '/vieja/');
    fireEvent.click(enlace);
    expect(alNavegar).not.toHaveBeenCalled();
  });
});
