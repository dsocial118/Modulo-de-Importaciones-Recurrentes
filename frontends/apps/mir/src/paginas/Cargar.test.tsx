import { act, fireEvent, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { envio, mostrar, resuelta } from '../pruebas';
import { Cargar } from './Cargar';

const api = vi.hoisted(() => ({ useCarga: vi.fn(), useCargarArchivo: vi.fn() }));
vi.mock('@mir/api', () => ({ ...api, mensajeDeError: () => 'error' }));

const PERIODO = { codigo: '2026_T1', estado: 'ABIERTO', fecha_desde: '2026-01-01', fecha_hasta: '2026-03-31' };

function archivo(codigo: string, extra = {}) {
  return {
    codigo,
    nombre: `Archivo ${codigo}`,
    obligatorio: true,
    estado: 'SIN_CARGAR',
    importada: false,
    filas: null,
    necesita: [],
    bloqueado_por: [],
    nombre_sugerido: `${codigo}_2026_T1_Chubut.xlsx`,
    ...extra,
  };
}

function carga(archivos: ReturnType<typeof archivo>[], extra = {}) {
  return {
    periodos: [PERIODO],
    periodo: PERIODO,
    jurisdiccion: 'Chubut',
    jurisdicciones: [],
    estado_legible: 'En carga',
    carga_abierta: true,
    puede_cargar: true,
    listo: false,
    archivos,
    ...extra,
  };
}

describe('Cargar', () => {
  beforeEach(() => {
    api.useCargarArchivo.mockReturnValue(envio());
  });

  it('dice en qué jurisdicción se carga', () => {
    api.useCarga.mockReturnValue(resuelta(carga([archivo('MPI')])));
    mostrar(<Cargar />);
    expect(screen.getByRole('heading', { name: /Chubut/ })).toBeInTheDocument();
  });

  it('un archivo que depende de otro sin importar no se puede subir, y se dice por qué', () => {
    api.useCarga.mockReturnValue(
      resuelta(carga([archivo('MPE', { necesita: ['LEGAJO_NYA'], bloqueado_por: ['LEGAJO_NYA'] })])),
    );
    mostrar(<Cargar />);
    expect(screen.getByText(/Primero hay que importar/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Seleccionar archivo' })).not.toBeInTheDocument();
  });

  it('«Importar» aparece recién después de elegir el archivo', () => {
    api.useCarga.mockReturnValue(resuelta(carga([archivo('MPI')])));
    const { container } = mostrar(<Cargar />);
    expect(screen.queryByRole('button', { name: /Importar/ })).not.toBeInTheDocument();
    const campo = container.querySelector('input[type=file]')!;
    fireEvent.change(campo, { target: { files: [new File(['x'], 'MPI_2026_T1_Chubut.xlsx')] } });
    expect(screen.getByRole('button', { name: /Importar/ })).toBeInTheDocument();
  });

  it('un archivo ya importado se reemplaza, no se importa de nuevo', () => {
    api.useCarga.mockReturnValue(resuelta(carga([archivo('MPI', { estado: 'VALIDA', importada: true, filas: 30 })])));
    const { container } = mostrar(<Cargar />);
    fireEvent.change(container.querySelector('input[type=file]')!, {
      target: { files: [new File(['x'], 'MPI_2026_T1_Chubut.xlsx')] },
    });
    expect(screen.getByRole('button', { name: /Reemplazar/ })).toBeInTheDocument();
  });

  it('mientras importa, la fila dice en qué va y no se puede importar otro', async () => {
    // Antes el botón desaparecía al apretarlo y la fila quedaba como si nada.
    let avanzar: (n: number) => void = () => {};
    api.useCargarArchivo.mockReturnValue({
      ...envio(),
      mutateAsync: (d: { alAvanzar: (n: number) => void }) => {
        avanzar = d.alAvanzar;
        return new Promise(() => {}); // no termina: se mira el durante
      },
    });
    api.useCarga.mockReturnValue(resuelta(carga([archivo('MPI'), archivo('MPE')])));
    const { container } = mostrar(<Cargar />);
    fireEvent.change(container.querySelector('input[type=file]')!, {
      target: { files: [new File(['x'], 'MPI_2026_T1_Chubut.xlsx')] },
    });
    fireEvent.click(screen.getByRole('button', { name: /Importar/ }));

    await act(async () => avanzar(40));
    expect(screen.getByText('Subiendo el archivo… 40 %')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Seleccionar archivo' })).toBeDisabled();

    await act(async () => avanzar(100));
    expect(screen.getByText('Revisando el archivo…')).toBeInTheDocument();
  });

  it('con la carga cerrada no se ofrece subir nada', () => {
    api.useCarga.mockReturnValue(
      resuelta(carga([archivo('MPI')], { carga_abierta: false, estado_legible: 'Carga cerrada' })),
    );
    mostrar(<Cargar />);
    expect(screen.getByText(/reabrir la carga/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Seleccionar archivo' })).not.toBeInTheDocument();
  });
});
