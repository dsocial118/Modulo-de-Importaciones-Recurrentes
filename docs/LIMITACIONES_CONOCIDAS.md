# Lo que este prototipo todavía no hace bien

**Para quien lo audite.** Esta página no defiende nada: lista lo que sabemos que
está mal, por qué está así y qué se hace con cada cosa. Si encontrás algo que no
figura acá, es un hallazgo genuino y queremos saberlo.

Última revisión: **24 de septiembre de 2026**.

---

## Antes de leer la lista: qué es y qué no es esto

**Es** un prototipo construido **deliberadamente afuera** de SISOC, para destrabar
decisiones funcionales con la contraparte mostrando algo que funciona. Esa
decisión está registrada y fechada: `docs/registro/decisiones/`.

**No es** un módulo listo para integrar. Al integrarse, lo que se reescribe está
escrito de antemano en el README, sección *«Lo que se reusa y lo que se tira al
integrar»*: usuarios, permisos, alcance territorial y auditoría pasan a ser los
de SISOC.

**Ya hubo una auditoría externa**, en septiembre de 2026: **51 hallazgos, 37
resueltos y verificados**. Los 14 que quedan son los de abajo. Ninguno está
abierto por descuido: cada uno tiene un motivo y un momento previsto.

**Cómo verificar el estado real** sin creerle a este documento:

```bash
bash entorno/estado.sh
```

Lee los contenedores, consulta las bases y lee git. No recuerda nada.

---

## Lo que arreglaríamos antes de cualquier exposición

Estos tres no esperan a la integración. Hoy no importan porque el prototipo
corre en una máquina, con datos ficticios y una sola persona usándolo. **Dejan de
no importar en el momento en que entre alguien más.**

### 1 · La jurisdicción viene en la URL y no se verifica

`jurisdiccion_de()` se usa sólo para el valor por defecto del selector. Nada
comprueba que la jurisdicción que llega en los parámetros sea la del usuario.

**Por qué está así:** el alcance territorial es de SISOC —`core/`— y el prototipo
no lo tiene. **Qué se hace:** al integrar, el control es el de SISOC. Mientras
tanto, si se expone a más de una persona, alcanza con verificar pertenencia
contra el usuario en cada operación.

### 2 · Configuración de desarrollo

`DEBUG` activo, clave por defecto, hosts abiertos. Deliberado para un prototipo
local, **inaceptable en cualquier entorno compartido**: un error muestra el
código y la configuración en pantalla.

### 3 · Borrado global de importaciones

Hay una herramienta de prueba que borra importaciones de **todas** las
jurisdicciones. Está restringida a administrador y **se excluye explícitamente de
la integración**.

---

## Lo que se resuelve al integrar, y por eso no se hizo antes

### 4 · El módulo no está clasificado según `MODULAR_BOUNDARIES.md`

Es el paso previo obligatorio del repositorio de SISOC: declarar dependencias,
propiedad de tablas y fachada pública. **No se hizo porque el prototipo vive
afuera**, y la clasificación describe un encaje que todavía no existe.

Es probablemente lo primero que esta auditoría va a querer ver. La ficha a medio
completar está en la base de conocimiento del proyecto, no en este repositorio.

### 5 · No hay migraciones

El esquema se crea con SQL directo —`entorno/sql/`, numerado y comentado— y los
modelos son `managed=False`. El SQL directo no queda auditado por los mecanismos
de Django.

**Por qué:** las tres capas se diseñaron y rediseñaron varias veces en tres
semanas; con migraciones, cada rediseño habría sido una cadena de parches. **Qué
se hace:** al integrar se generan las migraciones desde el esquema final, una
vez, y el SQL numerado queda como historia.

### 6 · `permissions.py` es provisorio

Usa nombres de grupos, no los permisos canónicos de SISOC. Lo declara el propio
archivo en su encabezado. Se reemplaza por el `iam/` de SISOC, incluido el
alcance territorial.

### 7 · El motor está duplicado

Vive en `runac/services/motor/` y también en la skill que genera la Capa 1. Las
dos copias se resincronizan a mano y ya divergieron una vez. **Al integrar queda
en un solo lugar.**

### 8 · No hay auditoría de accesos ni de descargas

Hay historial de ediciones —usuario, fecha, valor anterior y nuevo— pero no de
quién consultó ni quién descargó qué. El requerimiento lo pide. Es de SISOC:
`core/` ya tiene el mecanismo.

### 9 · Sin control de concurrencia en el circuito

Se lee el estado de una presentación y se escribe después, sin condición en la
escritura. Dos operaciones simultáneas pueden pisarse. Con una provincia
cargando no pasa; con veinticuatro, sí.

### 10 · Las definiciones usadas por un período se pueden modificar

La Capa 1 tiene versionado de estructura, pero nada impide editar una versión ya
usada para validar datos. Hay un control parcial —la definición sólo se cambia
con el período en preparación— que no cubre todos los caminos.

---

## Contradicciones del análisis funcional

No son del código: son del documento, y hay que corregirlo.

**11 ·** Se exige DNI único por hoja y a la vez se admiten varios eventos DAE de
la misma persona. Una de las dos reglas está mal y **depende de una definición de
la contraparte**, no nuestra.

**12 ·** El análisis describe dos representaciones paralelas del dato recibido;
el importador conserva una sola. Hay que decidir si se implementa la segunda o se
corrige el documento.

**13 ·** La regla de los campos de familia del MPE está descrita mal: la
obligatoriedad es condicional y el documento la presenta como absoluta.

**14 ·** Una observación sobre tipos de dato quedó en el análisis funcional y
corresponde al Excel de revisión de campos.

---

## Dos cosas que conviene mirar, aunque no sean hallazgos

**La obligatoriedad de un campo siempre frena el archivo**, y eso está escrito en
el código y no en la definición. Es la única regla del sistema donde no se puede
elegir entre advertir y bloquear: las otras diez lo declaran como dato. Hoy son
41 campos. Está pendiente decidir si la obligatoriedad pasa a ser una regla más.

**El motor no sabe nada de RUNAC.** Las reglas, los tipos, las listas y las
dependencias entre archivos son datos de la Capa 1, no código. Es lo que permitió
incorporar una planilla de otro programa (PAE) sin tocar una línea. **Si algo de
esta auditoría concluye que hay que meter lógica de negocio en el motor, conviene
discutirlo antes**: es la propiedad que hace que el módulo sirva para más de una
implementación.

---

## Dónde está lo demás

| Qué | Dónde |
|---|---|
| Qué hace el módulo y cómo está armado | `README.md` |
| Cómo levantarlo | `docs/INSTALAR.md` — dos comandos |
| El estado real, medido | `bash entorno/estado.sh` |
| Decisiones de diseño, fechadas | `docs/registro/decisiones/` |
| El análisis funcional completo | `docs/` (PDF) y la rama `runac` del repositorio de SISOC, en `docs/runac/` |
| Las pruebas | `runac/tests/` — 135, corren con `pytest` |

---

# Para infraestructura

Lo de arriba mira el código. Esta sección mira **dónde corre y qué necesita**,
que es otra conversación.

## Qué es, en términos de despliegue

| | |
|---|---|
| **Aplicación** | Python 3.11 · Django 5.2 · servidor de desarrollo |
| **Base** | MySQL 8.4, con `utf8mb4` **obligatorio** — sin eso los acentos entran mal y no se nota hasta mucho después |
| **Orquestación** | Docker Compose, dos servicios, autosuficiente |
| **Puertos** | la aplicación expone 8000 en el contenedor; la base, 3306 sólo por la red interna |
| **Persistencia** | un volumen para MySQL · `media/cargas` (los Excel que suben) · `media/informes` (los que genera) |

Se levanta con `bash entorno/preparar.sh` y no depende de ninguna red ni carpeta
externa al repositorio.

## Lo que hoy está mal y ustedes van a ver primero

**Corre con el servidor de desarrollo de Django** (`runserver`). No es un
servidor para servir a nadie: sin WSGI/ASGI adelante, un solo proceso atiende de
a uno.

**Las credenciales están en el `compose`**, con valores por defecto
(`runac_local`). Funciona porque es local; no hay ningún manejo de secretos.

**`DEBUG` activo, clave de Django por defecto, hosts abiertos.** Cualquier error
muestra la configuración en pantalla.

**No hay backup de nada.** Ni de la base, ni de los archivos que suben las
provincias.

**Los archivos que suben quedan en disco, sin cifrar.** Hoy son ficticios. El día
que sean reales, son datos de niñas, niños y adolescentes bajo medidas de
protección — el dato más sensible que maneja la Secretaría.

## Lo que necesitamos de ustedes

**1 · Cómo exponerlo para que la DNPYPI pruebe.** Necesitan entrar desde sus
máquinas, con datos ficticios, por un tiempo acotado. Nuestra idea era un túnel
con usuario y contraseña, pero **es su decisión, no la nuestra**: si tienen una
forma estándar, la usamos.

**2 · Cómo se despliega cuando se integre.** El plan es que MIR termine dentro
del monolito de SISOC, así que su infraestructura pasa a ser la de SISOC y casi
nada de este `compose` sobrevive. Conviene confirmar que esa lectura es correcta
antes de construir sobre ella.

**3 · Qué esperan de los datos reales.** Retención, backup, cifrado en reposo y
quién puede acceder al disco. Hoy no hay ninguna definición y no la vamos a
inventar nosotros.

**4 · Volumen.** No está medido. La planilla más grande de prueba no llega a
1 MB, pero no sabemos qué manda una provincia como Buenos Aires. Si tienen un
criterio de dimensionamiento, lo aplicamos.
