# Instalar

Para alguien que nunca vio el proyecto. Son dos comandos.

## Lo único que hace falta

**Docker Desktop.** Nada más: ni Python, ni MySQL, ni configurar nada. Todo
corre adentro de contenedores.

En Windows, los comandos van en **Git Bash**, no en PowerShell.

## Los dos comandos

```bash
git clone https://github.com/dsocial118/Modulo-de-Importaciones-Recurrentes.git
```

```bash
cd Modulo-de-Importaciones-Recurrentes && bash entorno/preparar.sh
```

La primera vez tarda unos minutos: descarga MySQL, construye la imagen de la
aplicación y carga la definición. Al terminar avisa:

```
campos a cargar en el período : …   (esperado: …)
acentos                       : Sí    (tiene que decir «Sí»)

Listo.  http://localhost:8100
```

Los dos números de «campos» tienen que coincidir. Después, para confirmar que
quedó bien:

```bash
bash entorno/estado.sh
```

En «DESFASAJES» tiene que decir **«ninguno»**.

De ahí en adelante, para levantarlo alcanza con `docker compose up -d`.

## Entrar

**http://localhost:8100**

| Usuario | Rol | Contraseña |
|---|---|---|
| `operador` | Operador provincial · Chubut | `runac` |
| `responsable` | Responsable provincial · Chubut | `runac` |
| `operador_chaco` | Operador provincial · Chaco | `runac` |
| `responsable_chaco` | Responsable provincial · Chaco | `runac` |
| `revisor` | Revisor técnico nacional | `runac` |
| `admin` | Administrador nacional | `runac` |

**La versión nueva, en React**, está en **http://localhost:8100/v2/mir/**, con
los mismos usuarios. Convive con la actual: lo que todavía no se migró lleva a
la pantalla de siempre. Ver [`docs/mir/front-v2.md`](mir/front-v2.md).

## Probar que anda

Entrá como `operador` y subí los seis archivos de
`entorno/mir-v2/archivos_de_prueba/Chubut_correctos/`. Los dispositivos y el
legajo van primero, porque las nóminas los referencian:

```
DISP_PENAL · DISP_SCP · LEGAJO_NYA · MPI · MPE · MPJ_DAE
```

Los seis tienen que quedar **VÁLIDA, con cero bloqueantes**. Alguno puede
traer advertencias de rango —DISP_PENAL las trae—, y es lo esperado. Después probá las otras dos
carpetas: `_con_advertencias` entra igual pero con avisos, `_con_errores` no
entra.

> El botón **«Armar demostración»** de la pantalla de inicio importa, en orden,
> los archivos de `Chubut_con_advertencias` que pide el período, y deja hechas
> unas correcciones para que el historial tenga contenido. **Borra antes todas
> las importaciones**: no usarlo en una base con datos que se quieran conservar.

## Cuando algo no anda

**No abre nada en el 8100.** Casi siempre es que la base todavía está
levantando, sobre todo después de reiniciar la máquina. `docker compose ps`
tiene que mostrar `mysql` en `healthy`. Si no:

```bash
docker compose logs mysql
```

**El puerto está ocupado.** Si ya tenés algo en el 8100 o el 3399, cambiálos en
`docker-compose.yml`.

**Dice que la base ya está armada.** Es correcto: `preparar.sh` no pisa lo que
hay. Para rehacerla desde cero, **borrando todo lo cargado**:

```bash
docker compose down -v && bash entorno/preparar.sh
```

**Aparece «SÃ­» en vez de «Sí».** La carga se hizo sin `utf8mb4`. No se arregla
con un UPDATE: hay que rehacer la base con el comando de arriba.

**Un archivo no entra por el nombre.** Es el sistema funcionando. El nombre
tiene que empezar por el código del archivo y decir el período y la
jurisdicción: `MPI_2026_T1_Chubut.xlsx`. Se admite lo que venga después.

**Una nómina no se deja subir.** También es correcto: las nóminas referencian a
los dispositivos, así que `DISP_PENAL` y `DISP_SCP` van primero. El mensaje lo
dice.

**`/v2/mir/` responde «El front nuevo no responde».** El servicio `front_mir`
todavía está arrancando, o se cayó: `docker compose logs front_mir`. La versión
actual sigue andando igual.

### Redes que inspeccionan el tráfico

Algunos antivirus corporativos —por ejemplo Kaspersky Endpoint Security—
inspeccionan las conexiones seguras con un certificado propio. Windows confía
en él, pero los contenedores no, y **la construcción de las imágenes falla al
descargar paquetes** con `certificate verify failed` o `connection reset`.

Se resuelve sin tocar el antivirus ni el repositorio:

1. Sacar el certificado de la conexión, desde Git Bash:

   ```bash
   mkdir -p certificados_locales && echo | openssl s_client -showcerts -connect registry.npmjs.org:443 -servername registry.npmjs.org 2>/dev/null | awk '/BEGIN CERTIFICATE/{n++} n==2{print} /END CERTIFICATE/ && n==2{exit}' > certificados_locales/ca.pem
   ```

2. Crear `docker-compose.override.yml`, que Docker lee solo, para pasárselo a
   la construcción:

   ```yaml
   services:
     web:
       build:
         secrets: [certificado_ca]
     front_mir:
       build:
         secrets: [certificado_ca]
   secrets:
     certificado_ca:
       file: ./certificados_locales/ca.pem
   ```

Las dos cosas están en `.gitignore`: son de esa máquina. Los Dockerfile **suman**
ese certificado a los habituales, no los reemplazan, porque el antivirus puede
inspeccionar unos sitios y otros no. Donde no hace falta, no se crea nada y todo
funciona igual.

## Qué hay adentro

Ver [`entorno/LEEME.md`](../entorno/LEEME.md): qué es cada carpeta, cuál es la
fuente de verdad de la definición y por qué.
