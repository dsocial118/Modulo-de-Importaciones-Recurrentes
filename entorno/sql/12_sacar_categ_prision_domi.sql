-- ===========================================================================
-- Capa 1 — «categ prision domi» no es una hoja de datos
--
-- La hoja EXISTE en el insumo de la DNPYPI («Base dispositivos PENAL modelo
-- 20260827 desproteg.xlsx», hoja 12 de 12). No se inventó. Lo que está mal es
-- cómo se la clasificó: su contenido completo son tres filas, y lo que
-- documenta es qué tipo admite cada columna y qué valores toma la última.
--
--   fila 1   Nombre del dispositvo | Dependencia institucional | El equipo…
--   fila 2   texto                 | texto                     | Sí
--   fila 3   —                     | —                         | No
--
-- Es una hoja de CATEGORÍAS, igual que «categorias CRC» o «Categorias CRSC».
--
-- Por qué se coló: una hoja se clasifica como «listas» cuando alguna
-- validación de otra hoja la apunta. Las otras cinco hojas de categorías están
-- apuntadas por una validación; ésta no. Al no estarlo, cayó en «datos» por
-- descarte. Es el mismo defecto que `Prov_Dto_Localidad` en el legajo, y
-- `clasificar_hoja()` sigue necesitando una señal mejor que «nadie me apunta,
-- entonces soy datos» — eso NO se arregla acá.
--
-- Consecuencias que esto saca de encima: la plantilla dejaba de pedirle a la
-- provincia una hoja que no tiene que completar, el importador dejaba de
-- exigirla, y los números vuelven a los que corresponde decir:
--
--   DISP_PENAL   6 hojas / 121 campos   ->   5 hojas / 118 campos
--   el período      368 campos          ->      365 campos
--
-- ---------------------------------------------------------------------------
-- POR QUÉ SE CORRIGE LA v1 Y NO SE ABRE UNA v2
--
-- La regla es que una versión en uso no se regenera, porque sus campos están
-- referenciados por los hallazgos ya registrados. Al correr este guion la base
-- de Capa 2 está VACÍA: cero importaciones, cero hallazgos, cero
-- observaciones. No hay nada que referencie los tres campos de esta hoja, así
-- que la razón de la regla no se aplica.
--
-- Las tres comprobaciones de abajo lo verifican antes de borrar nada. Si
-- alguna encuentra una referencia, ningún DELETE borra nada y la definición
-- queda intacta.
-- ===========================================================================

SET NAMES utf8mb4;

-- 1. Comprobaciones. Con una sola referencia en Capa 2, no se borra nada.
SELECT COUNT(*) INTO @usos_hallazgo
  FROM `mir_c2_reglas_incumplidas` r
  JOIN `mir_c1_campo` c ON c.id = r.campo_id
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
 WHERE h.`nombre_esperado` = 'categ prision domi';

SELECT COUNT(*) INTO @usos_historial
  FROM `mir_c2_historial_cambios` x
  JOIN `mir_c1_campo` c ON c.id = x.campo_id
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
 WHERE h.`nombre_esperado` = 'categ prision domi';

SELECT COUNT(*) INTO @usos_observacion
  FROM `mir_c2_observacion` o
  JOIN `mir_c1_campo` c ON c.id = o.campo_id
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
 WHERE h.`nombre_esperado` = 'categ prision domi';

SET @se_puede = (@usos_hallazgo + @usos_historial + @usos_observacion = 0);
SELECT IF(@se_puede, 'sin referencias en Capa 2: se puede sacar',
                     'HAY REFERENCIAS: los DELETE de abajo no van a borrar nada') AS control;

-- Cada borrado lleva la condición: si hubiera una sola referencia en Capa 2,
-- no se borra NADA y la definición queda como estaba. Es preferible a un
-- guion que aborta a la mitad y deja la hoja sin campos.

-- 2. Las reglas colgadas de sus campos (hoy son cero, pero el guion no lo asume).
DELETE cr FROM `mir_c1_campo_regla` cr
  JOIN `mir_c1_campo` c ON c.id = cr.campo_id
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id
  JOIN `mir_c1_archivo` a ON a.id = av.archivo_id
 WHERE a.`codigo` = 'DISP_PENAL' AND h.`nombre_esperado` = 'categ prision domi'
   AND @se_puede;

-- 3. Los campos.
DELETE c FROM `mir_c1_campo` c
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id
  JOIN `mir_c1_archivo` a ON a.id = av.archivo_id
 WHERE a.`codigo` = 'DISP_PENAL' AND h.`nombre_esperado` = 'categ prision domi'
   AND @se_puede;

-- 4. Los grupos de campos de la hoja, si los hubiera.
DELETE d FROM `mir_c1_dimension` d
  JOIN `mir_c1_hoja` h ON h.id = d.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id
  JOIN `mir_c1_archivo` a ON a.id = av.archivo_id
 WHERE a.`codigo` = 'DISP_PENAL' AND h.`nombre_esperado` = 'categ prision domi'
   AND @se_puede;

-- 5. La hoja.
DELETE h FROM `mir_c1_hoja` h
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id
  JOIN `mir_c1_archivo` a ON a.id = av.archivo_id
 WHERE a.`codigo` = 'DISP_PENAL' AND h.`nombre_esperado` = 'categ prision domi'
   AND @se_puede;

-- 6. La tabla receptora. Se nombra a mano porque el nombre se deduce por
--    convención y no se puede reconstruir en SQL, igual que en los guiones 06
--    y 11. `sincronizar_receptoras.py` confirma después que no quedó ninguna
--    tabla sin su hoja.
DROP TABLE IF EXISTS `mir_c2_disp_penal_v1_categprision`;

-- 7. Cómo quedó.
SELECT h.`nombre_esperado` AS hoja, h.`orden_procesamiento` AS orden,
       (SELECT COUNT(*) FROM `mir_c1_campo` c WHERE c.hoja_id = h.id) AS campos
  FROM `mir_c1_hoja` h
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `mir_c1_archivo` a ON a.id = av.archivo_id
 WHERE a.`codigo` = 'DISP_PENAL'
 ORDER BY h.`orden_procesamiento`;
