# Prototipo de RUNAC. Mismas versiones que SISOC, para que lo que se escriba acá
# se pueda mudar al repositorio sin sorpresas.
FROM python:3.11.15-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev build-essential pkg-config default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
      Django==5.2.16 \
      mysqlclient==2.1.1 \
      django-crispy-forms==2.5 \
      crispy-bootstrap5==2024.10 \
      djangorestframework==3.16.1 \
      openpyxl==3.1.5 \
      pandas==2.3.1 \
      mysql-connector-python==9.1.0

# Tooling de calidad: las MISMAS versiones que SISOC (requirements/dev.txt,
# lint.txt y test.txt). Es lo que exige AGENTS.md > Validacion.
RUN pip install --no-cache-dir \
      black==24.8.0 \
      pylint==3.2.6 \
      pylint-django==2.7.0 \
      pylint-plugin-utils==0.8.2 \
      djlint==1.34.2 \
      pytest==8.3.5 \
      pytest-django==4.11.1 \
      pytest-mock==3.14.1 \
      pytest-xdist==3.6.1

WORKDIR /app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
