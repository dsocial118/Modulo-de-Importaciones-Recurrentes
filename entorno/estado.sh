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

MYSQL_CONT="${MIR_MYSQL:-runac_c1_mysql}"
PASS="${MIR_MYSQL_PASS:-runac_local}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

sql() { docker exec "$MYSQL_CONT" mysql -uroot -p"$PASS" --default-character-set=utf8mb4 -N -s -e "$1" 2>/dev/null; }

echo
echo "  ══ QUÉ SIRVE CADA PUERTO ═══════════════════════════════════════════"
echo
docker ps --format '{{.Names}}\t{{.Ports}}' 2>/dev/null | grep -v mysql | grep -v phpmyadmin | while IFS=$'\t' read -r nombre puertos; do
    base=$(docker inspect "$nombre" --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | sed -n 's/^DATABASE_NAME=//p')
    [ -z "$base" ] && continue
    puerto=$(echo "$puertos" | grep -o '0\.0\.0\.0:[0-9]*' | head -1 | cut -d: -f2)
    # Qué versión de cada archivo está VIGENTE: es lo que el contenedor sirve.
    vig=$(sql "SELECT GROUP_CONCAT(CONCAT(a.codigo,' v',av.numero) ORDER BY a.codigo SEPARATOR ' · ')
               FROM ${base}.mir_c1_archivo a
               JOIN ${base}.mir_c1_archivo_version av ON av.archivo_id=a.id AND av.estado='VIGENTE';")
    printf "  %-6s %-12s %s\n" "${puerto:-—}" "$base" "${vig:-sin Capa 1}"
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

[ "$hubo" = "0" ] && echo "  ninguno"
echo
