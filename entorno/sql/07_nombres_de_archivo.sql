-- ===========================================================================
-- Capa 1 — Cómo se llama cada archivo
--
-- El archivo y la hoja son dos cosas distintas, y el modelo las tenía
-- mezcladas: `runac_c1_archivo_version.titulo` guardaba el encabezado de la
-- PRIMERA HOJA de la planilla. Así, el archivo de dispositivos penales
-- —que tiene cinco hojas: CRC, CRSC, MPT, CAD y Guardia Comisaría— aparecía en
-- pantalla como «Listado de los dispositivos penales Centros de Régimen
-- Cerrado», que es el título de una sola de ellas.
--
-- El nombre del archivo es un dato del archivo. Va en `runac_c1_archivo`, que
-- es la tabla que no se versiona: el archivo se sigue llamando igual aunque
-- cambie su estructura.
--
-- PROVISORIO EN DOS SENTIDOS, y conviene saberlo:
--
--   1. Estos nombres están escritos a mano acá. Cuando exista el CRUD de
--      archivos, los va a administrar el Responsable Nacional desde el sistema
--      y este guion deja de hacer falta.
--   2. `descripcion` se regenera al volver a generar la Capa 1, con un texto
--      automático del tipo «Archivo X de RUNAC. hoja "Y" con N campos». Si se
--      regenera, hay que volver a correr esto.
--
-- A CONFIRMAR con el responsable funcional: la redacción de los cinco nombres.
-- ===========================================================================

SET NAMES utf8mb4;

UPDATE `runac_c1_archivo` SET `descripcion` = CASE `codigo`
    WHEN 'DISP_PENAL' THEN 'Listado de dispositivos penales'
    WHEN 'DISP_SCP'   THEN 'Listado de dispositivos de cuidado residencial'
    WHEN 'MPI'        THEN 'Nómina de medidas de protección integral'
    WHEN 'MPE'        THEN 'Nómina de medidas de protección excepcional'
    WHEN 'MPJ_DAE'    THEN 'Nómina de medidas penales juveniles'
    WHEN 'LEGAJO_NYA' THEN 'Legajo de niñas, niños y adolescentes'
    ELSE `descripcion`
  END
 WHERE `codigo` IN ('DISP_PENAL', 'DISP_SCP', 'MPI', 'MPE', 'MPJ_DAE', 'LEGAJO_NYA');
