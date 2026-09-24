# RUNAC — Registro Único Nacional de Medidas de Protección y Medidas Penales Juveniles

> **Estado: análisis avanzado, sistema funcionando fuera del repositorio.**
> Refleja el estado al **17 de septiembre de 2026**. Todavía no es una
> especificación cerrada: cuando el módulo se integre, esta documentación se
> actualiza y se incorpora al índice general.

Documentación funcional y técnica. Es el material que el equipo de desarrollo va
a necesitar para implementarlo, y el registro de por qué las cosas están
definidas como están.

**Área requirente:** Dirección Nacional de Promoción y Protección Integral (DNPYPI).
**Programa:** Federal de Protección de Niñez y Adolescencia (PFPNYA).

---

## Lo primero: RUNAC no es un sistema, es una implementación

```
MIR      el módulo. Define qué archivo se espera, lo recibe, lo valida,
         permite corregirlo y lo consolida. No sabe qué es una MPI.
RUNAC    una implementación: su definición, sus usuarios, sus datos.
```

MIR —**Módulo de Importaciones Recurrentes**— es un nombre interno, del equipo.
Hacia afuera cada implementación lleva el suyo.

La distinción no es de vocabulario: **la definición de cada archivo vive en
filas de la base, no en el código**. Cuando una provincia cambia una planilla se
cambian datos, no programas. Y cuando otro programa reciba novedades periódicas
de las jurisdicciones, el motor sirve sin tocarlo.

Eso ya tiene nombres: en la reunión del 27 de agosto de 2026 se planteó
incorporar **Decreto 5/2023**, **PAE** y **RENNYA**. Los dos primeros comparten
universo con RUNAC —el MPE— y hoy se manejan en Excel. En
[03-arquitectura.md](../mir/arquitectura.md) está qué de eso cubre el módulo tal como
está, y qué no.

Está desarrollado en **[03-arquitectura.md](../mir/arquitectura.md)**, junto con la
decisión que hay que tomar antes de integrar: hoy cada implementación tiene su
propia base, y SISOC es una sola.

---

## Cómo leer esta carpeta

| Documento | Qué responde | Para quién |
|---|---|---|
| [alcance.md](alcance.md) | Qué es RUNAC, qué entra y qué no | Todos |
| [analisis-de-las-planillas.md](analisis-de-las-planillas.md) | Propuestas de rediseño de los Excel que se reciben | DNPYPI |
| [alcance-primera-version.md](alcance-primera-version.md) | Qué entra en el MVP y qué queda para después | Todos |
| [hechos-y-supuestos.md](hechos-y-supuestos.md) | **Qué está confirmado y qué supusimos nosotros**, y qué fuente le gana a cuál | Todos |
| [decisiones/](decisiones/) | Registro de decisiones, con fecha y motivo | Desarrollo |
| [presentacion-runac.pdf](presentacion-runac.pdf) | La presentación de la implementación | Todos |

### Lo que NO está acá, porque es del módulo

La arquitectura, las tres capas, el circuito, el proceso de importación, los
tipos de regla, los roles y el esquema en SQL viven en **[../mir/](../mir/)**:
valen igual para cualquier implementación.

Sus ejemplos salen de RUNAC, que es la primera. Lo que describen no depende
de ella.

---

## El estado, en números

Verificados contra la definición cargada, el 17 de septiembre de 2026.

| | |
|---|---|
| Archivos que presenta cada jurisdicción | **5**, con **10 hojas** de datos |
| Columnas a completar | **365**, de las cuales **31** son obligatorias |
| Catálogos | **93**, con **797** valores |
| Reglas declaradas sobre un campo | **156**, en **10 tipos** |
| Tablas del modelo | 11 de definición · 9 de control · 13 receptoras · 23 consolidadas |

El sistema está navegable con los cuatro roles, el circuito completo de nueve
pasos, y datos de prueba de dos jurisdicciones en tres variantes: correctos, con
advertencias y con errores.

---

## Lo que falta, ordenado por lo que bloquea

1. **El cargador de la Capa 3.** La base consolidada existe como esquema y está
   vacía: no hay todavía nada que lleve los datos recibidos hasta ella. Es lo que
   falta para poder hablar de un producto en uso.
2. **La decisión de una base o varias**, antes de escribir las migraciones de
   integración. Ver [03](../mir/arquitectura.md).
3. **Las reglas que sólo la DNPYPI puede definir**: los límites numéricos, qué
   controles bloquean y cuáles avisan, y las respuestas pendientes que están
   marcadas en cada documento.
