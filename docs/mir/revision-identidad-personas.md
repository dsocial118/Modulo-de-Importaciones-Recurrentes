# Revisión de identidad de personas

**Fecha:** 2 de octubre de 2026
**Estado:** diseño funcional acordado; pendiente de implementación.

## Objetivo y alcance

Permitir revisar visualmente dos registros cuya identidad quedó sin resolver. La pantalla explica la evidencia del comparador; no decide contando coincidencias ni reemplaza sus reglas.

Es reutilizable para comparar personas. Los campos y sus ámbitos dependen de la implementación. Para RUNAC, el registro entrante se contrasta con un candidato de SISOC y se utiliza ciudadano_id como referencia de identidad, según la [decisión de diseño](../registro/decisiones/2026-10-02-comparacion-identidad-personas.md).

El circuito completo, los permisos, el rol revisor y la búsqueda de candidatos quedan fuera de este documento.

## Cabecera y contexto

Título: **Revisar posible coincidencia**.

Mostrar el motivo concreto de la duda, por ejemplo: «Coincide el identificador provincial; hay diferencias en apellido y fecha de nacimiento».

Dos columnas claramente identificadas:
- **Registro recibido:** organismo, archivo o envío, referencia de origen y fecha disponible.
- **Persona registrada:** ciudadano_id y procedencia de los datos cuando se conozca.

No atribuir verificación a un dato por el solo hecho de estar registrado. Los identificadores provinciales del candidato sólo se muestran si una vinculación existente los aporta, sin suponer que son columnas de Ciudadano.

## Estados visuales

| Estado | Presentación | Significado |
|---|---|---|
| Coincide | Verde y etiqueta «Coincide» | Mismo valor, directamente o tras normalización |
| Parecido | Amarillo y etiqueta «Parecido» | Coincidencia parcial según una regla |
| Diferente | Rojo y etiqueta «Diferente» | Valores presentes, comparables y distintos |
| Sin dato | Gris y etiqueta «Sin dato» | Valor ausente en uno o ambos lados |

El color se acompaña siempre de texto o símbolo. Rojo no significa identidades distintas, amarillo no confirma identidad y gris no es discrepancia.

Si los ámbitos de un identificador difieren, mostrar una explicación neutral («Ámbitos distintos; no comparable»), sin forzar esa situación a «Diferente» o «Sin dato».

## Celdas y resaltado

- **Coincide:** una única celda que abarca las dos columnas de valores; no repetir el mismo texto.
- **Parecido:** dos celdas enfrentadas, resaltando en negrita las partes coincidentes.
- **Diferente:** dos celdas enfrentadas.
- **Sin dato:** dos celdas, con «No informado» donde corresponda.

Cuando la igualdad resulta de normalizar, mostrar un valor común de presentación y permitir consultar los originales. El valor presentado no sustituye ni modifica los datos almacenados.

En fechas, resaltar componentes completos (día, mes, año), no dígitos sueltos. No mostrar graduaciones por distancia entre años ni porcentajes de certeza.

## Dos modos de visualización

| Modo | Comportamiento |
|---|---|
| **Orden fijo**, predeterminado | Mantener siempre el mismo orden de campos |
| **Agrupar por coincidencia** | Arriba «Coinciden», con valores compartidos; debajo «Para revisar», con parecidos, diferentes y sin dato |

Orden inicial acordado: nombre, apellido, fecha de nacimiento, DNI, CUIL, otro documento e identificador de origen. En RUNAC, este último es provincia + id_Niño.

En el modo agrupado se mantiene ese mismo orden relativo dentro de cada bloque. Los identificadores no comparables se muestran explicados en «Para revisar».

Cambiar de modo sólo modifica la disposición: no oculta datos, no cambia el resultado ni produce decisiones.

Domicilio, referencias familiares y antecedentes podrán mostrarse en «Información adicional» cuando se definan y estén disponibles.

## Ejemplos ficticios

| Campo | Registro recibido | Candidato | Estado |
|---|---|---|---|
| Nombre | **María** | **María** Elena | Parecido |
| Fecha de nacimiento | **12/05/**2012 | **12/05/**2013 | Parecido: coinciden día y mes |
| Nombre | María | Luciana | Diferente |
| Fecha de nacimiento | 12/05/2012 | No informado | Sin dato |

Para «María Elena» y «María Elena», la interfaz muestra una sola celda «María Elena — Coincide». La tabla anterior sólo ejemplifica las filas que conservan dos valores.

Dos fechas completas con exactamente dos componentes iguales se muestran como parecidas, sin ponderar el tamaño de la diferencia del componente restante. La definición de semejanza de apellidos y otros casos de nombres sigue pendiente.

## Acciones previstas

| Acción | Alcance |
|---|---|
| **Es la misma persona** | Confirmar la vinculación con el candidato mostrado |
| **Son personas distintas** | Descartar esta pareja de candidatos, no todos los demás |
| **No puedo determinarlo** | Conservar la comparación pendiente |

La decisión conservará responsable, fecha, motivo y evidencia. El detalle de obligatoriedad del motivo y las confirmaciones se definirá con el circuito, especialmente cuando se confirme identidad pese a diferencias relevantes.

Descartar una pareja no crea automáticamente un ciudadano. Confirmar identidad tampoco sobrescribe nombres, documentos, nacimiento u otros valores. La selección o corrección de datos es una operación diferente.

## Pendientes y criterios de comprobación

Pendientes: rol autorizado, permisos, navegación entre candidatos, transiciones del circuito, reglas globales de identidad y tratamiento técnico de personas sin DNI.

La implementación deberá comprobar:
- Coincidencias en celdas compartidas y originales consultables.
- Dos valores visibles en parecidos, diferencias y faltantes.
- Resaltado de partes coincidentes sin depender sólo del color.
- Orden estable dentro de ambos modos y ausencia de pérdida de información.
- Separación entre decisión de identidad y modificación de datos.
- Mensajes de diferencia por campo que no afirmen por sí solos identidades diferentes.

No se implementa una pantalla ni se modifican datos mediante esta especificación.
