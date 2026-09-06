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

WORKDIR /app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
