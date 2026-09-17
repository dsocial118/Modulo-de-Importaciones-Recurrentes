# La portación — HECHA el 2026-09-17

> **Este documento ya se ejecutó.** Queda como registro de qué se hizo y por
> qué. Para instalar, ver **[INSTALAR.md](INSTALAR.md)**.
>
> Lo que decía que faltaba está hecho y verificado clonando en una carpeta
> limpia: el repositorio trae `entorno/` con la definición, las plantillas y los
> archivos de prueba; el `docker-compose.yml` levanta base y aplicación sin
> depender de nada externo; y `entorno/preparar.sh` arma todo con un comando.
>
> **Tres cosas aparecieron sólo al clonar en limpio**, y por eso están anotadas
> acá aunque el documento no las previera:
>
> 1. El volcado no puede excluir ninguna tabla. Al sacar `django_session`, como
>    el registro de migraciones venía en el mismo volcado diciendo que ya estaba
>    aplicada, `migrate` no la recreaba y la aplicación se caía al primer login.
> 2. La imagen de MySQL arranca dos veces —un servidor temporal para
>    inicializarse y después el definitivo— y entre los dos hay una ventana en la
>    que la base contesta y no está. El chequeo exige tres consultas seguidas por
>    TCP.
> 3. Los informes de importación son salida y estaban escribiéndose dentro de la
>    carpeta que se monta de sólo lectura. Van a `media/informes`.

---

# Hacer que el sistema corra en otra máquina

Encargo para quien lo implemente. Está escrito para que se pueda ejecutar sin
conocer el proyecto: lo que hay que saber está acá.

---

## 1. Por qué clonar el repositorio no alcanza hoy

El repositorio tiene la aplicación, pero **no tiene la base de datos ni sabe
armarla**. Al levantarlo en una máquina nueva falla por cuatro motivos, y
conviene entenderlos antes de tocar nada:

1. **`docker-compose.yml` no levanta MySQL.** Levanta sólo el contenedor web y
   lo engancha a una red `runac-c1_default` que crea *otro* proyecto de
   Docker Compose, que vive fuera del repositorio.
2. **Monta dos carpetas hermanas que no están versionadas**:
   `../analisis_datos/ModeloMySql/capa1` y `../Insumos`. Si no existen, el
   contenedor no arranca o arranca sin las plantillas.
3. **La base se carga a mano.** El esquema y la definición de la Capa 1 —los
   cinco archivos, sus once hojas, sus 368 columnas, sus catálogos y sus
   reglas— son un conjunto de `.sql` generados que hoy están en otra carpeta y
   se cargan corriendo un script con rutas absolutas de Windows.
4. **El orden de carga no es opcional y no se deduce de los nombres.** La
   Capa 2 referencia a la Capa 1, y el último archivo modifica tablas que crea
   el anteúltimo.

**El objetivo es que en la máquina nueva alcance con: clonar, un comando,
entrar al navegador.** Nada más.

---

## 2. Qué hay que construir

### 2.1 Traer al repositorio lo que hoy vive afuera

Crear la carpeta `entorno/` en la raíz del repositorio y copiar ahí estos
archivos, **sin modificarlos**. Las rutas de origen son de la máquina actual.

**`entorno/sql/`** — el esquema, desde
`C:\CNCPS\RUNAC\analisis_datos\ModeloMySql\sql\`:

| Archivo | Qué es |
|---|---|
| `01_schema.sql` | Capa 1: definición de archivos, hojas, campos, catálogos y reglas |
| `03_schema_capa2_control.sql` | Capa 2: períodos, presentaciones, importaciones, hallazgos |
| `05_schema_capa3.sql` | Capa 3: base consolidada (23 tablas) |
| `06_reglas_de_integridad.sql` | Reglas de integridad entre campos y entre archivos |

**`entorno/sql/datos/`** — la definición ya generada, desde
`C:\CNCPS\RUNAC\analisis_datos\ModeloMySql\capa1\sql\`:

| Archivo | Qué es |
|---|---|
| `02_DISP_PENAL.sql` | Capa 1 del archivo de dispositivos penales |
| `03_DISP_SCP.sql` | Capa 1 del archivo de dispositivos de cuidado |
| `04_MPI.sql` | Capa 1 de medidas de protección integral |
| `05_MPE.sql` | Capa 1 de medidas de protección excepcional |
| `06_MPJ_DAE.sql` | Capa 1 de medidas penales juveniles y admisión/egreso |
| `03_capa2_2026_T1.sql` | El período 2026_T1 y las tablas que reciben los datos |

Son unos 960 KB en total. Van al repositorio: son la definición del sistema, no
datos de nadie.

**`entorno/plantillas/`** — desde
`C:\CNCPS\RUNAC\analisis_datos\ModeloMySql\capa1\plantillas\`, los cinco
`*_2026_T1_MODELO.xlsx` (172 KB). **Hacen falta**: la pantalla «Plantillas del
período» los sirve para descargar.

**`entorno/archivos_de_prueba/`** — desde
`C:\CNCPS\RUNAC\analisis_datos\06_Archivos_de_prueba\` (2,8 MB). Son doce
carpetas: cuatro provincias por tres variantes (`_correctos`,
`_con_advertencias`, `_con_errores`). Datos inventados: nombres de una lista
corta y documentos de un rango que no corresponde a personas reales. Sin esto no
se puede probar nada en la máquina nueva.

**Lo que NO va al repositorio:** la carpeta `Insumos`, que tiene las planillas
originales de la contraparte. Sólo se usa para regenerar la Capa 1 desde cero
—cosa que la máquina nueva no necesita hacer— y no es material propio.

### 2.2 Un `docker-compose.yml` que levante todo

Reemplazar el actual por uno **autosuficiente**, con dos servicios:

- **`mysql`**: imagen `mysql:8.4`, base `runac`, usuario `root`, contraseña
  `runac_local`, `MYSQL_ROOT_PASSWORD` por variable de entorno con ese valor por
  omisión. Arranque con
  `--character-set-server=utf8mb4 --collation-server=utf8mb4_0900_ai_ci`
  (**no es opcional**: sin esto los acentos entran mal y quedan como `SÃ­`).
  `healthcheck` con `mysqladmin ping`. Volumen nombrado para los datos.
- **`web`**: el `Dockerfile` que ya está. `depends_on` de mysql con
  `condition: service_healthy` — **el web no puede arrancar antes que la base**,
  es la falla más frecuente al reiniciar la máquina. Puerto `8100:8000`.
  Variables de entorno: las mismas que hoy.

Montajes del servicio web:
- `.:/app` (como hoy)
- `./entorno:/trabajo/capa1:ro`

El segundo reemplaza al montaje de la carpeta hermana. Para que funcione,
`RUNAC_PLANTILLAS` tiene que resolver a `entorno/plantillas`: hoy
`config/settings.py:114` arma `RUNAC_CAPA1 / "plantillas"`, así que montando
`entorno/` en `/trabajo/capa1` queda bien sin tocar el código. **Verificarlo, no
suponerlo.**

Quitar la red externa `runac-c1_default` y el montaje de `../Insumos`.

### 2.3 Un comando que arme la base

Un script —`entorno/preparar.sh`, y que ande con Git Bash en Windows— que haga,
**en este orden exacto**:

1. `docker compose up -d` y esperar a que mysql esté `healthy`.
2. Cargar los `.sql` en este orden. **El orden importa**: cada uno necesita lo
   que crea el anterior.

   ```
   sql/01_schema.sql
   sql/datos/02_DISP_PENAL.sql
   sql/datos/03_DISP_SCP.sql
   sql/datos/04_MPI.sql
   sql/datos/05_MPE.sql
   sql/datos/06_MPJ_DAE.sql
   sql/03_schema_capa2_control.sql
   sql/datos/03_capa2_2026_T1.sql
   sql/05_schema_capa3.sql
   sql/06_reglas_de_integridad.sql
   ```

   Los dos últimos van al final a propósito: `06_reglas_de_integridad.sql`
   modifica columnas de las tablas que crea `03_capa2_2026_T1.sql`. Si se
   adelanta, falla.

   **Cada invocación de `mysql` tiene que llevar `--default-character-set=utf8mb4`.**
   Sin eso los acentos se cargan mal y el problema no se ve hasta mucho después.

3. `python manage.py migrate` en el contenedor web (las tablas de Django:
   usuarios, sesiones).
4. `python manage.py datos_iniciales` — crea los cuatro usuarios de prueba
   (`operador`, `responsable`, `revisor`, `admin`), todos con contraseña
   `runac`.

El script tiene que poder correrse dos veces seguidas sin romper nada, o avisar
claramente que la base ya está armada y que para rehacerla hay que borrar el
volumen.

### 2.4 Dejarlo escrito

Un `docs/INSTALAR.md` corto, para alguien que nunca vio el proyecto: requisitos
(Docker Desktop y nada más), los dos comandos, la dirección
`http://localhost:8100`, los cuatro usuarios con su contraseña, y qué hacer si
no arranca.

Y una línea en `README.md` que apunte ahí.

---

## 3. Cómo se sabe que quedó bien

No alcanza con que levante. Estas cinco comprobaciones, en una máquina donde el
proyecto nunca estuvo:

1. **Los tests pasan**: `docker compose exec web pytest runac/tests -q` → **115
   pasan**, ninguno falla.
2. **Las cuatro pantallas responden con los cuatro roles.** Entrar con cada
   usuario a `/`, `/cargar/`, `/resultado/`, `/reglas/` y `/plantillas/`. Todas
   dan 200, **salvo `revisor` en `/cargar/`, que tiene que dar 403**: el revisor
   nacional no importa archivos. Que dé 403 es la prueba de que el control de
   permisos está puesto, no una falla.
3. **La base tiene la definición completa.** En la pantalla de reglas tienen que
   verse los cinco archivos con sus once hojas. En la base: 368 campos.
4. **Los acentos están bien.** Mirar cualquier campo con tilde —por ejemplo el
   valor `Sí` del catálogo `si_no`—. Si aparece `SÃ­`, la carga se hizo sin
   `--default-character-set=utf8mb4` y hay que rehacerla desde cero, no
   arreglarla con un `UPDATE`.
5. **Un archivo limpio importa sin un solo hallazgo.** Entrar como `admin`,
   **abrir el período** (ver abajo), entrar como `operador`, elegir Chaco, y
   subir en este orden los cinco archivos de
   `entorno/archivos_de_prueba/Chaco_correctos/`: `DISP_PENAL`, `DISP_SCP`,
   `MPI`, `MPE`, `MPJ_DAE`. Los cinco tienen que quedar **VALIDA con cero
   bloqueantes y cero advertencias**. Después, los de `Chaco_con_advertencias`
   tienen que entrar igual pero con advertencias, y los de `Chaco_con_errores`
   tienen que quedar todos fallidos.

---

## 4. Cosas que van a hacer perder tiempo si no se saben

- **El período viene en «PREPARACIÓN» y en ese estado no se importa nada.** Es
  correcto: es la ventana de presentación, y la abre el nivel nacional. En la
  pantalla de inicio, entrando como `admin`, hay un botón «Abrir el período».
  Sin eso, todo intento de importar se rechaza con un mensaje que dice
  exactamente eso.
- **El nombre del archivo es restrictivo.** Tiene que empezar por el código del
  archivo y nombrar el período y la jurisdicción en curso:
  `MPI_2026_T1_Chaco.xlsx`. Se admite lo que venga después —el sufijo
  `_CON_ERRORES` de los archivos de prueba—, pero un archivo de otra provincia
  o de otro trimestre no entra. Si aparece un rechazo por nombre, es el sistema
  funcionando.
- **Hay dependencias entre archivos.** La nómina penal (`MPJ_DAE`) no se puede
  importar antes que los dispositivos penales (`DISP_PENAL`), porque los
  referencia. El sistema lo dice al intentarlo. Las demás no dependen de nada.
- **La importación es restrictiva.** Un solo error bloqueante y **no entra
  ninguna fila** del archivo. Un archivo que queda en cero filas con errores
  bloqueantes no es una falla de la instalación.
- **El web arrancando antes que MySQL** es la causa habitual de que el
  sistema «deje de andar» después de reiniciar la máquina. Por eso el
  `depends_on` con `service_healthy`. Si igual pasa:
  `docker restart runac_proto_web`.
- **Docker Desktop no arranca solo** en la máquina actual. Conviene revisarlo en
  la nueva.
- **`defusedxml` no se usa desde el código**, pero tiene que estar instalada:
  openpyxl la usa sola para leer los `.xlsx` sin quedar expuesto a un XML
  preparado. Ya está en el `Dockerfile`. Si alguien «limpia dependencias que no
  se importan», la saca y nadie se entera.

---

## 5. Lo que NO hay que hacer

- **No tocar la lógica.** Este encargo es de empaquetado. Si algo del código
  parece mal, anotarlo y consultarlo; no corregirlo de paso.
- **No reformatear archivos que no se tocan.** El repositorio usa `black`,
  `pylint`, `djlint` y `pytest` con las mismas versiones que SISOC, y los
  commits son chicos y revisables.
- **No agregar dependencias nuevas** sin decirlo. El objetivo es que la máquina
  nueva no necesite instalar nada más que Docker.
- **No subir la carpeta `Insumos`** ni ningún archivo con datos de personas. El
  sistema trabaja exclusivamente con datos inventados, y eso no se negocia.

---

## 6. Contexto mínimo del proyecto

Para que las decisiones de empaquetado no contradigan el diseño:

- **La lógica vive en los datos, no en el código.** El motor de importación lee
  la definición de la Capa 1 y la ejecuta: no sabe qué es un MPI. Por eso la
  base no es un accesorio del repositorio —es la mitad del sistema— y por eso
  los `.sql` de definición tienen que viajar con el código.
- **Tres capas.** Capa 1: qué archivos se esperan y qué reglas cumplen. Capa 2:
  lo que cada jurisdicción importó en cada período, con sus errores y sus
  correcciones. Capa 3: la base consolidada.
- **Es una implementación de MIR.** Trabaja sólo con datos inventados, muestra un cartel
  permanente que lo dice, y no está pensado para recibir datos reales. Lo que
  falta antes de integrarlo a SISOC está en el anexo técnico, no es un olvido.
