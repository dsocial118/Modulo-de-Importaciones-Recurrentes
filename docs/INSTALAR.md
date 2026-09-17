# Instalar

Para alguien que nunca vio el proyecto. Son dos comandos.

## Lo único que hace falta

**Docker Desktop.** Nada más: ni Python, ni MySQL, ni configurar nada. Todo
corre adentro de contenedores.

En Windows, los comandos van en **Git Bash**, no en PowerShell.

## Los dos comandos

```bash
git clone https://github.com/danielc76/runac-prototipo.git
```

```bash
cd runac-prototipo && bash entorno/preparar.sh
```

La primera vez tarda unos minutos: descarga MySQL, construye la imagen de la
aplicación y carga la definición. Al terminar avisa:

```
campos a cargar en el período : 365   (esperado: 365)
acentos                       : Sí    (tiene que decir «Sí»)

Listo.  http://localhost:8100
```

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

Entrá como `operador` y subí, **en este orden**, los cinco archivos de
`entorno/archivos_de_prueba/Chubut_correctos/`:

```
DISP_PENAL · DISP_SCP · MPI · MPE · MPJ_DAE
```

Los cinco tienen que quedar **VÁLIDA, con cero bloqueantes y cero
advertencias**. Después probá las otras dos carpetas: `_con_advertencias` entra
igual pero observado, `_con_errores` no entra.

Si preferís no subirlos a mano, en la pantalla de inicio hay un botón **«Armar
demostración»** que deja una presentación completa de una vez.

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
