#!/usr/bin/env bash
# Recorre el MIR de punta a punta con los seis usuarios de prueba, sobre una
# base descartable que arma desde entorno/base_inicial.sql y borra al terminar.
# No toca ninguna base de trabajo. Uso, desde la carpeta del repositorio:
#
#     bash entorno/pruebas/recorrido_completo.sh
#
# Necesita el compose levantado (servicios web y mysql).
set -euo pipefail
# En Git Bash, sin esto «/app» se convierte en una ruta de Windows.
export MSYS_NO_PATHCONV=1
BASE=descartable_recorrido
sed "8,9s/\`runac\`/\`$BASE\`/" entorno/base_inicial.sql \
  | docker compose exec -T mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" 2>/dev/null'
trap 'docker compose exec -T mysql sh -c "mysql -uroot -p\"\$MYSQL_ROOT_PASSWORD\" -e \"DROP DATABASE IF EXISTS '$BASE'\" 2>/dev/null"' EXIT
docker compose exec -T -w /app -e PYTHONPATH=/app -e DATABASE_NAME=$BASE -e RUNAC_DB_NAME=$BASE web \
  python entorno/pruebas/recorrido_completo.py 2>&1 | grep -v "^Bad Request\|^Forbidden\|^Conflict\|^Not Found"
