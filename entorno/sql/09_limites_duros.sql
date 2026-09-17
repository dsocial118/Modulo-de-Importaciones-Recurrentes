-- ===========================================================================
-- Capa 1 — Dos techos por campo numérico: el inusual y el imposible
--
-- El guion 08 puso rangos de sentido común, todos como ADVERTENCIA. Eso alcanza
-- para un valor raro —210 agentes— pero no para uno absurdo: escribir
-- 88.888.888.888 agentes dejaba una advertencia y el dato entraba igual.
--
-- Un número así no es un dato dudoso: es un dato que no puede ser. La diferencia
-- importa, y por eso ahora cada campo numérico tiene DOS reglas:
--
--   techo BLANDO   ADVERTENCIA   «esto es raro, conviene revisarlo»
--   techo DURO     BLOQUEANTE    «esto no puede ser»
--
-- Los dos techos son provisorios y están para conversar con la DNPYPI. El
-- criterio para el duro fue elegir un número que ningún caso real podría
-- alcanzar ni por asomo: si hiciera falta discutirlo, es que está mal puesto.
--
-- Excepción: las horas semanales tienen un solo techo y bloquea. Que una semana
-- tiene 168 horas no se discute, así que no hay zona intermedia.
--
-- Los archivos de prueba limpios siguen dando cero hallazgos: los valores que
-- genera el mock están muy por debajo de los techos blandos.
-- ===========================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- Los techos duros
-- ---------------------------------------------------------------------------

INSERT INTO `runac_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT t.id, r.nombre, r.descripcion, r.parametros
  FROM `runac_c1_tipo_regla` t
  JOIN (
    SELECT 'tope_plantel' AS nombre,
           'Techo imposible para la cantidad de personas que trabajan en un dispositivo.' AS descripcion,
           JSON_OBJECT('minimo', 0, 'maximo', 5000) AS parametros
    UNION ALL SELECT 'tope_alojados',
           'Techo imposible para la cantidad de chicas y chicos alojados.',
           JSON_OBJECT('minimo', 0, 'maximo', 5000)
    UNION ALL SELECT 'tope_dias_de_permanencia',
           'Techo imposible para los días de permanencia: cien años.',
           JSON_OBJECT('minimo', 0, 'maximo', 36500)
    UNION ALL SELECT 'tope_edad',
           'Techo imposible para una edad.',
           JSON_OBJECT('minimo', 0, 'maximo', 120)
    UNION ALL SELECT 'tope_monto_de_la_pena',
           'El monto de la pena no puede ser negativo ni desmesurado.',
           JSON_OBJECT('minimo', 0, 'maximo', 100000)
    UNION ALL SELECT 'tope_identificador',
           'Un identificador empieza en uno y no puede ser desmesurado.',
           JSON_OBJECT('minimo', 1, 'maximo', 999999999)
  ) r
 WHERE t.`nombre` = 'RANGO'
ON DUPLICATE KEY UPDATE `parametros` = VALUES(`parametros`),
                        `descripcion` = VALUES(`descripcion`);

INSERT INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`, `mensaje`)
SELECT c.id, r.id, 'BLOQUEANTE', m.mensaje
  FROM `runac_c1_campo` c
  JOIN (
    SELECT 'tope_plantel' AS regla, 'cantidad_de_agentes_%' AS patron,
           'Ese número de personas no puede ser. Hay que corregirlo en el Excel.' AS mensaje
    UNION ALL SELECT 'tope_plantel', 'cantidad_agentes_%',
           'Ese número de personas no puede ser. Hay que corregirlo en el Excel.'
    UNION ALL SELECT 'tope_plantel', 'cantidad_de_personal_%',
           'Ese número de personas no puede ser. Hay que corregirlo en el Excel.'
    UNION ALL SELECT 'tope_alojados', 'cantidad_de_nya_alojados_%',
           'Ese número de chicas y chicos no puede ser. Hay que corregirlo en el Excel.'
    UNION ALL SELECT 'tope_dias_de_permanencia', 'dias_de_permanencia',
           'Esa cantidad de días no puede ser. Hay que corregirla en el Excel.'
    UNION ALL SELECT 'tope_edad', 'edad',
           'Esa edad no puede ser. Hay que corregirla en el Excel.'
    UNION ALL SELECT 'tope_monto_de_la_pena', 'monto_de_la_pena',
           'Ese monto no puede ser. Hay que corregirlo en el Excel.'
    UNION ALL SELECT 'tope_identificador', 'id_familia',
           'Ese identificador no puede ser. Hay que corregirlo en el Excel.'
    UNION ALL SELECT 'tope_identificador', 'id_del_nino_nina_o_adolescente',
           'Ese identificador no puede ser. Hay que corregirlo en el Excel.'
  ) m ON c.`nombre` LIKE m.patron
  JOIN `runac_c1_regla` r ON r.`nombre` = m.regla
 WHERE c.`tipo_dato` IN ('ENTERO', 'DECIMAL')
ON DUPLICATE KEY UPDATE `mensaje` = VALUES(`mensaje`);

-- ---------------------------------------------------------------------------
-- Las horas semanales pasan a bloquear: no hay techo blando que discutir.
-- ---------------------------------------------------------------------------

UPDATE `runac_c1_campo_regla` cr
  JOIN `runac_c1_regla` r ON r.id = cr.regla_id
 SET cr.`severidad` = 'BLOQUEANTE',
     cr.`mensaje` = 'Son más horas de las que tiene una semana: el dato no puede ser correcto.'
 WHERE r.`nombre` = 'rango_horas_semanales';
