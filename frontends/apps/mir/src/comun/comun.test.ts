import { describe, expect, it } from 'vitest';
import { ESTADO_DEL_ARCHIVO, formaDe, tonoDeLaPresentacion } from './estados';
import { fecha, numero, plural } from './formato';
import { conFiltros } from './filtros';

describe('formato', () => {
  it('una fecha sola no se corre un día por el huso horario', () => {
    // A medianoche UTC, en Buenos Aires es todavía el día anterior.
    expect(fecha('2026-03-31')).toBe('31/3/2026');
  });

  it('una fecha que no está se dice con una raya', () => {
    expect(fecha(null)).toBe('—');
  });

  it('los números llevan separador de miles, como se leen acá', () => {
    expect(numero(12345)).toBe('12.345');
  });

  it('el plural concuerda con la cantidad', () => {
    expect(plural(1, 'advertencia', 'advertencias')).toBe('1 advertencia');
    expect(plural(3, 'advertencia', 'advertencias')).toBe('3 advertencias');
  });
});

describe('estados', () => {
  it('un archivo importado no se pinta de verde: el verde es de marca', () => {
    expect(ESTADO_DEL_ARCHIVO.VALIDA.tono).toBe('info');
  });

  it('un estado desconocido se muestra tal cual, sin romper la pantalla', () => {
    expect(formaDe(ESTADO_DEL_ARCHIVO, 'OTRO')).toEqual({ texto: 'OTRO', tono: 'pending' });
  });

  it('lo que espera respuesta de la jurisdicción va en atención', () => {
    expect(tonoDeLaPresentacion('OBSERVADA')).toBe('attention');
    expect(tonoDeLaPresentacion('HABILITADA')).toBe('info');
  });
});

describe('enlaces', () => {
  it('el período y la jurisdicción viajan de una sección a otra', () => {
    expect(conFiltros('/cargar', '2026_T1', 'Chubut')).toBe('/cargar?periodo=2026_T1&jurisdiccion=Chubut');
  });

  it('sin filtros, el enlace queda limpio', () => {
    expect(conFiltros('/cargar')).toBe('/cargar');
  });
});
