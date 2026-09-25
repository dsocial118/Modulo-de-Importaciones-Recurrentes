#!/usr/bin/env bash
# Regenera entorno/base_inicial.sql desde la base que se muestra.
#
#     bash entorno/exportar_base.sh              desde runac_v2
#     bash entorno/exportar_base.sh otra_base    desde otra
#
# POR QUÉ EXISTE. El 25-09-2026 se descubrió que la base del repositorio era la
# del 17-09: la base que se muestra se había corregido el 23 y nadie la volvió a
# copiar. Quien clonaba recibía una versión donde importar falla, y no había
# forma de darse cuenta. Hacerlo a mano, además, sale distinto cada vez: ese
# mismo día una opción mal puesta dejó una fila por instrucción y la carga
# tardaba diez minutos en vez de uno.
#
# Qué lleva: la estructura completa y los datos de la definición (Capa 1), el
# nomenclador territorial, las jurisdicciones, los períodos y los usuarios de
# prueba. Qué NO lleva: importaciones, datos recibidos, observaciones ni
# sesiones. Se carga siempre como `runac`, sea cual sea la base de origen.
#
# El encabezado guarda la huella de la Capa 1 de origen. estado.sh la compara y
# avisa cuando la base del repositorio quedó atrasada.
#
# Después de correrlo: probar una instalación desde cero (docs/INSTALAR.md) y
# commitear base_inicial.sql junto con el cambio que la motivó.

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/_comun.sh"

ORIGEN="${1:-runac_v2}"
MYSQL_CONT="$(contenedor_mysql)"
[ -z "$MYSQL_CONT" ] && { echo "No encuentro el contenedor de MySQL."; exit 1; }

hay=$(sql "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$ORIGEN' AND table_name='mir_c1_campo';")
[ "$hay" != "1" ] && { echo "La base «$ORIGEN» no tiene Capa 1."; exit 1; }

CON_DATOS=$(sql "SELECT GROUP_CONCAT(table_name ORDER BY table_name SEPARATOR ' ')
                 FROM information_schema.tables
                 WHERE table_schema='$ORIGEN' AND table_type='BASE TABLE'
                   AND (table_name LIKE 'mir\\_c1\\_%' OR table_name LIKE 'geo\\_%' OR table_name LIKE 'auth\\_%'
                        OR table_name IN ('django_content_type','django_migrations',
                                          'mir_c2_jurisdiccion','mir_c2_periodo','mir_c2_periodo_archivo'));")

resumen=$(sql "SELECT CONCAT(COUNT(DISTINCT av.archivo_id),' archivos · ',COUNT(c.id),' campos')
               FROM $ORIGEN.mir_c1_archivo_version av
               JOIN $ORIGEN.mir_c1_hoja h ON h.archivo_version_id=av.id
               JOIN $ORIGEN.mir_c1_campo c ON c.hoja_id=h.id
               WHERE av.estado='VIGENTE';")
campos=$(sql "SELECT COUNT(c.id) FROM $ORIGEN.mir_c1_archivo_version av
              JOIN $ORIGEN.mir_c1_hoja h ON h.archivo_version_id=av.id
              JOIN $ORIGEN.mir_c1_campo c ON c.hoja_id=h.id WHERE av.estado='VIGENTE';")
huella=$(huella_capa1 "$ORIGEN")

volcar() { docker exec "$MYSQL_CONT" mysqldump -uroot -p"$PASS" --default-character-set=utf8mb4 \
             --single-transaction --triggers --set-gtid-purged=OFF --no-tablespaces "$@" 2>/dev/null; }

DESTINO="$REPO/entorno/base_inicial.sql"
{
    echo "-- Base inicial del MIR, implementación RUNAC. La genera entorno/exportar_base.sh: no editar a mano."
    echo "-- origen: $ORIGEN"
    echo "-- generada: $(date +%Y-%m-%d)"
    echo "-- contenido: $resumen"
    echo "-- campos: $campos"
    echo "-- huella_capa1: $huella"
    echo "/*!50503 SET NAMES utf8mb4 */;"
    echo "CREATE DATABASE /*!32312 IF NOT EXISTS*/ \`runac\` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */;"
    echo "USE \`runac\`;"
    volcar --no-data "$ORIGEN"
    # shellcheck disable=SC2086
    volcar --no-create-info "$ORIGEN" $CON_DATOS
} | sed -E "s/ AUTO_INCREMENT=[0-9]+//; s/DEFINER=\`[^\`]*\`@\`[^\`]*\` //g; s/\`$ORIGEN\`\.//g" > "$DESTINO"

echo "Listo: entorno/base_inicial.sql desde «$ORIGEN» — $resumen · huella $huella"
echo "Falta: probar una instalación desde cero y commitearla."
