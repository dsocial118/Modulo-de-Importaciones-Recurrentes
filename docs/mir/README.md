# MIR — el motor

Documentación del módulo, con independencia de qué se importe con él.

```
docs/mir/      el motor: vale para cualquier implementación   ← estás acá
docs/runac/    la primera implementación
docs/pae/      la segunda
```

---

## Por dónde entrar

| Documento | Qué responde |
|---|---|
| [arquitectura.md](arquitectura.md) | Por qué es un módulo reusable y no un sistema, y dónde termina |
| [modelo-de-datos.md](modelo-de-datos.md) | Las tres capas, y qué vive en cada una |
| [circuito.md](circuito.md) | Los nueve pasos, de la carga a la consolidación |
| [proceso-de-importacion.md](proceso-de-importacion.md) | Qué pasa con un archivo desde que se sube |
| [reglas-de-validacion.md](reglas-de-validacion.md) | Los tipos de regla y cómo se declaran |
| [actores-y-roles.md](actores-y-roles.md) | Quién hace qué, dentro y fuera del sistema |
| [esquema/](esquema/) | El modelo en SQL, capa por capa |
| [presentacion-mir.pdf](presentacion-mir.pdf) | La presentación del módulo, para mostrar sin entrar al código |

---

## Dos cosas para leer esto sin confundirse

**Los ejemplos salen de la primera implementación.** Donde dice «MPI», «medida»
o «dispositivo», es un ejemplo de RUNAC, no un concepto del módulo. El motor no
sabe qué son: los recibe como archivos, columnas y reglas declaradas.

**Las Capas 1 y 2 son del motor; la Capa 3 es de la implementación.** Las dos
primeras describen archivos, columnas, tipos y reglas, y sirven igual para
cualquier universo. La tercera modela las entidades del dominio y por lo tanto
es distinta en cada caso. Es la línea donde el motor termina.

---

## Quién presenta

El módulo sólo necesita saber que hay **entidades que presentan** y **períodos en
los que presentan**. Que esas entidades sean jurisdicciones, organismos, áreas,
municipios, delegaciones o universidades lo define la implementación.

Esta documentación dice «entidad» por ese motivo. La primera implementación las
llama provincias; la segunda, de otra manera.
