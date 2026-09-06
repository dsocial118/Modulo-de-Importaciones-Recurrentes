"""Modelos del prototipo de RUNAC.

Generados con `inspectdb` sobre la base que arma la skill `runac-capa1`. Todos
llevan `managed = False`: **el prototipo no crea ni modifica el modelo, lo lee**.
La estructura la define la Capa 1 y la generan los scripts de la skill.

Las tablas receptoras de la Capa 2 (`runac_c2_cru_*` y `runac_c2_dat_*`) no están
acá a propósito: se generan dinámicamente desde la Capa 1 y cambian con cada
período, así que se acceden con SQL, no con modelos.

Para regenerar este archivo:
    docker exec runac_proto_web python manage.py inspectdb <tablas> > runac/models.py
"""

from django.db import models


class RunacC1Archivo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    codigo = models.CharField(unique=True, max_length=30, db_comment='Código estable que identifica el tipo de archivo, por ejemplo MPI, MPE o MPJ_DAE.')
    nombre_esperado = models.CharField(max_length=255, db_comment='Nombre que debe tener el archivo dentro de la carpeta seleccionada.')
    titulo = models.CharField(max_length=255, blank=True, null=True, db_comment='Título que encabeza la planilla, tal como aparece en la primera fila del Excel.')
    subtitulo = models.CharField(max_length=255, blank=True, null=True, db_comment='Subtítulo o segunda línea del encabezado, cuando la planilla lo tiene.')
    descripcion = models.TextField(blank=True, null=True, db_comment='Descripción funcional de la información contenida en el archivo.')
    orden_importacion = models.IntegerField(unique=True, db_comment='Orden en que debe procesarse respecto de los demás archivos.')
    obligatorio = models.IntegerField(db_comment='Indica si la ausencia del archivo impide continuar con la importación.')

    class Meta:
        managed = False
        db_table = 'runac_c1_archivo'
        db_table_comment = 'Define los archivos que el importador debe buscar y procesar.'


class RunacC1Campo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    hoja = models.ForeignKey('RunacC1Hoja', models.DO_NOTHING, db_comment='Hoja a la que pertenece el campo.')
    dimension = models.ForeignKey('RunacC1Dimension', models.DO_NOTHING, blank=True, null=True, db_comment='Dimensión que agrupa el campo. Puede quedar vacío cuando el campo no pertenece a una dimensión.')
    catalogo = models.ForeignKey('RunacC1Catalogo', models.DO_NOTHING, blank=True, null=True, db_comment='Catálogo que contiene los valores permitidos para el campo. Puede quedar vacío cuando el campo no utiliza una lista cerrada.')
    nombre = models.CharField(max_length=100, db_comment='Nombre técnico y estable del campo, escrito en snake_case y sin tildes ni caracteres especiales.')
    titulo_esperado = models.CharField(max_length=255, db_comment='Título exacto que debe aparecer en la columna del archivo Excel.')
    orden = models.IntegerField(db_comment='Posición esperada de la columna dentro de la hoja.')
    tipo_dato = models.CharField(max_length=7, db_comment='Tipo de dato esperado para el campo.')
    longitud_maxima = models.IntegerField(blank=True, null=True, db_comment='Cantidad máxima de caracteres admitidos para campos de tipo TEXTO. Si queda vacío, la columna receptora se creará como TEXT.')
    obligatorio = models.IntegerField(db_comment='Indica si el campo debe contener un valor. Las obligatoriedades condicionales se definirán posteriormente mediante reglas.')
    ayuda = models.TextField(blank=True, null=True, db_comment='Texto explicativo para la confección o validación del campo.')

    class Meta:
        managed = False
        db_table = 'runac_c1_campo'
        unique_together = (('hoja', 'nombre'), ('hoja', 'orden'),)
        db_table_comment = 'Define los campos o columnas esperados dentro de cada hoja.'


class RunacC1CampoRegla(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    campo = models.ForeignKey(RunacC1Campo, models.DO_NOTHING, db_comment='Campo sobre el que se aplica la regla.')
    regla = models.ForeignKey('RunacC1Regla', models.DO_NOTHING, db_comment='Regla que debe aplicarse.')
    severidad = models.CharField(max_length=11, db_comment='Indica si el incumplimiento bloquea la importación o genera una advertencia.')

    class Meta:
        managed = False
        db_table = 'runac_c1_campo_regla'
        unique_together = (('campo', 'regla'),)
        db_table_comment = 'Relaciona los campos con las reglas que deben aplicarse durante la importación.'


class RunacC1Catalogo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    codigo = models.CharField(unique=True, max_length=100, db_comment='Código técnico y estable del catálogo, escrito en snake_case.')
    nombre = models.CharField(max_length=255, db_comment='Nombre descriptivo del catálogo.')
    descripcion = models.TextField(blank=True, null=True, db_comment='Explicación funcional de los valores contenidos en el catálogo.')

    class Meta:
        managed = False
        db_table = 'runac_c1_catalogo'
        db_table_comment = 'Define un conjunto cerrado de valores admitidos para uno o más campos.'


class RunacC1CatalogoOpcion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    catalogo = models.ForeignKey(RunacC1Catalogo, models.DO_NOTHING, db_comment='Catálogo al que pertenece la opción.')
    codigo = models.CharField(max_length=100, db_comment='Código técnico y estable de la opción.')
    valor_esperado = models.CharField(max_length=255, db_comment='Texto que debe encontrarse en el archivo Excel.')
    descripcion = models.TextField(blank=True, null=True, db_comment='Explicación funcional de la opción.')
    orden = models.IntegerField(db_comment='Orden de presentación de la opción dentro del catálogo.')
    activo = models.IntegerField(db_comment='Indica si la opción se encuentra disponible para nuevas importaciones.')

    class Meta:
        managed = False
        db_table = 'runac_c1_catalogo_opcion'
        unique_together = (('catalogo', 'codigo'), ('catalogo', 'valor_esperado'), ('catalogo', 'orden'),)
        db_table_comment = 'Define cada valor permitido dentro de un catálogo.'


class RunacC1Dimension(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    hoja = models.ForeignKey('RunacC1Hoja', models.DO_NOTHING, db_comment='Hoja a la que pertenece la dimensión.')
    nombre_esperado = models.CharField(max_length=255, db_comment='Texto que debe aparecer en la celda combinada ubicada sobre los títulos de las columnas.')
    descripcion = models.TextField(blank=True, null=True, db_comment='Descripción funcional del grupo de campos representado por la dimensión.')
    orden = models.IntegerField(db_comment='Orden en que aparece la dimensión dentro de la hoja.')

    class Meta:
        managed = False
        db_table = 'runac_c1_dimension'
        unique_together = (('hoja', 'orden'),)
        db_table_comment = 'Define los encabezados que agrupan conjuntos de campos dentro de una hoja.'


class RunacC1Hoja(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    archivo = models.ForeignKey(RunacC1Archivo, models.DO_NOTHING, db_comment='Archivo al que pertenece la hoja.')
    nombre_esperado = models.CharField(max_length=255, db_comment='Nombre exacto que debe tener la hoja dentro del archivo Excel.')
    descripcion = models.TextField(blank=True, null=True, db_comment='Descripción funcional de la información contenida en la hoja.')
    orden_procesamiento = models.IntegerField(db_comment='Orden en que debe procesarse dentro del archivo.')
    fila_encabezados = models.IntegerField(db_comment='Fila donde se encuentran los nombres de los campos. Los datos comienzan en la fila siguiente.')
    obligatoria = models.IntegerField(db_comment='Indica si la ausencia de la hoja impide continuar con la importación.')

    class Meta:
        managed = False
        db_table = 'runac_c1_hoja'
        unique_together = (('archivo', 'nombre_esperado'), ('archivo', 'orden_procesamiento'),)
        db_table_comment = 'Define las hojas que deben encontrarse dentro de cada archivo.'


class RunacC1Regla(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    tipo_regla = models.ForeignKey('RunacC1TipoRegla', models.DO_NOTHING, db_comment='Tipo de validación que debe ejecutar el importador.')
    nombre = models.CharField(unique=True, max_length=255, db_comment='Nombre técnico y estable que identifica la regla concreta.')
    descripcion = models.TextField(blank=True, null=True, db_comment='Explicación funcional de la validación.')
    parametros = models.JSONField(blank=True, null=True, db_comment='Valores necesarios para ejecutar la regla, de acuerdo con los parámetros definidos para su tipo.')

    class Meta:
        managed = False
        db_table = 'runac_c1_regla'
        db_table_comment = 'Define una validación concreta que puede reutilizarse en distintos campos.'


class RunacC1TipoRegla(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    nombre = models.CharField(unique=True, max_length=100, db_comment='Nombre técnico y estable del tipo de regla, por ejemplo RANGO, OBLIGATORIO_SI o EJECUTAR_FUNCION.')
    descripcion = models.TextField(blank=True, null=True, db_comment='Explica el comportamiento general de la validación.')

    class Meta:
        managed = False
        db_table = 'runac_c1_tipo_regla'
        db_table_comment = 'Define los tipos de validación que el importador sabe ejecutar.'


class RunacC1TipoReglaParametro(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    tipo_regla = models.ForeignKey(RunacC1TipoRegla, models.DO_NOTHING, db_comment='Tipo de regla al que pertenece el parámetro.')
    nombre = models.CharField(max_length=100, db_comment='Nombre técnico del parámetro dentro del JSON, por ejemplo minimo, maximo, operador o campo_condicion.')
    tipo_parametro = models.CharField(max_length=8, db_comment='Tipo de valor que debe contener el parámetro.')
    obligatorio = models.IntegerField(db_comment='Indica si el parámetro debe estar presente para configurar la regla.')
    orden = models.IntegerField(db_comment='Orden de presentación del parámetro.')
    descripcion = models.TextField(blank=True, null=True, db_comment='Explica el significado y uso del parámetro.')

    class Meta:
        managed = False
        db_table = 'runac_c1_tipo_regla_parametro'
        unique_together = (('tipo_regla', 'nombre'), ('tipo_regla', 'orden'),)
        db_table_comment = 'Define los parámetros esperados por cada tipo de regla.'


class RunacC2Edicion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    importacion = models.ForeignKey('RunacC2Importacion', models.DO_NOTHING, db_comment='Importación cuyos datos se editaron.')
    numero_fila = models.IntegerField(db_comment='Fila editada.')
    campo = models.ForeignKey(RunacC1Campo, models.DO_NOTHING, db_comment='Campo editado.')
    observacion = models.ForeignKey('RunacC2Observacion', models.DO_NOTHING, blank=True, null=True, db_comment='Observación que motivó el cambio, cuando corresponde.')
    valor_anterior = models.TextField(blank=True, null=True, db_comment='Contenido previo al cambio.')
    valor_nuevo = models.TextField(blank=True, null=True, db_comment='Contenido posterior al cambio.')
    motivo = models.TextField(blank=True, null=True, db_comment='Justificación del cambio.')
    fecha = models.DateTimeField(db_comment='Momento del cambio.')
    usuario = models.CharField(max_length=150, db_comment='Usuario que realizó el cambio.')

    class Meta:
        managed = False
        db_table = 'runac_c2_edicion'
        db_table_comment = 'Historial de cambios sobre los datos importados. La tabla cruda nunca se pisa: conserva lo que la provincia mandó.'


class RunacC2Estructura(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    periodo = models.ForeignKey('RunacC2Periodo', models.DO_NOTHING, db_comment='Período para el que rige esta estructura.')
    archivo = models.ForeignKey(RunacC1Archivo, models.DO_NOTHING, db_comment='Archivo de Capa 1 cuya estructura se congela.')
    hoja = models.ForeignKey(RunacC1Hoja, models.DO_NOTHING, db_comment='Hoja concreta del archivo. Un archivo con varias hojas tiene una estructura por hoja, porque cada una tiene su propia tabla receptora.')
    version = models.IntegerField(db_comment='Número de versión de la estructura de ese archivo.')
    tabla_cruda = models.CharField(max_length=64, db_comment='Nombre de la tabla generada que recibe los datos tal como vienen del Excel, todo en texto.')
    tabla_tipada = models.CharField(max_length=64, db_comment='Nombre de la tabla generada que recibe los datos ya convertidos a sus tipos.')
    huella_estructura = models.CharField(max_length=40, db_comment='Huella de la definición de Capa 1 usada. Si cambia, hace falta una versión nueva.')
    creada_el = models.DateTimeField(db_comment='Momento en que se generaron las tablas.')

    class Meta:
        managed = False
        db_table = 'runac_c2_estructura'
        unique_together = (('periodo', 'hoja', 'version'),)
        db_table_comment = 'Vincula un período con la versión de estructura vigente y con las tablas generadas para recibirla. Un cambio en Capa 1 obliga a una versión nueva, sin tocar los datos ya importados.'


class RunacC2Hallazgo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    importacion = models.ForeignKey('RunacC2Importacion', models.DO_NOTHING, db_comment='Importación en la que se detectó.')
    campo = models.ForeignKey(RunacC1Campo, models.DO_NOTHING, blank=True, null=True, db_comment='Campo de Capa 1 afectado. Queda vacío cuando el hallazgo no es de un campo puntual.')
    regla = models.ForeignKey(RunacC1Regla, models.DO_NOTHING, blank=True, null=True, db_comment='Regla de Capa 1 que no se cumplió. Queda vacío en las validaciones de estructura.')
    codigo = models.CharField(max_length=50, db_comment='Código estable del hallazgo, para poder contarlos y filtrarlos.')
    severidad = models.CharField(max_length=11, db_comment='BLOQUEANTE impide presentar. ADVERTENCIA permite continuar pero requiere revisión.')
    nombre_hoja = models.CharField(max_length=255, blank=True, null=True, db_comment='Hoja del Excel donde está el problema.')
    numero_fila = models.IntegerField(blank=True, null=True, db_comment='Fila del Excel, tal como la ve el usuario.')
    columna = models.CharField(max_length=10, blank=True, null=True, db_comment='Letra de la columna en el Excel.')
    nombre_campo = models.CharField(max_length=255, blank=True, null=True, db_comment='Título de la columna, para que el informe se entienda sin unir tablas.')
    valor_encontrado = models.TextField(blank=True, null=True, db_comment='El valor que provocó el hallazgo, tal como vino.')
    descripcion = models.TextField(db_comment='Explicación en lenguaje claro: qué está mal y qué hay que corregir.')

    class Meta:
        managed = False
        db_table = 'runac_c2_hallazgo'
        db_table_comment = 'Cada incumplimiento detectado, con archivo, hoja, fila, columna, código, severidad y descripción, como pide el circuito de importación.'


class RunacC2Importacion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    presentacion = models.ForeignKey('RunacC2Presentacion', models.DO_NOTHING, db_comment='Presentación a la que pertenece este intento.')
    estructura = models.ForeignKey(RunacC2Estructura, models.DO_NOTHING, blank=True, null=True, db_comment='Estructura contra la que se validó. Queda vacío cuando el archivo no se pudo identificar.')
    nombre_archivo = models.CharField(max_length=255, db_comment='Nombre del archivo tal como lo subió el usuario.')
    sha1 = models.CharField(max_length=40, blank=True, null=True, db_comment='Huella del archivo subido. Permite detectar que se volvió a subir el mismo.')
    bytes = models.BigIntegerField(blank=True, null=True, db_comment='Tamaño del archivo.')
    estado = models.CharField(max_length=20, db_comment='Estado del lote, independiente del estado de la presentación: un lote puede estar NORMALIZADO y la presentación seguir en BORRADOR.')
    filas_totales = models.IntegerField(db_comment='Filas de datos leídas del archivo.')
    filas_validas = models.IntegerField(db_comment='Filas sin ningún hallazgo bloqueante.')
    filas_con_error = models.IntegerField(db_comment='Filas con al menos un hallazgo bloqueante.')
    bloqueantes = models.IntegerField(db_comment='Cantidad total de hallazgos bloqueantes.')
    advertencias = models.IntegerField(db_comment='Cantidad total de advertencias.')
    iniciada_el = models.DateTimeField(db_comment='Momento en que se recibió el archivo.')
    terminada_el = models.DateTimeField(blank=True, null=True, db_comment='Momento en que terminó el procesamiento.')
    duracion_ms = models.IntegerField(blank=True, null=True, db_comment='Duración del procesamiento, en milisegundos.')
    usuario = models.CharField(max_length=150, blank=True, null=True, db_comment='Usuario que subió el archivo.')
    reemplaza_a = models.ForeignKey('self', models.DO_NOTHING, db_column='reemplaza_a', blank=True, null=True, db_comment='Importación anterior que este intento deja sin efecto. Conserva el historial de intentos.')
    detalle_error = models.TextField(blank=True, null=True, db_comment='Motivo del rechazo cuando el estado es ESTRUCTURA_INVALIDA o ERROR_TECNICO.')

    class Meta:
        managed = False
        db_table = 'runac_c2_importacion'
        db_table_comment = 'Cada intento de importación de un archivo, incluidos los que fallaron. Nunca se borra: es la trazabilidad.'


class RunacC2Observacion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    presentacion = models.ForeignKey('RunacC2Presentacion', models.DO_NOTHING, db_comment='Presentación observada.')
    importacion = models.ForeignKey(RunacC2Importacion, models.DO_NOTHING, blank=True, null=True, db_comment='Importación puntual observada.')
    numero_fila = models.IntegerField(blank=True, null=True, db_comment='Fila puntual observada.')
    campo = models.ForeignKey(RunacC1Campo, models.DO_NOTHING, blank=True, null=True, db_comment='Campo puntual observado.')
    texto = models.TextField(db_comment='La observación, escrita por el revisor.')
    estado = models.CharField(max_length=11, db_comment='Seguimiento de la observación.')
    respuesta = models.TextField(blank=True, null=True, db_comment='Respuesta de la provincia.')
    creada_el = models.DateTimeField(db_comment='Momento en que se formuló.')
    usuario_observa = models.CharField(max_length=150, db_comment='Revisor que la formuló.')
    usuario_responde = models.CharField(max_length=150, blank=True, null=True, db_comment='Usuario provincial que respondió.')

    class Meta:
        managed = False
        db_table = 'runac_c2_observacion'
        db_table_comment = 'Observaciones del revisor nacional. El revisor no modifica datos provinciales: observa.'


class RunacC2Periodo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    codigo = models.CharField(unique=True, max_length=30, db_comment='Código del período, por ejemplo 2026_T1.')
    anio = models.SmallIntegerField(db_comment='Año del corte.')
    numero = models.IntegerField(db_comment='Número de corte dentro del año. Con periodicidad trimestral va de 1 a 4.')
    fecha_desde = models.DateField(db_comment='Primer día del período de referencia.')
    fecha_hasta = models.DateField(db_comment='Último día del período de referencia.')
    estado = models.CharField(max_length=11, db_comment='PREPARACION: se está definiendo la estructura y la Capa 1 todavía puede cambiar. ABIERTO: las provincias importan y la Capa 1 queda congelada. CERRADO: no se admiten más cargas.')
    abierto_el = models.DateTimeField(blank=True, null=True, db_comment='Momento en que se habilitó la carga.')
    cerrado_el = models.DateTimeField(blank=True, null=True, db_comment='Momento en que se cerró la carga.')

    class Meta:
        managed = False
        db_table = 'runac_c2_periodo'
        unique_together = (('anio', 'numero'),)
        db_table_comment = 'Períodos de corte. Mientras un período está ABIERTO la Capa 1 no puede modificarse: alguna provincia ya pudo haber importado.'


class RunacC2Presentacion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    periodo = models.ForeignKey(RunacC2Periodo, models.DO_NOTHING, db_comment='Período al que corresponde la presentación.')
    jurisdiccion = models.CharField(max_length=120, db_comment='Provincia que presenta.')
    version = models.IntegerField(db_comment='Número de versión. Una subsanación genera una versión nueva; la anterior se conserva.')
    estado = models.CharField(max_length=11, db_comment='Estado del circuito provincia-nación. No se mezcla con el estado de cada importación.')
    presentada_el = models.DateTimeField(blank=True, null=True, db_comment='Momento en que el responsable provincial la envió a revisión.')
    aceptada_el = models.DateTimeField(blank=True, null=True, db_comment='Momento en que el revisor nacional la aceptó.')
    expediente = models.CharField(max_length=100, blank=True, null=True, db_comment='Número de presentación TAD/GDE de la versión consolidada.')
    usuario_presenta = models.CharField(max_length=150, blank=True, null=True, db_comment='Usuario que realizó la presentación formal.')
    usuario_acepta = models.CharField(max_length=150, blank=True, null=True, db_comment='Usuario que aceptó la presentación.')
    reemplaza_a = models.ForeignKey('self', models.DO_NOTHING, db_column='reemplaza_a', blank=True, null=True, db_comment='Presentación anterior que esta versión subsana.')

    class Meta:
        managed = False
        db_table = 'runac_c2_presentacion'
        unique_together = (('periodo', 'jurisdiccion', 'version'),)
        db_table_comment = 'Presentación de una provincia para un período. Agrupa las importaciones de los distintos archivos.'


class RunacC3Cambio(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    entidad = models.CharField(max_length=40, db_comment='Tabla de Capa 3 donde ocurrió el cambio.')
    entidad_id = models.BigIntegerField(db_comment='Registro modificado.')
    campo = models.CharField(max_length=100, db_comment='Columna que cambió.')
    valor_anterior = models.TextField(blank=True, null=True, db_comment='Contenido antes del cambio.')
    valor_nuevo = models.TextField(blank=True, null=True, db_comment='Contenido después del cambio.')
    presentacion = models.ForeignKey(RunacC2Presentacion, models.DO_NOTHING, blank=True, null=True, db_comment='Presentación que produjo el cambio. Queda vacío en las correcciones manuales.')
    usuario = models.CharField(max_length=150, blank=True, null=True, db_comment='Usuario responsable, cuando el cambio fue manual.')
    motivo = models.TextField(blank=True, null=True, db_comment='Justificación del cambio.')
    fecha = models.DateTimeField(db_comment='Momento del cambio.')

    class Meta:
        managed = False
        db_table = 'runac_c3_cambio'
        db_table_comment = 'Historial campo a campo. Permite reconstruir cómo estaba un registro en cualquier momento y saber qué presentación lo modificó.'


class RunacC3Coincidencia(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    importacion = models.ForeignKey(RunacC2Importacion, models.DO_NOTHING, db_comment='Importación que produjo la duda.')
    numero_fila = models.IntegerField(db_comment='Fila del Excel en cuestión.')
    persona_candidata = models.ForeignKey('RunacC3Persona', models.DO_NOTHING, blank=True, null=True, db_comment='Persona del padrón que podría ser la misma.')
    motivo = models.CharField(max_length=255, db_comment='Por qué se sospecha que son la misma persona, o por qué no se pudo decidir.')
    puntaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, db_comment='Grado de similitud calculado, de 0 a 100.')
    estado = models.CharField(max_length=10, db_comment='Resolución de la ambigüedad.')
    resuelta_por = models.CharField(max_length=150, blank=True, null=True, db_comment='Usuario que la resolvió.')
    resuelta_el = models.DateTimeField(blank=True, null=True, db_comment='Momento de la resolución.')

    class Meta:
        managed = False
        db_table = 'runac_c3_coincidencia'
        db_table_comment = 'Coincidencias de identidad que requieren revisión humana, como pide el circuito de importación. Ninguna se resuelve sola.'


class RunacC3Dispositivo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID SISOC del dispositivo. Se asigna en la primera carga y las plantillas siguientes deben traerlo.')
    jurisdiccion = models.CharField(max_length=120, db_comment='Provincia a la que pertenece.')
    nombre = models.CharField(max_length=255, db_comment='Nombre del dispositivo, residencia, hogar o centro.')
    tipo = models.CharField(max_length=11, db_comment='Tipo de dispositivo. Determina qué archivo lo puede referenciar.')
    dependencia = models.CharField(max_length=255, blank=True, null=True, db_comment='Organismo del que depende.')
    gestion = models.CharField(max_length=60, blank=True, null=True, db_comment='Tipo de gestión: estatal, convenio, mixta.')
    localidad = models.CharField(max_length=120, blank=True, null=True, db_comment='Localidad donde funciona.')
    domicilio = models.CharField(max_length=255, blank=True, null=True, db_comment='Domicilio del dispositivo.')
    capacidad = models.IntegerField(blank=True, null=True, db_comment='Capacidad declarada.')
    activo = models.IntegerField(db_comment='Indica si sigue en funcionamiento.')
    creado_el = models.DateTimeField(db_comment='Alta en el registro maestro.')
    actualizado_el = models.DateTimeField(db_comment='Última modificación.')

    class Meta:
        managed = False
        db_table = 'runac_c3_dispositivo'
        unique_together = (('jurisdiccion', 'nombre', 'tipo'),)
        db_table_comment = 'Registro maestro de dispositivos. Regla del requerimiento: en la primera carga se relaciona por provincia, nombre y tipo; una vez asignado el ID SISOC, las plantillas futuras deben incorporarlo para evitar errores de escritura y duplicados.'


class RunacC3Familia(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID SISOC de la familia.')
    jurisdiccion = models.CharField(max_length=120, db_comment='Provincia que la registra.')
    id_provincial = models.CharField(max_length=60, blank=True, null=True, db_comment='Identificador que usa la provincia.')
    tipo = models.CharField(max_length=22, blank=True, null=True, db_comment='Modalidad de cuidado familiar.')
    descripcion = models.CharField(max_length=255, blank=True, null=True, db_comment='Referencia para identificarla.')

    class Meta:
        managed = False
        db_table = 'runac_c3_familia'
        unique_together = (('jurisdiccion', 'id_provincial'),)
        db_table_comment = 'Familias vinculadas a modalidades de cuidado del MPE, cuando la modalidad no es residencial.'


class RunacC3Medida(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID SISOC de la medida o episodio.')
    persona = models.ForeignKey('RunacC3Persona', models.DO_NOTHING, db_comment='Persona sobre la que recae. Una persona puede tener varias medidas a lo largo del tiempo.')
    universo = models.CharField(max_length=3, db_comment='Tipo de medida o evento, según el archivo del que proviene.')
    jurisdiccion = models.CharField(max_length=120, db_comment='Provincia que la informa.')
    id_provincial = models.CharField(max_length=60, blank=True, null=True, db_comment='Identificador que la provincia usa para la medida.')
    dispositivo = models.ForeignKey(RunacC3Dispositivo, models.DO_NOTHING, blank=True, null=True, db_comment='Dispositivo interviniente, cuando corresponde.')
    familia = models.ForeignKey(RunacC3Familia, models.DO_NOTHING, blank=True, null=True, db_comment='Familia interviniente, en modalidades de cuidado familiar del MPE.')
    referente = models.ForeignKey('RunacC3Persona', models.DO_NOTHING, related_name='runacc3medida_referente_set', blank=True, null=True, db_comment='Persona que actúa como referente adulto, en el MPI.')
    fecha_inicio = models.DateField(blank=True, null=True, db_comment='Fecha en que se dictó o formalizó la medida, o fecha de ingreso en los eventos.')
    fecha_fin = models.DateField(blank=True, null=True, db_comment='Fecha de cese o egreso. Queda vacía mientras la medida esté vigente.')
    vigente = models.IntegerField(db_comment='Indica si la medida sigue en curso. Se deriva de fecha_fin.')
    motivo = models.CharField(max_length=255, blank=True, null=True, db_comment='Causa o motivo principal.')
    origen_demanda = models.CharField(max_length=120, blank=True, null=True, db_comment='Origen de la demanda.')
    motivo_cese = models.CharField(max_length=255, blank=True, null=True, db_comment='Causa de finalización.')
    equipo_interviniente = models.CharField(max_length=255, blank=True, null=True, db_comment='Equipo o área responsable.')
    datos = models.JSONField(blank=True, null=True, db_comment='Campos propios de cada universo que no son comunes a todos. Evita una tabla distinta por universo mientras el modelo se estabiliza.')
    creada_el = models.DateTimeField(db_comment='Alta en el consolidado.')
    actualizada_el = models.DateTimeField(db_comment='Última modificación.')

    class Meta:
        managed = False
        db_table = 'runac_c3_medida'
        unique_together = (('persona', 'universo', 'fecha_inicio', 'jurisdiccion'),)
        db_table_comment = 'Medidas MPI, MPE, MPJ y eventos DAE. Se insertan; si el mismo episodio vuelve en otra presentación se actualiza por su clave natural, no se duplica.'


class RunacC3Origen(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    entidad = models.CharField(max_length=40, db_comment='Tabla de Capa 3 a la que pertenece el registro, por ejemplo persona o medida.')
    entidad_id = models.BigIntegerField(db_comment='Registro de esa tabla.')
    presentacion = models.ForeignKey(RunacC2Presentacion, models.DO_NOTHING, db_comment='Presentación provincial de la que provino el dato.')
    importacion = models.ForeignKey(RunacC2Importacion, models.DO_NOTHING, db_comment='Importación concreta.')
    numero_fila = models.IntegerField(blank=True, null=True, db_comment='Fila del Excel de la que salió, para poder volver al origen.')
    accion = models.CharField(max_length=13, db_comment='Qué hizo esta presentación con el registro.')
    fecha = models.DateTimeField(db_comment='Momento de la consolidación.')

    class Meta:
        managed = False
        db_table = 'runac_c3_origen'
        db_table_comment = 'Responde "de dónde salió este dato": provincia, período, archivo, fila y versión. Es la trazabilidad que pide el requerimiento.'


class RunacC3Persona(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID SISOC de la persona. Se asigna una sola vez y no cambia nunca.')
    ciudadano_id = models.BigIntegerField(blank=True, null=True, db_comment='Vínculo con ciudadanos.Ciudadano de SISOC, cuando se resuelva esa integración. Hoy queda vacío: es una decisión funcional pendiente.')
    tipo_documento = models.CharField(max_length=30, blank=True, null=True, db_comment='Tipo de documento informado.')
    numero_documento = models.CharField(max_length=20, blank=True, null=True, db_comment='Número de documento, sin puntos ni espacios.')
    cuil = models.CharField(max_length=13, blank=True, null=True, db_comment='CUIL normalizado.')
    apellidos = models.CharField(max_length=120, blank=True, null=True, db_comment='Apellido o apellidos.')
    nombres = models.CharField(max_length=120, blank=True, null=True, db_comment='Nombre o nombres.')
    fecha_nacimiento = models.DateField(blank=True, null=True, db_comment='Fecha de nacimiento.')
    genero = models.CharField(max_length=30, blank=True, null=True, db_comment='Género informado.')
    pais_nacimiento = models.CharField(max_length=120, blank=True, null=True, db_comment='País de nacimiento.')
    rol = models.CharField(max_length=11, db_comment='Rol principal con el que la persona entró al registro. Una misma persona puede cumplir más de uno a lo largo del tiempo.')
    estado_identidad = models.CharField(max_length=15, db_comment='Resultado del cotejo de identidad. REVISION_MANUAL marca las coincidencias ambiguas que alguien debe resolver.')
    creada_el = models.DateTimeField(db_comment='Alta en el padrón.')
    actualizada_el = models.DateTimeField(db_comment='Última modificación.')

    class Meta:
        managed = False
        db_table = 'runac_c3_persona'
        unique_together = (('tipo_documento', 'numero_documento'),)
        db_table_comment = 'Padrón de personas. Una persona se registra UNA sola vez, aunque aparezca en muchas presentaciones y en varios archivos.'


class RunacC3PersonaDatoOrigen(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='Identificador interno.')
    persona = models.ForeignKey(RunacC3Persona, models.DO_NOTHING, db_comment='Persona del padrón a la que se atribuyó este dato.')
    presentacion = models.ForeignKey(RunacC2Presentacion, models.DO_NOTHING, db_comment='Presentación en la que llegó.')
    id_provincial = models.CharField(max_length=60, blank=True, null=True, db_comment='Identificador que la provincia usa para esa persona, si lo informa.')
    tipo_documento = models.CharField(max_length=30, blank=True, null=True, db_comment='Tipo de documento tal como llegó.')
    numero_documento = models.CharField(max_length=30, blank=True, null=True, db_comment='Número tal como llegó, sin normalizar.')
    apellidos = models.CharField(max_length=255, blank=True, null=True, db_comment='Apellidos tal como llegaron.')
    nombres = models.CharField(max_length=255, blank=True, null=True, db_comment='Nombres tal como llegaron.')
    fecha_nacimiento = models.CharField(max_length=30, blank=True, null=True, db_comment='Fecha tal como llegó, en texto: puede venir mal escrita y hay que conservarla.')
    coincide = models.IntegerField(db_comment='Indica si los datos coinciden con los del padrón o hay diferencias.')
    diferencias = models.TextField(blank=True, null=True, db_comment='Detalle de en qué difiere respecto del padrón.')

    class Meta:
        managed = False
        db_table = 'runac_c3_persona_dato_origen'
        db_table_comment = 'Los datos personales tal como los mandó cada provincia, coincidan o no con el padrón. Es lo que permite detectar un DNI con error de tipeo comparando nombre y fecha de nacimiento.'
