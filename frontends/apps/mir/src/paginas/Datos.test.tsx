import { fireEvent, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { envio, mostrar, resuelta } from '../pruebas';
import { Datos } from './Datos';

const api = vi.hoisted(() => ({
  useDatos: vi.fn(),
  useCorregir: vi.fn(),
  useObservarDato: vi.fn(),
  useResponder: vi.fn(),
  useReabrirObservacion: vi.fn(),
  useDesestimarObservacion: vi.fn(),
}));
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
      presentacion_id: 8,
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
        identificacion: '9 · Paz · Ana',
        estado: 'VALIDA',
        avisos: [{ nombre_campo: 'Edad', severidad: 'ADVERTENCIA', descripcion: 'Es mayor que 17.' }],
        celdas: [
          { nombre: 'fecha_de_nacimiento', titulo: 'Fecha de nacimiento', obligatorio: true, tipo_dato: 'FECHA', valor: '27/10/2014', opciones: [], tiene_aviso: false, campo_id: 1, observacion: null },
          { nombre: 'edad', titulo: 'Edad', obligatorio: false, tipo_dato: 'ENTERO', valor: '107', opciones: [], tiene_aviso: true, campo_id: 2, observacion: null },
        ],
      },
    ],
    historial: [],
    descarga_historial: '/api/mir/importaciones/11/historial.xlsx',
    puede_observar: false,
    puede_responder: true,
    observaciones: [] as unknown[],
    ...extra,
  };
}

const abrirLaFila = () => fireEvent.click(screen.getByText('9 · Paz · Ana · fila 12 del Excel'));

describe('Corregir datos', () => {
  beforeEach(() => {
    for (const hook of [api.useCorregir, api.useObservarDato, api.useResponder, api.useReabrirObservacion, api.useDesestimarObservacion])
      hook.mockReturnValue(envio());
  });

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

  it('cada fila y la confirmación dicen de quién es, no sólo el número', () => {
    // «Fila 5 del Excel» sola no le decía nada a quien corrige (#67).
    api.useDatos.mockReturnValue(resuelta(datos()));
    mostrar(<Datos />, { ruta: '/resultado/11/datos', patron: '/resultado/:id/datos' });
    abrirLaFila();
    const edad = screen.getByLabelText(/^Edad/);
    fireEvent.change(edad, { target: { value: '12' } });
    fireEvent.blur(edad);
    expect(screen.getByRole('dialog')).toHaveTextContent('9 · Paz · Ana · fila 12 del Excel');
  });

  it('el nivel nacional ve los datos pero no los cambia', () => {
    api.useDatos.mockReturnValue(resuelta(datos({ puede_editar: false })));
    mostrar(<Datos />, { ruta: '/resultado/11/datos', patron: '/resultado/:id/datos' });
    expect(screen.getByText(/no modifica datos provinciales/)).toBeInTheDocument();
    abrirLaFila();
    expect(screen.getByLabelText(/^Edad/)).toHaveAttribute('readonly');
  });

  const observacion = (extra = {}) => ({
    id: 7,
    estado: 'ABIERTA',
    texto: 'La edad no coincide con la fecha de nacimiento.',
    usuario_observa: 'revisor',
    creada_el: '2026-09-27T10:00:00',
    archivo_codigo: 'MPI',
    numero_fila: 12,
    importacion_id: 11,
    hoja: 'MPI',
    campo: 'edad',
    campo_titulo: 'Edad',
    identificador_registro: '9 · Paz · Ana',
    respuesta: null,
    usuario_responde: null,
    respondida_el: null,
    ...extra,
  });

  const conObservacion = (extra = {}) => {
    const base = datos(extra);
    const o = observacion();
    base.observaciones = [o];
    (base.filas[0].celdas[1] as { observacion: unknown }).observacion = o;
    return base;
  };

  it('la provincia ve las observaciones sin resolver arriba y puede responder que está bien así', () => {
    api.useDatos.mockReturnValue(resuelta(conObservacion()));
    mostrar(<Datos />, { ruta: '/resultado/11/datos', patron: '/resultado/:id/datos' });
    expect(screen.getByText('Observaciones sin resolver: 1')).toBeInTheDocument();
    expect(screen.getByText('MPI · 9 · Paz · Ana · Edad')).toBeInTheDocument();
    // La fila observada arranca abierta y lo dice en su título.
    expect(screen.getByText('1 observación')).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: 'Está bien así' }).length).toBeGreaterThan(0);
    expect(screen.queryByRole('button', { name: 'Observar' })).not.toBeInTheDocument();
  });

  it('el revisor observa un dato, y no ve cómo corregirlo', () => {
    api.useDatos.mockReturnValue(resuelta(datos({ puede_editar: false, puede_observar: true, puede_responder: false })));
    mostrar(<Datos />, { ruta: '/resultado/11/datos', patron: '/resultado/:id/datos' });
    abrirLaFila();
    expect(screen.getAllByRole('button', { name: 'Observar' })).toHaveLength(2);
    expect(screen.getByLabelText(/^Edad/)).toHaveAttribute('readonly');
    fireEvent.click(screen.getAllByRole('button', { name: 'Observar' })[1]);
    expect(screen.getByLabelText('Qué hay que revisar en este dato')).toBeInTheDocument();
  });

  it('en grilla, los datos van en una tabla y se corrigen con doble clic, con la misma confirmación', () => {
    api.useDatos.mockReturnValue(resuelta(datos()));
    mostrar(<Datos />, { ruta: '/resultado/11/datos?vista=grilla', patron: '/resultado/:id/datos' });
    expect(screen.getByRole('columnheader', { name: /Fecha de nacimiento/ })).toBeInTheDocument();
    expect(screen.getByRole('rowheader', { name: /9 · Paz · Ana/ })).toBeInTheDocument();
    fireEvent.doubleClick(screen.getByText('107'));
    const edad = screen.getByLabelText('Edad');
    fireEvent.change(edad, { target: { value: '12' } });
    fireEvent.keyDown(edad, { key: 'Enter' });
    expect(screen.getByText('Confirmar el cambio')).toBeInTheDocument();
  });

  it('en grilla, quien no corrige elige el dato pero no lo edita', () => {
    api.useDatos.mockReturnValue(resuelta(datos({ puede_editar: false, puede_observar: true, puede_responder: false })));
    mostrar(<Datos />, { ruta: '/resultado/11/datos?vista=grilla', patron: '/resultado/:id/datos' });
    fireEvent.click(screen.getByText('107'));
    // Después del clic el valor aparece dos veces: en la grilla y en el dato elegido.
    fireEvent.doubleClick(screen.getAllByText('107')[0]);
    expect(screen.queryByLabelText('Edad')).not.toBeInTheDocument();
    expect(screen.getByText('Dato elegido')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Observar' })).toBeInTheDocument();
  });
});
