# API del MIR

**Estado al 25-09-2026: iniciada.** Existen la base y los dos primeros puntos de
acceso; el resto está planificado y se construye pantalla por pantalla, a
medida que el front pasa a React. Este documento separa siempre lo que **está
hecho** de lo que **está previsto**.

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

| Punto de acceso | Qué devuelve |
|---|---|
| `GET /api/mir/sesion/` | Quién está conectado, su rol, su entidad, qué puede hacer, las secciones de su menú y el token de CSRF |
| `GET /api/mir/inicio/` | Los períodos, el estado de la presentación de la entidad y, por archivo, su estado de carga, filas y hallazgos |
| `GET /api/esquema/` | El esquema OpenAPI completo. Requiere sesión |

Y la pieza que los sirve al navegador: Django recibe `/v2/mir/` y lo reenvía al
servicio del front (`runac/views/front_v2.py`), con las mismas reglas que SISOC:
lista de módulos fija, sólo lectura, login obligatorio, 503 si el front no
responde.

## 4 · Previsto para el front

Uno por pantalla, en el orden en que se migren:

| Pantalla | Puntos de acceso previstos |
|---|---|
| Plantillas | listar las del período · descargar una o todas |
| Carga | subir un archivo · ver qué necesita cargado antes |
| Resultado | resumen de la importación · detalle de hallazgos, paginado y con filtros · descargar el informe y el archivo marcado |
| Edición de datos | ver las filas de una importación · corregir un dato · justificar una advertencia |
| Circuito | cerrar y reabrir la carga · observar · responder · habilitar · presentar · registrar el expediente |
| Reglas | la estructura de cada archivo, con sus campos y reglas |
| Períodos | crear, abrir y cerrar períodos (depende del diseño de roles y períodos en curso) |

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
