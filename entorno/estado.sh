#!/usr/bin/env bash
# Muestra cómo está el sistema DE VERDAD, leyéndolo de los contenedores, de las
# bases y de git — nunca de un documento.
#
#     bash entorno/estado.sh
#
# POR QUÉ EXISTE. El 23-09-2026 un chat leyó la documentación y concluyó que la
# base buena era `runac`. Había dejado de serlo el día anterior. El documento no
# mentía: contaba un hecho del 22 que seguía siendo cierto como hecho, pero ya
# no describía el presente. Un registro cuenta qué pasó; un estado dice qué es
# cierto ahora, y hay que poder pedirlo en vez de deducirlo leyendo el historial.
#
# La última sección es la que importa: DESFASAJES. Es la familia de errores que
# mordió tres veces el 22 y el 23 —la Capa 1 cambia y el material derivado no la
# sigue— y es lo único que un documento no puede avisar.
#
# No recuerda nada. Si algo cambió, la próxima corrida lo dice.

set -u

source "$(dirname "${BASH_SOURCE[0]}")/_comun.sh"

MYSQL_CONT="$(contenedor_mysql)"
if [ -z "$MYSQL_CONT" ] || ! sql "SELECT 1" >/dev/null; then
    echo
    echo "  No encuentro la base: ningún contenedor de MySQL responde."
    echo "  ¿Está levantado?  docker compose ps"
    echo
    exit 1
fi

echo
echo "  ══ QUÉ SIRVE CADA PUERTO ═══════════════════════════════════════════"
echo
docker ps --format '{{.Names}}\t{{.Ports}}' 2>/dev/null | grep -v mysql | grep -v phpmyadmin | while IFS=$'\t' read -r nombre puertos; do
    entorno=$(docker inspect "$nombre" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null)
    base=$(echo "$entorno" | sed -n 's/^DATABASE_NAME=//p' | head -1)
    [ -z "$base" ] && continue
    puerto=$(echo "$puertos" | grep -o '0\.0\.0\.0:[0-9]*' | head -1 | cut -d: -f2)
    # Cada web se consulta en SU MySQL. Hasta el 26-09-2026 se consultaba
    # siempre el principal, y la instancia de React (8110), que tiene base
    # propia con el mismo nombre `runac`, figuraba con la definición de la 8100.
    suyo=$(mysql_de_la_web "$nombre" "$(echo "$entorno" | sed -n 's/^DATABASE_HOST=//p' | head -1)")
    [ -z "$suyo" ] && suyo="$MYSQL_CONT"
    clave=$(echo "$entorno" | sed -n 's/^DATABASE_PASSWORD=//p' | head -1)
    # Qué versión de cada archivo está VIGENTE: es lo que el contenedor sirve.
    vig=$(sql_en "$suyo" "${clave:-$PASS}" "SELECT GROUP_CONCAT(CONCAT(a.codigo,' v',av.numero) ORDER BY a.codigo SEPARATOR ' · ')
               FROM ${base}.mir_c1_archivo a
               JOIN ${base}.mir_c1_archivo_version av ON av.archivo_id=a.id AND av.estado='VIGENTE';")
    # Un contenedor sin Capa 1 no es del MIR (por ejemplo, el SISOC local).
    [ -z "$vig" ] && continue
    # Si la base no está en el MySQL principal se dice en cuál: dos bases
    # pueden llamarse igual y no ser la misma.
    etiqueta="$base"
    if [ "$suyo" != "$MYSQL_CONT" ]; then
        pm=$(docker port "$suyo" 3306 2>/dev/null | grep -o '0\.0\.0\.0:[0-9]*' | head -1 | cut -d: -f2)
        etiqueta="$base (MySQL ${pm:-$suyo})"
    fi
    printf "  %-6s %-20s %s\n" "${puerto:-—}" "$etiqueta" "$vig"
done
echo

for base in $(sql "SELECT schema_name FROM information_schema.schemata
                   WHERE schema_name NOT IN ('mysql','sys','performance_schema','information_schema');"); do
    tiene=$(sql "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$base' AND table_name='mir_c1_campo';")
    [ "$tiene" != "1" ] && continue
    echo "  ══ CAPA 1 · $base ═══════════════════════════════════════════════"
    sql "SELECT CONCAT('  ', COUNT(DISTINCT a.id),' archivos · ',
                       COUNT(c.id),' campos · ', SUM(c.obligatorio),' obligatorios · ',
                       (SELECT COUNT(*) FROM ${base}.mir_c1_campo_regla cr
                          JOIN ${base}.mir_c1_campo c2 ON c2.id=cr.campo_id
                          JOIN ${base}.mir_c1_hoja h2 ON h2.id=c2.hoja_id
                          JOIN ${base}.mir_c1_archivo_version av2 ON av2.id=h2.archivo_version_id AND av2.estado='VIGENTE'),
                       ' reglas aplicadas')
           FROM ${base}.mir_c1_archivo a
           JOIN ${base}.mir_c1_archivo_version av ON av.archivo_id=a.id AND av.estado='VIGENTE'
           JOIN ${base}.mir_c1_hoja h ON h.archivo_version_id=av.id
           JOIN ${base}.mir_c1_campo c ON c.hoja_id=h.id;"
    echo
done

echo "  ══ REPOSITORIO ═════════════════════════════════════════════════════"
echo
rama=$(git -C "$REPO" branch --show-current 2>/dev/null)
commit=$(git -C "$REPO" log --oneline -1 2>/dev/null)
sucio=$(git -C "$REPO" status --porcelain 2>/dev/null | wc -l)
adelante=$(git -C "$REPO" rev-list --count "origin/$rama..$rama" 2>/dev/null || echo "?")
printf "  %s · %s\n" "$rama" "$commit"
if [ "$sucio" -gt 0 ]; then printf "  %s archivos sin commitear\n" "$sucio"; else echo "  árbol limpio"; fi
[ "$adelante" != "0" ] && [ "$adelante" != "?" ] && printf "  %s commits sin subir\n" "$adelante"
echo

echo "  ══ DESFASAJES ══════════════════════════════════════════════════════"
echo
hubo=0
for base in $(sql "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('mysql','sys','performance_schema','information_schema');"); do
    tiene=$(sql "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$base' AND table_name='mir_c1_campo';")
    [ "$tiene" != "1" ] && continue

    # La receptora tiene que aguantar lo que la Capa 1 declara. Si la definición
    # cambió y la tabla no, la importación muere al insertar y el error no dice
    # nada de lo que en realidad pasa.
    malos=$(sql "
      SELECT CONCAT('  $base · ', k.table_name,'.',k.column_name,'  declarado ',k.tipo,', la tabla tiene ',k.data_type)
      FROM (
        SELECT co.table_name, co.column_name, co.data_type, c.tipo_dato tipo,
               -- Una familia por tipo, no un nombre exacto: int y bigint
               -- son los dos enteros, y avisar de eso seria ruido.
               CASE c.tipo_dato
                 WHEN 'TEXTO'   THEN 'varchar,char,text,mediumtext,longtext'
                 WHEN 'ENTERO'  THEN 'bigint,int,mediumint,smallint,tinyint'
                 WHEN 'DECIMAL' THEN 'decimal,double,float'
                 WHEN 'FECHA'   THEN 'date,datetime,timestamp'
                 WHEN 'HORA'    THEN 'time' END esperado
        FROM ${base}.mir_c1_campo c
        JOIN ${base}.mir_c1_hoja h ON h.id=c.hoja_id
        JOIN ${base}.mir_c1_archivo_version av ON av.id=h.archivo_version_id AND av.estado='VIGENTE'
        JOIN information_schema.columns co ON co.table_schema='$base'
             AND co.table_name LIKE 'mir_c2_%' AND co.column_name=c.nombre
             -- Solo las receptoras. Las tablas del circuito tienen columnas que
             -- se llaman igual que un campo de alguna planilla y no son lo mismo.
             AND co.table_name NOT IN ('mir_c2_jurisdiccion','mir_c2_periodo','mir_c2_presentacion',
                 'mir_c2_importacion','mir_c2_observacion','mir_c2_historial_cambios',
                 'mir_c2_reglas_incumplidas','mir_c2_errores_de_importacion','mir_c2_periodo_archivo')
      ) k
      WHERE FIND_IN_SET(k.data_type, k.esperado) = 0
      GROUP BY 1;")
    [ -n "$malos" ] && { echo "$malos"; hubo=1; }

    cortos=$(sql "
      SELECT CONCAT('  $base · ', co.table_name,'.',co.column_name,'  admite ',
                    co.character_maximum_length,' y la Capa 1 declara ', MAX(c.longitud_maxima))
      FROM ${base}.mir_c1_campo c
      JOIN ${base}.mir_c1_hoja h ON h.id=c.hoja_id
      JOIN ${base}.mir_c1_archivo_version av ON av.id=h.archivo_version_id AND av.estado='VIGENTE'
      JOIN information_schema.columns co ON co.table_schema='$base'
           AND co.table_name LIKE 'mir_c2_%' AND co.column_name=c.nombre AND co.data_type='varchar'
           AND co.table_name NOT IN ('mir_c2_jurisdiccion','mir_c2_periodo','mir_c2_presentacion',
               'mir_c2_importacion','mir_c2_observacion','mir_c2_historial_cambios',
               'mir_c2_reglas_incumplidas','mir_c2_errores_de_importacion','mir_c2_periodo_archivo')
      WHERE c.tipo_dato='TEXTO' AND c.longitud_maxima IS NOT NULL
      GROUP BY co.table_name, co.column_name, co.character_maximum_length
      HAVING co.character_maximum_length < MAX(c.longitud_maxima);")
    [ -n "$cortos" ] && { echo "$cortos"; hubo=1; }

    # Un campo que declara una lista vacía no valida contra nada, y en la
    # plantilla sale como un desplegable sin opciones.
    vacias=$(sql "
      SELECT CONCAT('  $base · ', a.codigo,'.',c.nombre,'  apunta a la lista «',cat.codigo,'», que no tiene opciones')
      FROM ${base}.mir_c1_campo c
      JOIN ${base}.mir_c1_catalogo cat ON cat.id=c.catalogo_id
      JOIN ${base}.mir_c1_hoja h ON h.id=c.hoja_id
      JOIN ${base}.mir_c1_archivo_version av ON av.id=h.archivo_version_id AND av.estado='VIGENTE'
      JOIN ${base}.mir_c1_archivo a ON a.id=av.archivo_id
      WHERE cat.codigo NOT LIKE 'nomenclador%'
        AND NOT EXISTS (SELECT 1 FROM ${base}.mir_c1_catalogo_opcion o WHERE o.catalogo_id=cat.id AND o.activo=1);")
    [ -n "$vacias" ] && { echo "$vacias"; hubo=1; }
done

# La base del repositorio es una copia de la que se muestra. Si la de origen
# cambió y la copia no, quien clona recibe una versión vieja y no hay cómo
# darse cuenta: pasó el 25-09-2026. Sólo se puede comparar donde está la base
# de origen, o sea en la máquina de trabajo.
origen=$(dato_de_la_base_inicial origen)
guardada=$(dato_de_la_base_inicial huella_capa1)
if [ -z "$guardada" ]; then
    echo "  entorno/base_inicial.sql no tiene huella: regenerarla con  bash entorno/exportar_base.sh"
    hubo=1
elif [ -n "$(sql "SHOW DATABASES LIKE '$origen';")" ]; then
    actual=$(huella_capa1 "$origen")
    if [ "$actual" != "$guardada" ]; then
        echo "  entorno/base_inicial.sql quedó atrasada: la Capa 1 de $origen cambió desde que se exportó."
        echo "      regenerarla con  bash entorno/exportar_base.sh  y commitearla"
        hubo=1
    fi
fi

[ "$hubo" = "0" ] && echo "  ninguno"
echo
