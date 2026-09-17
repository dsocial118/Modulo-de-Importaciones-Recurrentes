"""Modelos de MIR — implementación RUNAC.

Generados con `inspectdb` sobre la base que arma la skill `runac-capa1`. Todos
llevan `managed = False`: **el sistema no crea ni modifica el modelo, lo lee**.
La estructura la define la Capa 1 y la generan los scripts de la skill.

Las tablas receptoras de la Capa 2 (`mir_c2_<archivo>_v<n>[_<hoja>]`) no están
acá a propósito: se generan dinámicamente desde la Capa 1, hay una por versión de
estructura y cambian con cada período, así que se acceden con SQL, no con modelos.

Para regenerar este archivo:
    docker exec runac_proto_web python manage.py inspectdb > /tmp/m.py
    (y quitar las tablas receptoras)
"""

# Archivo GENERADO por `manage.py inspectdb`: los comentarios de cada campo
# vienen de la base y su largo no es una decision de estilo. Se suprimen solo
# esas dos reglas, no el archivo entero.
# pylint: disable=line-too-long, too-many-lines

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_group_permissions"
        unique_together = (("group", "permission"),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_groups"
        unique_together = (("user", "group"),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_user_permissions"
        unique_together = (("user", "permission"),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        "DjangoContentType", models.DO_NOTHING, blank=True, null=True
    )
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"


class RunacC1Archivo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    codigo = models.CharField(
        unique=True,
        max_length=30,
        db_comment="Código estable que identifica el tipo de archivo, por ejemplo MPI, MPE o MPJ_DAE. No cambia nunca.",
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        db_comment="Descripción funcional de la información contenida en el archivo.",
    )
    activo = models.IntegerField(
        db_comment="Indica si el archivo sigue formando parte de los que se solicitan."
    )

    class Meta:
        managed = False
        db_table = "mir_c1_archivo"
        db_table_comment = "La identidad del archivo. Todo lo que puede cambiar entre períodos vive en la versión."


class RunacC1ArchivoVersion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    archivo = models.ForeignKey(
        RunacC1Archivo,
        models.DO_NOTHING,
        db_comment="Archivo cuya estructura describe esta versión.",
    )
    numero = models.IntegerField(
        db_comment="Número de versión, correlativo dentro del archivo."
    )
    estado = models.CharField(
        max_length=9,
        db_comment="BORRADOR: se está editando. VIGENTE: rige para el período abierto. HISTORICA: fue usada por un período anterior y no se modifica.",
    )
    nombre_esperado = models.CharField(
        max_length=255,
        db_comment="Nombre que debe tener el archivo. Puede cambiar entre versiones.",
    )
    titulo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_comment="Título que encabeza la planilla, tal como aparece en la primera fila del Excel.",
    )
    subtitulo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_comment="Subtítulo o segunda línea del encabezado, cuando la planilla lo tiene.",
    )
    orden_importacion = models.IntegerField(
        db_comment="Orden en que debe procesarse respecto de los demás archivos de la misma versión de período."
    )
    obligatorio = models.IntegerField(
        db_comment="Indica si la ausencia del archivo impide continuar con la importación."
    )
    creada_el = models.DateTimeField(db_comment="Momento en que se creó la versión.")
    creada_por = models.CharField(
        max_length=150, blank=True, null=True, db_comment="Usuario que la creó."
    )
    copiada_de = models.ForeignKey(
        "self",
        models.DO_NOTHING,
        db_column="copiada_de",
        blank=True,
        null=True,
        db_comment="Versión anterior a partir de la cual se copió para su edición.",
    )
    nota = models.TextField(
        blank=True, null=True, db_comment="Qué cambió respecto de la versión anterior."
    )

    class Meta:
        managed = False
        db_table = "mir_c1_archivo_version"
        unique_together = (("archivo", "numero"),)
        db_table_comment = "Cada versión de la estructura de un archivo. Hojas, dimensiones, campos y reglas cuelgan de la versión, no del archivo."


class RunacC1Campo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    hoja = models.ForeignKey(
        "RunacC1Hoja", models.DO_NOTHING, db_comment="Hoja a la que pertenece el campo."
    )
    dimension = models.ForeignKey(
        "RunacC1Dimension",
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Dimensión que agrupa el campo. Puede quedar vacío cuando el campo no pertenece a una dimensión.",
    )
    catalogo = models.ForeignKey(
        "RunacC1Catalogo",
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Catálogo que contiene los valores permitidos para el campo. Puede quedar vacío cuando el campo no utiliza una lista cerrada.",
    )
    nombre = models.CharField(
        max_length=100,
        db_comment="Nombre técnico y estable del campo, escrito en snake_case y sin tildes ni caracteres especiales.",
    )
    titulo_esperado = models.CharField(
        max_length=255,
        db_comment="Título exacto que debe aparecer en la columna del archivo Excel.",
    )
    orden = models.IntegerField(
        db_comment="Posición esperada de la columna dentro de la hoja."
    )
    tipo_dato = models.CharField(
        max_length=7, db_comment="Tipo de dato esperado para el campo."
    )
    longitud_maxima = models.IntegerField(
        blank=True,
        null=True,
        db_comment="Cantidad máxima de caracteres admitidos para campos de tipo TEXTO. Si queda vacío, la columna receptora se creará como TEXT.",
    )
    obligatorio = models.IntegerField(
        db_comment="Indica si el campo debe contener un valor. Las obligatoriedades condicionales se definen mediante reglas."
    )
    ayuda = models.TextField(
        blank=True,
        null=True,
        db_comment="Texto explicativo para la confección o validación del campo.",
    )

    class Meta:
        managed = False
        db_table = "mir_c1_campo"
        unique_together = (
            ("hoja", "orden"),
            ("hoja", "nombre"),
        )
        db_table_comment = "Define los campos o columnas esperados dentro de cada hoja."


class RunacC1CampoRegla(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    campo = models.ForeignKey(
        RunacC1Campo,
        models.DO_NOTHING,
        db_comment="Campo sobre el que se aplica la regla.",
    )
    regla = models.ForeignKey(
        "RunacC1Regla", models.DO_NOTHING, db_comment="Regla que debe aplicarse."
    )
    severidad = models.CharField(
        max_length=11,
        db_comment="Atributo de la regla APLICADA, no del tipo: un mismo tipo puede ser bloqueante en un campo y advertencia en otro.",
    )
    mensaje = models.TextField(
        blank=True,
        null=True,
        db_comment="Mensaje al usuario, en lenguaje claro. Vive en la definición y no en el código, de modo que pueda mejorarse sin desarrollo.",
    )

    class Meta:
        managed = False
        db_table = "mir_c1_campo_regla"
        unique_together = (("campo", "regla"),)
        db_table_comment = "Relaciona los campos con las reglas que deben aplicarse, con su severidad y su mensaje."


class RunacC1Catalogo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    codigo = models.CharField(
        unique=True,
        max_length=100,
        db_comment="Código técnico y estable del catálogo, escrito en snake_case.",
    )
    nombre = models.CharField(
        max_length=255, db_comment="Nombre descriptivo del catálogo."
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        db_comment="Explicación funcional de los valores contenidos en el catálogo.",
    )

    class Meta:
        managed = False
        db_table = "mir_c1_catalogo"
        db_table_comment = "Define un conjunto cerrado de valores admitidos para uno o más campos. Una lista que reaparece en varios archivos se define una sola vez."


class RunacC1CatalogoOpcion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    catalogo = models.ForeignKey(
        RunacC1Catalogo,
        models.DO_NOTHING,
        db_comment="Catálogo al que pertenece la opción.",
    )
    codigo = models.CharField(
        max_length=100,
        db_comment="Código técnico y estable de la opción. NO cambia aunque cambie el texto: es lo que permite comparar series históricas.",
    )
    valor_esperado = models.CharField(
        max_length=255,
        db_comment="Texto que debe encontrarse en el archivo Excel. Puede cambiar sin que cambie el código.",
    )
    descripcion = models.TextField(
        blank=True, null=True, db_comment="Explicación funcional de la opción."
    )
    orden = models.IntegerField(
        db_comment="Orden de presentación de la opción dentro del catálogo."
    )
    activo = models.IntegerField(
        db_comment="Baja lógica. Una opción inactiva no se admite en nuevas importaciones, pero el registro se conserva para que los datos anteriores sigan siendo legibles."
    )
    vigente_desde_periodo = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        db_comment="Código del primer período en que la opción se admite. Vacío significa que rige desde el inicio. Se guarda el código y no el id para que la Capa 1 no dependa de la Capa 2.",
    )
    vigente_hasta_periodo = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        db_comment="Código del último período en que la opción se admite. Vacío significa que sigue vigente.",
    )

    class Meta:
        managed = False
        db_table = "mir_c1_catalogo_opcion"
        unique_together = (
            ("catalogo", "orden"),
            ("catalogo", "valor_esperado"),
            ("catalogo", "codigo"),
        )
        db_table_comment = "Cada valor permitido dentro de un catálogo, con su vigencia. Permite validar cada archivo contra las opciones que regían en su período."


class RunacC1Dimension(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    hoja = models.ForeignKey(
        "RunacC1Hoja",
        models.DO_NOTHING,
        db_comment="Hoja a la que pertenece la dimensión.",
    )
    nombre_esperado = models.CharField(
        max_length=255,
        db_comment="Texto que debe aparecer en la celda combinada ubicada sobre los títulos de las columnas.",
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        db_comment="Descripción funcional del grupo de campos representado por la dimensión.",
    )
    orden = models.IntegerField(
        db_comment="Orden en que aparece la dimensión dentro de la hoja."
    )

    class Meta:
        managed = False
        db_table = "mir_c1_dimension"
        unique_together = (("hoja", "orden"),)
        db_table_comment = (
            "Define los encabezados que agrupan conjuntos de campos dentro de una hoja."
        )


class RunacC1Hoja(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    archivo_version = models.ForeignKey(
        RunacC1ArchivoVersion,
        models.DO_NOTHING,
        db_comment="Versión de archivo a la que pertenece la hoja.",
    )
    nombre_esperado = models.CharField(
        max_length=255,
        db_comment="Nombre exacto que debe tener la hoja dentro del archivo Excel.",
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        db_comment="Descripción funcional de la información contenida en la hoja.",
    )
    orden_procesamiento = models.IntegerField(
        db_comment="Orden en que debe procesarse dentro del archivo."
    )
    fila_encabezados = models.IntegerField(
        db_comment="Fila donde se encuentran los nombres de los campos. Los datos comienzan en la fila siguiente."
    )
    obligatoria = models.IntegerField(
        db_comment="Indica si la ausencia de la hoja impide continuar con la importación."
    )

    class Meta:
        managed = False
        db_table = "mir_c1_hoja"
        unique_together = (
            ("archivo_version", "orden_procesamiento"),
            ("archivo_version", "nombre_esperado"),
        )
        db_table_comment = (
            "Define las hojas que deben encontrarse dentro de cada versión de archivo."
        )


class RunacC1Regla(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    tipo_regla = models.ForeignKey(
        "RunacC1TipoRegla",
        models.DO_NOTHING,
        db_comment="Tipo de validación que debe ejecutar el importador.",
    )
    nombre = models.CharField(
        unique=True,
        max_length=255,
        db_comment="Nombre técnico y estable que identifica la regla concreta.",
    )
    descripcion = models.TextField(
        blank=True, null=True, db_comment="Explicación funcional de la validación."
    )
    parametros = models.JSONField(
        blank=True,
        null=True,
        db_comment="Valores necesarios para ejecutar la regla, de acuerdo con los parámetros definidos para su tipo.",
    )

    class Meta:
        managed = False
        db_table = "mir_c1_regla"
        db_table_comment = "Una validación concreta, reutilizable en distintos campos."


class RunacC1TipoRegla(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    nombre = models.CharField(
        unique=True,
        max_length=100,
        db_comment="Nombre técnico y estable del tipo de regla, por ejemplo RANGO, OBLIGATORIO_SI, EXISTE_EN o EJECUTAR_FUNCION.",
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        db_comment="Explica el comportamiento general de la validación.",
    )

    class Meta:
        managed = False
        db_table = "mir_c1_tipo_regla"
        db_table_comment = "Vocabulario genérico de validaciones. Los mismos tipos sirven para cualquier relevamiento; cambian los parámetros."


class RunacC1TipoReglaParametro(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    tipo_regla = models.ForeignKey(
        RunacC1TipoRegla,
        models.DO_NOTHING,
        db_comment="Tipo de regla al que pertenece el parámetro.",
    )
    nombre = models.CharField(
        max_length=100,
        db_comment="Nombre técnico del parámetro dentro del JSON, por ejemplo minimo, maximo, operador o campo_condicion.",
    )
    tipo_parametro = models.CharField(
        max_length=8, db_comment="Tipo de valor que debe contener el parámetro."
    )
    obligatorio = models.IntegerField(
        db_comment="Indica si el parámetro debe estar presente para configurar la regla."
    )
    orden = models.IntegerField(db_comment="Orden de presentación del parámetro.")
    descripcion = models.TextField(
        blank=True, null=True, db_comment="Explica el significado y uso del parámetro."
    )

    class Meta:
        managed = False
        db_table = "mir_c1_tipo_regla_parametro"
        unique_together = (
            ("tipo_regla", "orden"),
            ("tipo_regla", "nombre"),
        )
        db_table_comment = "Define los parámetros esperados por cada tipo de regla."


class RunacC2ErroresDeImportacion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    importacion = models.ForeignKey(
        "RunacC2Importacion",
        models.DO_NOTHING,
        db_comment="Intento en el que se detectó.",
    )
    tipo = models.CharField(
        max_length=22,
        db_comment="Los cinco primeros son discrepancias con la estructura esperada. FILA_VACIA_INTERCALADA es una fila en blanco en el medio de los datos, que el requerimiento pide corregir antes de importar. ARCHIVO_ILEGIBLE y ERROR_TECNICO no dependen del contenido: formato no reconocido, archivo dañado, interrupción del proceso o pérdida de conexión.",
    )
    hoja = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_comment="Hoja donde se detectó, cuando corresponde.",
    )
    numero_fila = models.IntegerField(
        blank=True,
        null=True,
        db_comment="Fila del Excel, cuando el problema tiene una ubicación puntual.",
    )
    esperado = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_comment="Nombre de hoja, título de columna o posición que se esperaba encontrar.",
    )
    encontrado = models.CharField(
        max_length=255, blank=True, null=True, db_comment="Qué se encontró en su lugar."
    )
    descripcion = models.TextField(
        db_comment="Mensaje en lenguaje claro para el operador."
    )
    detalle_tecnico = models.TextField(
        blank=True,
        null=True,
        db_comment="Traza del error, para soporte. No se muestra al usuario.",
    )

    class Meta:
        managed = False
        db_table = "mir_c2_errores_de_importacion"
        db_table_comment = "Motivos por los que un archivo no pudo importarse. Un archivo equivocado suele fallar por varias razones a la vez: se informan todas juntas para que el operador corrija una sola vez."


class RunacC2HistorialCambios(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    importacion = models.ForeignKey(
        "RunacC2Importacion",
        models.DO_NOTHING,
        db_comment="Importación cuyos datos se editaron.",
    )
    numero_fila = models.IntegerField(db_comment="Fila editada.")
    campo = models.ForeignKey(
        RunacC1Campo, models.DO_NOTHING, db_comment="Campo editado."
    )
    identificador_registro = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_comment="Identificador provincial del registro editado.",
    )
    observacion = models.ForeignKey(
        "RunacC2Observacion",
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Observación que motivó el cambio, cuando corresponde.",
    )
    valor_anterior = models.TextField(
        blank=True, null=True, db_comment="Contenido previo al cambio."
    )
    valor_nuevo = models.TextField(
        blank=True, null=True, db_comment="Contenido posterior al cambio."
    )
    motivo = models.TextField(
        blank=True, null=True, db_comment="Justificación del cambio."
    )
    fecha = models.DateTimeField(db_comment="Momento del cambio.")
    usuario = models.CharField(
        max_length=150, db_comment="Usuario que realizó el cambio."
    )

    class Meta:
        managed = False
        db_table = "mir_c2_historial_cambios"
        db_table_comment = "Correcciones sobre los datos importados, con usuario, fecha, valor anterior y valor nuevo. Responde a la pregunta: el Excel decía X y el operador puso Y. No confundir con el historial de la Capa 3, que registra la evolución del dato consolidado entre períodos."


class RunacC2Importacion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    presentacion = models.ForeignKey(
        "RunacC2Presentacion",
        models.DO_NOTHING,
        db_comment="Presentación a la que pertenece este intento.",
    )
    archivo = models.ForeignKey(
        RunacC1Archivo,
        models.DO_NOTHING,
        db_comment="Archivo que el operador declaró estar cargando. El operador elige el archivo: el nombre del fichero no lo determina.",
    )
    archivo_version = models.ForeignKey(
        RunacC1ArchivoVersion,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Versión contra la que se validó. Queda vacío cuando el archivo no se pudo identificar.",
    )
    nombre_archivo = models.CharField(
        max_length=255, db_comment="Nombre del archivo tal como lo subió el usuario."
    )
    sha1 = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        db_comment="Huella del archivo subido. Permite detectar que se volvió a subir el mismo.",
    )
    bytes = models.BigIntegerField(
        blank=True, null=True, db_comment="Tamaño del archivo."
    )
    ruta_archivo = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        db_comment="Ubicación del archivo recibido, tal como llegó. Es lo que permite devolver al operador su propio Excel con las celdas marcadas, y el respaldo documental de lo presentado.",
    )
    estado = models.CharField(
        max_length=7,
        db_comment="VALIDA: admitida e incorporada. ANULADA: reemplazada por una importación posterior del mismo archivo. FALLIDA: rechazada en el control de admisión o interrumpida por un error técnico. Dado que la importación es restrictiva, un archivo con bloqueantes no genera una importación válida.",
    )
    filas_leidas = models.IntegerField(db_comment="Filas de datos leídas del archivo.")
    filas_incorporadas = models.IntegerField(
        db_comment="Filas efectivamente incorporadas."
    )
    bloqueantes = models.IntegerField(
        db_comment="Cantidad de reglas incumplidas con severidad bloqueante."
    )
    advertencias = models.IntegerField(
        db_comment="Cantidad de reglas incumplidas con severidad advertencia."
    )
    iniciada_el = models.DateTimeField(
        db_comment="Momento en que se recibió el archivo."
    )
    terminada_el = models.DateTimeField(
        blank=True, null=True, db_comment="Momento en que terminó el procesamiento."
    )
    duracion_ms = models.IntegerField(
        blank=True, null=True, db_comment="Duración del procesamiento, en milisegundos."
    )
    usuario = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_comment="Usuario que subió el archivo.",
    )
    anulada_por = models.ForeignKey(
        "self",
        models.DO_NOTHING,
        db_column="anulada_por",
        blank=True,
        null=True,
        db_comment="Importación posterior que dejó sin efecto a esta. Conserva el historial de intentos.",
    )

    class Meta:
        managed = False
        db_table = "mir_c2_importacion"
        db_table_comment = "Cada intento de importación de un archivo, incluidos los que fallaron. Nunca se borra: es la trazabilidad. Permite distinguir a quien no cargó de quien intentó cargar y no pudo."


class RunacC2Jurisdiccion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    codigo = models.CharField(
        unique=True, max_length=20, db_comment="Código estable de la jurisdicción."
    )
    nombre = models.CharField(
        max_length=120, db_comment="Denominación de la jurisdicción."
    )
    modalidad = models.CharField(
        max_length=22,
        db_comment="PRESENTACION_PERIODICA: aporta archivos en cada corte, y una nueva importación reemplaza a la anterior. GESTION_CONTINUA: registra novedades dentro del sistema, y la importación incorpora sin descartar lo existente.",
    )
    activa = models.IntegerField(db_comment="Baja lógica.")

    class Meta:
        managed = False
        db_table = "mir_c2_jurisdiccion"
        db_table_comment = "Unidad que presenta. Es una entidad y no un texto, para que el mismo mecanismo sirva a provincias, municipios u organismos."


class RunacC2Observacion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    presentacion = models.ForeignKey(
        "RunacC2Presentacion", models.DO_NOTHING, db_comment="Presentación observada."
    )
    importacion = models.ForeignKey(
        RunacC2Importacion,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Importación puntual observada.",
    )
    numero_fila = models.IntegerField(
        blank=True, null=True, db_comment="Fila puntual observada."
    )
    campo = models.ForeignKey(
        RunacC1Campo,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Campo puntual observado.",
    )
    identificador_registro = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_comment="Identificador provincial del registro observado.",
    )
    texto = models.TextField(
        db_comment="La observación, escrita por el revisor técnico nacional."
    )
    estado = models.CharField(
        max_length=11, db_comment="Seguimiento de la observación."
    )
    respuesta = models.TextField(
        blank=True, null=True, db_comment="Respuesta de la jurisdicción."
    )
    creada_el = models.DateTimeField(db_comment="Momento en que se formuló.")
    usuario_observa = models.CharField(
        max_length=150, db_comment="Revisor que la formuló."
    )
    respondida_el = models.DateTimeField(
        blank=True, null=True, db_comment="Momento de la respuesta."
    )
    usuario_responde = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_comment="Usuario provincial que respondió.",
    )

    class Meta:
        managed = False
        db_table = "mir_c2_observacion"
        db_table_comment = "Observaciones del revisor nacional. El revisor no modifica datos provinciales: observa. El ciclo de observación y subsanación no tiene límite de rondas."


class RunacC2Periodo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    codigo = models.CharField(
        unique=True,
        max_length=30,
        db_comment="Código del período, por ejemplo 2026_T1.",
    )
    anio = models.SmallIntegerField(db_comment="Año del corte.")
    numero = models.IntegerField(
        db_comment="Número de corte dentro del año. Con periodicidad trimestral va de 1 a 4."
    )
    fecha_desde = models.DateField(db_comment="Primer día del período de referencia.")
    fecha_hasta = models.DateField(
        db_comment="Último día del período de referencia. Es la fecha de corte: la fotografía se toma a ese día."
    )
    estado = models.CharField(
        max_length=11,
        db_comment="PREPARACION: se está definiendo la estructura y la Capa 1 todavía puede cambiar. ABIERTO: las jurisdicciones importan y la estructura queda congelada. CERRADO: no se admiten más cargas.",
    )
    declaro_cambios = models.IntegerField(
        db_comment="El administrador declaró, al abrir el período, si había cambios de estructura respecto del anterior."
    )
    usuario_declara = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_comment="Usuario que realizó la declaración.",
    )
    declarado_el = models.DateTimeField(
        blank=True, null=True, db_comment="Momento de la declaración."
    )
    abierto_el = models.DateTimeField(
        blank=True, null=True, db_comment="Momento en que se habilitó la carga."
    )
    cerrado_el = models.DateTimeField(
        blank=True, null=True, db_comment="Momento en que se cerró la carga."
    )

    class Meta:
        managed = False
        db_table = "mir_c2_periodo"
        unique_together = (("anio", "numero"),)
        db_table_comment = "Períodos de corte. Mientras un período está ABIERTO la estructura que utiliza no puede modificarse: alguna jurisdicción ya pudo haber importado."


class RunacC2PeriodoArchivo(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    periodo = models.ForeignKey(
        RunacC2Periodo, models.DO_NOTHING, db_comment="Período."
    )
    archivo_version = models.ForeignKey(
        RunacC1ArchivoVersion,
        models.DO_NOTHING,
        db_comment="Versión de estructura que rige para ese archivo en ese período.",
    )

    class Meta:
        managed = False
        db_table = "mir_c2_periodo_archivo"
        unique_together = (("periodo", "archivo_version"),)
        db_table_comment = "Qué versión de cada archivo rige en cada período. Si no hubo cambios, dos períodos apuntan a la misma versión y no se duplica ninguna definición. El nombre de la tabla receptora se deduce por convención del archivo y la versión."


class RunacC2Presentacion(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    periodo = models.ForeignKey(
        RunacC2Periodo,
        models.DO_NOTHING,
        db_comment="Período al que corresponde la presentación.",
    )
    jurisdiccion = models.ForeignKey(
        RunacC2Jurisdiccion, models.DO_NOTHING, db_comment="Jurisdicción que presenta."
    )
    version = models.IntegerField(
        db_comment="Número de versión. Una subsanación genera una versión nueva; la anterior se conserva con sus observaciones."
    )
    estado = models.CharField(
        max_length=11,
        db_comment="Estado del circuito jurisdicción-Nación. No se mezcla con el estado de cada importación: una presentación puede tener importaciones anuladas y estar igual en condiciones de cerrarse.",
    )
    cerrada_el = models.DateTimeField(
        blank=True,
        null=True,
        db_comment="Cierre de carga: el responsable provincial declaró terminada la carga y la envió a revisión.",
    )
    habilitada_el = models.DateTimeField(
        blank=True,
        null=True,
        db_comment="Momento en que el revisor técnico nacional habilitó la presentación formal.",
    )
    presentada_el = models.DateTimeField(
        blank=True,
        null=True,
        db_comment="Presentación formal. Se generó el comprobante.",
    )
    consolidada_el = models.DateTimeField(
        blank=True,
        null=True,
        db_comment="Momento en que los datos se incorporaron a la Capa 3.",
    )
    expediente = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_comment="Número GDE, incorporado por el responsable provincial tras remitir el comprobante. Su ausencia no impide la consolidación: es un resguardo documental de la jurisdicción.",
    )
    usuario_cierra = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_comment="Responsable provincial que cerró la carga.",
    )
    usuario_habilita = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_comment="Revisor técnico nacional que habilitó la presentación.",
    )
    usuario_presenta = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_comment="Responsable provincial que presentó formalmente.",
    )
    reemplaza_a = models.ForeignKey(
        "self",
        models.DO_NOTHING,
        db_column="reemplaza_a",
        blank=True,
        null=True,
        db_comment="Presentación anterior que esta versión subsana.",
    )

    class Meta:
        managed = False
        db_table = "mir_c2_presentacion"
        unique_together = (("periodo", "jurisdiccion", "version"),)
        db_table_comment = "Presentación de una jurisdicción para un período. Agrupa las importaciones de los distintos archivos."


class RunacC2ReglasIncumplidas(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment="Identificador interno.")
    importacion = models.ForeignKey(
        RunacC2Importacion,
        models.DO_NOTHING,
        db_comment="Importación en la que se detectó.",
    )
    campo = models.ForeignKey(
        RunacC1Campo,
        models.DO_NOTHING,
        db_comment="Campo de Capa 1 afectado. Siempre presente: un incumplimiento sin campo es un problema del archivo y va a mir_c2_errores_de_importacion.",
    )
    regla = models.ForeignKey(
        RunacC1Regla,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Regla de Capa 1 que no se cumplió. Queda vacío cuando el incumplimiento es de una validación intrínseca del campo —tipo de dato, obligatoriedad, valor de catálogo o longitud máxima—, que se define en mir_c1_campo y no en mir_c1_regla. El código indica de cuál se trata.",
    )
    codigo = models.CharField(
        max_length=50,
        db_comment="Código estable del incumplimiento, para contarlos y agruparlos: qué regla se incumple con más frecuencia, si se repite entre períodos.",
    )
    severidad = models.CharField(
        max_length=11, db_comment="Tomada de la regla aplicada al campo."
    )
    nombre_hoja = models.CharField(
        max_length=255, db_comment="Hoja del Excel donde está el problema."
    )
    numero_fila = models.IntegerField(
        db_comment="Fila del Excel, tal como la ve el usuario."
    )
    columna = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        db_comment="Letra de la columna en el Excel.",
    )
    nombre_campo = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_comment="Título de la columna, para que el informe se entienda sin unir tablas.",
    )
    identificador_registro = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_comment="Identificador provincial de la fila afectada.",
    )
    valor_encontrado = models.TextField(
        blank=True,
        null=True,
        db_comment="El valor que provocó el incumplimiento, tal como vino.",
    )
    descripcion = models.TextField(
        db_comment="Mensaje en lenguaje claro, tomado de la definición de la regla."
    )
    resuelta = models.IntegerField(
        db_comment="Indica si la advertencia fue corregida o justificada dentro del sistema."
    )

    class Meta:
        managed = False
        db_table = "mir_c2_reglas_incumplidas"
        db_table_comment = "Validaciones no superadas en un archivo que SÍ fue admitido. Una fila por incumplimiento, con su ubicación exacta."


class RunacC3Cambio(models.Model):
    id = models.BigAutoField(primary_key=True)
    entidad = models.CharField(max_length=40)
    entidad_id = models.BigIntegerField()
    campo = models.CharField(max_length=100)
    valor_anterior = models.TextField(blank=True, null=True)
    valor_nuevo = models.TextField(blank=True, null=True)
    presentacion = models.ForeignKey(
        RunacC2Presentacion, models.DO_NOTHING, blank=True, null=True
    )
    usuario = models.CharField(max_length=150, blank=True, null=True)
    motivo = models.CharField(max_length=13, blank=True, null=True)
    justificacion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_cambio"
        db_table_comment = "El historial campo a campo. No es un accesorio de auditoria: es la fuente de las series historicas, porque la base guarda una sola fila por chico con el dato vigente. Por eso registra el valor ANTERIOR y la presentacion que produjo el cambio."


class RunacC3Coincidencia(models.Model):
    id = models.BigAutoField(primary_key=True)
    importacion = models.ForeignKey(RunacC2Importacion, models.DO_NOTHING)
    numero_fila = models.IntegerField(blank=True, null=True)
    persona_candidata = models.ForeignKey(
        "RunacC3Persona", models.DO_NOTHING, blank=True, null=True
    )
    motivo = models.CharField(max_length=255)
    puntaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=10)
    resuelta_por = models.CharField(max_length=150, blank=True, null=True)
    resuelta_el = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_coincidencia"
        db_table_comment = "Coincidencias de identidad que no se pueden decidir solas: documento y nombre que coinciden parcialmente, o nombre y fecha de nacimiento sin documento."


class RunacC3DispAlcanceTerritorial(models.Model):
    id = models.BigAutoField(primary_key=True)
    dispositivo = models.ForeignKey("RunacC3Dispositivo", models.DO_NOTHING)
    jurisdiccion_alcanzada = models.CharField(max_length=120)

    class Meta:
        managed = False
        db_table = "mir_c3_disp_alcance_territorial"
        unique_together = (("dispositivo", "jurisdiccion_alcanzada"),)
        db_table_comment = "MPT, CAD y guardia informan VARIAS jurisdicciones de alcance. Por eso es una relacion y no un campo de texto: permite responder que dispositivos alcanzan a un municipio determinado."


class RunacC3DispCad(models.Model):
    dispositivo = models.OneToOneField(
        "RunacC3Dispositivo", models.DO_NOTHING, primary_key=True
    )

    class Meta:
        managed = False
        db_table = "mir_c3_disp_cad"
        db_table_comment = "27 campos, 22 compartidos con CRC. Propios: resolucion de creacion, articulacion interministerial, alcance territorial y tiempo maximo de permanencia en horas."


class RunacC3DispCrc(models.Model):
    dispositivo = models.OneToOneField(
        "RunacC3Dispositivo", models.DO_NOTHING, primary_key=True
    )

    class Meta:
        managed = False
        db_table = "mir_c3_disp_crc"
        db_table_comment = "36 campos. Grupos: capacidad por genero, proyecto institucional y normativa convivencial, personal por funcion, 6 protocolos, contacto socioafectivo, educacion obligatoria por nivel y horas, formacion profesional y talleres, espacios, condiciones de las celdas."


class RunacC3DispCrsc(models.Model):
    dispositivo = models.OneToOneField(
        "RunacC3Dispositivo", models.DO_NOTHING, primary_key=True
    )

    class Meta:
        managed = False
        db_table = "mir_c3_disp_crsc"
        db_table_comment = "36 campos IDENTICOS a los de CRC: mismos nombres, misma cantidad. Se mantiene como registro propio porque son regimenes distintos y sus cuestionarios pueden diferenciarse. Consulta abierta a la DNPYPI: corresponde relevar lo mismo?"


class RunacC3DispGuardia(models.Model):
    dispositivo = models.OneToOneField(
        "RunacC3Dispositivo", models.DO_NOTHING, primary_key=True
    )

    class Meta:
        managed = False
        db_table = "mir_c3_disp_guardia"
        db_table_comment = "9 campos, todos contenidos en CAD: es un subconjunto exacto. Consulta abierta a la DNPYPI: faltan campos propios de la guardia?"


class RunacC3DispMpt(models.Model):
    dispositivo = models.OneToOneField(
        "RunacC3Dispositivo", models.DO_NOTHING, primary_key=True
    )

    class Meta:
        managed = False
        db_table = "mir_c3_disp_mpt"
        db_table_comment = "10 campos, 8 de ellos tambien en CRC. Propios: espacio de grupalidad y alcance territorial. Es un programa en territorio, no un lugar de alojamiento."


class RunacC3DispResidencial(models.Model):
    dispositivo = models.OneToOneField(
        "RunacC3Dispositivo", models.DO_NOTHING, primary_key=True
    )

    class Meta:
        managed = False
        db_table = "mir_c3_disp_residencial"
        db_table_comment = "61 campos. Grupos: datos institucionales, gestion y convenio con el OPN, el establecimiento cuenta con..., protocolos, capacidad y cobertura, perfiles poblacionales admitidos, personal por funcion, 14 capacitaciones, proyecto de restitucion de derechos, insercion familiar y comunitaria. Comparte con los penales solo 5 de sus 61 campos, los de identificacion: son instrumentos distintos."


class RunacC3Dispositivo(models.Model):
    id = models.BigAutoField(
        primary_key=True,
        db_comment="ID SISOC del dispositivo. Las plantillas siguientes deben traerlo.",
    )
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    tipo = models.CharField(max_length=11)
    denominacion = models.CharField(max_length=255)
    dependencia_institucional = models.CharField(max_length=255, blank=True, null=True)
    localidad = models.CharField(max_length=120, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=60, blank=True, null=True)
    estado = models.CharField(max_length=15)
    creado_el = models.DateTimeField(blank=True, null=True)
    actualizado_el = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_dispositivo"
        unique_together = (("jurisdiccion", "denominacion", "tipo"),)
        db_table_comment = "El lugar donde se lleva a cabo la medida. Identificacion comun a los seis tipos: un identificador unico que el resto del sistema referencia sin conocer el tipo. Son los cinco campos que efectivamente aparecen en las seis hojas. Localidad y direccion faltan en la hoja Guardia Comisaria: omision senalada a la DNPYPI."


class RunacC3FamiliaAcogimiento(models.Model):
    id = models.BigAutoField(primary_key=True)
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    modalidad = models.CharField(max_length=8)
    id_provincial = models.CharField(max_length=60, blank=True, null=True)
    denominacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_familia_acogimiento"
        unique_together = (("jurisdiccion", "modalidad", "id_provincial"),)
        db_table_comment = "La planilla MPE informa dos modalidades en columnas paralelas, y hoy reune identificador y apellido de los cuidadores en un mismo campo. La separacion fue solicitada a la DNPYPI."


class RunacC3MedidaDae(models.Model):
    id = models.BigAutoField(primary_key=True)
    nino_adolescente = models.ForeignKey("RunacC3NinoAdolescente", models.DO_NOTHING)
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    dispositivo = models.ForeignKey(
        RunacC3Dispositivo,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="CAD o guardia especializada.",
    )
    fecha_hora_ingreso = models.DateTimeField(blank=True, null=True)
    fecha_hora_egreso = models.DateTimeField(blank=True, null=True)
    fuerza_interviniente = models.CharField(max_length=120, blank=True, null=True)
    dependencia = models.CharField(max_length=255, blank=True, null=True)
    tiempo_permanencia = models.CharField(max_length=60, blank=True, null=True)
    destino = models.CharField(max_length=120, blank=True, null=True)
    denuncia_por_apremios = models.CharField(max_length=30, blank=True, null=True)
    presentacion = models.ForeignKey(
        RunacC2Presentacion, models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "mir_c3_medida_dae"
        unique_together = (("nino_adolescente", "dispositivo", "fecha_hora_ingreso"),)
        db_table_comment = "Ingreso y egreso de CAD o permanencia en dependencia policial. A diferencia de las otras tres, describe un HECHO ya ocurrido: se acumula, no se actualiza. Puede haber varios por chico. El requerimiento advierte que no debe confundirse con una medida penal prolongada."


class RunacC3MedidaMpe(models.Model):
    id = models.BigAutoField(primary_key=True)
    nino_adolescente = models.ForeignKey("RunacC3NinoAdolescente", models.DO_NOTHING)
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_cese = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=12, blank=True, null=True)
    motivo_cese = models.CharField(max_length=255, blank=True, null=True)
    modalidad_cuidado = models.CharField(max_length=16, blank=True, null=True)
    dispositivo = models.ForeignKey(
        RunacC3Dispositivo,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Solo cuando la modalidad es residencial.",
    )
    familia = models.ForeignKey(
        RunacC3FamiliaAcogimiento,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Familia de acogimiento formal.",
    )
    familia_ampliada = models.ForeignKey(
        RunacC3FamiliaAcogimiento,
        models.DO_NOTHING,
        related_name="runacc3medidampe_familia_ampliada_set",
        blank=True,
        null=True,
        db_comment="Familia ampliada.",
    )
    motivo = models.CharField(max_length=255, blank=True, null=True)
    proyecto_restitucion = models.CharField(max_length=120, blank=True, null=True)
    participa_nya_en_per = models.CharField(max_length=30, blank=True, null=True)
    articulacion_per_plan_estadia = models.CharField(
        max_length=30, blank=True, null=True
    )
    intervencion_judicial = models.CharField(max_length=120, blank=True, null=True)
    control_legalidad_juzgado_familia = models.CharField(
        max_length=30, blank=True, null=True
    )
    adoptabilidad = models.CharField(max_length=60, blank=True, null=True)
    autonomia = models.CharField(max_length=60, blank=True, null=True)
    pae = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        db_comment="Programa de Acompanamiento para el Egreso.",
    )
    presentacion_alta = models.ForeignKey(
        RunacC2Presentacion, models.DO_NOTHING, blank=True, null=True
    )
    presentacion_actualizacion = models.ForeignKey(
        RunacC2Presentacion,
        models.DO_NOTHING,
        related_name="runacc3medidampe_presentacion_actualizacion_set",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "mir_c3_medida_mpe"
        unique_together = (("nino_adolescente", "jurisdiccion", "fecha_inicio"),)
        db_table_comment = "Medida de Proteccion Excepcional. La modalidad determina si se enlaza a un dispositivo residencial o a una familia."


class RunacC3MedidaMpi(models.Model):
    id = models.BigAutoField(primary_key=True)
    nino_adolescente = models.ForeignKey("RunacC3NinoAdolescente", models.DO_NOTHING)
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_cese = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=12, blank=True, null=True)
    motivo_cese = models.CharField(max_length=255, blank=True, null=True)
    origen_demanda = models.CharField(max_length=120, blank=True, null=True)
    causas = models.CharField(max_length=255, blank=True, null=True)
    destinatario = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        db_comment="La planilla lo agrupa entre los datos del chico, pero describe la medida.",
    )
    linea_de_accion = models.CharField(
        max_length=120, blank=True, null=True, db_comment="Idem."
    )
    plazo_previsto = models.CharField(max_length=120, blank=True, null=True)
    referente_adulto = models.ForeignKey(
        "RunacC3ReferenteAdulto", models.DO_NOTHING, blank=True, null=True
    )
    relacion_vincular = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        db_comment="Vinculo del referente con este chico.",
    )
    unidad_interviniente = models.ForeignKey(
        "RunacC3UnidadInterviniente",
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Referencia normalizada.",
    )
    unidad_denominacion_informada = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_comment="Tal como la informo la jurisdiccion. Sostiene la trazabilidad.",
    )
    unidad_dependencia = models.CharField(max_length=255, blank=True, null=True)
    unidad_localidad = models.CharField(max_length=120, blank=True, null=True)
    unidad_domicilio = models.CharField(max_length=255, blank=True, null=True)
    unidad_equipo = models.CharField(max_length=255, blank=True, null=True)
    unidad_responsable = models.CharField(max_length=255, blank=True, null=True)
    unidad_telefono = models.CharField(max_length=60, blank=True, null=True)
    unidad_mail = models.CharField(max_length=120, blank=True, null=True)
    presentacion_alta = models.ForeignKey(
        RunacC2Presentacion, models.DO_NOTHING, blank=True, null=True
    )
    presentacion_actualizacion = models.ForeignKey(
        RunacC2Presentacion,
        models.DO_NOTHING,
        related_name="runacc3medidampi_presentacion_actualizacion_set",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "mir_c3_medida_mpi"
        unique_together = (("nino_adolescente", "jurisdiccion", "fecha_inicio"),)
        db_table_comment = (
            "Medida de Proteccion Integral. Se actualiza cuando presenta novedades."
        )


class RunacC3MedidaMpj(models.Model):
    id = models.BigAutoField(primary_key=True)
    nino_adolescente = models.ForeignKey("RunacC3NinoAdolescente", models.DO_NOTHING)
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_cese = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=12, blank=True, null=True)
    descripcion_causa_penal = models.CharField(max_length=500, blank=True, null=True)
    dependencia_judicial = models.CharField(max_length=255, blank=True, null=True)
    situacion_procesal = models.CharField(max_length=120, blank=True, null=True)
    monto_de_la_pena = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    dispositivo = models.ForeignKey(
        RunacC3Dispositivo,
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Dispositivo penal donde se encuentra el adolescente.",
    )
    fecha_ingreso_dispositivo = models.DateField(blank=True, null=True)
    edad_al_ingreso = models.IntegerField(blank=True, null=True)
    procedencia = models.CharField(max_length=120, blank=True, null=True)
    procedencia_dispositivo = models.ForeignKey(
        RunacC3Dispositivo,
        models.DO_NOTHING,
        related_name="runacc3medidampj_procedencia_dispositivo_set",
        blank=True,
        null=True,
        db_comment="Cuando la procedencia es otro dispositivo del padron.",
    )
    fecha_egreso_dispositivo = models.DateField(blank=True, null=True)
    destino_al_egreso = models.CharField(max_length=120, blank=True, null=True)
    destino_dispositivo = models.ForeignKey(
        RunacC3Dispositivo,
        models.DO_NOTHING,
        related_name="runacc3medidampj_destino_dispositivo_set",
        blank=True,
        null=True,
        db_comment="Cuando el egreso es hacia otro dispositivo penal.",
    )
    presentacion_alta = models.ForeignKey(
        RunacC2Presentacion, models.DO_NOTHING, blank=True, null=True
    )
    presentacion_actualizacion = models.ForeignKey(
        RunacC2Presentacion,
        models.DO_NOTHING,
        related_name="runacc3medidampj_presentacion_actualizacion_set",
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = "mir_c3_medida_mpj"
        unique_together = (("nino_adolescente", "jurisdiccion", "fecha_inicio"),)
        db_table_comment = "Medida Penal Juvenil. Referencia hasta tres dispositivos: el actual, la procedencia y el destino al egreso. DEFINICION PENDIENTE: como informan las jurisdicciones el traslado de un adolescente entre dispositivos por la misma causa penal."


class RunacC3NinoAdolescente(models.Model):
    id = models.BigAutoField(primary_key=True)
    persona = models.OneToOneField("RunacC3Persona", models.DO_NOTHING)
    apellidos = models.CharField(max_length=120, blank=True, null=True)
    nombres = models.CharField(max_length=120, blank=True, null=True)
    situacion_documentacion = models.CharField(max_length=60, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    genero = models.CharField(max_length=30, blank=True, null=True)
    pais_nacimiento = models.CharField(max_length=120, blank=True, null=True)
    asiste_institucion_educativa = models.CharField(
        max_length=30, blank=True, null=True
    )
    maximo_nivel_educativo = models.CharField(max_length=60, blank=True, null=True)
    cobertura_salud = models.CharField(max_length=60, blank=True, null=True)
    enfermedad_cronica = models.CharField(max_length=30, blank=True, null=True)
    problematica_salud = models.CharField(max_length=255, blank=True, null=True)
    consumo_problematico = models.CharField(max_length=30, blank=True, null=True)
    presenta_discapacidad = models.CharField(max_length=30, blank=True, null=True)
    tipo_discapacidad = models.CharField(max_length=60, blank=True, null=True)
    posee_cud = models.CharField(max_length=30, blank=True, null=True)
    seguridad_social = models.CharField(max_length=60, blank=True, null=True)
    asignacion_universal_por_hijo = models.CharField(
        max_length=30, blank=True, null=True
    )
    pueblo_originario = models.CharField(max_length=30, blank=True, null=True)
    pueblo_originario_especificar = models.CharField(
        max_length=120, blank=True, null=True
    )
    tiene_hijos = models.CharField(max_length=30, blank=True, null=True)
    domicilio_actual = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_comment="Solo lo releva el MPI: en proteccion integral el chico vive ahi.",
    )
    provincia = models.CharField(max_length=120, blank=True, null=True)
    localidad = models.CharField(max_length=120, blank=True, null=True)
    partido = models.CharField(max_length=120, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    creado_el = models.DateTimeField(blank=True, null=True)
    actualizado_el = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_nino_adolescente"
        db_table_comment = "Todo lo relevado sobre el chico, con independencia del archivo que lo informo y de la medida que tenga: la medida es circunstancial y el chico no. UNA fila por chico, con el dato vigente; si una presentacion informa un valor distinto se actualiza y el cambio va a mir_c3_cambio, que es la fuente de las series historicas."


class RunacC3NyaIdProvincial(models.Model):
    id = models.BigAutoField(primary_key=True)
    nino_adolescente = models.ForeignKey(RunacC3NinoAdolescente, models.DO_NOTHING)
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    identificador = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = "mir_c3_nya_id_provincial"
        unique_together = (("jurisdiccion", "identificador"),)
        db_table_comment = "Identificador provincial del chico. Uno por jurisdiccion: un chico informado por dos provincias tiene un identificador en cada una y ambos lo designan. Debe ser obligatorio y estable en el tiempo. FALTA EN EL MPI: omision senalada a la DNPYPI."


class RunacC3Origen(models.Model):
    id = models.BigAutoField(primary_key=True)
    entidad = models.CharField(
        max_length=40, db_comment="Tabla de Capa 3 a la que pertenece el registro."
    )
    entidad_id = models.BigIntegerField()
    presentacion = models.ForeignKey(RunacC2Presentacion, models.DO_NOTHING)
    importacion = models.ForeignKey(RunacC2Importacion, models.DO_NOTHING)
    numero_fila = models.IntegerField(blank=True, null=True)
    accion = models.CharField(max_length=13, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_origen"
        db_table_comment = "Responde de donde salio cada dato: provincia, periodo, archivo, hoja, fila y version."


class RunacC3Persona(models.Model):
    id = models.BigAutoField(
        primary_key=True, db_comment="ID SISOC. Se asigna una vez y no cambia."
    )
    ciudadano_id = models.BigIntegerField(
        blank=True,
        null=True,
        db_comment="Vinculo con ciudadanos.Ciudadano de SISOC. Definicion pendiente.",
    )
    tipo_documento = models.CharField(max_length=30, blank=True, null=True)
    numero_documento = models.CharField(max_length=20, blank=True, null=True)
    cuil = models.CharField(max_length=13, blank=True, null=True)
    creada_el = models.DateTimeField(blank=True, null=True)
    actualizada_el = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_persona"
        unique_together = (("tipo_documento", "numero_documento"),)
        db_table_comment = "El mismo ser humano, y unicamente su identidad resuelta. Todo lo relevado sobre una persona vive en su caracterizacion: nino o adolescente, o referente adulto. Una misma persona puede tener las dos."


class RunacC3Precedencia(models.Model):
    id = models.BigAutoField(primary_key=True)
    entidad = models.CharField(max_length=40)
    entidad_id = models.BigIntegerField(blank=True, null=True)
    campo = models.CharField(max_length=100)
    valor_elegido = models.TextField(blank=True, null=True)
    regla = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        db_comment="Jerarquia por archivo, ultimo informado, fuente externa, o decision manual.",
    )
    usuario = models.CharField(max_length=150, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_precedencia"
        db_table_comment = "La decision sobre que valor prevalece, conservada para las presentaciones siguientes: la misma discrepancia no se resuelve dos veces."


class RunacC3ReferenteAdulto(models.Model):
    id = models.BigAutoField(primary_key=True)
    persona = models.OneToOneField(RunacC3Persona, models.DO_NOTHING)
    apellidos = models.CharField(max_length=120, blank=True, null=True)
    nombres = models.CharField(max_length=120, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=30, blank=True, null=True)
    nacionalidad = models.CharField(max_length=120, blank=True, null=True)
    domicilio_actual = models.CharField(max_length=255, blank=True, null=True)
    provincia = models.CharField(max_length=120, blank=True, null=True)
    localidad = models.CharField(max_length=120, blank=True, null=True)
    partido = models.CharField(max_length=120, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=60, blank=True, null=True)
    mail = models.CharField(max_length=120, blank=True, null=True)
    nivel_escolar = models.CharField(max_length=60, blank=True, null=True)
    situacion_laboral = models.CharField(max_length=60, blank=True, null=True)
    creado_el = models.DateTimeField(blank=True, null=True)
    actualizado_el = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_referente_adulto"
        db_table_comment = "18 campos, informados unicamente en el MPI. Limitacion: la planilla no preve identificador propio del referente; sin documento, cada presentacion lo registra como un adulto distinto."


class RunacC3UnidadAlias(models.Model):
    id = models.BigAutoField(primary_key=True)
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    denominacion_informada = models.CharField(max_length=255)
    unidad_interviniente = models.ForeignKey(
        "RunacC3UnidadInterviniente",
        models.DO_NOTHING,
        blank=True,
        null=True,
        db_comment="Vacio mientras esta pendiente de normalizar.",
    )
    estado = models.CharField(max_length=9)
    resuelta_por = models.CharField(max_length=150, blank=True, null=True)
    resuelta_el = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mir_c3_unidad_alias"
        unique_together = (("jurisdiccion", "denominacion_informada"),)
        db_table_comment = "El diccionario. Opera en la importacion (Capa 2) y se perfecciona en cada iteracion: lo ya conocido se resuelve solo, lo nuevo queda pendiente y su resolucion incorpora una entrada para la proxima vez. Su mejora se puede aplicar a lo ya consolidado; ese reproceso queda en mir_c3_cambio."


class RunacC3UnidadInterviniente(models.Model):
    id = models.BigAutoField(primary_key=True)
    jurisdiccion = models.ForeignKey(RunacC2Jurisdiccion, models.DO_NOTHING)
    denominacion_normalizada = models.CharField(max_length=255)
    dependencia = models.CharField(max_length=255, blank=True, null=True)
    tipo_espacio = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        db_comment="Recomendado a la DNPYPI: servicio local, programa municipal, programa provincial, hogar o residencia, centro de dia, otro.",
    )

    class Meta:
        managed = False
        db_table = "mir_c3_unidad_interviniente"
        unique_together = (("jurisdiccion", "denominacion_normalizada"),)
        db_table_comment = "Tabla referencial de servicios, equipos y programas de proteccion integral. No es un padron que las jurisdicciones completen: se construye con lo que efectivamente se informa. El universo es abierto y por eso no admite un padron cerrado."
