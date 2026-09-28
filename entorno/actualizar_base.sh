#!/usr/bin/env bash
# Pone al día la base de una instalación que ya existía, SIN borrar lo cargado.
#
# Aplica los guiones de la definición que se agregaron después de armarla y
# que todavía no tiene. Cada uno se aplica una sola vez: si ya está, se saltea.
# Uso, desde la carpeta del repositorio y con el compose levantado:
#
#     bash entorno/actualizar_base.sh
#
# Para empezar de cero hace falta otra cosa: `docker compose down -v` borra la
# base entera, y al volver a levantar se carga `entorno/base_inicial.sql`.
set -euo pipefail
export MSYS_NO_PATHCONV=1
BASE="${DATABASE_NAME:-runac}"

sql() {
  docker compose exec -T mysql sh -c "mysql -uroot -p\"\$MYSQL_ROOT_PASSWORD\" --default-character-set=utf8mb4 -N $BASE" 2>/dev/null
}

hay_columna() {
  echo "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='$BASE' AND table_name='$1' AND column_name='$2';" | sql
}

echo "Base: $BASE"

# 35 · nombre corto de cada archivo (27-09-2026)
if [ "$(hay_columna mir_c1_archivo nombre_corto)" = "0" ]; then
  sql < entorno/sql/35_nombre_corto_del_archivo.sql
  echo "  aplicado: 35 · nombre corto de los archivos"
else
  echo "  ya estaba: 35 · nombre corto de los archivos"
fi

# 36 · provincias del operativo (27-09-2026). Se puede repetir sin problema.
sql < entorno/sql/36_provincias_del_operativo.sql
echo "  aplicado: 36 · provincias del operativo"

echo "Listo. Reiniciar la web para que tome los cambios: docker compose restart web"
