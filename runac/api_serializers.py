"""Forma de las respuestas de la API del front v2.

Describen la salida —y, donde la API recibe datos, la entrada—. Existen para
que el contrato quede escrito en un lugar —el esquema OpenAPI sale de acá— y
para que un cambio en un service que rompa la forma se note en los tests y no
en el navegador.

Los nombres van en snake_case, como en el resto de SISOC: el front los usa
tal como vienen.
"""

# Los de salida nunca crean ni actualizan nada, así que no implementan create()
# ni update(), y pylint lo marca en cada uno.
# pylint: disable=abstract-method

from rest_framework import serializers

# ---------------------------------------------------------------------------
# Comunes
# ---------------------------------------------------------------------------


class PermisosSerializer(serializers.Serializer):
    cargar = serializers.BooleanField()
    presentar = serializers.BooleanField()
    editar_datos = serializers.BooleanField()
    revisar = serializers.BooleanField()
    administrar = serializers.BooleanField()


class SeccionSerializer(serializers.Serializer):
    clave = serializers.CharField()
    etiqueta = serializers.CharField()
    detalle = serializers.CharField(allow_blank=True)
    # Mientras convivan las dos versiones, una sección que todavía no se migró
    # lleva a la pantalla vieja. `en_v2` dice cuál de las dos es.
    ruta = serializers.CharField()
    en_v2 = serializers.BooleanField()


class SesionSerializer(serializers.Serializer):
    # El nombre con que se presenta la implementación: RUNAC, PAE… Es el
    # primer término del vocabulario de la instancia.
    instancia = serializers.CharField()
    usuario = serializers.CharField()
    rol = serializers.CharField(allow_null=True)
    nombre_del_rol = serializers.CharField()
    es_nacional = serializers.BooleanField()
    jurisdiccion = serializers.CharField(allow_null=True)
    permisos = PermisosSerializer()
    menu = SeccionSerializer(many=True)
    csrf_token = serializers.CharField()
    salir = serializers.CharField()
    # La etiqueta «datos de prueba». Vacía cuando no corresponde mostrarla.
    aviso = serializers.CharField(allow_blank=True)


class PeriodoSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    estado = serializers.CharField()
    fecha_desde = serializers.DateField()
    fecha_hasta = serializers.DateField()


class MensajeSerializer(serializers.Serializer):
    """Lo que devuelve una acción: qué pasó, dicho para una persona."""

    mensaje = serializers.CharField()


class HallazgoResumidoSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    severidad = serializers.CharField()
    casos = serializers.IntegerField()
    ejemplo = serializers.CharField(allow_null=True)


# ---------------------------------------------------------------------------
# Inicio
# ---------------------------------------------------------------------------


class ArchivoDelPeriodoSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre = serializers.CharField(allow_blank=True)
    obligatorio = serializers.BooleanField()
    campos = serializers.IntegerField()
    reglas = serializers.IntegerField()
    estado = serializers.CharField()
    filas = serializers.IntegerField(allow_null=True)
    bloqueantes = serializers.IntegerField()
    advertencias = serializers.IntegerField()


class PresentacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    estado = serializers.CharField()
    estado_legible = serializers.CharField()


class AvanceSerializer(serializers.Serializer):
    cargados = serializers.IntegerField()
    total = serializers.IntegerField()


class InicioSerializer(serializers.Serializer):
    periodos = PeriodoSerializer(many=True)
    periodo = PeriodoSerializer(allow_null=True)
    jurisdiccion = serializers.CharField(allow_null=True)
    # Sólo el nivel nacional elige jurisdicción; para el provincial va vacía.
    jurisdicciones = serializers.ListField(child=serializers.CharField())
    presentacion = PresentacionSerializer(allow_null=True)
    archivos = ArchivoDelPeriodoSerializer(many=True)
    avance = AvanceSerializer()


class EstadoDelPeriodoSerializer(serializers.Serializer):
    """Lo que se pide para abrir, cerrar o volver a preparar un período."""

    estado = serializers.ChoiceField(choices=["PREPARACION", "ABIERTO", "CERRADO"])


class PeriodoCambiadoSerializer(serializers.Serializer):
    estado = serializers.CharField()
    mensaje = serializers.CharField()
    aviso = serializers.CharField(allow_blank=True)


# ---------------------------------------------------------------------------
# Plantillas
# ---------------------------------------------------------------------------


class PlantillaSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre = serializers.CharField(allow_blank=True)
    hojas = serializers.IntegerField()
    campos = serializers.IntegerField()
    obligatorio = serializers.BooleanField()
    descarga = serializers.CharField()


class PlantillasSerializer(serializers.Serializer):
    periodos = PeriodoSerializer(many=True)
    periodo = PeriodoSerializer(allow_null=True)
    archivos = PlantillaSerializer(many=True)
    descarga_todas = serializers.CharField(allow_blank=True)


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------


class ArchivoACargarSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre = serializers.CharField(allow_blank=True)
    obligatorio = serializers.BooleanField()
    estado = serializers.CharField()
    importada = serializers.BooleanField()
    filas = serializers.IntegerField(allow_null=True)
    # De la importación vigente: es lo que se pierde al reemplazarla, y se dice
    # en la confirmación.
    advertencias = serializers.IntegerField(allow_null=True)
    correcciones = serializers.IntegerField()
    # Lo que nombra, esté importado o no: se muestra siempre, para que se sepa
    # antes de intentar. Y lo que falta de eso, que es lo que traba.
    necesita = serializers.ListField(child=serializers.CharField())
    bloqueado_por = serializers.ListField(child=serializers.CharField())
    nombre_sugerido = serializers.CharField()


class CargaSerializer(serializers.Serializer):
    periodos = PeriodoSerializer(many=True)
    periodo = PeriodoSerializer(allow_null=True)
    jurisdiccion = serializers.CharField(allow_null=True)
    jurisdicciones = serializers.ListField(child=serializers.CharField())
    estado_legible = serializers.CharField()
    carga_abierta = serializers.BooleanField()
    puede_cargar = serializers.BooleanField()
    listo = serializers.BooleanField()
    archivos = ArchivoACargarSerializer(many=True)


class ResultadoDeImportarSerializer(serializers.Serializer):
    """Cómo le fue a un archivo recién subido."""

    rechazado = serializers.BooleanField()
    mensaje = serializers.CharField(allow_blank=True)
    importacion_id = serializers.IntegerField(allow_null=True)
    estado = serializers.CharField(allow_null=True)
    filas = serializers.IntegerField(allow_null=True)
    bloqueantes = serializers.IntegerField()
    advertencias = serializers.IntegerField()


# ---------------------------------------------------------------------------
# Resultado y circuito
# ---------------------------------------------------------------------------


class ImportacionBreveSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    estado = serializers.CharField()
    filas_leidas = serializers.IntegerField(allow_null=True)
    filas_incorporadas = serializers.IntegerField(allow_null=True)
    bloqueantes = serializers.IntegerField()
    advertencias = serializers.IntegerField()


class ArchivoDelResultadoSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre = serializers.CharField(allow_blank=True)
    estado = serializers.CharField()
    importada = serializers.BooleanField()
    importacion = ImportacionBreveSerializer(allow_null=True)
    resumen = HallazgoResumidoSerializer(many=True)


class AccionSerializer(serializers.Serializer):
    accion = serializers.CharField()
    etiqueta = serializers.CharField()
    ayuda = serializers.CharField()


class ObservacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    estado = serializers.CharField()
    texto = serializers.CharField()
    usuario_observa = serializers.CharField(allow_null=True)
    creada_el = serializers.DateTimeField(allow_null=True)
    archivo_codigo = serializers.CharField(allow_null=True)
    numero_fila = serializers.IntegerField(allow_null=True)
    respuesta = serializers.CharField(allow_null=True)
    usuario_responde = serializers.CharField(allow_null=True)
    respondida_el = serializers.DateTimeField(allow_null=True)


class PasoSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    actual = serializers.BooleanField()


class PresentacionDelResultadoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    estado = serializers.CharField()
    estado_legible = serializers.CharField()
    estado_ayuda = serializers.CharField(allow_blank=True)
    version = serializers.IntegerField(allow_null=True)
    expediente = serializers.CharField(allow_null=True)


class TotalesSerializer(serializers.Serializer):
    filas = serializers.IntegerField()
    validas = serializers.IntegerField()
    bloqueantes = serializers.IntegerField()
    advertencias = serializers.IntegerField()


class ResultadoSerializer(serializers.Serializer):
    periodos = PeriodoSerializer(many=True)
    periodo = PeriodoSerializer(allow_null=True)
    jurisdiccion = serializers.CharField(allow_null=True)
    jurisdicciones = serializers.ListField(child=serializers.CharField())
    presentacion = PresentacionDelResultadoSerializer(allow_null=True)
    pasos = PasoSerializer(many=True)
    archivos = ArchivoDelResultadoSerializer(many=True)
    totales = TotalesSerializer()
    acciones = AccionSerializer(many=True)
    observaciones = ObservacionSerializer(many=True)
    puede_responder = serializers.BooleanField()
    puede_presentar = serializers.BooleanField()
    puede_editar = serializers.BooleanField()
    listo = serializers.BooleanField()


class AccionHechaSerializer(serializers.Serializer):
    estado = serializers.CharField()
    estado_legible = serializers.CharField()
    mensaje = serializers.CharField()


class NuevaObservacionSerializer(serializers.Serializer):
    texto = serializers.CharField()
    importacion_id = serializers.IntegerField(required=False, allow_null=True)
    numero_fila = serializers.IntegerField(required=False, allow_null=True)


class RespuestaSerializer(serializers.Serializer):
    respuesta = serializers.CharField()


class ExpedienteSerializer(serializers.Serializer):
    expediente = serializers.CharField(max_length=100)


class PresentacionEnRevisionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    jurisdiccion = serializers.CharField()
    estado = serializers.CharField()
    estado_legible = serializers.CharField()
    version = serializers.IntegerField(allow_null=True)
    importados = serializers.IntegerField()
    observaciones = serializers.IntegerField()
    cerrada_el = serializers.DateTimeField(allow_null=True)
    expediente = serializers.CharField(allow_null=True)
    acciones = AccionSerializer(many=True)
    puede_observar = serializers.BooleanField()


class RevisionSerializer(serializers.Serializer):
    periodos = PeriodoSerializer(many=True)
    periodo = PeriodoSerializer(allow_null=True)
    es_revisor = serializers.BooleanField()
    presentaciones = PresentacionEnRevisionSerializer(many=True)


class ArchivoDelComprobanteSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    nombre_archivo = serializers.CharField(allow_null=True)
    filas_incorporadas = serializers.IntegerField(allow_null=True)
    iniciada_el = serializers.DateTimeField(allow_null=True)


class ComprobanteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    version = serializers.IntegerField(allow_null=True)
    estado = serializers.CharField()
    presentada_el = serializers.DateTimeField(allow_null=True)
    usuario_presenta = serializers.CharField(allow_null=True)
    expediente = serializers.CharField(allow_null=True)
    jurisdiccion = serializers.CharField()
    periodo = serializers.CharField()
    fecha_desde = serializers.DateField()
    fecha_hasta = serializers.DateField()
    archivos = ArchivoDelComprobanteSerializer(many=True)


# ---------------------------------------------------------------------------
# Detalle de una importación
# ---------------------------------------------------------------------------


class ImportacionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    archivo_codigo = serializers.CharField(allow_null=True)
    nombre_archivo = serializers.CharField(allow_null=True)
    estado = serializers.CharField()
    filas_leidas = serializers.IntegerField(allow_null=True)
    filas_incorporadas = serializers.IntegerField(allow_null=True)
    bloqueantes = serializers.IntegerField(allow_null=True)
    advertencias = serializers.IntegerField(allow_null=True)
    duracion_ms = serializers.IntegerField(allow_null=True)
    jurisdiccion = serializers.CharField(allow_null=True)
    periodo = serializers.CharField(allow_null=True)


class ErrorDelArchivoSerializer(serializers.Serializer):
    tipo = serializers.CharField()
    hoja = serializers.CharField(allow_null=True)
    numero_fila = serializers.IntegerField(allow_null=True)
    esperado = serializers.CharField(allow_null=True)
    encontrado = serializers.CharField(allow_null=True)
    descripcion = serializers.CharField(allow_null=True)


class DescargasSerializer(serializers.Serializer):
    errores = serializers.CharField()
    marcado = serializers.CharField()


class DetalleSerializer(serializers.Serializer):
    importacion = ImportacionSerializer()
    hojas = serializers.ListField(child=serializers.CharField())
    errores_archivo = ErrorDelArchivoSerializer(many=True)
    resumen = HallazgoResumidoSerializer(many=True)
    # Si todos los hallazgos son de una misma severidad, cuál: no hace falta
    # ni la columna ni el filtro.
    severidad_unica = serializers.CharField(allow_null=True)
    puede_editar = serializers.BooleanField()
    descargas = DescargasSerializer()


class HallazgoSerializer(serializers.Serializer):
    numero_fila = serializers.IntegerField(allow_null=True)
    nombre_hoja = serializers.CharField(allow_null=True)
    columna = serializers.CharField(allow_null=True)
    nombre_campo = serializers.CharField(allow_null=True)
    severidad = serializers.CharField()
    codigo = serializers.CharField()
    valor_encontrado = serializers.CharField(allow_null=True)
    descripcion = serializers.CharField(allow_null=True)
    identificador_registro = serializers.CharField(allow_null=True)


# ---------------------------------------------------------------------------
# Edición de datos
# ---------------------------------------------------------------------------


class ContextoDeEdicionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    archivo_codigo = serializers.CharField()
    jurisdiccion = serializers.CharField()
    periodo = serializers.CharField()
    version = serializers.IntegerField()
    estado_presentacion = serializers.CharField()
    estado_legible = serializers.CharField()
    editable = serializers.BooleanField()


class HojaSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()


class AvisoDeFilaSerializer(serializers.Serializer):
    nombre_campo = serializers.CharField(allow_null=True)
    severidad = serializers.CharField()
    descripcion = serializers.CharField(allow_null=True)


class CeldaSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    titulo = serializers.CharField()
    obligatorio = serializers.BooleanField()
    tipo_dato = serializers.CharField(allow_null=True)
    valor = serializers.CharField(allow_blank=True)
    opciones = serializers.ListField(child=serializers.CharField())
    tiene_aviso = serializers.BooleanField()


class FilaDeDatosSerializer(serializers.Serializer):
    numero_fila = serializers.IntegerField()
    estado = serializers.CharField(allow_null=True)
    avisos = AvisoDeFilaSerializer(many=True)
    celdas = CeldaSerializer(many=True)


class CambioSerializer(serializers.Serializer):
    numero_fila = serializers.IntegerField(allow_null=True)
    documento = serializers.CharField(allow_blank=True)
    campo = serializers.CharField(allow_null=True)
    valor_anterior = serializers.CharField(allow_null=True)
    valor_nuevo = serializers.CharField(allow_null=True)
    motivo = serializers.CharField(allow_null=True)
    usuario = serializers.CharField(allow_null=True)
    fecha = serializers.DateTimeField(allow_null=True)


class DatosSerializer(serializers.Serializer):
    contexto = ContextoDeEdicionSerializer()
    hojas = HojaSerializer(many=True)
    hoja = HojaSerializer()
    puede_editar = serializers.BooleanField()
    total = serializers.IntegerField()
    pagina = serializers.IntegerField()
    paginas = serializers.IntegerField()
    con_advertencia = serializers.IntegerField()
    filas = FilaDeDatosSerializer(many=True)
    historial = CambioSerializer(many=True)


class CorreccionSerializer(serializers.Serializer):
    """Lo que se manda para corregir un dato."""

    hoja_id = serializers.IntegerField()
    numero_fila = serializers.IntegerField()
    campo = serializers.CharField()
    valor = serializers.CharField(allow_blank=True)
    motivo = serializers.CharField(allow_blank=True, required=False, default="")


class CorreccionHechaSerializer(serializers.Serializer):
    sin_cambios = serializers.BooleanField()
    valor = serializers.CharField(allow_blank=True)
    advertencias = serializers.IntegerField()
    # Lo que quedó observado en ESTE campo con el valor nuevo: guardar y quedar
    # bien no son lo mismo.
    observaciones = serializers.ListField(child=serializers.CharField())


# ---------------------------------------------------------------------------
# Reglas
# ---------------------------------------------------------------------------


class HojaDeReglasSerializer(serializers.Serializer):
    clave = serializers.CharField()
    etiqueta = serializers.CharField()


class ValoresAdmitidosSerializer(serializers.Serializer):
    texto = serializers.CharField(allow_blank=True)
    detalle = serializers.CharField(allow_blank=True)
    opciones = serializers.ListField(child=serializers.CharField())


class TechoSerializer(serializers.Serializer):
    """Un rango: desde dónde y hasta dónde, escrito como se lee en castellano."""

    minimo = serializers.CharField(allow_blank=True)
    maximo = serializers.CharField(allow_blank=True)
    texto = serializers.CharField(allow_blank=True)
    compartida = serializers.BooleanField()


class RangosSerializer(serializers.Serializer):
    avisa = TechoSerializer(allow_null=True)
    frena = TechoSerializer(allow_null=True)


class CondicionSerializer(serializers.Serializer):
    aplicacion_id = serializers.IntegerField()
    severidad = serializers.CharField()
    texto = serializers.CharField(allow_blank=True)


class CampoDeReglasSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    letra = serializers.CharField()
    titulo = serializers.CharField()
    nombre = serializers.CharField(allow_blank=True)
    ayuda = serializers.CharField(allow_blank=True)
    obligatorio = serializers.BooleanField()
    condicionado = serializers.BooleanField()
    numerico = serializers.BooleanField()
    valores = ValoresAdmitidosSerializer()
    rangos = RangosSerializer()
    otras = CondicionSerializer(many=True)


class ReglasSerializer(serializers.Serializer):
    hojas = HojaDeReglasSerializer(many=True)
    hoja = serializers.CharField(allow_blank=True)
    ver_tecnico = serializers.BooleanField()
    puede_editar = serializers.BooleanField()
    periodo_abierto = serializers.CharField(allow_null=True)
    campos = CampoDeReglasSerializer(many=True)


class CambioDeCampoSerializer(serializers.Serializer):
    campo_id = serializers.IntegerField()
    obligatorio = serializers.BooleanField(required=False)
    # Los dos límites de cada techo viajan juntos o no viajan: si sólo llegara
    # uno, el ausente se leería como «vaciado».
    advierte = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        min_length=2,
        max_length=2,
        required=False,
    )
    bloquea = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        min_length=2,
        max_length=2,
        required=False,
    )


class SeveridadNuevaSerializer(serializers.Serializer):
    aplicacion_id = serializers.IntegerField()
    severidad = serializers.ChoiceField(choices=["ADVERTENCIA", "BLOQUEANTE"])


class CambiosDeReglasSerializer(serializers.Serializer):
    cambios = CambioDeCampoSerializer(many=True, required=False, default=list)
    severidades = SeveridadNuevaSerializer(many=True, required=False, default=list)


class ReglasGuardadasSerializer(serializers.Serializer):
    mensaje = serializers.CharField()
    detalle = serializers.ListField(child=serializers.CharField())
    errores = serializers.ListField(child=serializers.CharField())


class PaginaDeHallazgosSerializer(serializers.Serializer):
    """Una página de hallazgos, con la forma estándar de DRF."""

    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = HallazgoSerializer(many=True)
