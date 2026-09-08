"""Configuración de pytest para el prototipo.

Los modelos son `managed = False`: la estructura la crea la Capa 1, no Django.
Por eso los tests no crean base de datos, salvo los marcados `mysql_compat`,
que corren contra la base de trabajo real —el mismo criterio que usa SISOC.
"""

import django
from django.conf import settings


def pytest_configure():
    if not settings.configured:  # pragma: no cover
        django.setup()
