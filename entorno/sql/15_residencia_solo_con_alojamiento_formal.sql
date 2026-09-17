-- ===========================================================================
-- Capa 1 — La residencia sólo se nombra si la modalidad es alojamiento formal
--
-- LA REGLA, EN CASTELLANO
--
-- En el MPE, «Nombre de la residencia/hogar» tiene que quedar VACÍO cuando
-- «Modalidad de cuidado» es distinta de «Alojamiento formal».
--
-- Si la provincia informa que el chico está con su familia ampliada o en una
-- familia de acogimiento, no puede además nombrar una residencia: son dos
-- afirmaciones que se contradicen, y no hay forma de saber cuál vale.
--
-- Las cuatro opciones de la modalidad:
--   Alojamiento formal · Familia ampliada · Familia de acogimiento · Otro
--
-- POR QUÉ BLOQUEANTE Y NO ADVERTENCIA
--
-- Las otras cuatro reglas PROHIBIDO_SI de la base son todas bloqueantes: son
-- las del DNI cuando la situación de documentación declara que no lo tiene.
-- Ésta es del mismo tipo —una contradicción entre dos campos de la misma
-- fila, no un valor llamativo— así que sigue la misma convención.
--
-- Decisión del responsable funcional, 2026-09-16.
--
-- NO HIZO FALTA TOCAR CÓDIGO
--
-- El tipo de regla PROHIBIDO_SI y el operador DISTINTO ya existían. Esto es
-- una fila nueva en una tabla, que es exactamente lo que el módulo promete:
-- una validación más no es un cambio de programa.
--
-- El campo antes tenía una sola regla —que la residencia exista en el archivo
-- de dispositivos de cuidado residencial— y por eso se podía nombrar una
-- residencia real junto a una modalidad que la excluye.
-- ===========================================================================

SET NAMES utf8mb4;

-- 1. La regla. `NOT EXISTS` para que correr el guion dos veces no la duplique.
INSERT INTO `runac_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT tr.id,
       'mpe_residencia_solo_si_alojamiento_formal',
       'La residencia no se nombra cuando la modalidad de cuidado no es alojamiento formal.',
       '{"campo_condicion": "modalidad_de_cuidado", "operador": "DISTINTO", "valor_condicion": "Alojamiento formal"}'
  FROM `runac_c1_tipo_regla` tr
 WHERE tr.`nombre` = 'PROHIBIDO_SI'
   AND NOT EXISTS (
       SELECT 1 FROM `runac_c1_regla` r
        WHERE r.`nombre` = 'mpe_residencia_solo_si_alojamiento_formal');

-- 2. Colgarla del campo.
INSERT IGNORE INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'BLOQUEANTE'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_archivo` a ON a.id = av.archivo_id
  JOIN `runac_c1_regla` r ON r.`nombre` = 'mpe_residencia_solo_si_alojamiento_formal'
 WHERE a.`codigo` = 'MPE'
   AND c.`nombre` = 'nombre_de_la_residencia_hogar';

-- 3. Cómo quedó el campo.
SELECT a.`codigo` AS archivo, c.`titulo_esperado` AS campo,
       tr.`nombre` AS tipo, cr.`severidad`, r.`parametros`
  FROM `runac_c1_campo_regla` cr
  JOIN `runac_c1_regla` r ON r.id = cr.regla_id
  JOIN `runac_c1_tipo_regla` tr ON tr.id = r.tipo_regla_id
  JOIN `runac_c1_campo` c ON c.id = cr.campo_id
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_archivo` a ON a.id = av.archivo_id
 WHERE a.`codigo` = 'MPE' AND c.`nombre` = 'nombre_de_la_residencia_hogar';

-- ===========================================================================
-- 4. LA CONTRADICCIÓN QUE DESTAPÓ LA REGLA ANTERIOR
--
-- Al sembrar la regla, el MPE limpio pasó a quedar FALLIDA con 19 bloqueantes,
-- y NO por la regla nueva: por `OBLIGATORIO_VACIO`.
--
-- «Nombre de la residencia/hogar» estaba declarado **obligatorio para todas
-- las filas**. O sea que el sistema le exigía nombrar una residencia también a
-- un chico que está con su familia ampliada. Eso ya estaba mal antes de hoy;
-- lo que hizo la regla nueva fue volverlo imposible de ignorar: un campo no
-- puede ser obligatorio y prohibido en la misma fila.
--
-- La forma correcta es que sea obligatorio EXACTAMENTE cuando corresponde:
--
--   modalidad = Alojamiento formal   ->  la residencia es obligatoria
--   modalidad ≠ Alojamiento formal   ->  la residencia tiene que estar vacía
--
-- Las dos reglas son la misma idea vista de los dos lados, y entre las dos
-- cubren las cuatro opciones de la modalidad sin dejar hueco.
-- ===========================================================================

-- 4.1. Deja de ser obligatorio siempre.
UPDATE `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_archivo` a ON a.id = av.archivo_id
 SET c.`obligatorio` = 0
 WHERE a.`codigo` = 'MPE' AND c.`nombre` = 'nombre_de_la_residencia_hogar';

-- 4.2. Pasa a ser obligatorio cuando la modalidad SÍ es alojamiento formal.
INSERT INTO `runac_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT tr.id,
       'mpe_residencia_obligatoria_si_alojamiento_formal',
       'Si la modalidad de cuidado es alojamiento formal, hay que decir en qué residencia.',
       '{"campo_condicion": "modalidad_de_cuidado", "operador": "IGUAL", "valor_condicion": "Alojamiento formal"}'
  FROM `runac_c1_tipo_regla` tr
 WHERE tr.`nombre` = 'OBLIGATORIO_SI'
   AND NOT EXISTS (
       SELECT 1 FROM `runac_c1_regla` r
        WHERE r.`nombre` = 'mpe_residencia_obligatoria_si_alojamiento_formal');

INSERT IGNORE INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'BLOQUEANTE'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_archivo` a ON a.id = av.archivo_id
  JOIN `runac_c1_regla` r ON r.`nombre` = 'mpe_residencia_obligatoria_si_alojamiento_formal'
 WHERE a.`codigo` = 'MPE' AND c.`nombre` = 'nombre_de_la_residencia_hogar';

-- 4.3. Cómo quedó.
SELECT c.`titulo_esperado` AS campo, c.`obligatorio`,
       tr.`nombre` AS tipo, cr.`severidad`, r.`parametros`
  FROM `runac_c1_campo_regla` cr
  JOIN `runac_c1_regla` r ON r.id = cr.regla_id
  JOIN `runac_c1_tipo_regla` tr ON tr.id = r.tipo_regla_id
  JOIN `runac_c1_campo` c ON c.id = cr.campo_id
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_archivo` a ON a.id = av.archivo_id
 WHERE a.`codigo` = 'MPE' AND c.`nombre` = 'nombre_de_la_residencia_hogar';
