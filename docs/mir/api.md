# API del MIR

**Estado al 25-09-2026: hecha para el front; falta la carga entre sistemas.**
Existen todos los puntos de acceso que usan las pantallas en React. Este
documento separa siempre lo que **está hecho** de lo que **está previsto**.

---

## 1 · Qué es y para qué sirve

Una API HTTP con respuestas JSON, bajo **`/api/mir/`**. Cumple dos funciones:

1. **Es el único canal del front nuevo.** Las pantallas en React no leen la
   base ni dependen de plantillas de Django: todo lo que muestran y todo lo que
   hacen pasa por acá.
2. **Va a ser la vía de carga entre sistemas.** Además de subir una planilla,
   una entidad que presenta va a poder enviar la información directamente desde
   su propio sistema. Ver §5.

Las dos usan **el mismo motor y las mismas validaciones** que la carga por
planilla. No hay una segunda lógica de negocio.

## 2 · Reglas de diseño

Son las de la norma de SISOC para el front nuevo
(`docs/implementaciones/frontend_v2.md` en el repositorio de SISOC), para que
el módulo se pueda integrar sin reescribir la API.

| Regla | Cómo se cumple |
|---|---|
| La lógica vive en los services | Las vistas de la API (`runac/api_views.py`) son delgadas y llaman a los mismos `runac/services/` que las pantallas actuales |
| Autenticación del front | Sesión de Django en el mismo dominio, con CSRF. No hay tokens en el navegador |
| Permisos | Siempre en el servidor. Lo que el front oculte es comodidad, no seguridad |
| Contrato | Esquema OpenAPI generado con `drf-spectacular`; el front genera sus tipos desde ahí con `openapi-typescript`. Si el back cambia una respuesta, el front deja de compilar |
| Convenciones | Nombres en `snake_case`, paginación y errores estándar de Django REST Framework, fechas ISO 8601 |
| Archivos | `api_urls.py`, `api_views.py` y `api_serializers.py` dentro de la app, como en el resto de SISOC |

**Alcance de datos por usuario.** La API resuelve sobre qué entidad trabaja
cada pedido **a partir del usuario, no de la dirección**: un usuario de una
entidad sólo ve la suya aunque pida otra. Es el pendiente §4.1 de
`docs/PENDIENTES_ARQUITECTURA.md`, resuelto en la API nueva; las pantallas
actuales todavía no lo cumplen. Está cubierto por pruebas automáticas
(`runac/tests/test_api_front_v2.py`).

## 3 · Hecho

**Todo lo que usan las pantallas del front nuevo.** El detalle de cada punto de
acceso —qué recibe y qué devuelve— está en el esquema OpenAPI, en
`/api/esquema/` (requiere sesión) y en `frontends/packages/api/esquema.yaml`.

Todo va bajo `/api/mir/`:

| Área | Puntos de acceso |
|---|---|
| Sesión | `sesion/` |
| Inicio y período | `inicio/` · `periodos/<codigo>/estado/` |
| Plantillas | `plantillas/` · `plantillas/<periodo>/<archivo>/` · `plantillas/<periodo>/todas/` |
| Carga | `carga/` · `carga/<archivo>/` (subida) |
| Resultado y circuito | `resultado/` · `presentaciones/<id>/acciones/<accion>/` · `presentaciones/<id>/observaciones/` · `presentaciones/<id>/expediente/` · `presentaciones/<id>/comprobante/` · `observaciones/<id>/respuesta/` · `revision/` |
| Una importación | `importaciones/<id>/` · `importaciones/<id>/hallazgos/` (paginado) · `importaciones/<id>/errores.xlsx` · `importaciones/<id>/marcado.xlsx` · `importaciones/<id>/datos/` (ver y corregir) |
| Reglas | `reglas/` (ver y guardar) |
| Pruebas | `pruebas/armar-demo/` · `pruebas/borrar-importaciones/` |

**Lo que se pide por número —una presentación, una importación, una
observación— se controla contra la jurisdicción del usuario**, y lo ajeno da
404. En las pantallas actuales no: verificado el 25-09-2026, un operador de una
provincia ve el detalle, baja los errores y ve los datos de otra escribiendo la
dirección.

Y la pieza que los sirve al navegador: Django recibe `/v2/mir/` y lo reenvía al
servicio del front (`runac/views/front_v2.py`), con las mismas reglas que SISOC:
lista de módulos fija, sólo lectura, login obligatorio, 503 si el front no
responde.

## 4 · Pendiente

- **La carga entre sistemas**, en §5.
- **Un error del servicio de edición, que la API hereda:** al corregir un dato
  de un archivo que cruza con otro —por ejemplo, el MPI con el legajo—, la regla
  que verifica la referencia no puede leer el archivo referenciado y la
  corrección se rechaza. Pasa igual en las pantallas actuales. Visto el
  25-09-2026.

## 5 · Previsto para la carga entre sistemas

**Todavía no hay código.** Lo que sigue es la intención, para discutir con
infraestructura antes de construirlo.

- **Mismo circuito.** Lo que llega por API entra como una importación más: pasa
  por el control de estructura y las validaciones, y queda sujeto a revisión,
  observación y presentación igual que una planilla.
- **Qué se envía.** Las filas de un archivo del período en JSON, con los mismos
  campos que define la estructura. La forma exacta sale del esquema OpenAPI,
  que se genera desde la misma definición.
- **Autenticación entre sistemas.** No puede ser la sesión de un usuario. La
  propuesta es una **clave por entidad que presenta**, que la identifica y la
  limita a sus propios datos. SISOC ya usa `djangorestframework-api-key` para
  otros clientes, y conviene no sumar otro mecanismo.
- **Respuesta.** El mismo resultado que ve quien sube una planilla: si entró,
  cuántas filas y qué hallazgos, con el mismo detalle por fila y campo.
- **Reintentos seguros.** Un mismo envío repetido no puede duplicar una carga.
- **Registro.** Cada envío queda asociado a la clave que lo hizo.

## 6 · Preguntas para infraestructura

1. **Dónde vive el módulo**, que es la decisión abierta de
   `docs/PENDIENTES_ARQUITECTURA.md` §7: ¿módulo dentro de SISOC o servicio
   independiente? Define si la API queda bajo el dominio de SISOC o en uno propio.
2. **Autenticación entre sistemas:** ¿alcanza con claves por entidad, o se
   requiere otro mecanismo, por ejemplo certificados o un proveedor de identidad?
3. **Cifrado de los datos en tránsito** (pendiente #79): ¿basta con TLS de punta
   a punta, o se pide cifrado adicional del contenido?
4. **Exposición:** ¿la API para otros sistemas se publica en internet, por VPN
   o sólo entre redes del Estado?
5. **Límites:** tamaño máximo de un envío y frecuencia permitida por entidad.

---

Ver también: `docs/mir/front-v2.md` (el front nuevo) y
`docs/PENDIENTES_ARQUITECTURA.md` (lo que falta a nivel de plataforma).
