-- ===========================================================================
-- Las tablas pasan de `runac_` a `mir_`
--
-- POR QUÉ
--
-- El prefijo era lo ÚLTIMO que ataba el motor a RUNAC. Se midió antes de
-- tocarlo: de las 158 menciones a «runac» en `services/motor/`, todas son
-- nombres de tabla o comentarios. Se buscó lógica de negocio —MPI, MPE,
-- dispositivos, niño, medida de protección— y lo único que aparece es un
-- ejemplo dentro de un comentario. **El motor no sabe qué es un MPI**, y eso
-- ahora es verificable, no una afirmación.
--
-- Cada implementación tiene su propia base. En una base llamada `runac`, unas
-- tablas llamadas `runac_c1_campo` son redundantes; en una base de otro
-- programa serían mentira. El prefijo que corresponde es el del módulo.
--
--   runac_c1_*  ->  mir_c1_*     la definición
--   runac_c2_*  ->  mir_c2_*     el control y las tablas que reciben
--   runac_c3_*  ->  mir_c3_*     la base consolidada
--
-- SE HACE EN LAS DOS BASES
--
-- `runac` y `runac_v2` comparten el mismo código. Si se renombra en una sola,
-- la otra deja de funcionar al instante. Este guion las toma a las dos.
--
-- ES UN RENOMBRE, NO UNA MIGRACIÓN
--
-- `RENAME TABLE` no copia datos ni toca las claves foráneas: MySQL las sigue
-- solo. Es reversible dando vuelta el SELECT que arma las sentencias.
--
-- Se corre con `--aplicar` desde `renombrar_prefijo.py`, que arma y ejecuta el
-- RENAME de cada tabla. Este archivo queda como registro de la decisión.
-- ===========================================================================

SET NAMES utf8mb4;

-- Lo que hay que renombrar, en las dos bases. El script lo lee de acá.
SELECT table_schema AS base, table_name AS tabla,
       CONCAT('mir_', SUBSTRING(table_name, 7)) AS nuevo
  FROM information_schema.tables
 WHERE table_schema IN ('runac', 'runac_v2')
   AND table_name LIKE 'runac\_%'
 ORDER BY table_schema, table_name;

-- ---------------------------------------------------------------------------
-- LO QUE EL RENOMBRE NO TOCA, Y ESTÁ BIEN QUE NO TOQUE
--
-- `RENAME TABLE` cambia el nombre de la tabla y nada más. Quedan con el
-- prefijo viejo:
--
--   36 índices          runac_c1_campo_index_3, runac_c1_archivo_version_unica…
--   28 claves foráneas  runac_c1_campo_regla_fk_…
--
-- Son identificadores internos: no aparecen en ninguna consulta, ni en el
-- código, ni en las pantallas. Sólo se ven haciendo `SHOW CREATE TABLE`.
--
-- No se renombran a propósito. Renombrar 64 objetos más agrega riesgo sin
-- ninguna ganancia, y una clave foránea mal renombrada rompe la integridad
-- referencial de verdad, no el nombre. Si algún día molesta, se hace con
-- `ALTER TABLE … RENAME INDEX` y volviendo a crear las claves.
--
-- Queda escrito para que quien los vea sepa que es deliberado y no un
-- renombre a medio hacer.
-- ---------------------------------------------------------------------------
