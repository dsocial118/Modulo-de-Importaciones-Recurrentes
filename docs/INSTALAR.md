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
| `revisor` | Revisor técnico nacional | `runac` |
| `admin` | Administrador nacional | `runac` |

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

> El botón **«Armar demostración»** de la pantalla de inicio **hoy no sirve con
> esta definición**: usa los Excel de `runac/demo/`, que son de la definición
> anterior, y los rechaza por encabezados. Verificado el 25-09-2026.

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

## Qué hay adentro

Ver [`entorno/LEEME.md`](../entorno/LEEME.md): qué es cada carpeta, cuál es la
fuente de verdad de la definición y por qué.
