# Comparación reutilizable de identidad de personas

**Fecha:** 2 de octubre de 2026
**Estado:** diseño acordado; pendiente de implementación.
**Decide:** responsable funcional.

## Objetivo y decisión

Comparar la evidencia de identidad de dos registros de personas mediante un servicio reutilizable y configurable. RUNAC lo utilizará aportando sus datos y su política de comparación.

Se prefiere composición y configuración a una jerarquía de herencia: cada implementación utiliza el comparador sin tener que redefinir el algoritmo. No se introduce un comparador universal de cualquier entidad ni un paso obligatorio para todas las importaciones de MIR.

La ubicación definitiva del componente en MIR o como capacidad compartida de SISOC queda pendiente. Esta decisión no crea un servicio desplegable, una dependencia interdominio ni una nueva estructura de tablas.

## Entradas

- Dos registros de personas con los datos disponibles.
- Una política de comparación identificada y versionada: alcance de los identificadores y reglas de decisión.

Los identificadores se expresarán mediante tipo, ámbito y valor. Los datos personales podrán incluir nombres, apellidos y fecha de nacimiento. Domicilio y referencias familiares podrán incorporarse como evidencia complementaria cuando se definan su significado, origen y vigencia.

Un dato faltante no cuenta como diferencia; dos valores vacíos tampoco constituyen una coincidencia. La normalización para comparar conservará los valores originales.

## Aplicación en RUNAC

RUNAC adaptará sus campos al contrato común. El comparador no necesitará conocer medidas, MPJ, MPE ni la estructura de los legajos.

| Dato | Tratamiento acordado |
|---|---|
| idProvincia + id_Niño | Se reciben separados y se evalúan como una clave compuesta. id_Niño es único dentro de su provincia |
| DNI | Identificador propio, separado de otros documentos |
| CUIL | Identificador propio; su validación de ingreso no prueba por sí sola su correcta asignación al registro |
| Otro documento | Se compara por tipo, país emisor y número |
| Nombre, apellido y fecha de nacimiento | Evidencia para corroborar coincidencias o detectar contradicciones |
| Domicilio, idFamilia e idFamiliaAmpliada | Posible evidencia complementaria; alcance y reglas aún por definir |

El mismo id_Niño en provincias diferentes no es coincidencia ni contradicción. Una identidad consolidada podrá estar vinculada a varios identificadores provinciales; esa persistencia corresponde al circuito, no al comparador.

La coincidencia de provincia e id_Niño se contrastará con los demás datos disponibles antes de concluir identidad. La permanencia del identificador entre períodos y su eventual reutilización deberán quedar definidas en la política.

Compartir familia o domicilio no confirma identidad, y una diferencia no basta para descartarla. La coincidencia de DNI y CUIL no se tratará automáticamente como dos evidencias independientes.

## Salida y límites de la decisión

El resultado será uno de los siguientes:

- **Misma persona.**
- **Personas distintas.**
- **Sin resolver.**

Incluirá los motivos, coincidencias, contradicciones, datos faltantes y la regla y versión de política utilizadas.

Las condiciones concretas para confirmar o descartar siguen pendientes de definición y validación. No se considera suficiente un identificador diferente o un puntaje de similitud bajo para afirmar identidades distintas. La semejanza de nombres por sí sola tampoco confirma identidad.

Los puntajes de semejanza, si se utilizan, no se presentarán como probabilidades de identidad. La función distinguirá evidencia insuficiente de evidencia contradictoria.

## Responsabilidad del componente

El comparador recibe datos ya seleccionados; no consulta directamente la Capa 3, no modifica registros, no crea personas y no guarda vinculaciones. No depende de pantallas, roles ni solicitudes HTTP.

La búsqueda de candidatos, la revisión y la persistencia utilizarán este resultado mediante un circuito separado.

## Fuera de alcance y pendientes

Se definirán aparte:

- La búsqueda de candidatos en Capa 3 y en registros pendientes de consolidación.
- El uso de datos personales para buscar candidatos cuando falten claves, sin confundir admisión con confirmación de identidad.
- La pantalla de comparación, el rol revisor y las decisiones manuales.
- El alta, vinculación, desvinculación y tratamiento de candidatos múltiples.
- La forma definitiva de recibir el universo de personas y sus relaciones con las intervenciones.
- Las reglas de confirmación y exclusión, el significado de evidencia verificada y el tratamiento de contradicciones.
- Los umbrales de semejanza, la normalización y las pruebas con casos representativos.
- La ubicación técnica definitiva del componente y su contrato detallado.

La implementación deberá probar el comparador por separado del circuito, incluyendo faltantes, homónimos, identificadores de diferentes ámbitos y evidencia contradictoria.

## Referencia

- [Documentación del motor MIR](../../mir/README.md): separación entre el motor y las implementaciones; la Capa 3 pertenece a cada implementación.
