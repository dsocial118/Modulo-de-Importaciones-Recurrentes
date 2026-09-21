-- ===========================================================================
-- Las versiones en borrador también tenían campos declarados FECHA sin serlo
--
-- POR QUÉ
--
-- El guion 16 corrigió siete campos mal tipados, pero sólo en las versiones
-- VIGENTES. El legajo del niño y el MPE v2 están en BORRADOR y quedaron
-- afuera: tienen el mismo defecto, con el mismo origen —la planilla trae
-- aplicado formato de fecha en columnas que no son fechas, y el extractor le
-- creyó al formato—.
--
-- Son seis, y ninguno es una fecha:
--
--   LEGAJO_NYA  Departamento
--   MPE v2      Departamento de residencia de la familia   (dos columnas)
--               ID familia ampliada
--               Familia Ampliada
--               Vínculo con el NyA
--
-- Pasan a TEXTO, que es lo que son: nombres de lugar, un identificador y un
-- vínculo familiar.
--
-- Y SE VAN LAS REGLAS QUE ARRASTRABAN
--
-- Cuatro de ellos tenían «no puede ser una fecha futura». Sobre un campo que
-- guarda «Chacabuco» o «tía materna», esa regla no se puede evaluar: o no
-- dice nada o rechaza datos correctos, que es el peor resultado posible.
--
-- Corregir el tipo y dejar la regla sería arreglar la mitad.
--
-- LO QUE NO SE TOCA, Y ESTÁ BIEN QUE NO SE TOQUE
--
-- «Nº DNI», «Nº de CUIL» y «Cuil o documento de identidad» siguen siendo
-- TEXTO aunque parezcan números. Un DNI puede empezar con cero y un CUIL se
-- escribe con guiones: convertirlos a número perdería el cero y rechazaría
-- los guiones.
-- ===========================================================================

SET NAMES utf8mb4;

-- 1. El tipo, en las versiones en borrador.
UPDATE mir_c1_campo SET tipo_dato = 'TEXTO'
 WHERE id IN (501, 530, 531, 532, 533, 534)
   AND tipo_dato = 'FECHA';

-- 2. Las reglas de fecha que quedaron colgadas de esos campos.
DELETE cr FROM mir_c1_campo_regla cr
  JOIN mir_c1_regla r ON r.id = cr.regla_id
 WHERE cr.campo_id IN (501, 530, 531, 532, 533, 534)
   AND JSON_EXTRACT(r.parametros, '$.valor') = 'HOY';

-- 3. Verificación: las dos consultas tienen que dar cero.
SELECT COUNT(*) AS campos_que_siguen_como_fecha
  FROM mir_c1_campo WHERE id IN (501, 530, 531, 532, 533, 534) AND tipo_dato = 'FECHA';

SELECT COUNT(*) AS reglas_de_fecha_sobre_campos_que_no_lo_son
  FROM mir_c1_campo_regla cr
  JOIN mir_c1_regla r ON r.id = cr.regla_id
  JOIN mir_c1_campo c ON c.id = cr.campo_id
 WHERE JSON_EXTRACT(r.parametros, '$.valor') = 'HOY'
   AND c.tipo_dato NOT IN ('FECHA', 'HORA');
