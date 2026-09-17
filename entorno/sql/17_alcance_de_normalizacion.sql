-- ===========================================================================
-- Capa 1 — El alcance de normalización de un campo de texto
--
-- Aprobado por el responsable funcional el 2026-09-16.
--
-- QUÉ DECLARA
--
-- Un campo de texto sin lista puede tener tres destinos, y no es un sí/no:
--
--   SIN_NORMALIZAR  el texto queda como viene (un apellido, una observación)
--   UNIVERSO        un diccionario para todos    (un pueblo originario)
--   POR_ENTIDAD     un diccionario por cada una  (un programa provincial)
--
-- POR QUÉ EL ALCANCE NO ES COSMÉTICO
--
-- Decide si dos textos iguales son la misma cosa. «Hogar San José» en Chubut y
-- «Hogar San José» en Salta son DOS dispositivos distintos: con un diccionario
-- único, normalizarlos los fusiona y se pierde uno. «Mapuche», en cambio, es lo
-- mismo en las veinticuatro jurisdicciones, y tenerlo veinticuatro veces obliga
-- a decidir lo mismo veinticuatro veces.
--
-- La regla para elegir: ¿el nombre identifica a la cosa por sí solo, o sólo
-- dentro de su jurisdicción?
--
-- POR QUÉ SE LLAMA «POR_ENTIDAD» Y NO «POR_JURISDICCIÓN»
--
-- La entidad que particiona es de la instancia, no del campo. En RUNAC es la
-- jurisdicción; en otro programa pueden ser organismos, áreas o regiones. El
-- valor guardado es genérico y la instancia declara cuál es la suya. En el
-- Excel de supuestos que ve la contraparte se escribe con el nombre real que
-- tiene ahí —«por jurisdicción»—, porque quien lo completa no habla de
-- entidades.
--
-- No hace falta plomería para la partición: cada fila llega a su jurisdicción
-- por su importación, y la importación por su presentación.
--
-- QUÉ NO HACE
--
-- **Nada al importar.** El campo sigue admitiendo el texto como viene. Es una
-- declaración para después: cuando exista la pantalla que agrupa lo que llegó
-- y permite elegir el valor canónico.
--
-- Arranca en SIN_NORMALIZAR para todos. Lo que corresponda se propone en el
-- Excel de supuestos y lo confirma la contraparte: es un supuesto, no una
-- decisión nuestra.
-- ===========================================================================

SET NAMES utf8mb4;

ALTER TABLE `runac_c1_campo`
  ADD COLUMN `normalizacion` enum('SIN_NORMALIZAR','UNIVERSO','POR_ENTIDAD')
      NOT NULL DEFAULT 'SIN_NORMALIZAR'
      COMMENT 'Si los valores de este campo se unifican contra un diccionario, y con qué alcance. No afecta la importacion: es una declaracion para la normalizacion posterior.'
      AFTER `longitud_maxima`;

SELECT `normalizacion`, COUNT(*) AS campos
  FROM `runac_c1_campo`
 GROUP BY `normalizacion`;
