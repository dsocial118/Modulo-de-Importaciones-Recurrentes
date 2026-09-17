-- ===========================================================================
-- Capa 1 — Siete campos declarados FECHA que no lo son
--
-- QUÉ PASABA
--
-- Siete columnas quedaron declaradas FECHA. El generador de datos de prueba
-- escribía fechas ahí, así que en pantalla se leía «ID familia ampliada:
-- 13/07/2025», que fue como se descubrió.
--
-- Pero lo grave no es lo que se ve: es que **tres arrastran reglas que
-- rechazan el archivo entero**. «Especificar destino al egreso» —donde la
-- provincia escribe en qué lugar quedó el chico— tiene una regla BLOQUEANTE
-- que exige que sea posterior o igual a la fecha de ingreso al dispositivo.
-- Con un archivo real, que va a decir «Domicilio familiar», esa comparación
-- falla y el MPJ_DAE no entra.
--
-- Es el único defecto de los encontrados que **rechaza datos buenos**. Los
-- demás dejan pasar datos malos, que es menos urgente.
--
-- LOS SIETE
--
--   MPE  familia                          FECHA -> TEXTO
--   MPE  id_familia_ampliada              FECHA -> ENTERO
--   MPE  familia_ampliada                 FECHA -> TEXTO
--   MPJ  especificar_destino_al_egreso    FECHA -> TEXTO
--   DAE  especificar_destino_al_egreso    FECHA -> TEXTO
--   DAE  hora_de_ingreso_al_dispositivo   FECHA -> HORA
--   DAE  hora_de_egreso_del_dispositivo   FECHA -> HORA
--
-- Los cuatro primeros van de a pares en la planilla: un identificador y un
-- nombre, dos veces. Ninguno es una fecha. `id_familia` —el par que sí quedó
-- bien— es ENTERO, y por eso `id_familia_ampliada` va igual y con sus mismas
-- reglas de identificador.
--
-- QUÉ REGLAS SE VAN Y CUÁLES SE QUEDAN
--
-- Se van las que sólo tienen sentido sobre una fecha:
--
--   COMPARAR_VALOR «no posterior a HOY»   en los siete
--   COMPARAR_CAMPO «posterior al ingreso» en los dos «especificar destino»
--
-- Se quedan:
--
--   OBLIGATORIO_SI  en los dos «especificar destino»: si el destino al egreso
--                   está en cierta lista, hay que especificar. Es correcta.
--   (ver el punto 6: la de «hora de egreso» tambien sale, y por un motivo
--    que solo se ve despues de arreglar el tipo)
--
-- LA CAUSA YA ESTÁ ARREGLADA APARTE
--
-- `inferir.py` tomaba «ingreso», «egreso» y «alta» como palabras de fecha por
-- sí solas, y no tenía forma de que un nombre VETARA un formato. Las dos cosas
-- se corrigieron en el mismo cambio que este guion. Sin eso, la próxima
-- planilla vuelve a traer el mismo error.
-- ===========================================================================

SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- 1. Las reglas que sólo valen sobre una fecha. Se saca el enganche, no la
--    regla: cada una la usan también los campos que sí son fechas.
-- ---------------------------------------------------------------------------
DELETE cr FROM `mir_c1_campo_regla` cr
  JOIN `mir_c1_regla` r ON r.id = cr.regla_id
  JOIN `mir_c1_campo` c ON c.id = cr.campo_id
 WHERE r.`nombre` IN (
        'mpe_familia_comparar_valor',
        'mpe_id_familia_ampliada_comparar_valor',
        'mpe_familia_ampliada_comparar_valor',
        'mpj_dae_especificar_destino_al_egreso_comparar_valor',
        'mpj_dae_hora_de_ingreso_al_dispositivo_comparar_valor',
        'mpj_dae_hora_de_egreso_del_dispositivo_comparar_valor'
       );

-- La bloqueante que rechaza el archivo entero. Sólo la del «especificar
-- destino»: la de «hora de egreso» se conserva, ahí la comparación sí vale.
DELETE cr FROM `mir_c1_campo_regla` cr
  JOIN `mir_c1_regla` r ON r.id = cr.regla_id
 WHERE r.`nombre` = 'mpj_dae_especificar_destino_al_egreso_comparar_campo';

-- ---------------------------------------------------------------------------
-- 2. Los tipos.
-- ---------------------------------------------------------------------------
UPDATE `mir_c1_campo` c
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
 SET c.`tipo_dato` = 'TEXTO', c.`longitud_maxima` = 120
 WHERE c.`nombre` IN ('familia', 'familia_ampliada');

UPDATE `mir_c1_campo` c
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
 SET c.`tipo_dato` = 'TEXTO', c.`longitud_maxima` = 255
 WHERE c.`nombre` = 'especificar_destino_al_egreso';

UPDATE `mir_c1_campo` c
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
 SET c.`tipo_dato` = 'ENTERO', c.`longitud_maxima` = NULL
 WHERE c.`nombre` = 'id_familia_ampliada';

UPDATE `mir_c1_campo` c
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
 SET c.`tipo_dato` = 'HORA', c.`longitud_maxima` = NULL
 WHERE c.`nombre` IN ('hora_de_ingreso_al_dispositivo', 'hora_de_egreso_del_dispositivo');

-- ---------------------------------------------------------------------------
-- 3. El identificador nuevo lleva las mismas reglas que su par `id_familia`.
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO `mir_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'ADVERTENCIA'
  FROM `mir_c1_campo` c
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `mir_c1_regla` r ON r.`nombre` = 'rango_identificador'
 WHERE c.`nombre` = 'id_familia_ampliada';

INSERT IGNORE INTO `mir_c1_campo_regla` (`campo_id`, `regla_id`, `severidad`)
SELECT c.id, r.id, 'BLOQUEANTE'
  FROM `mir_c1_campo` c
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `mir_c1_regla` r ON r.`nombre` = 'tope_identificador'
 WHERE c.`nombre` = 'id_familia_ampliada';

-- ---------------------------------------------------------------------------
-- 4. Las columnas que reciben el dato.
-- ---------------------------------------------------------------------------
ALTER TABLE `mir_c2_mpe_v1`
  MODIFY `familia` varchar(120) NULL,
  MODIFY `familia_ampliada` varchar(120) NULL,
  MODIFY `id_familia_ampliada` bigint NULL;

ALTER TABLE `mir_c2_mpj_dae_v1_mpj`
  MODIFY `especificar_destino_al_egreso` varchar(255) NULL;

ALTER TABLE `mir_c2_mpj_dae_v1_dae`
  MODIFY `especificar_destino_al_egreso` varchar(255) NULL,
  MODIFY `hora_de_ingreso_al_dispositivo` time NULL,
  MODIFY `hora_de_egreso_del_dispositivo` time NULL;

-- ---------------------------------------------------------------------------
-- 5. Cómo quedó. No tiene que quedar ningún FECHA sin la palabra «fecha».
-- ---------------------------------------------------------------------------
SELECT a.`codigo` AS archivo, h.`nombre_esperado` AS hoja,
       c.`titulo_esperado` AS campo, c.`tipo_dato`,
       (SELECT GROUP_CONCAT(CONCAT(tr.`nombre`, '/', cr.`severidad`))
          FROM `mir_c1_campo_regla` cr
          JOIN `mir_c1_regla` r ON r.id = cr.regla_id
          JOIN `mir_c1_tipo_regla` tr ON tr.id = r.tipo_regla_id
         WHERE cr.campo_id = c.id) AS reglas
  FROM `mir_c1_campo` c
  JOIN `mir_c1_hoja` h ON h.id = c.hoja_id
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `mir_c1_archivo` a ON a.id = av.archivo_id
 WHERE c.`nombre` IN ('familia', 'familia_ampliada', 'id_familia_ampliada',
                      'especificar_destino_al_egreso',
                      'hora_de_ingreso_al_dispositivo', 'hora_de_egreso_del_dispositivo')
 ORDER BY a.`codigo`, h.`orden_procesamiento`, c.`orden`;

-- ===========================================================================
-- 6. UNA MÁS, QUE SÓLO SE VE DESPUÉS DE ARREGLAR EL TIPO
--
-- `hora_de_egreso_del_dispositivo` conservaba una COMPARAR_CAMPO bloqueante
-- que, mirada de cerca, compara **una hora contra una fecha**:
--
--   hora_de_egreso  MAYOR_IGUAL  fecha_de_ingreso_al_dispositivo
--
-- Quedó de cuando el campo estaba inferido como FECHA y la comparación era
-- entre dos fechas. Hoy no explota —el motor no puede comparar los dos tipos,
-- lo toma como no evaluable y no reporta nada— pero es una regla muerta que
-- dice algo falso sobre el dato.
--
-- LO QUE SÍ HARÍA FALTA, Y HOY NO SE PUEDE ESCRIBIR
--
-- La comparación con sentido es «el egreso es posterior al ingreso», y entre
-- dispositivos de tránsito eso cruza la medianoche: se entra 23:15 y se sale
-- 08:30 del día siguiente. O sea que hay que comparar **fecha + hora contra
-- fecha + hora**, y `COMPARAR_CAMPO` compara un campo contra otro campo, no
-- un par contra otro par.
--
-- No se inventa ahora. Queda como pendiente: o un tipo de regla que compare
-- pares, o un campo calculado. Mientras tanto, la regla se saca en vez de
-- dejarla diciendo una falsedad.
-- ===========================================================================

DELETE cr FROM `mir_c1_campo_regla` cr
  JOIN `mir_c1_regla` r ON r.id = cr.regla_id
 WHERE r.`nombre` = 'mpj_dae_hora_de_egreso_del_dispositivo_comparar_campo';
