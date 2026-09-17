# MIR — Módulo de Importaciones Recurrentes

**Implementación: RUNAC** — Registro Único Nacional de Medidas de Protección y
Medidas Penales Juveniles.

MIR recibe planillas que las jurisdicciones mandan cada período, las valida
contra una definición declarada, permite corregirlas dentro del sistema y las
consolida en una base única.

**Lo que hace distinto:** la definición de cada archivo —hojas, columnas, tipos,
listas de valores y reglas de validación— vive en la base de datos, no en el
código. El motor la lee y la ejecuta: **no sabe qué es una MPI**. Cuando llega
una planilla nueva se cambian datos, no programas.

## Las tres cosas y cómo se llaman

```
MIR        el módulo. Define, recibe, valida, corrige y consolida.
RUNAC      una implementación: su definición, su base, sus usuarios.
           Mañana puede haber otras, cada una con su base.
```

Para los usuarios finales cada implementación lleva su propio nombre; «MIR» es
cómo le decimos al módulo entre nosotros.

> **Todavía no está en producción.** Trabaja con datos de prueba y le falta lo
> que exige el repositorio de SISOC: auditoría de accesos, control de alcance
> territorial y las validaciones de seguridad. Ver «Qué falta» más abajo.

## Levantarlo

Hace falta **Docker Desktop y nada más**. En Windows, Git Bash.

```bash
git clone https://github.com/danielc76/runac-prototipo.git
```

```bash
cd runac-prototipo && bash entorno/preparar.sh
```

Y se abre en **http://localhost:8100**. Después, para levantarlo alcanza con
`docker compose up -d`.

Los detalles —usuarios, cómo probar que anda, qué hacer si no arranca— están en
**[docs/INSTALAR.md](docs/INSTALAR.md)**.

El repositorio trae todo lo necesario: la definición en el estado verificado,
las plantillas, los archivos de prueba y los guiones que explican cada
corrección. Ver **[entorno/LEEME.md](entorno/LEEME.md)**.

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

Para recrearlos: `docker exec runac_proto_web python manage.py datos_iniciales`

---

## Publicarlo con ngrok

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

El análisis funcional completo del que sale este circuito no forma parte de este
repositorio: lo mantiene el responsable funcional en documentos aparte.

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
docker exec runac_proto_web python manage.py inspectdb <tablas> > runac/models.py
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
docker exec runac_proto_web black runac/ config/
docker exec runac_proto_web pylint runac/ config/
docker exec runac_proto_web djlint runac/templates/ --reformat
docker exec runac_proto_web pytest runac/tests/ -q
```

Los tests cubren las reglas del circuito —quién puede hacer qué, desde qué
estado—, la convención de nombres de las tablas receptoras y, en
`test_garantias.py`, las promesas que el módulo hace: que el cero es un dato,
que los números se leen igual en las dos pantallas, que ninguna vista queda sin
control de sección, que la completitud no la decide el navegador y que una
regla que el motor no sabe evaluar no pasa en silencio.

No tocan la base: no hace falta, porque lo que prueban es la decisión, no el
guardado.
