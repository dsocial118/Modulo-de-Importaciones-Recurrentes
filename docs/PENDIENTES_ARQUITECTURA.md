| Documentación del motor | `docs/mir/` |
| Documentación por implementación | `docs/runac/` · `docs/pae/` |# Pendientes de arquitectura

Estado del módulo respecto de las decisiones de arquitectura, seguridad y
operación que todavía no están tomadas o no están implementadas.

**Alcance de este documento.** Registra lo que falta a nivel de plataforma. No
trata el alcance funcional ni las definiciones de negocio, que se documentan
aparte.

Revisión: **24 de septiembre de 2026**.

---

## 1 · Qué es el módulo

MIR es un motor de importaciones recurrentes: recibe archivos estructurados de
terceros con periodicidad definida, valida su contenido contra una definición
declarada y los incorpora a un modelo consolidado.

**La definición es dato, no código.** Los archivos esperados, sus hojas, sus
columnas, los tipos, las listas de valores admitidos, las reglas de validación y
las dependencias entre archivos se declaran en tablas. El motor no contiene
lógica específica de ninguna implementación.

**Modelo en tres capas:**

| Capa | Contenido |
|---|---|
| 1 | La definición: qué se espera recibir y bajo qué reglas |
| 2 | Lo recibido de cada origen, tal como llegó, con su trazabilidad |
| 3 | El modelo consolidado, con las entidades resueltas y unificadas |

**Una implementación en producción de pruebas y una segunda verificada.** La
segunda se incorporó sin modificar el motor, lo que valida la parametrización.

---

## 2 · Estado del desarrollo

**Primera versión funcional (MVP), no productiva.** Se construyó fuera de la
plataforma, de forma deliberada y registrada, con el objetivo de validar
decisiones funcionales sobre algo ejecutable. Recorre el circuito completo y
está en uso para pruebas con el organismo requirente.

| | |
|---|---|
| Aplicación | Python 3.11 · Django 5.2 |
| Servidor | de desarrollo (`runserver`) — **no apto para servir** |
| Base | MySQL 8.4, `utf8mb4` requerido |
| Orquestación | Docker Compose, dos servicios, sin dependencias externas |
| Pruebas | 135 automatizadas |

**Auditoría externa de código realizada en septiembre de 2026:** 51 hallazgos,
37 resueltos y verificados. Los restantes se detallan en este documento.

---

## 3 · Seguridad

**No hay arquitectura de seguridad definida.** Es el pendiente principal y
condiciona cualquier exposición del módulo fuera de un entorno local.

### 3.1 · Transporte

Sin TLS. El módulo se sirve por HTTP. Los datos que procesa son de sensibilidad
alta y el requisito de cifrado en tránsito está planteado pero no implementado.

### 3.2 · Cifrado en reposo

No implementado, en ninguno de los tres niveles posibles:

| Nivel | Impacto en el código |
|---|---|
| Disco o volumen | Ninguno |
| Base de datos | Ninguno |
| Campo por campo | **Alto** — ver nota |

> **Nota sobre el cifrado a nivel campo.** La Capa 3 resuelve identidad
> comparando identificadores entre orígenes distintos. Un identificador cifrado
> con esquema no determinístico no admite comparación ni indexado, lo que
> invalida esa resolución. Si el requisito incluye este nivel, debe definirse
> antes del diseño de la Capa 3, e implica cifrado determinístico, tokenización
> o índices ciegos.

### 3.3 · Gestión de secretos

Credenciales de base de datos y clave de aplicación con valores por defecto,
declarados en el archivo de orquestación. Sin gestor de secretos.

### 3.4 · Configuración de entorno

`DEBUG` habilitado, hosts permitidos sin restringir. Ante un error, la
configuración queda expuesta en la respuesta.

### 3.5 · Archivos recibidos y generados

Los archivos que cargan los organismos y los informes que el módulo genera se
almacenan en el sistema de archivos sin cifrar y sin política de retención.

### 3.6 · Auditoría de accesos

Existe historial de modificaciones a nivel de registro —usuario, fecha, valor
anterior y valor nuevo—. **No existe registro de accesos ni de descargas.**

---

## 4 · Identidad y autorización

### 4.1 · Alcance de datos por usuario

El identificador del organismo que presenta llega por parámetro y **no se
verifica pertenencia** contra el usuario autenticado. El control existía como
responsabilidad de la plataforma, bajo el supuesto de integración al monolito.

### 4.2 · Modelo de permisos

Provisorio: resuelve por pertenencia a grupos y no por permisos canónicos de la
plataforma. Declarado como provisorio en el propio código.

### 4.3 · Herramientas administrativas sin acotar

Existe una operación de borrado masivo con alcance sobre todos los orígenes,
incorporada para pruebas. Debe excluirse de cualquier entorno compartido.

> **Estos tres pendientes dependen de una decisión que cambió de contexto.** Se
> asumieron resueltos por absorción al integrar al monolito. Si el módulo pasa a
> ser un servicio independiente —ver §7— dejan de resolverse solos y requieren
> diseño propio o consumo de servicios compartidos.

---

## 5 · Persistencia y esquema

### 5.1 · Sin migraciones

El esquema se crea mediante SQL versionado y numerado; los modelos del ORM están
declarados como no gestionados. El esquema no queda bajo los mecanismos de
control de la plataforma.

Fue una decisión de etapa: el modelo se rediseñó varias veces durante el
análisis. La generación de migraciones a partir del esquema final está prevista.

### 5.2 · Inmutabilidad de definiciones utilizadas

La Capa 1 versiona sus definiciones, pero no impide modificar una versión ya
utilizada para validar datos incorporados. Existe un control parcial por estado
del período que no cubre todos los caminos.

### 5.3 · Concurrencia

Las transiciones de estado leen y escriben sin condición en la escritura. Dos
operaciones simultáneas sobre el mismo objeto pueden perder una de las dos.

---

## 6 · Operación

| Pendiente | Situación |
|---|---|
| **Respaldo** | Inexistente, para base y para archivos |
| **Observabilidad** | Sin métricas ni trazas. Registro de aplicación sin centralizar |
| **Dimensionamiento** | No medido. El mayor archivo de prueba no supera 1 MB; el volumen real de los orígenes grandes se desconoce |
| **Servidor de aplicación** | Sin WSGI/ASGI. Un proceso atiende de a una petición |
| **Duplicación de código** | El motor de validación existe en dos copias que se sincronizan manualmente |

---

## 7 · Decisión abierta que condiciona lo anterior

El módulo se diseñó para integrarse a la plataforma como componente interno, y
varios de los pendientes de §4 y §5 se consideraron resueltos por esa vía.

Con la plataforma orientándose hacia un modelo híbrido con servicios
independientes, esa premisa está en revisión. **Mientras no se defina, seis de
los pendientes de este documento no tienen responsable asignable.**

**A definir:**

| | |
|---|---|
| 1 | Si el módulo es componente interno, servicio independiente, o ambos por etapas |
| 2 | Si la identidad y el alcance de datos se consumen como servicio compartido o se implementan localmente |
| 3 | Qué nivel de cifrado en reposo se exige (§3.2) |
| 4 | Política de retención, respaldo y acceso al almacenamiento |
| 5 | Mecanismo de exposición para pruebas con usuarios externos, con datos ficticios y por tiempo acotado |

---

## 8 · Verificación del estado

El estado real del entorno se obtiene del sistema, no de este documento:

```bash
bash entorno/estado.sh
```

Informa qué instancia sirve cada puerto, las cifras de cada definición cargada,
el estado del repositorio y los desfasajes detectados entre la definición y el
esquema.

| Referencia | Ubicación |
|---|---|
| Descripción del módulo | `README.md` |
| Instalación | `docs/INSTALAR.md` |
| Documentación del motor | `docs/mir/` |
| Documentación por implementación | `docs/runac/` · `docs/pae/` |
| Decisiones de diseño, fechadas | `docs/registro/decisiones/` |
| Pruebas | `runac/tests/` |
