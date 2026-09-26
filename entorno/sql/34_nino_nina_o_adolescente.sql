-- 34 · Siempre «niño, niña o adolescente», en ese orden y completo.
--
-- Pedido del responsable funcional el 26-09-2026: donde diga «Niño o
-- adolescente» —o cualquier otra forma— tiene que decir «Niño, niña o
-- adolescente»; en plural, «niños, niñas y adolescentes».
--
-- Nada de esto cambia qué archivos se aceptan:
--   · los grupos de columnas no se validan al importar;
--   · el título de la columna del ID sólo cambia mayúsculas, y el importador
--     compara los títulos sin mayúsculas ni tildes (`clave()` en
--     motor/comun.py): los archivos que dicen «ID del Niño, niña o
--     Adolescente» siguen entrando.
--
-- Los nombres oficiales no se tocan: la Ley 26.061 se llama «de Protección
-- Integral de los Derechos de las Niñas, Niños y Adolescentes».

UPDATE mir_c1_dimension SET nombre_esperado = 'Niño, niña o adolescente'
 WHERE nombre_esperado = 'Niño o adolescente';

UPDATE mir_c1_campo SET titulo_esperado = 'ID del niño, niña o adolescente'
 WHERE titulo_esperado = 'ID del Niño, niña o Adolescente';

UPDATE mir_c1_archivo SET descripcion = 'Legajo de niños, niñas y adolescentes'
 WHERE descripcion = 'Legajo de niñas, niños y adolescentes';

UPDATE mir_c1_archivo_version SET que_es_una_fila = 'Niño, niña o adolescente'
 WHERE que_es_una_fila = 'Niña, niño o adolescente';
