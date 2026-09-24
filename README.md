# MIR — Módulo de Importaciones Recurrentes

**Esto no es un sistema para RUNAC. Es un motor, y RUNAC es lo primero que se
construyó con él.**

Hay una necesidad que se repite en toda la Secretaría: un programa tiene que
juntar información que le mandan otros, cada cierto tiempo, en planillas. Cada
vez que aparece, se construye un sistema nuevo desde cero. MIR es ese sistema,
construido una sola vez y parametrizable.

## Qué resuelve

| | |
|---|---|
| **Define** | qué archivo se espera: hojas, columnas, tipos, listas de valores y reglas |
| **Entrega** | la plantilla Excel generada desde esa definición, no escrita a mano |
| **Recibe** | el archivo completado, en períodos sucesivos |
| **Valida** | contra la definición, distinguiendo lo que avisa de lo que bloquea |
| **Devuelve** | el error en criollo, y el archivo propio con las celdas marcadas |
| **Corrige** | dentro del sistema, sin volver a mandar el Excel, con historial de quién cambió qué |
| **Circula** | carga → cierre → revisión → observaciones → subsanación → presentación formal |
| **Consolida** | en una base única, sabiendo de dónde vino cada dato |

**No es sólo importar.** Es un sistema de gestión: quien carga corrige adentro,
quien revisa observa, quien responde subsana, y todo queda registrado. El Excel
entra una vez; a partir de ahí se trabaja en el sistema.

## Quién presenta no es necesariamente una provincia

Hoy son las 24 jurisdicciones porque la primera implementación es federal. Pero
la pieza que reparte el trabajo es **genérica**: puede ser un organismo, un área,
un sector, un municipio, una delegación, una universidad. El módulo sólo necesita
saber que hay **entidades que presentan** y **períodos en los que presentan**.

Lo mismo vale para la normalización de los datos: un catálogo puede ser único
para todo el universo, o distinto por entidad. Quién es la entidad lo define la
implementación, no el motor.

## Por qué se puede reusar

La definición de cada archivo **vive en filas de la base de datos, no en el
código**. El motor la lee y la ejecuta: **no sabe qué es una MPI**.

No es una aspiración de diseño, es verificable: en todo el motor no hay una sola
regla de negocio de RUNAC. Se buscó —MPI, MPE, dispositivos, medida de
protección— y lo único que aparece es un ejemplo dentro de un comentario.

Por eso, cuando una planilla cambia, **se cambian datos y no programas**. Y
cuando aparezca el próximo programa que recibe novedades periódicas, el motor
sirve sin tocarlo.

## Las tres cosas y cómo se llaman

```
MIR        el módulo. Define, recibe, valida, corrige, circula y consolida.
RUNAC      una implementación: su definición, su base, sus usuarios.
```

Para los usuarios finales cada implementación lleva su propio nombre. «MIR» es
cómo le decimos al módulo entre nosotros.

### Las implementaciones

| | Programa | Estado |
|---|---|---|
| 1 | **RUNAC** — Registro Único Nacional de Medidas de Protección y Medidas Penales Juveniles | **Construida.** Es lo que se ve en este repositorio |
| 2 | **Decreto 5/2023** | Planteado el 27-08-2026. Mismo universo que el MPE, hoy en Excel |
| 3 | **PAE** — Programa de Acompañamiento para el Egreso | Planteado el 27-08-2026. Mismo universo que el MPE, hoy en Excel y PDF |
| — | **RENNYA** | En evaluación. **No encaja tal cual**: no participan las provincias, es gestión de expedientes caso por caso |

Que dos de los tres compartan universo con RUNAC —las mismas provincias, el mismo
período, la misma persona— es lo que vuelve razonable que compartan motor en vez
de construirse tres veces.

> **Falta el administrador de instancias**, y es deliberado: la prioridad es que
> RUNAC funcione. Hoy cada implementación tendría su propia base. Lo que va
> arriba —qué implementaciones existen, sus datos de conexión, qué tableros se
> habilitan a cada una— es una segunda etapa. Las dos condiciones para que siga
> siendo posible ya se cumplen: cada implementación tiene sus datos separados, y
> el motor no tiene lógica de ninguna.

> **Todavía no está en producción.** Trabaja con datos de prueba y le falta lo
> que exige el repositorio de SISOC: auditoría de accesos, control de alcance
> territorial y las validaciones de seguridad. Ver «Qué falta» más abajo.

## Levantarlo

Hace falta **Docker Desktop y nada más**. En Windows, Git Bash.

```bash
git clone https://github.com/dsocial118/Modulo-de-Importaciones-Recurrentes.git
```

```bash
cd Modulo-de-Importaciones-Recurrentes && bash entorno/preparar.sh
```

Y se abre en **http://localhost:8100**. Después, para levantarlo alcanza con
`docker compose up -d`.

Los detalles —usuarios, cómo probar que anda, qué hacer si no arranca— están en
**[docs/INSTALAR.md](docs/INSTALAR.md)**.

Hay una presentación por ámbito: la del módulo en
**[docs/mir/presentacion-mir.pdf](docs/mir/presentacion-mir.pdf)** y la de la
primera implementación en
**[docs/runac/presentacion-runac.pdf](docs/runac/presentacion-runac.pdf)**.

El repositorio trae todo lo necesario: la definición en el estado verificado,
las plantillas, los archivos de prueba y los guiones que explican cada
corrección. Ver **[entorno/LEEME.md](entorno/LEEME.md)**.

## Arquitectura, seguridad y operación

Lo que todavía no está definido o no está implementado a nivel de plataforma se
registra en **[docs/PENDIENTES_ARQUITECTURA.md](docs/PENDIENTES_ARQUITECTURA.md)**.

## Por dónde empezar a leer el código

| Archivo | Qué responde |
|---|---|
| `runac/services/motor/importar.py` | El motor: lee la definición de la Capa 1 y la ejecuta |
| `runac/services/importacion_service.py` | Cómo se importa y por qué una importación se rechaza entera |
| `runac/services/circuito_service.py` | Las transiciones: quién puede hacer qué y desde qué estado |
| `runac/permissions.py` | Los roles, y la diferencia entre menú y acceso |
| `runac/tests/` | Las reglas escritas como casos: 121 tests |

## Usuarios de prueba

La contraseña de todos es `runac`.

| Usuario | Rol | Jurisdicción |
|---|---|---|
| `operador` | Operador provincial | Chaco |
| `responsable` | Responsable provincial | Chaco |
| `revisor` | Revisor técnico nacional | — |
| `admin` | Administrador nacional | — |

Para recrearlos: `docker compose exec web python manage.py datos_iniciales`

---

## Primeras pruebas - se publicará con ngrok

**Siempre con contraseña.** La URL de ngrok es pública y se filtra sola: queda
en un mail reenviado, en un chat, en el historial de alguien.

```
ngrok http 8100 --basic-auth "runac:LA_CLAVE_QUE_ELIJAS"
```

Dos reglas, y no son negociables:

1. **MIR nunca recibe datos reales.** Sólo los mock, que tienen nombres
   inventados y documentos en un rango que no corresponde a personas. Si alguien
   quiere probar con un archivo real de una provincia, se hace en la máquina
   local, no por el túnel.
2. **El túnel va con `--basic-auth`.** Sin eso, cualquiera con la URL entra.

Los datos son inventados, pero lo que sí queda expuesto es **la estructura del
registro**: qué se le pregunta a una provincia sobre un chico con medida de
protección. No es secreto, pero tampoco es para que ande suelto.

---

## Qué hay hecho

| Pantalla | Estado |
|---|---|
| Entrar | ✅ |
| Inicio — estado de la presentación | ✅ |
| Descargar plantillas | ✅ |
| Cargar archivos, de a uno y con control de orden | ✅ |
| Resultado de la importación | ✅ |
| Detalle de errores, con filtros | ✅ |
| Descargar el archivo propio con las celdas marcadas | ✅ |
| Descargar la lista de errores en Excel | ✅ |
| Cierre de carga | ✅ |
| Revisión nacional y observaciones | ✅ |
| Subsanación | ✅ |
| Presentación y comprobante | ✅ |
| Registro del expediente GDE | ✅ |
| Estructura y campos de la Capa 1 | ✅ |
| Editar un dato dentro del sistema | ✅ |
| Consolidación a la Capa 3 | pendiente |
| Coincidencias de identidad | pendiente |
| Reportes y alertas | pendiente |

El circuito de nueve pasos del análisis funcional está implementado de punta a
punta, incluida la corrección de datos dentro del sistema.

**Cada rol ve y accede sólo a las secciones que le corresponden.** El menú se
arma según el rol, y el acceso se verifica también al entrar por dirección
directa: ocultar un enlace no es un permiso.

Lo que **todavía no** se verifica es la pertenencia territorial: el sistema
comprueba qué puede hacer un rol, no sobre qué jurisdicción puede hacerlo. La
jurisdicción llega como parámetro y se puede cambiar a mano. Es deliberado
—permite mostrar el circuito de cualquier provincia sin crear un usuario por
cada una— y es lo primero que se reemplaza al integrar, con el alcance
territorial de SISOC.

**Mobile first.** El diseño arranca en teléfono y suma tablet (768px) y
escritorio (992px). En pantalla chica las tablas se convierten en fichas, con el
nombre de cada dato; desde tablet vuelven a ser tablas, con el encabezado fijo al
desplazarse.

El circuito de nueve pasos —quién puede hacer qué y desde qué estado— está en
`runac/services/circuito_service.py`, en el diccionario `ACCIONES`. Es el único
lugar donde viven las transiciones: si una acción no está ahí, no existe.

La documentación funcional vive en **[docs/mir/](docs/mir/)** —el motor— y en una
carpeta por implementación:
**[docs/runac/](docs/runac/)** y **[docs/pae/](docs/pae/)**.

---

## Cómo está armado

Con **la misma estructura que las apps de SISOC**, a propósito: es lo que hace
que el código se pueda mudar en vez de reescribirlo. No es copiar la carpeta:
la tabla de más abajo dice qué se reusa y qué se tira, y el anexo técnico
enumera lo que hay que resolver antes —permisos con alcance territorial,
migraciones, trazabilidad y clasificación modular—.

**La lógica vive en `services/`; las vistas no deciden nada.**

```
runac/
├── models.py                       Generado con inspectdb. El sistema LEE el
│                                   modelo, no lo crea.
├── permissions.py                  Roles provisorios. Provisorio: SISOC
│                                   resuelve esto con iam/services.py.
├── views/                          Delgadas: piden al servicio y arman contexto.
│   ├── carga.py                    Cargar de a uno, resultado y detalle.
│   ├── circuito.py                 Acciones del circuito y descargas.
│   ├── edicion.py                  Corregir un dato ya importado.
│   ├── estructura.py               Qué espera la Capa 1.
│   ├── inicio.py
│   └── plantillas.py
├── services/
│   ├── importacion_service.py      Importar, estado del período, dependencias.
│   ├── circuito_service.py         Las transiciones del circuito. Están acá y
│   │                               en ningún otro lado.
│   ├── edicion_service.py          Edición de datos, con validación por tipo.
│   ├── informe_errores_service.py  Los dos informes que el operador se lleva.
│   └── motor/                      Python puro, sin Django. Es COPIA de la
│                                   skill `runac-capa1`: si se toca uno hay que
│                                   sincronizar el otro.
├── templates/runac/
├── tests/
└── management/commands/
```

**El motor está duplicado** entre este repositorio y la skill `runac-capa1`. Es
deuda conocida: al integrar el módulo a SISOC tiene que quedar en un solo lugar.

Versiones: **Django 5.2.16, Python 3.11.15, openpyxl 3.1.5, crispy-forms con
Bootstrap 5** — las mismas que `requirements/base.txt` del repositorio.

### Lo que se reusa y lo que se tira al integrar

| Pieza | Al integrar a SISOC |
|---|---|
| `services/motor/` | **Se reusa entero.** No depende de Django |
| `services/importacion_service.py` | **Se reusa** |
| `models.py` | **Se reusa**, pasando a migraciones |
| `views/` | Se reusan casi todas, por ser delgadas |
| `templates/` | Se adaptan al layout de SISOC |
| `permissions.py` | **Se tira.** SISOC tiene `iam/services.py` |
| Login y usuarios | **Se tira.** SISOC tiene los suyos |
| `config/` | **Se tira.** Es el proyecto contenedor |

### Los modelos son de sólo lectura

Todos llevan `managed = False`, que en Django significa que **las migraciones
no crean ni modifican esas tablas**: la estructura la produce la skill
`runac-capa1`, que es la que sabe leer los Excel y generar las tres capas.

No significa que los datos sean de sólo lectura: el sistema escribe en la
Capa 2 —importaciones, filas, correcciones— con SQL directo. Lo que no toca es
la definición de las tablas.

Para regenerarlos si cambia la base:

```
docker compose exec web python manage.py inspectdb <tablas> > runac/models.py
```

---

## Qué falta antes de pensar en integrarlo

**Decisiones funcionales**, que no son del equipo de desarrollo:

1. **Los datos personales repetidos** en las cuatro planillas nominales. Hay tres
   alternativas sobre la mesa y la elegida condiciona el rediseño de las
   planillas. Decide la DNPYPI.
2. **Anulación excepcional después de consolidar**, y si el responsable
   provincial puede hacer además lo del operador. Son los dos supuestos abiertos
   del circuito.

**Decisiones técnicas**, que sí son del equipo:

3. **La clasificación de RUNAC** según `docs/ia/MODULAR_BOUNDARIES.md` de SISOC.
   Es el paso 0 obligatorio de la norma del repositorio y todavía no se hizo.
4. **Si las personas de RUNAC son las de `ciudadanos`** o un registro propio
   vinculado. Hoy el sistema asume registro propio.
5. **Las dependencias entre archivos deberían declararse en la Capa 1**, no
   derivarse del orden de importación. Hoy `DISP_SCP` queda bloqueado por
   `DISP_PENAL` aunque sean independientes; las dependencias reales son
   MPE→residenciales y MPJ/DAE→penales.
6. **Unificar el motor**, hoy duplicado con la skill `runac-capa1`.

---

## Validación

El sistema usa **las mismas herramientas y versiones que SISOC**, con su misma
configuración (`.pylintrc`, `.djlintrc` y `pyproject.toml` son copia del
repositorio). Es lo que pide `AGENTS.md` en su sección *Validación*.

```
docker compose exec web black runac/ config/
docker compose exec web pylint runac/ config/
docker compose exec web djlint runac/templates/ --reformat
docker compose exec web pytest runac/tests/ -q
```

Los tests cubren las reglas del circuito —quién puede hacer qué, desde qué
estado—, la convención de nombres de las tablas receptoras y, en
`test_garantias.py`, las promesas que el módulo hace: que el cero es un dato,
que los números se leen igual en las dos pantallas, que ninguna vista queda sin
control de sección, que la completitud no la decide el navegador y que una
regla que el motor no sabe evaluar no pasa en silencio.

No tocan la base: no hace falta, porque lo que prueban es la decisión, no el
guardado.
