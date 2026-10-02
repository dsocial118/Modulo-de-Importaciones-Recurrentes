# MIR — Propuesta de seguridad, escalabilidad y confiabilidad

Este documento describe los controles y capacidades previstos para que el Módulo de Importaciones Recurrentes de SISOC reciba, procese, almacene y permita utilizar información de distintos organismos y sistemas, incluidos orígenes de gran volumen.

Es una propuesta de arquitectura objetivo. No acredita capacidades implementadas aún, ni reemplaza el registro del estado actual del módulo. Cada control deberá identificar su alcance, responsable, estado y evidencia de verificación.

El diseño será independiente del contenido importado. Cada implementación definirá la sensibilidad de su información, los accesos autorizados, el volumen esperado y las necesidades de conservación y disponibilidad.

La protección abarcará todo el ciclo: ingreso, almacenamiento, modificación autorizada, consulta, intercambio, exportación y eliminación y está sujeta a aprobación y mejora del área de Infraestructura.

## 1. Identidad y pertenencia a organismos

Cada persona accederá con una identidad propia, preferentemente mediante la autenticación institucional siguiendo los mecanismos de autenticación de SISOC.

Los sistemas conectados tendrán identidades técnicas diferenciadas de las cuentas personales, con permisos mínimos y posibilidad de revocación. Se contempla un segundo factor para accesos privilegiados o de mayor riesgo.

La autorización combinará identidad, función y pertenencia al organismo o entidad. Cada operación verificará quién la realiza, qué acción tiene permitida y sobre qué información puede actuar.

Los controles se aplicarán en el servidor y comprenderán consultas, modificaciones, archivos, descargas, exportaciones y tareas automáticas. Cambiar un identificador en una solicitud no deberá permitir acceder a información ajena.

Se aplicará denegación por defecto. La separación entre entidades podrá complementarse con aislamiento de bases, esquemas, almacenamiento o servicios cuando corresponda.

## 2. Comunicaciones protegidas

Se prevé utilizar TLS para cifrar las comunicaciones en todos los tramos de red, incluyendo usuarios, servicios, sistemas de origen o destino y bases de datos.

El diseño identificará dónde comienza y termina cada conexión cifrada y qué componentes pueden acceder al contenido descifrado para procesarlo. La protección no deberá limitarse a la entrada pública.

Para conexiones entre sistemas se contempla mTLS, cuando resulte necesario autenticar ambos extremos mediante certificados. Se definirán emisión, renovación, revocación y asociación de las identidades técnicas con sus permisos.

La capa de transporte estará separada de la lógica funcional. No se permitirá deshabilitar la verificación de certificados como solución habitual a problemas de conexión.

Una conexión cifrada y autenticada no reemplazará los controles de autorización sobre los datos.

## 3. Elección y configuración segura de la base de datos

La base contará con controles propios de seguridad, además de los implementados en MIR. Su configuración deberá limitar las consultas, las modificaciones y la administración.

La elección definitiva del motor de base de datos queda abierta, supeditada a los requerimientos de seguridad, auditoría, rendimiento, volumen, disponibilidad e integración que se definan, así como a las capacidades operativas y de soporte disponibles.

El motor utilizado en el prototipo no constituye una decisión definitiva para producción. La selección deberá respaldarse con una evaluación de cumplimiento y pruebas representativas de importación y consulta. Si requiere una migración, se contemplarán su compatibilidad, costo y riesgos.

Los requisitos se expresarán independientemente de PostgreSQL, MySQL u otro motor. Se evaluarán las capacidades efectivamente disponibles en la versión y edición consideradas, sus herramientas complementarias y las condiciones de soporte.

Se prevé:

- Mantener la base fuera de exposición pública y permitir conexiones únicamente desde servicios y equipos autorizados.
- Utilizar conexiones cifradas con verificación de certificados.
- Deshabilitar cuentas innecesarias y reemplazar credenciales predeterminadas.
- Evitar que la aplicación opere con privilegios de administrador o de propietario general.
- Otorgar permisos sobre los recursos estrictamente necesarios.
- Separar las credenciales de operación de las utilizadas para mantenimiento y cambios de estructura.
- Restringir la creación y modificación de tablas, permisos, funciones y mecanismos de auditoría.
- Mantener versiones soportadas, actualizaciones y revisiones de configuración.
- Controlar conexiones simultáneas, duración de consultas y operaciones que puedan bloquear el servicio.

La separación prevista será:

| Tipo de acceso | Alcance |
|---|---|
| Consulta | Lectura sobre conjuntos y campos autorizados |
| Importación | Escritura limitada a los recursos necesarios para la carga |
| Corrección funcional | Modificaciones mediante operaciones autorizadas y con historial |
| Publicación o consolidación | Actualización controlada de los resultados habilitados |
| Mantenimiento y cambios de estructura | Privilegios específicos, por procedimientos controlados |
| Administración excepcional | Acceso restringido, identificable y auditado |

Se evaluarán vistas, permisos por columna y políticas por fila cuando el motor y la implementación lo permitan. Estos mecanismos complementarán la autorización de la aplicación.

Los privilegios de administración absoluta deberán ser excepcionales. No se asumirá que una configuración de permisos impide actuar a quien controla completamente el servidor; se limitará ese acceso y se conservarán evidencias fuera de su ámbito operativo habitual.

## 4. Integridad y modificaciones autorizadas

El objetivo será impedir cambios no autorizados, no impedir las escrituras necesarias para importar, corregir o publicar información.

Se prevé que las modificaciones funcionales se realicen mediante operaciones definidas, con autorización, validación y registro del responsable. No se utilizará la edición directa de tablas como procedimiento habitual de trabajo.

Los controles comprenderán:

- Restricciones de integridad, unicidad y relaciones entre registros.
- Escrituras transaccionales en las unidades que deban confirmarse juntas.
- Control de concurrencia para evitar pérdida de cambios.
- Identificación de la operación que originó cada modificación.
- Historial suficiente para explicar cambios y efectuar correcciones controladas.
- Tratamiento explícito de eliminaciones y operaciones masivas.
- Consultas parametrizadas y validación de las solicitudes, evitando que los datos recibidos se interpreten como instrucciones SQL.

Las intervenciones directas de mantenimiento deberán identificar motivo, alcance, responsable y resultado. La conservación de valores anteriores se ajustará a su sensibilidad y a la política de retención.

## 5. Seguridad de consultas, descargas y exportaciones

La utilización de los datos tendrá el mismo nivel de atención que su importación.

Los servicios de consulta utilizarán permisos de lectura cuando no necesiten modificar información. Deberán verificar el alcance autorizado antes de devolver resultados y limitar campos o registros según la función del usuario o sistema.

Se prevé controlar:

- Búsquedas, listados y consultas de detalle.
- Consultas por API y herramientas de análisis autorizadas.
- Descargas y exportaciones masivas.
- Acceso a archivos de resultados y errores.
- Enlaces temporales y resultados generados en segundo plano.

Las exportaciones tendrán identificación, permisos, vigencia y registro de descarga. Cuando no sea necesario entregar todo el detalle, se evaluarán resultados agregados, campos reducidos o técnicas de desidentificación adecuadas.

Las consultas extensas deberán disponer de límites y mecanismos de ejecución compatibles con el servicio. La paginación, las exportaciones en segundo plano o la separación de recursos permitirán atender grandes volúmenes sin convertir una consulta en una degradación general.

## 6. Auditoría de accesos y consultas sobre la Capa 3

La auditoría de la información consolidada en la Capa 3 abarcará las consultas, además de las modificaciones y exportaciones.

Se prevé registrar:

- Usuario o servicio y organismo.
- Fecha, hora e identificador de operación.
- Tipo de acceso: búsqueda, listado, detalle, API o exportación.
- Recurso y alcance consultado.
- Resultado: autorizado, denegado, cancelado o fallido.
- Cantidad de registros entregados, cuando pueda determinarse.
- Referencias necesarias para reconstruir qué información se entregó, según su sensibilidad.

Se distinguirá una consulta solicitada de una respuesta efectivamente entregada. Una consulta registrada no demuestra por sí sola que el usuario recibió o leyó toda la información.

Para resultados masivos se evaluarán manifiestos, versiones de conjuntos u otras referencias que permitan reconstruir su alcance sin copiar la respuesta completa en la auditoría.

Se combinarán dos niveles:

| Nivel | Qué permite identificar |
|---|---|
| Aplicación | La persona o sistema que actúa, su organismo y la operación funcional |
| Base de datos | Las operaciones de las cuentas técnicas, los accesos directos y las intervenciones administrativas |

Ambos niveles deberán relacionarse mediante identificadores de operación cuando corresponda. Si la aplicación utiliza una cuenta técnica común para sus conexiones, los registros de la base no sustituirán la identificación del usuario en la aplicación.

La auditoría incluirá respuestas desde caché. Los accesos directos a bases se restringirán y tendrán controles complementarios.

Como la Capa 3 pertenece a cada implementación, deberá quedar definido qué componente registra sus consultas. Cuando MIR entregue información a otro sistema, registrará la entrega; el receptor será responsable de auditar su utilización posterior.

## 7. Protección del almacenamiento y credenciales

La protección de la base se apoyará en accesos restringidos, permisos mínimos, separación de funciones y auditoría, preservando el rendimiento de las importaciones y consultas.

No se prevé cifrado individual de campos como parte del diseño general. Cualquier requisito adicional de cifrado del almacenamiento deberá evaluarse según la sensibilidad de la información y su impacto medido sobre el rendimiento.

Los respaldos tendrán acceso restringido y protección acorde con su lugar de almacenamiento y traslado.

Las contraseñas, claves y certificados privados se mantendrán fuera del código y de los registros de actividad, con acceso limitado y mecanismos de renovación y revocación.

## 8. Recepción segura

El tratamiento de la información recibida contemplará que un envío puede ser incorrecto, malicioso o excesivo, incluso si proviene de una conexión autenticada.

Se prevén controles sobre:

- Autorización del emisor.
- Formatos, estructuras y versiones admitidas.
- Tamaño, cantidad de registros y frecuencia.
- Recursos y tiempo de procesamiento.
- Contenido activo o potencialmente malicioso.

Los archivos permanecerán fuera de ubicaciones públicas y se procesarán sin ejecutar macros ni contenido activo. Se incorporará análisis antimalware cuando corresponda.

Los envíos pendientes, rechazados y aceptados tendrán estados diferenciados. Los errores informados no expondrán credenciales, detalles internos innecesarios ni información ajena al emisor.

## 9. Importación de grandes volúmenes

Se prevé incorporar procesamiento por lotes y segmentación, aprovechando la capacidad del equipamiento dedicado para alcanzar el mayor rendimiento sostenible.

Las importaciones extensas no dependerán de una única solicitud del navegador ni de mantener toda la base en memoria.

La estrategia contemplará:

- Ejecución en segundo plano.
- Lectura progresiva.
- División por claves, particiones, períodos u otros criterios estables.
- Tamaños de lote configurables según registros, bytes y costo de procesamiento.
- Paralelismo ajustado a la capacidad del origen, la red y el destino.
- Pausa, consulta de avance y reanudación.
- Separación o reserva de recursos para las consultas habituales cuando sea necesario.

Cada ejecución y lote tendrán identificación persistente, alcance, definición aplicada, estado, intentos y cantidades procesadas.

La memoria se utilizará intensivamente cuando aporte rendimiento, evitando que su consumo crezca sin control con el tamaño total del conjunto. El paralelismo se aumentará mientras produzca mejoras comprobables.

## 10. Continuidad ante cortes y fallas

La importación deberá conservar el trabajo confirmado ante cortes de conexión, reinicios y fallas transitorias.

Se prevén puntos de recuperación persistentes. Un lote se considerará confirmado cuando sus datos y su estado de control queden guardados de forma consistente.

Cuando compartan una base transaccional, se buscará confirmar ambas escrituras juntas. Si intervienen componentes distintos, se definirá un mecanismo de conciliación que impida registrar avances inexistentes.

Los reintentos deberán ser idempotentes: repetir una operación aplicada no duplicará sus efectos.

| Situación | Comportamiento previsto |
|---|---|
| Corte antes de confirmar un lote | Reprocesar el lote pendiente |
| Datos confirmados y respuesta perdida | Reconocer lo aplicado y evitar duplicaciones |
| Reinicio del servicio | Recuperar el estado persistido |
| Falla transitoria | Reintentar con esperas progresivas y límites |
| Error de permisos o estructura | Detener el proceso afectado y solicitar corrección |
| Lote inválido | Aislarlo y aplicar la política de aceptación |

Las tareas interrumpidas podrán reasignarse sin que dos procesos apliquen simultáneamente el mismo lote.

Se conservará el trabajo confirmado. El lote que estaba en curso podrá requerir repetición; no se considerará recuperable aquello que todavía no había sido guardado.

## 11. Consistencia del origen y cargas incrementales

Dividir una extracción en lotes no garantiza su consistencia si el origen cambia durante el proceso.

Cada conector definirá una referencia estable para extraer y reanudar: exportación fija, instantánea, cursor con garantías conocidas o seguimiento de cambios.

La segmentación utilizará un orden estable y una continuación inequívoca. Se evitará depender únicamente de posiciones de página sobre conjuntos cambiantes.

Si la referencia vence o no puede recuperarse, el proceso detectará esa condición y aplicará una estrategia explícita de reinicio o conciliación.

Después de una carga inicial podrán incorporarse cargas incrementales cuando el origen permita identificar cambios confiablemente. Se contemplarán altas, modificaciones, bajas, cambios tardíos y conciliaciones.

Una fecha de actualización no se considerará suficiente sin conocer sus garantías. Tampoco se impondrán consultas o transacciones prolongadas que perjudiquen el sistema de origen.

## 12. Validación y publicación

El pipeline de verificaciones distinguirá recepción, validación, procesamiento y disponibilidad del resultado.

Confirmar un lote no significará que toda la importación esté aceptada ni que deba publicarse de inmediato.

Se contempla un área intermedia para verificar y conciliar antes de habilitar la información para consultas. Las reglas que relacionan registros o lotes deberán ejecutarse en el alcance correspondiente.

Cada implementación definirá si la aceptación es completa o parcial. Cuando sea parcial, quedará explícito qué se aceptó, qué se rechazó y qué resta resolver.

Cuando se requiera publicación completa, se evaluará preparar una nueva versión y habilitarla al finalizar, evitando una única transacción masiva durante toda la carga.

La conciliación verificará lotes faltantes, cantidades, duplicados y controles acordados. Los usuarios deberán poder conocer el estado y la vigencia de la información disponible.

## 13. Datos de origen, definiciones y trazabilidad del procesamiento

Se mantendrá la distinción entre datos crudos y datos elaborados o consolidados.

La trazabilidad relacionará origen, envío, lote, definición, validaciones, correcciones y resultado. No requerirá conservar indefinidamente todas las copias del contenido.

Las estructuras, reglas y plantillas declaradas como datos tendrán validación, permisos de modificación y versionado. La configuración no permitirá ejecutar código arbitrario.

Cada ejecución conservará la referencia a la versión aplicada. Esa versión no cambiará silenciosamente durante el procesamiento ni al reanudarlo.

Los hashes podrán apoyar comprobaciones de integridad, pero no reemplazarán cifrado, autenticación ni identificación de operaciones.

Las decisiones estructurales se documentarán mediante registros de decisión de arquitectura —ADR—.

## 14. Retención y eliminación

Se definirá una política de retención diferenciada.

| Información | Criterio previsto |
|---|---|
| Temporales | Conservación mínima y eliminación verificable |
| Lotes en recuperación | Conservación durante el plazo necesario para resolverlos |
| Datos aceptados | Plazo acorde con su finalidad y obligaciones |
| Exportaciones e informes | Acceso restringido y vigencia |
| Auditoría y controles de ejecución | Conservación para seguimiento e investigación |
| Respaldos | Calendario de conservación y recuperación |

Los plazos expresados en horas para temporales serán compatibles con las cargas extensas y sus ventanas de recuperación.

No se eliminarán fragmentos necesarios para reanudar un proceso activo ni la única copia válida antes de comprobar su almacenamiento duradero.

Se distinguirán recepción técnica, almacenamiento y aceptación funcional. Las políticas contemplarán también las copias presentes en cachés, exportaciones y respaldos.

## 15. Caché y contratos de integración

La caché se incorporará cuando aporte beneficios medidos. Respetará permisos, separación entre entidades, vigencia y auditoría.

Los cambios de permisos impedirán que respuestas almacenadas sigan otorgando acceso indebido. Se establecerá cómo invalidar resultados cuando cambien los datos publicados.

La separación del conector y de la seguridad del transporte permitirá adaptar credenciales y mecanismos de comunicación sin modificar las reglas del motor.

Cada interacción entre sistemas documentará:

- Origen, destino, dirección y finalidad.
- Información autorizada.
- Mecanismo de envío o extracción.
- Identidades y permisos.
- Volumen, frecuencia, segmentación y límites.
- Garantías de consistencia.
- Confirmaciones, reintentos y recuperación.
- Tratamiento de altas, modificaciones y bajas.
- Responsables operativos.

Recibir envíos y extraer información son modalidades distintas. Sus particularidades se documentarán por integración.

## 16. Operación, rendimiento y recuperación

Se prevén despliegues reproducibles, configuración separada del código, monitoreo y recuperación ante fallas transitorias.

La preparación para producción comprenderá entornos separados, pruebas con datos sintéticos, actualización de componentes y exclusión de depuración y herramientas destructivas de demostración.

Se medirán conjuntamente importación y utilización:

- Velocidad de lectura, transferencia, validación y escritura.
- Tiempos de respuesta de consultas y exportaciones.
- Memoria, almacenamiento, conexiones y bloqueos.
- Impacto sobre los sistemas de origen.
- Comportamiento con cargas y consultas simultáneas.
- Costo del cifrado, los permisos y la auditoría.
- Duración de lotes, reintentos y tiempo sin progreso.

El dimensionamiento incluirá datos, temporales, índices, registros transaccionales, auditoría y respaldos. Se ajustarán recursos y concurrencia según pruebas representativas.

Los respaldos estarán protegidos y se realizarán pruebas de restauración que incluyan los controles de ejecución necesarios para recuperar procesos.

Se definirán tiempos de recuperación, pérdida máxima tolerable y procedimientos de incidentes, revocación de accesos y retorno al servicio.

Los registros de auditoría tendrán protección frente a alteraciones, acceso restringido y supervisión. No incluirán credenciales ni contenido sensible innecesario. Su volumen no deberá provocar fallas silenciosas; se establecerá cómo actuar si el registro deja de estar disponible.

## 17. Implementación y verificación

Los controles de esta propuesta se incorporarán progresivamente. Su estado y los pendientes se mantendrán actualizados en la documentación del módulo.

Antes de utilizar cada integración con información real, se verificarán los permisos, la trazabilidad, la recuperación ante fallas y el rendimiento con volúmenes representativos. Un control se considerará completo cuando exista evidencia de su funcionamiento en el alcance previsto.

## Referencias técnicas

Estas referencias respaldan los criterios de la propuesta. No implican adoptar un producto, proveedor o motor determinado.

- [OWASP — Seguridad del transporte](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html): TLS, certificados y autenticación mutua.
- [OWASP — Autorización](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html): permisos mínimos y verificación de acceso a cada recurso.
- [OWASP — Recepción de archivos](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html): controles sobre los archivos recibidos.
- [OWASP — Registro de eventos](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html): auditoría y protección de los registros.
- [Microsoft — Patrón de reintentos](https://learn.microsoft.com/en-us/azure/architecture/patterns/retry): fallas transitorias, reintentos e idempotencia.
- [Microsoft — Cargas incrementales](https://learn.microsoft.com/en-us/azure/data-factory/tutorial-incremental-copy-overview): marcas de avance y seguimiento de cambios del origen.

## Documentación relacionada

- [Pendientes de arquitectura](../PENDIENTES_ARQUITECTURA.md): brechas y decisiones abiertas; este documento no las da por resueltas.
- [API de MIR](api.md): capacidades documentadas y propuesta de intercambio entre sistemas.
- [Arquitectura](arquitectura.md): alcance del motor y de sus implementaciones.
- [Actores y roles](actores-y-roles.md): responsabilidades y permisos funcionales.
