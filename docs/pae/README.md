# PAE — segunda implementación

**Programa de Acompañamiento para el Egreso.**

Estado: **estructura cargada y verificada, sin circuito armado.**

---

## Por qué está acá

Es la prueba de que MIR es un motor y no un sistema: **la planilla de PAE se
incorporó sin modificar una línea de código.** Se leyó el archivo, se cargó su
definición en la Capa 1 y el importador la procesó con las mismas reglas que
usa para la primera implementación.

Eso es lo que separa un módulo parametrizable de uno que promete serlo.

---

## Qué hay cargado

| | |
|---|---|
| Base | `mir_pae` |
| Archivos | 1 |
| Campos | 69 |
| Reglas aplicadas | 22 |

Las cifras se verifican con `bash entorno/estado.sh`, que las lee de la base.

**Las reglas salieron del instructivo del propio archivo**, no de una definición
funcional. La planilla trae una hoja con las instrucciones de llenado y de ahí
se tomaron los campos obligatorios, los valores admitidos y dos conceptos que el
módulo todavía no modela: **campo calculado** y **campo que completa el organismo
receptor**.

---

## Lo que falta

Todo lo que no sea la definición: el circuito, los usuarios, las plantillas y el
modelo consolidado. No se construyó porque **PAE todavía no es un proyecto**: se
usó para verificar que el motor sirve para más de una planilla.

Cuando sea un proyecto, lo que se hace es declarar su definición. El motor ya
está.

---

Ver [../mir/](../mir/) para la documentación del módulo.
