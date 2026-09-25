# El front del MIR pasa a React, con las reglas de SISOC

**Fecha:** 25 de septiembre de 2026
**Decide:** responsable funcional

---

## Qué se decidió

Que **todas las pantallas del MIR pasan a React**, con el diseño del equipo de
UI/UX, siguiendo sin cambios la norma que SISOC fijó el 24-09 para su propio
front (`docs/implementaciones/frontend_v2.md` en su repositorio,
secretarianaf/SISOC#2577).

## Por qué

- SISOC ya va hacia ahí, y un MIR distinto del resto se integraría peor.
- Las pantallas más pesadas del MIR —el detalle de hallazgos con filtros, la
  corrección en línea, la revisión— son las que más ganan con actualizar sólo
  lo que cambia, en lugar de recargar la página entera.
- La lógica ya está separada en `runac/services/`: el cambio es de pantallas y
  de API, no de motor.

## Cómo

- En la rama `front-react`, en su propia carpeta (un *worktree* de git), sin
  tocar `main` mientras no se apruebe: lo que se muestra a la contraparte sale
  de `main`.
- El front nuevo convive con el actual bajo `/v2/mir/` y se migra de a una
  pantalla. La primera fue Inicio, para validar la forma antes de seguir.

## Costo asumido

- Hace falta construir la API completa, que no existía. Sirve además para la
  carga entre sistemas prevista en el proyecto (`docs/mir/api.md`).
- El diseño de roles y circuito está abierto: algunas pantallas van a cambiar
  cuando se cierre. Se aceptó: cambiar una pantalla hecha cuesta menos que
  esperar para hacerla.

## Lo que cambió al hacer la primera pantalla

- **La API resuelve la entidad por el usuario**, no por la dirección. Las
  pantallas actuales todavía no: es el hallazgo #10 de la auditoría.
- **El avance cuenta sólo lo que entró.** La pantalla actual contaba como
  cargado un archivo con errores.
