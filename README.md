# Prototipo de RUNAC

**Esto es un prototipo.** No es el módulo de SISOC y no está listo para
producción: no tiene auditoría de accesos, ni control de alcance territorial, ni
las validaciones de seguridad que exige el repositorio.

Sirve para que el equipo técnico de RUNAC pruebe el circuito con **datos de
prueba** y decida cómo tiene que funcionar. Recién después se integra a SISOC.

---

## Cómo se levanta

Desde esta carpeta:

```
docker compose -p runac-proto up -d
```

Y se abre en **http://localhost:8100**

Necesita que la base esté corriendo, porque el prototipo **lee** el modelo de
tres capas, no lo crea:

```
cd ../analisis_datos/ModeloMySql
docker compose -p runac-c1 up -d
```

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

1. **El prototipo nunca recibe datos reales.** Sólo los mock, que tienen nombres
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

**Cada rol ve y accede sólo a lo suyo.** El menú se arma según el rol, y el
acceso se verifica también al entrar por dirección directa: ocultar un enlace no
es un permiso.

**Mobile first.** El diseño arranca en teléfono y suma tablet (768px) y
escritorio (992px). En pantalla chica las tablas se convierten en fichas, con el
nombre de cada dato; desde tablet vuelven a ser tablas, con el encabezado fijo al
desplazarse.

El circuito completo, con todas las pantallas previstas, está en
`../analisis_funcional/08_Circuito_completo_y_pantallas.md`.

---

## Cómo está armado

Con **la misma estructura que las apps de SISOC**, a propósito: cuando esto se
integre, se copia la carpeta en vez de reescribirla.

```
runac/
├── models.py        generados con inspectdb, todos con managed = False
├── views/           delgadas: reciben, llaman al servicio, arman el contexto
├── services/
│   ├── importacion_service.py   la lógica
│   └── motor/                   el motor, Python puro, sin Django
├── permissions.py   provisorio: SISOC resuelve esto con iam/
├── templates/runac/
└── management/commands/
```

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

Todos llevan `managed = False`. **El prototipo no crea ni modifica el modelo: lo
lee.** La estructura la produce la skill `runac-capa1`, que es la que sabe leer
los Excel y generar las tres capas.

Para regenerarlos si cambia la base:

```
docker exec runac_proto_web python manage.py inspectdb <tablas> > runac/models.py
```

---

## Qué falta antes de pensar en integrarlo

1. Las decisiones funcionales pendientes — están listadas en
   `../analisis_funcional/08_Circuito_completo_y_pantallas.md`, parte 4.
2. La clasificación de RUNAC según `docs/ia/MODULAR_BOUNDARIES.md`. Es el paso 0
   obligatorio de la norma del repositorio.
3. Definir si las personas de RUNAC son las de `ciudadanos` o un registro propio.

---

## Validación

El prototipo usa **las mismas herramientas y versiones que SISOC**, con su misma
configuración (`.pylintrc`, `.djlintrc` y `pyproject.toml` son copia del
repositorio). Es lo que pide `AGENTS.md` en su sección *Validación*.

```
docker exec runac_proto_web black runac/ config/
docker exec runac_proto_web pylint runac/ config/
docker exec runac_proto_web djlint runac/templates/ --reformat
docker exec runac_proto_web pytest runac/tests/ -q
```

Los tests cubren las reglas del circuito —quién puede hacer qué, desde qué
estado— y la convención de nombres de las tablas receptoras. No tocan la base:
los modelos son `managed = False`, porque la estructura la define la Capa 1 y no
Django.

---

## Cómo está organizado

Sigue la forma que pide SISOC: **la lógica vive en `services/`, las vistas no
deciden nada.**

```
runac/
├── models.py                       Generado con inspectdb. El prototipo LEE el
│                                   modelo, no lo crea.
├── permissions.py                  Roles del prototipo. Provisorio: SISOC
│                                   resuelve esto con iam/services.py.
├── views/                          Delgadas: piden al servicio y arman contexto.
│   ├── carga.py                    Cargar de a uno, resultado y detalle.
│   ├── circuito.py                 Acciones del circuito y descargas.
│   ├── estructura.py               Qué espera la Capa 1.
│   ├── inicio.py
│   └── plantillas.py
├── services/
│   ├── importacion_service.py      Importar, estado del período, dependencias.
│   ├── circuito_service.py         Las transiciones del circuito. Están acá y
│   │                               en ningún otro lado.
│   ├── informe_errores_service.py  Los dos informes que el operador se lleva.
│   └── motor/                      Python puro, sin Django. Es COPIA de la
│                                   skill `runac-capa1`: si se toca uno hay que
│                                   sincronizar el otro.
├── templates/runac/
└── tests/
```

**El motor está duplicado** entre este prototipo y la skill `runac-capa1`. Es
deuda conocida: al integrar el módulo a SISOC tiene que quedar en un solo lugar.
