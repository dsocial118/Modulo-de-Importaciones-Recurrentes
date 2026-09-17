-- ===========================================================================
-- Capa 1 — Un campo con lista tiene que admitir su opción más larga
--
-- «Modalidad de cuidado» quedó declarado con un máximo de 20 caracteres, y su
-- lista correcta tiene un valor de 22: «Familia de acogimiento». Resultado: el
-- archivo traía un valor que la propia definición ofrece como válido, y el
-- importador lo rechazaba por largo.
--
-- El largo se infiere de los datos que había en la planilla al relevarla. Si
-- después cambia la lista asociada —como pasó al corregir a qué catálogo
-- apuntaba este campo— el largo puede quedar corto.
--
-- No es una decisión: es una contradicción de la definición consigo misma. Se
-- corrige en los dos lados, porque el largo vive en dos:
--
--   la definición   runac_c1_campo.longitud_maxima
--   la tabla        la columna varchar(N) que recibe el dato
--
-- Sólo AGRANDA. Achicar podría no entrar en datos ya cargados, y además nunca
-- es lo que hace falta acá.
-- ===========================================================================

SET NAMES utf8mb4;

-- 1. La definición: el máximo declarado nunca por debajo de su opción más larga.
UPDATE `runac_c1_campo` c
  JOIN (
    SELECT cat.id, MAX(CHAR_LENGTH(o.valor_esperado)) AS mas_largo
      FROM `runac_c1_catalogo` cat
      JOIN `runac_c1_catalogo_opcion` o ON o.catalogo_id = cat.id
     GROUP BY cat.id
  ) lista ON lista.id = c.catalogo_id
 SET c.`longitud_maxima` = lista.mas_largo
 WHERE c.`longitud_maxima` IS NOT NULL
   AND c.`longitud_maxima` < lista.mas_largo;

-- 2. La tabla receptora. Se nombra sólo la que hay que corregir hoy: el nombre
--    de estas tablas se deduce por convención y no se puede reconstruir en SQL,
--    igual que en el guion 06. Si aparecieran más, conviene hacerlo desde
--    `sincronizar_receptoras.py`, que sí sabe deducirlo.
ALTER TABLE `runac_c2_mpe_v1` MODIFY `modalidad_de_cuidado` varchar(22) NULL;
