import { screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { mostrar, resuelta } from '../pruebas';
import { FranjaDelCircuito } from './Franja';

const api = vi.hoisted(() => ({ useFranja: vi.fn() }));
vi.mock('@mir/api', () => api);

const pasos = ['Carga', 'Revisión nacional', 'Subsanación', 'Presentación', 'Consolidación'];

function franja(extra = {}) {
  return {
    jurisdiccion: 'Chubut',
    periodo: '2026_T1',
    estado: 'OBSERVADA',
    estado_legible: 'Observada',
    que_pasa: 'Tiene observaciones y volvió a la jurisdicción.',
    pasos: pasos.map((nombre, i) => ({ nombre, actual: i === 2, hecho: i < 2 })),
    te_toca: ['Cerrar la carga'],
    archivos_importados: 6,
    archivos_esperados: 6,
    observaciones_abiertas: 2,
    ...extra,
  };
}

describe('Franja del avance del circuito', () => {
  it('marca el paso actual y dice qué falta', () => {
    api.useFranja.mockReturnValue(resuelta(franja()));
    mostrar(<FranjaDelCircuito />);
    expect(screen.getByRole('navigation', { name: 'Avance del circuito' })).toBeInTheDocument();
    expect(screen.getByText('Subsanación').closest('li')).toHaveAttribute('aria-current', 'step');
    expect(screen.getByText('2 observaciones sin resolver')).toBeInTheDocument();
    expect(screen.getByText('6 archivos observados')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'cerrar la carga' })).toBeInTheDocument();
  });

  it('en la carga cuenta los importados; después dice en qué están', () => {
    api.useFranja.mockReturnValue(resuelta(franja({ estado: 'EN_CARGA', archivos_importados: 5 })));
    mostrar(<FranjaDelCircuito />);
    expect(screen.getByText('5 de 6 archivos importados')).toBeInTheDocument();
  });

  it('esperando revisión, los archivos están en revisión', () => {
    api.useFranja.mockReturnValue(resuelta(franja({ estado: 'CERRADA' })));
    mostrar(<FranjaDelCircuito />);
    expect(screen.getByText('6 archivos en revisión')).toBeInTheDocument();
  });

  it('sin jurisdicción elegida no se muestra', () => {
    api.useFranja.mockReturnValue(resuelta(franja({ estado: null, pasos: [] })));
    mostrar(<FranjaDelCircuito />);
    expect(screen.queryByRole('navigation', { name: 'Avance del circuito' })).not.toBeInTheDocument();
  });
});
