-- ===========================================================================
-- Capa 1 — Los encabezados suben una fila en las hojas de dispositivos
--
-- QUÉ PASABA
--
-- En las hojas de dispositivos la fila 1 quedaba vacía en la plantilla que se
-- entrega. La planilla se abría con un renglón en blanco arriba de todo, y eso
-- se lee como un error de armado.
--
-- Queda vacía porque el armador coloca el título justo encima de los
-- encabezados, y los encabezados están declarados en la fila 3. En el insumo
-- original la fila 1 no está vacía: lleva «ATENCIÓN: Respetar clasificaciones
-- previstas en campos con DESPLEGABLES». Nosotros no reponemos ese aviso —es
-- criterio a acordar con la DNPYPI— así que el lugar sobra.
--
-- QUÉ CAMBIA
--
--   DISP_PENAL  CRC, CRSC, MPT, CAD, Guardia Comisaría    3  ->  2
--   DISP_SCP    M Residencial                             4  ->  3
--
-- Las hojas de nóminas —MPI, MPE, MPJ, DAE— NO se tocan: tienen una fila de
-- grupos de campos entre el título y los encabezados, así que su fila 1 ya
-- está ocupada por el título.
--
-- ---------------------------------------------------------------------------
-- EL RIESGO, QUE NO ES CERO Y ESTÁ ACEPTADO
--
-- `fila_encabezados` no es decoración: es el número contra el que el
-- importador lee los títulos de columna del archivo que sube la provincia
-- (`importar.py`, `procesar_hoja`). Al bajarlo, el sistema pasa a esperar los
-- encabezados en la fila 2.
--
-- Consecuencia: **un archivo armado sobre el Excel original de la DNPYPI, que
-- los tiene en la fila 3, deja de entrar.** Sólo entran los armados sobre la
-- plantilla que entrega el sistema, que es como está pensado el circuito.
--
-- Decisión del responsable funcional del 2026-09-15, tomada con esto dicho: se
-- muestra así en la reunión, se avisa a la contraparte que quedó distinto del
-- original y se acuerda con ellos si conviene volver atrás. Relacionado: la
-- DNPYPI usa colores para separar los grupos de campos, que tampoco
-- reproducimos, y es parte de la misma conversación.
-- ===========================================================================

SET NAMES utf8mb4;

-- Sólo las hojas cuya fila 1 queda vacía, y sólo si todavía no se bajaron.
-- Correr el guion dos veces no vuelve a restar.
UPDATE `mir_c1_hoja` h
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `mir_c1_archivo` a ON a.id = av.archivo_id
 SET h.`fila_encabezados` = h.`fila_encabezados` - 1
 WHERE (a.`codigo` = 'DISP_PENAL' AND h.`fila_encabezados` = 3)
    OR (a.`codigo` = 'DISP_SCP' AND h.`fila_encabezados` = 4);

-- Cómo quedó. Los dispositivos en 2 y 3; las nóminas, intactas en 3.
SELECT a.`codigo` AS archivo, h.`nombre_esperado` AS hoja,
       h.`fila_encabezados` AS encabezados_en_la_fila
  FROM `mir_c1_hoja` h
  JOIN `mir_c1_archivo_version` av ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'
  JOIN `mir_c1_archivo` a ON a.id = av.archivo_id
 ORDER BY a.`codigo`, h.`orden_procesamiento`;
