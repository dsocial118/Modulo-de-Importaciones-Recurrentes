# entorno/

Todo lo que hace falta para levantar MIR con la implementación RUNAC en una
máquina donde el proyecto nunca estuvo.

| Qué | Para qué |
|---|---|
| `base_inicial.sql` | **La definición, en el estado verificado.** Es lo que carga `preparar.sh`: los cinco archivos, sus diez hojas de datos, sus 365 campos, sus catálogos y sus reglas. |
| `sql/` | Los guiones que llevaron la definición hasta ese estado. **No se cargan**: están para leer qué se corrigió y por qué, y para rehacerla desde los Excel originales. Cada uno lo explica en su encabezado. |
| `plantillas/` | Los cinco Excel modelo que el sistema entrega a las provincias. La pantalla «Plantillas» los sirve desde acá. |
| `archivos_de_prueba/` | Dos jurisdicciones por tres variantes: correctos, con advertencias, con errores. Datos inventados. |
| `preparar.sh` | El comando que arma todo, en orden. |

## Por qué hay dos fuentes y cuál manda

**Manda `base_inicial.sql`.** Es el estado que se verificó importando los tres
juegos de archivos de prueba y corriendo los tests.

Los guiones de `sql/` son la historia: explican cada corrección, con el problema
que resolvía. Sirven para entender, y para rehacer la definición desde cero
leyendo los Excel de la contraparte — que es un trabajo que la máquina nueva no
necesita hacer.

Si algún día se regenera la definición desde los Excel, el orden de los guiones
**no es opcional**: cada uno modifica lo que crea el anterior.

## Los datos son inventados

Nombres de una lista corta y documentos de un rango que no corresponde a
personas reales. **Acá no hay datos de nadie**, y no los va a haber: para eso
está la instalación de producción.
