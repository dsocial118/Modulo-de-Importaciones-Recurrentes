-- 35 · El nombre corto con el que las pantallas nombran cada archivo.
--
-- Las pantallas mostraban el código del archivo: DISP_PENAL, LEGAJO_NYA,
-- MPJ_DAE. El responsable funcional marcó el 27-09-2026 que no se entiende, y
-- pidió «Dispositivos penales», «Legajo de niños, niñas y adolescentes» y
-- «MPJ y DAE». El código no cambia: sigue en los nombres de los Excel que
-- suben las provincias y en las direcciones.
--
-- Va en la definición y no en el código porque el motor sirve para cualquier
-- implementación. Si queda vacío, se muestra el código.

ALTER TABLE mir_c1_archivo
  ADD COLUMN nombre_corto varchar(80) NULL
  COMMENT 'Cómo se nombra el archivo en las pantallas. Vacío: se muestra el código.';

UPDATE mir_c1_archivo SET nombre_corto = 'Dispositivos penales' WHERE codigo = 'DISP_PENAL';
UPDATE mir_c1_archivo SET nombre_corto = 'Dispositivos de cuidado residencial' WHERE codigo = 'DISP_SCP';
UPDATE mir_c1_archivo SET nombre_corto = 'Legajo de niños, niñas y adolescentes' WHERE codigo = 'LEGAJO_NYA';
UPDATE mir_c1_archivo SET nombre_corto = 'MPI' WHERE codigo = 'MPI';
UPDATE mir_c1_archivo SET nombre_corto = 'MPE' WHERE codigo = 'MPE';
UPDATE mir_c1_archivo SET nombre_corto = 'MPJ y DAE' WHERE codigo = 'MPJ_DAE';
