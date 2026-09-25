# entorno/

Todo lo que hace falta para levantar MIR con la implementación RUNAC en una
máquina donde el proyecto nunca estuvo.

| Qué | Para qué |
|---|---|
| `base_inicial.sql` | **La definición, en el estado verificado.** Es lo que carga `preparar.sh`: los archivos, sus campos, sus catálogos y sus reglas, más el nomenclador territorial, las jurisdicciones, el período y los usuarios de prueba. Sin importaciones. **No se edita a mano**: la genera `exportar_base.sh`, y su encabezado dice de qué base salió, cuándo y qué contiene. |
| `exportar_base.sh` | Regenera `base_inicial.sql` desde la base que se muestra (`runac_v2`). Se corre cada vez que esa base cambia, y se commitea junto con el cambio. |
| `_comun.sh` | Lo que comparten `estado.sh` y `exportar_base.sh`. No se corre solo. |
| `sql/` | Los guiones que llevaron la definición hasta ese estado. **No se cargan**: están para leer qué se corrigió y por qué, y para rehacerla desde los Excel originales. Cada uno lo explica en su encabezado. Llegan hasta el 19; los del 20 al 31 están en `analisis_datos\ModeloMySql\sql\`, fuera del repositorio. |
| `mir-v2/archivos_de_prueba/` | Dos jurisdicciones por tres variantes —correctos, con advertencias, con errores— para la definición vigente. Datos inventados. |
| `mir-v1/` | Lo mismo para la definición anterior. Se conserva para comparar. |
| `preparar.sh` | El comando que arma todo, en orden. |
| `estado.sh` | Muestra cómo está el sistema de verdad: qué base sirve cada puerto, cuántos campos y reglas tiene, y si hay desfasajes, incluido que `base_inicial.sql` haya quedado atrasada. **Las cifras de la definición se consultan acá, no en los documentos.** |

Las plantillas ya no se guardan en disco: el sistema las genera contra la base
en el momento de descargarlas.

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
