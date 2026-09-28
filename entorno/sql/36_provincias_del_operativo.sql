-- 36 · Las provincias del operativo.
--
-- El «Estado de situación» del nivel nacional muestra sólo las jurisdicciones
-- que tienen que presentar, no las 24 (pedido del responsable funcional,
-- 27-09-2026: «hoy en día son 10»). Se marcan con `mir_c2_jurisdiccion.activa`,
-- que ya existía, y el administrador las cambia desde Administración.
--
-- ESTAS DIEZ SON DE EJEMPLO, elegidas sin ningún criterio: hay que
-- reemplazarlas por las del operativo real. Chubut y Chaco van porque son las
-- que tienen usuarios de prueba.

INSERT INTO mir_c2_jurisdiccion (codigo, nombre, modalidad, activa)
SELECT nuevas.codigo, nuevas.nombre, 'PRESENTACION_PERIODICA', 1 FROM (
    SELECT 'CHUBUT' AS codigo, 'Chubut' AS nombre
    UNION ALL SELECT 'CHACO', 'Chaco'
    UNION ALL SELECT 'MENDOZA', 'Mendoza'
    UNION ALL SELECT 'CÓRDOBA', 'Córdoba'
    UNION ALL SELECT 'SALTA', 'Salta'
    UNION ALL SELECT 'NEUQUÉN', 'Neuquén'
    UNION ALL SELECT 'ENTRE RÍOS', 'Entre Ríos'
    UNION ALL SELECT 'CORRIENTES', 'Corrientes'
    UNION ALL SELECT 'SAN JUAN', 'San Juan'
    UNION ALL SELECT 'TUCUMÁN', 'Tucumán'
) nuevas
WHERE NOT EXISTS (SELECT 1 FROM mir_c2_jurisdiccion j WHERE j.nombre = nuevas.nombre);

UPDATE mir_c2_jurisdiccion
   SET activa = nombre IN ('Chubut', 'Chaco', 'Mendoza', 'Córdoba', 'Salta',
                           'Neuquén', 'Entre Ríos', 'Corrientes', 'San Juan', 'Tucumán');
