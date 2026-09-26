-- 33 · Qué representa una fila de cada archivo.
--
-- El informe de la importación identifica cada problema por la fila en la que
-- está («3 · Villalba · Bautista · 90000411»). La columna se titulaba «De quién
-- es la fila», genérico para cualquier archivo. El responsable funcional pidió
-- el 26-09-2026 que diga lo que es según el archivo.
--
-- Va en la definición y no en el código porque el motor sirve para cualquier
-- implementación: PAE no tiene por qué saber qué es un legajo. Si queda vacío,
-- el informe dice «Registro».
--
-- Se cruza con el pendiente #74: qué representa una fila de MPI, MPE o MPJ es
-- una de las definiciones que la DNPYPI tiene que confirmar. Esto es el rótulo
-- que se muestra; la definición de fondo sigue abierta.

ALTER TABLE mir_c1_archivo_version
  ADD COLUMN que_es_una_fila varchar(80) NULL
  COMMENT 'Qué representa una fila del archivo, para titular la identificación en los informes.';

UPDATE mir_c1_archivo_version av JOIN mir_c1_archivo a ON a.id = av.archivo_id
   SET av.que_es_una_fila = 'Niña, niño o adolescente'
 WHERE a.codigo IN ('LEGAJO_NYA', 'MPI', 'MPE', 'MPJ_DAE');

UPDATE mir_c1_archivo_version av JOIN mir_c1_archivo a ON a.id = av.archivo_id
   SET av.que_es_una_fila = 'Dispositivo'
 WHERE a.codigo IN ('DISP_PENAL', 'DISP_SCP');
