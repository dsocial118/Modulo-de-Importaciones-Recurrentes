-- 32 · Hojas de referencia: van ocultas en la plantilla y no se controlan.
--
-- Pendiente #87, decidido por el responsable funcional el 26-09-2026.
--
-- El problema. La planilla del legajo trae la hoja `Prov_Dto_Localidad`: el
-- nomenclador territorial que armó la DNPYPI. Desde el 13-09 el nomenclador se
-- ofrece por catálogos filtrados por jurisdicción y la hoja dejó de ser
-- obligatoria, pero seguía declarada como hoja de datos. Salía visible en la
-- plantilla —parecía que había que completarla— y el importador validaba sus
-- filas: una importación del legajo se rechazó por una fila vacía en esa hoja.
--
-- La solución. Una hoja de referencia es parte de la planilla, pero no trae
-- datos de la provincia. El generador de plantillas la oculta y el importador
-- no la lee. Queda declarada para poder abrir los archivos que la traen.
--
-- Los guiones 20 a 31 están en analisis_datos\ModeloMySql\sql\, fuera del
-- repositorio. Desde el 26-09-2026 los guiones nuevos van acá.

ALTER TABLE mir_c1_hoja
  ADD COLUMN referencia boolean NOT NULL DEFAULT false
  COMMENT 'Hoja de consulta: la plantilla la oculta y el importador no la valida.';

UPDATE mir_c1_hoja SET referencia = true WHERE nombre_esperado = 'Prov_Dto_Localidad';
