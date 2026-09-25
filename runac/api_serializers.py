"""Forma de las respuestas de la API del front v2.

Sólo describen la salida: la API no recibe datos todavía. Existen para que el
contrato quede escrito en un lugar —el esquema OpenAPI sale de acá— y para que
un cambio en un service que rompa la forma se note en los tests y no en el
navegador.

Los nombres van en snake_case, como en el resto de SISOC: el front los usa
tal como vienen.
"""

# Son de sólo salida: nunca crean ni actualizan nada, así que no implementan
# create() ni update(), y pylint lo marca en cada uno.
# pylint: disable=abstract-method

from rest_framework import serializers


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
