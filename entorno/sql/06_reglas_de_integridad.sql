-- ===========================================================================
-- Capa 1 — Reglas de integridad entre campos y entre archivos
--
-- Se aplica DESPUÉS de generar la Capa 1 desde las planillas. Lo que agrega no
-- se puede inferir del título de una columna: son las reglas que dicen cuándo
-- un dato contradice a otro, y son decisiones funcionales.
--
-- Dos tipos de regla nuevos:
--
--   PROHIBIDO_SI       el reverso de OBLIGATORIO_SI: el campo tiene que quedar
--                      VACÍO cuando otro campo cumple una condición.
--   EXISTE_EN_ARCHIVO  el valor tiene que existir en otro archivo ya importado
--                      del mismo período. Es la razón por la que hay un orden
--                      de importación, y de acá lee el sistema qué archivo
--                      necesita a cuál: la dependencia es la referencia, no el
--                      orden.
--
-- El guion se puede correr más de una vez sin duplicar nada.
--
-- PENDIENTE DE CONFIRMAR CON LA DNPYPI: las tres decisiones funcionales están
-- señaladas más abajo con «A CONFIRMAR».
-- ===========================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- 1. Los dos tipos de regla y sus parámetros
-- ---------------------------------------------------------------------------

INSERT INTO `runac_c1_tipo_regla` (`nombre`, `descripcion`) VALUES
  ('PROHIBIDO_SI',
   'Determina que un campo deba quedar vacío cuando otro campo cumple una condición.'),
  ('EXISTE_EN_ARCHIVO',
   'Verifica que el valor exista en otro archivo ya importado del mismo período.')
ON DUPLICATE KEY UPDATE `descripcion` = VALUES(`descripcion`);

INSERT INTO `runac_c1_tipo_regla_parametro`
  (`tipo_regla_id`, `nombre`, `tipo_parametro`, `obligatorio`, `orden`, `descripcion`)
SELECT t.id, p.nombre, p.tipo_parametro, p.obligatorio, p.orden, p.descripcion
  FROM `runac_c1_tipo_regla` t
  JOIN (
    SELECT 'PROHIBIDO_SI' AS tipo, 'campo_condicion' AS nombre, 'CAMPO' AS tipo_parametro,
           1 AS obligatorio, 1 AS orden,
           'Campo cuyo valor prohíbe completar este.' AS descripcion
    UNION ALL SELECT 'PROHIBIDO_SI', 'operador', 'TEXTO', 1, 2,
           'IGUAL, DISTINTO, ES_VACIO, NO_ES_VACIO, EN_LISTA o NO_EN_LISTA.'
    UNION ALL SELECT 'PROHIBIDO_SI', 'valor_condicion', 'TEXTO', 0, 3,
           'Valor de la condición, cuando el operador lo requiere.'
    UNION ALL SELECT 'EXISTE_EN_ARCHIVO', 'archivo', 'TEXTO', 1, 1,
           'Código del archivo referenciado.'
    UNION ALL SELECT 'EXISTE_EN_ARCHIVO', 'hoja', 'TEXTO', 0, 2,
           'Hoja del archivo referenciado; se puede omitir si tiene una sola.'
    UNION ALL SELECT 'EXISTE_EN_ARCHIVO', 'campo', 'CAMPO', 1, 3,
           'Campo del archivo referenciado donde tiene que existir el valor.'
  ) p ON p.tipo = t.nombre
ON DUPLICATE KEY UPDATE `descripcion` = VALUES(`descripcion`);

-- ---------------------------------------------------------------------------
-- 2. Número de DNI y situación de documentación
--
-- La planilla admite declarar «No posee N° DNI» y traer igual un número. Son
-- dos afirmaciones que no pueden ser ciertas a la vez, y con las dos cargadas
-- no se sabe cuál de ellas es la verdadera.
--
-- Por eso el campo deja de ser obligatorio siempre: la propia planilla admite
-- que no haya número. Pasa a ser obligatorio cuando la situación dice que lo
-- hay, y prohibido cuando dice que no.
--
-- A CONFIRMAR con la DNPYPI, tres cosas:
--   a) qué opciones significan que NO hay número. Acá se toman «No posee N°
--      DNI», «Sin inscripción» y «DNI en trámite».
--   b) qué opciones significan que SÍ lo hay. Acá se toman «Posee N° DNI» y
--      «Perdida de documentación» —el documento se perdió, el número existe—.
--   c) «Posee N° doc. Extranjero» y «Sin datos» no obligan ni prohíben.
--
-- La severidad es BLOQUEANTE: se corrige en el Excel, que es donde se corrigen
-- los bloqueantes, y no dentro del sistema.
-- ---------------------------------------------------------------------------

INSERT INTO `runac_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT t.id, r.nombre, r.descripcion, r.parametros
  FROM `runac_c1_tipo_regla` t
  JOIN (
    SELECT 'PROHIBIDO_SI' AS tipo, CONCAT(a.cod, '_n_dni_prohibido_si') AS nombre,
           'El número de DNI no se completa cuando la situación de documentación declara que no hay número.' AS descripcion,
           JSON_OBJECT('campo_condicion', 'situacion_de_documentacion',
                       'operador', 'EN_LISTA',
                       'valor_condicion', JSON_ARRAY('No posee N° DNI', 'Sin inscripción', 'DNI en trámite')) AS parametros
      FROM (SELECT 'mpi' AS cod UNION ALL SELECT 'mpe'
            UNION ALL SELECT 'mpj' UNION ALL SELECT 'dae') a
    UNION ALL
    SELECT 'OBLIGATORIO_SI', CONCAT(a.cod, '_n_dni_obligatorio_si'),
           'El número de DNI es obligatorio cuando la situación de documentación declara que la persona lo tiene.',
           JSON_OBJECT('campo_condicion', 'situacion_de_documentacion',
                       'operador', 'EN_LISTA',
                       'valor_condicion', JSON_ARRAY('Posee N° DNI', 'Perdida de documentación'))
      FROM (SELECT 'mpi' AS cod UNION ALL SELECT 'mpe'
            UNION ALL SELECT 'mpj' UNION ALL SELECT 'dae') a
  ) r ON r.tipo = t.nombre
ON DUPLICATE KEY UPDATE `parametros` = VALUES(`parametros`);

-- El campo deja de ser obligatorio **sólo donde las reglas condicionales pueden
-- aplicarse**, es decir donde la hoja tiene «Situación de documentación».
--
-- El guion decía antes `WHERE c.nombre = 'n_dni'` a secas. Con el legajo del
-- niño eso habría dejado su Nº DNI simplemente opcional y sin ninguna regla: la
-- planilla del legajo no tiene «Situación de documentación» sino «Tipo de
-- documento de identidad», con opciones distintas («DNI», «Documento
-- extranjero», «Otro tipo de documentación», «Sin documentación»). Relajar la
-- obligatoriedad sin poner la regla que la reemplaza es debilitar el control en
-- silencio, que es peor que dejarlo como está.
--
-- A CONFIRMAR con la DNPYPI: si «Sin documentación» del legajo equivale a «No
-- posee N° DNI». Hasta que se confirme, el Nº DNI del legajo queda como lo
-- declara la planilla.
-- La condición va como JOIN y no como EXISTS: MySQL no deja consultar en una
-- subconsulta la misma tabla que se está actualizando.
UPDATE `runac_c1_campo` c
  JOIN `runac_c1_campo` c2
    ON c2.hoja_id = c.hoja_id AND c2.nombre = 'situacion_de_documentacion'
 SET c.`obligatorio` = 0
 WHERE c.`nombre` = 'n_dni';

-- Las dos reglas se enganchan al campo n_dni de cada nómina. La hoja se usa
-- para armar el nombre de la regla: MPJ y DAE viven en el mismo archivo.
INSERT INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`, `mensaje`)
SELECT c.id, r.id, 'BLOQUEANTE',
       CASE WHEN r.nombre LIKE '%_prohibido_si'
            THEN 'La situación de documentación dice que no hay número de DNI, y sin embargo el campo trae uno. Hay que corregir una de las dos cosas en el Excel.'
            ELSE 'La situación de documentación dice que la persona tiene número de DNI, y el campo está vacío.'
       END
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_regla` r
    ON r.nombre IN (CONCAT(LOWER(h.nombre_esperado), '_n_dni_prohibido_si'),
                    CONCAT(LOWER(h.nombre_esperado), '_n_dni_obligatorio_si'))
 WHERE c.`nombre` = 'n_dni'
   AND EXISTS (SELECT 1 FROM `runac_c1_campo` c2
                WHERE c2.hoja_id = c.hoja_id
                  AND c2.nombre = 'situacion_de_documentacion')
ON DUPLICATE KEY UPDATE `mensaje` = VALUES(`mensaje`);

-- ---------------------------------------------------------------------------
-- 3. El dispositivo que nombra la nómina penal tiene que existir
--
-- Es la referencia entre archivos, y la razón por la que los dispositivos se
-- importan antes que las nóminas.
--
-- La severidad es ADVERTENCIA y no BLOQUEANTE a propósito: el nombre puede
-- estar escrito distinto en las dos planillas —no hay un identificador—, y
-- eso se resuelve dentro del sistema, no rehaciendo el Excel.
--
-- A CONFIRMAR con la DNPYPI: si las nóminas de protección (MPI, MPE) tienen
-- que referenciar el archivo de dispositivos de cuidado (DISP_SCP). El campo
-- de MPI se llama «Nombre del programa/dispositivo», que puede ser un programa
-- y no un dispositivo declarado. Hasta que se confirme, no se declara.
-- ---------------------------------------------------------------------------

INSERT INTO `runac_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT t.id, CONCAT(a.cod, '_nombre_del_dispositivo_existe_en_archivo'),
       'El dispositivo nombrado en la nómina tiene que estar declarado en el archivo de dispositivos penales.',
       JSON_OBJECT('archivo', 'DISP_PENAL', 'campo', 'nombre_del_dispositvo')
  FROM `runac_c1_tipo_regla` t
  JOIN (SELECT 'mpj' AS cod UNION ALL SELECT 'dae') a
 WHERE t.`nombre` = 'EXISTE_EN_ARCHIVO'
ON DUPLICATE KEY UPDATE `parametros` = VALUES(`parametros`);

INSERT INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`, `mensaje`)
SELECT c.id, r.id, 'ADVERTENCIA',
       'El dispositivo no figura en el archivo de dispositivos penales de este período. Puede ser un nombre escrito distinto o un dispositivo que falta declarar.'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_regla` r
    ON r.nombre = CONCAT(LOWER(h.nombre_esperado), '_nombre_del_dispositivo_existe_en_archivo')
 WHERE c.`nombre` = 'nombre_del_dispositivo'
ON DUPLICATE KEY UPDATE `mensaje` = VALUES(`mensaje`);

-- ---------------------------------------------------------------------------
-- 4. Las tablas receptoras tienen que admitir lo que la Capa 1 admite
--
-- La columna se genera NOT NULL cuando el campo es obligatorio. Si después la
-- obligatoriedad pasa a ser condicional, la tabla queda más exigente que la
-- definición y la importación falla al insertar.
--
-- Esto nombraba las cuatro tablas a mano, con el número de versión escrito
-- (`runac_c2_mpe_v1`). Con una estructura v2 apuntaba a la tabla vieja y dejaba
-- la nueva sin corregir. Ahora no nombra ninguna: recorre las que existen y
-- relaja las que contradicen a la Capa 1, sea cual sea la versión.
--
-- Sólo AFLOJA restricciones —de NOT NULL a NULL—, nunca al revés: endurecer una
-- columna podría fallar sobre datos ya cargados, y eso no es algo que un guion
-- deba decidir solo.
--
-- En producción esto no haría falta: un cambio de obligatoriedad es una versión
-- nueva de estructura y su tabla receptora se genera de cero. Acá existe porque
-- el prototipo corrige la definición sobre versiones ya creadas.
-- ---------------------------------------------------------------------------

-- Esto NO se hace acá, y el primer intento de hacerlo fue un error instructivo:
-- un procedimiento SQL que emparejaba las columnas por nombre aflojó también el
-- Nº DNI del legajo, que la Capa 1 declara obligatorio. El nombre de la columna
-- no alcanza para saber a qué hoja y a qué versión pertenece.
--
-- El nombre de la tabla receptora no está guardado en ningún lado: se deduce por
-- convención, con la misma función que usan el generador y el importador. Un SQL
-- que quisiera reconstruirlo tendría que repetir esa convención.
--
-- Después de correr este guion:
--
--   docker exec runac_python python /trabajo/scripts/sincronizar_receptoras.py
--   docker exec runac_python python /trabajo/scripts/sincronizar_receptoras.py --aplicar
--
-- La primera forma informa y no toca nada. La segunda afloja lo que la Capa 1
-- declara opcional, y lo que habría que endurecer lo informa sin tocarlo.

-- ---------------------------------------------------------------------------
-- 5. La residencia que nombra la nómina de protección tiene que existir
--
-- Es la misma idea que la regla del dispositivo penal, del otro lado del
-- sistema: el MPE nombra la residencia u hogar donde está alojado el chico, y
-- eso tiene que estar declarado en el archivo de dispositivos de cuidado.
--
-- ADVERTENCIA y no BLOQUEANTE, por el mismo motivo que la otra: no hay un
-- identificador, sólo el nombre escrito, y una diferencia de redacción se
-- resuelve dentro del sistema y no rehaciendo el Excel.
--
-- Además de verificar el dato, es lo que hace que el archivo de dispositivos de
-- cuidado deba importarse antes que el MPE.
-- ---------------------------------------------------------------------------

INSERT INTO `runac_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT t.id, 'mpe_nombre_de_la_residencia_existe_en_archivo',
       'La residencia u hogar que nombra el MPE tiene que estar declarada en el archivo de dispositivos de cuidado.',
       JSON_OBJECT('archivo', 'DISP_SCP', 'campo', 'nombre_del_dispositvo')
  FROM `runac_c1_tipo_regla` t
 WHERE t.`nombre` = 'EXISTE_EN_ARCHIVO'
ON DUPLICATE KEY UPDATE `parametros` = VALUES(`parametros`);

INSERT INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`, `mensaje`)
SELECT c.id, r.id, 'ADVERTENCIA',
       'La residencia no figura en el archivo de dispositivos de cuidado de este período. Puede ser un nombre escrito distinto o un dispositivo que falta declarar.'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_regla` r ON r.nombre = 'mpe_nombre_de_la_residencia_existe_en_archivo'
 WHERE c.`nombre` = 'nombre_de_la_residencia_hogar'
ON DUPLICATE KEY UPDATE `mensaje` = VALUES(`mensaje`);
