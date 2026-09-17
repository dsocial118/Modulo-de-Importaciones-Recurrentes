#!/usr/bin/env bash
# MIR — implementación RUNAC. Deja el sistema andando desde cero.
#
#   bash entorno/preparar.sh
#
# Se puede correr dos veces: si la base ya está armada, avisa y no toca nada.
# Anda con Git Bash en Windows.

set -euo pipefail

BASE="${DATABASE_NAME:-runac}"
CLAVE="${DATABASE_PASSWORD:-runac_local}"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$AQUI")"
cd "$RAIZ"

# Todas las invocaciones de mysql llevan --default-character-set=utf8mb4. Sin
# eso los acentos se cargan mal y el problema aparece mucho después.
mysql_en_el_contenedor() {
  # -h 127.0.0.1 fuerza TCP. Sin eso el cliente busca un socket que en la
  # imagen de MySQL 8.4 no está donde él espera, y falla con un error que no
  # dice nada del verdadero motivo.
  docker compose exec -T mysql mysql --default-character-set=utf8mb4 \
    -h 127.0.0.1 -uroot -p"$CLAVE" "$@"
}

echo "== 1. Levantando los contenedores =="
docker compose up -d

echo
echo "== 2. Esperando a que la base esté realmente lista =="
# La imagen de MySQL arranca DOS veces: primero un servidor temporal para
# inicializarse, que responde por el socket y no por TCP, y después el
# definitivo. Entre los dos hay una ventana en la que la base parece estar y no
# está, y ahí es donde se cae la carga con un error que no dice nada del
# verdadero motivo.
#
# Por eso se exige una consulta de verdad, por TCP, TRES veces seguidas. Una
# sola respuesta puede ser la del servidor temporal.
seguidas=0
for intento in $(seq 1 90); do
  if docker compose exec -T mysql mysql -h 127.0.0.1 -uroot -p"$CLAVE" \
       -N -B -e "SELECT 1" >/dev/null 2>&1; then
    seguidas=$((seguidas + 1))
    if [ "$seguidas" -ge 3 ]; then
      echo "   la base responde"
      break
    fi
  else
    seguidas=0
  fi
  if [ "$intento" = 90 ]; then
    echo "   La base no terminó de levantar. Ver: docker compose logs mysql"
    exit 1
  fi
  sleep 2
done

echo
echo "== 3. Cargando la definición =="
YA=$(mysql_en_el_contenedor -N -B -e \
  "SELECT COUNT(*) FROM information_schema.tables
    WHERE table_schema='$BASE' AND table_name='runac_c1_campo';" 2>/dev/null || echo 0)

if [ "${YA//[$'\r\n ']/}" != "0" ]; then
  echo "   La base «$BASE» ya está armada. No se toca nada."
  echo "   Para rehacerla desde cero:  docker compose down -v  y volver a correr esto."
else
  # `base_inicial.sql` es el estado verificado de la definición: los cinco
  # archivos, sus diez hojas de datos, sus 365 campos, sus catálogos y sus
  # reglas, con todas las correcciones aplicadas. Es lo que se carga.
  #
  # Los guiones de `entorno/sql/` NO se cargan acá: están para leer cómo se
  # llegó hasta este estado y por qué, y para rehacer la definición desde los
  # Excel originales. Cada uno explica en su encabezado qué corrige.
  echo "   Cargando entorno/base_inicial.sql"
  mysql_en_el_contenedor < entorno/base_inicial.sql
  echo "   listo"
fi

echo
echo "== 4. Tablas de Django y usuarios de prueba =="
docker compose exec -T web python manage.py migrate --noinput
docker compose exec -T web python manage.py datos_iniciales

echo
echo "== 5. Comprobación =="
docker compose exec -T web python - <<'PY'
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from django.db import connection

with connection.cursor() as cur:
    cur.execute(
        """SELECT COUNT(*) FROM runac_c1_campo c
             JOIN runac_c1_hoja h ON h.id = c.hoja_id
             JOIN runac_c1_archivo_version av
               ON av.id = h.archivo_version_id AND av.estado = 'VIGENTE'"""
    )
    campos = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM runac_c1_campo_regla")
    reglas = cur.fetchone()[0]
    # Si acá sale «SÃ­» en vez de «Sí», la carga se hizo sin utf8mb4 y hay que
    # rehacerla desde cero, no arreglarla con un UPDATE.
    cur.execute(
        """SELECT o.valor_esperado FROM runac_c1_catalogo_opcion o
             JOIN runac_c1_catalogo c ON c.id = o.catalogo_id
            WHERE c.codigo = 'si_no' ORDER BY o.orden LIMIT 1"""
    )
    fila = cur.fetchone()
    acento = fila[0] if fila else "(no hay catálogo si_no)"

print(f"   campos a cargar en el período : {campos}   (esperado: 365)")
print(f"   reglas enganchadas            : {reglas}")
print(f"   acentos                       : {acento}   (tiene que decir «Sí»)")
PY

echo
echo "Listo.  http://localhost:8100"
echo "Usuarios: operador · responsable · revisor · admin   —   contraseña: runac"
