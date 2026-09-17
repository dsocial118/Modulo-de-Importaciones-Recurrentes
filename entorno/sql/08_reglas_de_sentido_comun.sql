-- ===========================================================================
-- Capa 1 — Rangos de sentido común sobre los campos numéricos
--
-- De 33 campos numéricos, sólo los cuatro «Edad» tenían alguna regla. El resto
-- —cantidad de agentes, horas semanales, días de permanencia, monto de la
-- pena— admitía cualquier número: 8888 agentes, 500 horas semanales, o un
-- identificador negativo.
--
-- QUÉ SON ESTAS REGLAS, Y QUÉ NO SON
--
-- Son **provisorias y para conversar**. Ninguna sale de un documento de la
-- DNPYPI: salen de mirar qué dice cada columna y preguntarse qué número sería
-- imposible o absurdo. Están para que el sistema muestre que sabe controlar
-- estas cosas, y para que la contraparte diga cuál es el número correcto.
--
-- Por eso **todas son ADVERTENCIA y ninguna bloquea**: un archivo con un valor
-- raro entra igual y queda señalado. Si se confirmara que alguna es un límite
-- duro, pasar a BLOQUEANTE es cambiar una palabra.
--
-- Hay un solo fundamento que no es opinión: una semana tiene 168 horas.
--
-- Los topes se eligieron además de modo que **los archivos de prueba limpios
-- sigan dando cero hallazgos**: si cada corrida de prueba produjera
-- advertencias inventadas, dejaría de servir para saber si algo anda mal.
--
-- A CONFIRMAR CON LA DNPYPI: los máximos de plantel, de alojados, de días de
-- permanencia, y en qué unidad se informa el monto de la pena.
-- ===========================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- Las reglas. Una por criterio: la misma regla se engancha después a todos los
-- campos que le corresponden, en cualquier archivo y cualquier hoja.
-- ---------------------------------------------------------------------------

INSERT INTO `mir_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT t.id, r.nombre, r.descripcion, r.parametros
  FROM `mir_c1_tipo_regla` t
  JOIN (
    SELECT 'rango_horas_semanales' AS nombre,
           'Las horas semanales no pueden superar las que tiene una semana.' AS descripcion,
           JSON_OBJECT('minimo', 0, 'maximo', 168) AS parametros
    UNION ALL SELECT 'rango_plantel',
           'Cantidad de personas que trabajan en el dispositivo. El máximo es provisorio.',
           JSON_OBJECT('minimo', 0, 'maximo', 200)
    UNION ALL SELECT 'rango_alojados',
           'Cantidad de chicas y chicos alojados. El máximo es provisorio.',
           JSON_OBJECT('minimo', 0, 'maximo', 200)
    UNION ALL SELECT 'rango_dias_de_permanencia',
           'Días de permanencia. El máximo provisorio son diez años.',
           JSON_OBJECT('minimo', 0, 'maximo', 3650)
    UNION ALL SELECT 'rango_no_negativo',
           'Una cantidad informada no puede ser negativa.',
           JSON_OBJECT('minimo', 0)
    UNION ALL SELECT 'rango_identificador',
           'Un identificador empieza en uno: no es cero ni negativo.',
           JSON_OBJECT('minimo', 1)
  ) r
 WHERE t.`nombre` = 'RANGO'
ON DUPLICATE KEY UPDATE `parametros` = VALUES(`parametros`),
                        `descripcion` = VALUES(`descripcion`);

-- ---------------------------------------------------------------------------
-- A qué campos se engancha cada una.
--
-- Por nombre técnico y no por id: el mismo campo aparece en varias hojas —hay
-- cinco «cantidad de agentes» entre las hojas de dispositivos penales— y así
-- quedan cubiertas todas sin enumerarlas.
-- ---------------------------------------------------------------------------

INSERT INTO `mir_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`, `mensaje`)
SELECT c.id, r.id, 'ADVERTENCIA', m.mensaje
  FROM `mir_c1_campo` c
  JOIN (
    SELECT 'rango_horas_semanales' AS regla,
           'cantidad_de_horas_semanales_%' AS patron,
           'Son más horas de las que tiene una semana. Conviene revisar el dato.' AS mensaje
    UNION ALL SELECT 'rango_plantel', 'cantidad_de_agentes_%',
           'Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'
    UNION ALL SELECT 'rango_plantel', 'cantidad_agentes_%',
           'Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'
    UNION ALL SELECT 'rango_plantel', 'cantidad_de_personal_%',
           'Es una cantidad de personal inusualmente alta. Conviene revisar el dato.'
    UNION ALL SELECT 'rango_alojados', 'cantidad_de_nya_alojados_%',
           'Es una cantidad de chicas y chicos inusualmente alta. Conviene revisar el dato.'
    UNION ALL SELECT 'rango_dias_de_permanencia', 'dias_de_permanencia',
           'Son más de diez años de permanencia. Conviene revisar el dato.'
    UNION ALL SELECT 'rango_no_negativo', 'monto_de_la_pena',
           'El monto de la pena no puede ser negativo.'
    UNION ALL SELECT 'rango_identificador', 'id_familia',
           'Un identificador empieza en uno.'
    UNION ALL SELECT 'rango_identificador', 'id_del_nino_nina_o_adolescente',
           'Un identificador empieza en uno.'
  ) m ON c.`nombre` LIKE m.patron
  JOIN `mir_c1_regla` r ON r.`nombre` = m.regla
 WHERE c.`tipo_dato` IN ('ENTERO', 'DECIMAL')
ON DUPLICATE KEY UPDATE `mensaje` = VALUES(`mensaje`);
