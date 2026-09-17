-- ===========================================================================
-- Capa 1 — «Modalidad de cuidado» apuntaba a la lista equivocada
--
-- La columna del MPE tiene TRES listas desplegables superpuestas en la planilla
-- —sobrantes de una versión anterior del archivo— y el extractor se quedó con
-- la que estaba primero. Resultado:
--
--   MPE v1  ->  lista «Provincia»              (24 provincias)
--   MPE v2  ->  lista «Trim1..Trim4»           (trimestres)
--
-- Ninguna de las dos tiene que ver con la modalidad de cuidado. La lista
-- correcta ya estaba cargada, con sus cuatro valores:
--
--   Alojamiento formal · Familia ampliada · Familia de acogimiento · Otro
--
-- Esto cierra el pendiente #22 de la bitácora, abierto el 2026-09-09: se había
-- corregido el Excel de revisión que va a la DNPYPI, pero la definición en la
-- base seguía mal.
--
-- No es una decisión funcional nuestra: es corregir a qué lista apunta el
-- campo, con la lista que la propia planilla trae.
-- ===========================================================================

SET NAMES utf8mb4;

UPDATE `runac_c1_campo` c
  JOIN `runac_c1_catalogo` correcto ON correcto.`codigo` = 'modalidad_de_cuidado'
 SET c.`catalogo_id` = correcto.id
 WHERE c.`nombre` = 'modalidad_de_cuidado'
   AND c.`catalogo_id` <> correcto.id;
