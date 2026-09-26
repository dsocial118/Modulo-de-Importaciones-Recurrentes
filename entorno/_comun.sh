#!/usr/bin/env bash
# Lo que comparten estado.sh y exportar_base.sh. No se corre solo: se incluye.

PASS="${MIR_MYSQL_PASS:-runac_local}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Qué contenedor tiene la base. En la máquina de trabajo es `runac_c1_mysql`;
# en una instalación hecha con preparar.sh es el servicio `mysql` de este
# repositorio, que Docker nombra según la carpeta. Si no se encuentra ninguno
# hay que decirlo: seguir de largo mostraba todo vacío y «ninguno» en los
# desfasajes, que se lee como que está todo bien.
contenedor_mysql() {
    if [ -n "${MIR_MYSQL:-}" ]; then echo "$MIR_MYSQL"; return; fi
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx runac_c1_mysql; then
        echo runac_c1_mysql; return
    fi
    docker compose -f "$REPO/docker-compose.yml" ps -q mysql 2>/dev/null | head -1
}

sql() { docker exec "$MYSQL_CONT" mysql -uroot -p"$PASS" --default-character-set=utf8mb4 -N -s -e "$1" 2>/dev/null; }

# Lo mismo, contra otro contenedor y con otra clave.
sql_en() { docker exec "$1" mysql -uroot -p"$2" --default-character-set=utf8mb4 -N -s -e "$3" 2>/dev/null; }

# El MySQL que usa un contenedor web: el que responde al nombre de su
# DATABASE_HOST en alguna de sus redes. La instancia de React tiene el suyo y
# también se llama `mysql`, así que buscarlo por nombre no alcanza.
mysql_de_la_web() {
    local web="$1" host="$2" red otro
    [ -z "$host" ] && return
    for red in $(docker inspect "$web" --format '{{range $k, $v := .NetworkSettings.Networks}}{{println $k}}{{end}}' 2>/dev/null); do
        for otro in $(docker ps --filter "network=$red" --format '{{.Names}}' 2>/dev/null); do
            if docker inspect "$otro" --format "{{with index .NetworkSettings.Networks \"$red\"}}{{join .Aliases \" \"}}{{end}}" 2>/dev/null \
                 | tr ' ' '\n' | grep -qx "$host"; then
                echo "$otro"
                return
            fi
        done
    done
}

# La huella de la Capa 1 de una base: cambia si cambia cualquier fila de la
# definición. Contar campos no alcanza —los desfasajes del 22 y el 23 fueron
# cambios de tipo, con la misma cantidad de campos—.
huella_capa1() {
    local base="$1" tablas
    tablas=$(sql "SELECT GROUP_CONCAT(CONCAT('\`$base\`.\`',table_name,'\`') ORDER BY table_name)
                  FROM information_schema.tables
                  WHERE table_schema='$base' AND table_type='BASE TABLE' AND table_name LIKE 'mir\\_c1\\_%';")
    [ -z "$tablas" ] && return
    sql "CHECKSUM TABLE $tablas;" | sed "s/^$base\.//" | sort | md5sum | cut -c1-16
}

# Lo que dice el encabezado de base_inicial.sql.
BASE_INICIAL="${MIR_BASE_INICIAL:-$REPO/entorno/base_inicial.sql}"
dato_de_la_base_inicial() { head -12 "$BASE_INICIAL" | sed -n "s/^-- $1: //p" | tr -d '\r'; }
