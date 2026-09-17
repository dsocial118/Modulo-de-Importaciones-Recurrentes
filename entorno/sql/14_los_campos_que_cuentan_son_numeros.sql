-- ===========================================================================
-- Capa 1 — Diez campos que cuentan cosas estaban declarados TEXTO
--
-- QUÉ PASABA
--
-- En «Capacidad de alojamiento mujeres (plazas disponibles)» se podía escribir
-- 3444444444444444444444444444 y el sistema no decía nada. No es que faltara
-- una regla: el campo estaba declarado **TEXTO con longitud 255**, así que
-- veintiocho dígitos son un texto corto y perfectamente válido.
--
-- Las reglas de rango no se podían aplicar porque un rango sobre un texto no
-- significa nada. Primero hay que arreglar el tipo.
--
-- ESTO NO ES UNA OPINIÓN NUESTRA
--
-- La propia planilla de la DNPYPI lo declara. En las hojas de categorías
-- —«Categorias CAD», «Categorias Guardia Comisaria»— la fila que documenta el
-- tipo de cada columna dice, para todas estas:
--
--   Capacidad de alojamiento mujeres (plazas disponibles)   ->  Número
--   Capacidad de alojamiento varones (plazas disponibles)   ->  Número
--   Tiempo máximo de permanencia dentro del dispositivo     ->  Número
--
-- El extractor no lee esas hojas como fuente de tipos —pendiente #29— así que
-- infirió TEXTO de los datos que había. Mientras eso no se arregle, cada
-- planilla nueva puede traer el mismo problema.
--
-- LOS DIEZ CAMPOS
--
--   DISP_PENAL  CRC, CRSC, CAD   Capacidad de alojamiento mujeres      TEXTO -> ENTERO
--   DISP_PENAL  CRC, CRSC, CAD   Capacidad de alojamiento varones      TEXTO -> ENTERO
--   DISP_PENAL  CAD, Guardia     Tiempo máximo de permanencia (horas)  TEXTO -> ENTERO
--   DISP_SCP    M Residencial    Capacidad de alojamiento (Plazas)     TEXTO -> ENTERO
--   MPJ_DAE     DAE              Edad al ingreso                       FECHA -> ENTERO
--
-- El último es de otra familia y va acá porque es el mismo síntoma: «Edad al
-- ingreso» quedó declarada FECHA —el extractor la infirió del formato de la
-- columna, igual que los seis del pendiente #26— y encima tenía colgada una
-- regla de rango numérico, que sobre una fecha no evalúa nada.
--
-- LOS LÍMITES
--
--   capacidad de alojamiento   reusa rango_alojados (aviso >200)
--                              y tope_alojados (bloquea >5000)
--   horas de permanencia       reglas nuevas: aviso >168 (una semana),
--                              bloquea >8760 (un año)
--   edad al ingreso            ya tenia su propio aviso 0-17; se le suma
--                              tope_edad (bloquea >120) y se le saca la regla
--                              de fecha que arrastraba
--
-- La unidad de la permanencia NO se adivinó: está en el nombre del campo,
-- «…dentro del dispositivo en horas». El techo blando de una semana es
-- provisorio y entra en la lista de preguntas a la DNPYPI, junto con el resto
-- de los límites.
--
-- Se corrige en los dos lados, como siempre: la definición y la columna que
-- recibe el dato.
-- ===========================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- 1. El tipo declarado.
-- ---------------------------------------------------------------------------
UPDATE `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
 SET c.`tipo_dato` = 'ENTERO', c.`longitud_maxima` = NULL
 WHERE c.`titulo_esperado` LIKE 'Capacidad de alojamiento%'
    OR c.`titulo_esperado` LIKE 'Tiempo máximo de permanencia%'
    OR c.`titulo_esperado` = 'Edad al ingreso';

-- ---------------------------------------------------------------------------
-- 2. Las reglas nuevas, sólo las que no existen. Los dos techos: uno avisa,
--    el otro impide importar.
-- ---------------------------------------------------------------------------
INSERT INTO `runac_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT tr.id, 'rango_horas_de_permanencia',
       'Permanencia declarada en horas: más de una semana llama la atención en un dispositivo de tránsito.',
       '{"minimo": 0, "maximo": 168}'
  FROM `runac_c1_tipo_regla` tr
 WHERE tr.`nombre` = 'RANGO'
   AND NOT EXISTS (SELECT 1 FROM `runac_c1_regla` r WHERE r.`nombre` = 'rango_horas_de_permanencia');

INSERT INTO `runac_c1_regla` (`tipo_regla_id`, `nombre`, `descripcion`, `parametros`)
SELECT tr.id, 'tope_horas_de_permanencia',
       'Más de un año en horas no es un dato: es un error de carga.',
       '{"minimo": 0, "maximo": 8760}'
  FROM `runac_c1_tipo_regla` tr
 WHERE tr.`nombre` = 'RANGO'
   AND NOT EXISTS (SELECT 1 FROM `runac_c1_regla` r WHERE r.`nombre` = 'tope_horas_de_permanencia');

-- ---------------------------------------------------------------------------
-- 3. Colgar las reglas de cada campo. `INSERT IGNORE` para que correr el guion
--    dos veces no duplique nada.
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'ADVERTENCIA'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_regla` r ON r.`nombre` = 'rango_alojados'
 WHERE c.`titulo_esperado` LIKE 'Capacidad de alojamiento%';

INSERT IGNORE INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'BLOQUEANTE'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_regla` r ON r.`nombre` = 'tope_alojados'
 WHERE c.`titulo_esperado` LIKE 'Capacidad de alojamiento%';

INSERT IGNORE INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'ADVERTENCIA'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_regla` r ON r.`nombre` = 'rango_horas_de_permanencia'
 WHERE c.`titulo_esperado` LIKE 'Tiempo máximo de permanencia%';

INSERT IGNORE INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'BLOQUEANTE'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_regla` r ON r.`nombre` = 'tope_horas_de_permanencia'
 WHERE c.`titulo_esperado` LIKE 'Tiempo máximo de permanencia%';

INSERT IGNORE INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'ADVERTENCIA'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_regla` r ON r.`nombre` = 'rango_edad'
 WHERE c.`titulo_esperado` = 'Edad al ingreso';

INSERT IGNORE INTO `runac_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'BLOQUEANTE'
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_regla` r ON r.`nombre` = 'tope_edad'
 WHERE c.`titulo_esperado` = 'Edad al ingreso';

-- ---------------------------------------------------------------------------
-- 4. Las columnas que reciben el dato. Se nombran a mano porque el nombre se
--    deduce por convención y no se puede reconstruir en SQL, igual que en los
--    guiones 06, 11 y 12.
-- ---------------------------------------------------------------------------
ALTER TABLE `runac_c2_disp_penal_v1_crc`
  MODIFY `capacidad_de_alojamiento_mujeres_plazas_disponibles` int NULL,
  MODIFY `capacidad_de_alojamiento_varones_plazas_disponibles` int NULL;

ALTER TABLE `runac_c2_disp_penal_v1_crsc`
  MODIFY `capacidad_de_alojamiento_mujeres_plazas_disponibles` int NULL,
  MODIFY `capacidad_de_alojamiento_varones_plazas_disponibles` int NULL;

ALTER TABLE `runac_c2_disp_penal_v1_cad`
  MODIFY `capacidad_de_alojamiento_mujeres_plazas_disponibles` int NULL,
  MODIFY `capacidad_de_alojamiento_varones_plazas_disponibles` int NULL,
  MODIFY `tiempo_maximo_de_permanencia_dentro_del_dispositivo_en_horas` int NULL;

ALTER TABLE `runac_c2_disp_penal_v1_guardiacomis`
  MODIFY `tiempo_maximo_de_permanencia_dentro_del_dispositivo_en_horas` int NULL;

ALTER TABLE `runac_c2_disp_scp_v1`
  MODIFY `capacidad_de_alojamiento_plazas` int NULL;

ALTER TABLE `runac_c2_mpj_dae_v1_dae`
  MODIFY `edad_al_ingreso` int NULL;

-- ---------------------------------------------------------------------------
-- 5. Cómo quedó.
-- ---------------------------------------------------------------------------
SELECT a.`codigo` AS archivo, h.`nombre_esperado` AS hoja,
       LEFT(c.`titulo_esperado`, 44) AS campo, c.`tipo_dato`,
       (SELECT GROUP_CONCAT(CONCAT(r.`nombre`, '/', cr.`severidad`) ORDER BY cr.`severidad`)
          FROM `runac_c1_campo_regla` cr
          JOIN `runac_c1_regla` r ON r.id = cr.regla_id
         WHERE cr.campo_id = c.id) AS reglas
  FROM `runac_c1_campo` c
  JOIN `runac_c1_hoja` h ON h.id = c.hoja_id
  JOIN `runac_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `runac_c1_archivo` a ON a.id = av.archivo_id
 WHERE c.`titulo_esperado` LIKE 'Capacidad de alojamiento%'
    OR c.`titulo_esperado` LIKE 'Tiempo máximo de permanencia%'
    OR c.`titulo_esperado` = 'Edad al ingreso'
 ORDER BY a.`codigo`, h.`orden_procesamiento`, c.`orden`;

-- ---------------------------------------------------------------------------
-- 6. Una regla que sobraba, y que sólo se ve al arreglar el tipo.
--
-- «Edad al ingreso» tenía colgada `mpj_dae_edad_al_ingreso_comparar_valor`,
-- que comprueba que el valor no sea posterior a HOY. Se le puso cuando el
-- campo estaba inferido como FECHA. Ahora es un número, y preguntarle a una
-- edad si es anterior a hoy no quiere decir nada.
--
-- Se saca el enganche, no la regla: la usan los campos que sí son fechas.
-- ---------------------------------------------------------------------------
DELETE cr FROM `runac_c1_campo_regla` cr
  JOIN `runac_c1_regla` r ON r.id = cr.regla_id
  JOIN `runac_c1_campo` c ON c.id = cr.campo_id
 WHERE c.`titulo_esperado` = 'Edad al ingreso'
   AND r.`nombre` = 'mpj_dae_edad_al_ingreso_comparar_valor';
