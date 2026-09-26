import { fireEvent, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { envio, mostrar, resuelta } from '../pruebas';
import { Datos } from './Datos';

const api = vi.hoisted(() => ({ useDatos: vi.fn(), useCorregir: vi.fn() }));
vi.mock('@mir/api', () => ({ ...api, mensajeDeError: () => 'error' }));

function datos(extra = {}) {
  return {
    contexto: {
      id: 11,
      archivo_codigo: 'MPI',
      jurisdiccion: 'Chubut',
      periodo: '2026_T1',
      version: 1,
      estado_presentacion: 'EN_CARGA',
      estado_legible: 'En carga',
      editable: true,
    },
    hojas: [{ id: 1, nombre: 'MPI' }],
    hoja: { id: 1, nombre: 'MPI' },
    puede_editar: true,
    total: 1,
    pagina: 1,
    paginas: 1,
    con_advertencia: 1,
    filas: [
      {
        numero_fila: 12,
        estado: 'VALIDA',
        avisos: [{ nombre_campo: 'Edad', severidad: 'ADVERTENCIA', descripcion: 'Es mayor que 17.' }],
        celdas: [
          { nombre: 'fecha_de_nacimiento', titulo: 'Fecha de nacimiento', obligatorio: true, tipo_dato: 'FECHA', valor: '27/10/2014', opciones: [], tiene_aviso: false },
          { nombre: 'edad', titulo: 'Edad', obligatorio: false, tipo_dato: 'ENTERO', valor: '107', opciones: [], tiene_aviso: true },
        ],
      },
    ],
    historial: [],
    ...extra,
  };
}

const abrirLaFila = () => fireEvent.click(screen.getByText('Fila 12 del Excel'));

describe('Corregir datos', () => {
  beforeEach(() => api.useCorregir.mockReturnValue(envio()));

  it('la fecha se ve tal como viene, no vacía', () => {
    // El campo de fecha del navegador sólo entiende 2014-10-27: mostraba vacío
    // un 27/10/2014, y pasar por el campo podía guardarlo vacío.
    api.useDatos.mockReturnValue(resuelta(datos()));
    mostrar(<Datos />, { ruta: '/resultado/11/datos', patron: '/resultado/:id/datos' });
    abrirLaFila();
    expect(screen.getByLabelText(/Fecha de nacimiento/)).toHaveValue('27/10/2014');
  });

  it('cambiar un dato pide confirmación antes de guardarlo', () => {
    api.useDatos.mockReturnValue(resuelta(datos()));
    mostrar(<Datos />, { ruta: '/resultado/11/datos', patron: '/resultado/:id/datos' });
    abrirLaFila();
    const edad = screen.getByLabelText(/^Edad/);
    fireEvent.change(edad, { target: { value: '12' } });
    fireEvent.blur(edad);
    expect(screen.getByText('Confirmar el cambio')).toBeInTheDocument();
    expect(screen.getByText(/de «107» a «12»/)).toBeInTheDocument();
  });

  it('el nivel nacional ve los datos pero no los cambia', () => {
    api.useDatos.mockReturnValue(resuelta(datos({ puede_editar: false })));
    mostrar(<Datos />, { ruta: '/resultado/11/datos', patron: '/resultado/:id/datos' });
    expect(screen.getByText(/no modifica datos provinciales/)).toBeInTheDocument();
    abrirLaFila();
    expect(screen.getByLabelText(/^Edad/)).toHaveAttribute('readonly');
  });
});
