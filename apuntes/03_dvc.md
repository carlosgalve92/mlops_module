# DVC (Data Version Control)

**DVC** es un sistema de control de versiones *open-source* diseñado específicamente para gestionar grandes volúmenes de datos, modelos de *Machine Learning* y flujos de trabajo reproducibles. Actúa como una extensión de Git: permite rastrear, versionar y compartir archivos de datos sin comprometer la eficiencia del repositorio, ya que Git conserva únicamente ligeros ficheros de metadatos mientras que los datos pesados se almacenan aparte.

> **Convenciones de este documento**
> - `<archivo>`, `<nombre_repositorio>`, etc. son *marcadores de posición*: sustitúyelos por los valores reales.
> - Los bloques de comandos asumen que se ejecutan desde la raíz del repositorio.
> - Se presupone que el proyecto ya está inicializado con Git.

---

## 1. Inicialización del repositorio

```bash
dvc init
```

Este comando genera la siguiente estructura:

- **Directorio `.dvc/`**, que contiene:
  - **`.dvc/cache/`** — almacén local donde DVC guarda las distintas versiones del contenido de los ficheros añadidos al control de versiones.
  - **`.dvc/tmp/`** — ficheros temporales y de estado que DVC utiliza internamente (bloqueos, ejecución de experimentos, etc.).
  - **`.dvc/.gitignore`** — indica a Git qué rutas internas de DVC no deben subirse al repositorio.
  - **`.dvc/config`** — contiene la configuración de DVC. Los datos sensibles (credenciales, tokens) se guardan en `.dvc/config.local`, que queda excluido de Git a través de `.dvc/.gitignore`.
- **Fichero `.dvcignore`** — análogo a `.gitignore`, permite indicar los directorios y ficheros que DVC debe ignorar.

Tras la inicialización se recomienda confirmar en Git los ficheros que DVC prepara automáticamente en el *stage*:

- `.dvc/.gitignore`
- `.dvc/config`
- `.dvcignore`

---

## 2. Versionado de datos

### Añadir archivos al control de versiones

```bash
dvc add <archivo>
```

Este comando genera, en la misma ruta de `<archivo>`:

- **`<archivo>.dvc`** — fichero de metadatos que guarda la referencia (*hash*) al dataset.
- **`.gitignore`** — se crea o actualiza para que Git ignore el archivo original y evitar así subir información pesada al repositorio.

A continuación se recomienda registrar los cambios en Git añadiendo los ficheros de metadatos generados:

```bash
git add <archivo>.dvc
git add <ruta_archivo>/.gitignore
```

Finalmente se confirma el *commit* y, si se trabaja con un repositorio remoto, se sincroniza:

```bash
cz commit   # o 'git commit' si no se usa Commitizen
git push
```

> **Nota:** `cz commit` corresponde a **Commitizen**, una herramienta que guía la redacción de mensajes de *commit* estandarizados. Puede sustituirse por `git commit` sin afectar al flujo de DVC.

### Eliminar archivos del control de versiones

```bash
dvc remove <archivo>.dvc
```

### Consultar el estado

Muestra el estado de los archivos referenciados dentro del control de versiones:

```bash
dvc status
```

---

## 3. Configuración del repositorio remoto

El repositorio remoto es el almacenamiento externo (S3, Azure Blob Storage, etc.) donde se sincronizan los datos versionados.

```bash
dvc remote add <nombre_repositorio> <url_del_repositorio_remoto>
```

Por convención, al repositorio remoto principal se le suele asignar el nombre `origin`.

Para establecerlo además como remoto por defecto:

```bash
dvc remote default <nombre_repositorio>
```

### Configuración de credenciales

Las credenciales se almacenan en local (`--local`) para que no se suban a Git:

```bash
# Genérico (S3 y compatibles)
dvc remote modify --local <nombre_repositorio> access_key_id MI_ACCESS_KEY
dvc remote modify --local <nombre_repositorio> secret_access_key MI_SECRET_KEY
```

### Caso particular: Azure Blob Storage

Acceder a un remoto de Azure Blob Storage supone tres pasos: **declarar el remoto**, **darle credenciales** y **sincronizar**.

**1. Declarar el remoto.** La URL usa el esquema `azure://` con el nombre del contenedor y, opcionalmente, una ruta dentro de él. Esta configuración se guarda en `.dvc/config` (que **sí** se versiona en Git, porque no contiene secretos):

```bash
dvc remote add origin azure://<nombre_contenedor>/<ruta_opcional>
dvc remote default origin
```

**2. Configurar las credenciales.** Todo lo sensible va con `--local` para que se guarde en `.dvc/config.local` y no acabe en Git. Azure admite varias formas de autenticarse; se elige **una** según lo que proporcione quien administra la cuenta:

```bash
# Opción A — SAS token
dvc remote modify --local origin account_name <nombre_cuenta_almacenamiento>
dvc remote modify --local origin sas_token "<sas_token>"

# Opción B — clave de la cuenta (account key)
dvc remote modify --local origin account_name <nombre_cuenta_almacenamiento>
dvc remote modify --local origin account_key "<account_key>"

# Opción C — connection string (incluye cuenta y llave en una sola cadena)
dvc remote modify --local origin connection_string "<connection_string>"

# Opción D — identidad administrada (managed identity) de la máquina virtual (MV)
#            con permisos sobre la cuenta de almacenamiento
dvc remote modify --local origin account_name <nombre_cuenta_almacenamiento>
```

> **Nota:** `account_name` es el nombre de la **cuenta de almacenamiento** (*storage account*), un nivel por encima del contenedor. No debe confundirse con el nombre del contenedor que se indica en la URL del remoto.

**3. Comprobar y sincronizar.** Una vez configurado el acceso, se emplean los comandos de sincronización de la sección 4 (`dvc push`, `dvc pull`, `dvc fetch`).

> **Requisito previo:** puede ser necesario instalar el soporte de Azure, que DVC empaqueta como un extra opcional:
>
> ```bash
> pip install "dvc[azure]"
> ```

> **Lectura frente a escritura:** para descargar datos (`dvc pull`) basta con permisos de **lectura** sobre el contenedor; para subir versiones nuevas (`dvc push`) se necesitan permisos de **escritura**. Si se usa un SAS token, este debe incluir los permisos adecuados (típicamente lectura, escritura y listado) o la subida fallará con un error de autorización.

> **Trabajo en equipo:** `.dvc/config.local` es personal e intransferible, así que **cada persona configura sus propias credenciales en local**. Por Git solo se comparte `.dvc/config` con la URL del remoto; las llaves nunca se versionan.

---

## 4. Sincronización de datos

Subir datos al repositorio remoto:

```bash
dvc push
```

Descargar datos del repositorio remoto (los baja a la *cache* local **y** los materializa en el *workspace*):

```bash
dvc pull
```

Descargar los datos del remoto a la *cache* local **sin** volcarlos al *workspace* (a diferencia de `dvc pull`). Útil para prellenar la cache sin alterar el directorio de trabajo, por ejemplo en pipelines de CI/CD:

```bash
dvc fetch
```

Comprobar si hay cambios respecto al remoto **sin descargar los datos** (lista los ficheros referenciados que faltan en la cache; es decir, lo que descargaría `dvc pull`):

```bash
dvc status -c   # forma larga: --cloud
```

---

## 5. Recuperación de versiones anteriores

Para volver a una versión anterior de los datos siempre se empieza por situarse en el *commit* de Git que apunta a esa versión. Esto actualiza el fichero de metadatos `<archivo>.dvc` (el *puntero*), pero **no modifica el archivo de datos real** del *workspace*, ya que Git no lo gestiona:

```bash
git checkout <hash_del_commit>
```

El segundo paso depende de dónde se encuentre esa versión de los datos.

**Caso 1 — los datos ya están en la *cache* local.** Basta con materializarlos en el *workspace*:

```bash
dvc checkout
```

**Caso 2 — los datos solo están en el repositorio remoto.** Se usa `dvc pull`, que los descarga *y* actualiza el *workspace* en un único paso:

```bash
dvc pull
```

> **Nota:** `dvc pull` equivale internamente a `dvc fetch` (remoto → *cache*) seguido de `dvc checkout` (*cache* → *workspace*). Por eso, tras un `dvc pull` no es necesario ejecutar `dvc checkout` de nuevo. Se recurre a `dvc checkout` por sí solo cuando la versión ya está en la *cache* local y solo falta reflejarla en el *workspace* (por ejemplo, al cambiar de rama o de *commit*).

---

## 6. Reproducción de pipelines y gestión de experimentos

DVC no solo versiona datos: también permite definir un **pipeline** —una secuencia de etapas encadenadas— y reproducirlo de forma determinista. Todo el flujo (`dvc repro` y `dvc exp run`) gira en torno al fichero `dvc.yaml`.

### El pipeline: `dvc.yaml` y `dvc.lock`

Cada etapa (*stage*) del `dvc.yaml` declara principalmente cuatro cosas:

- **`cmd`** — el comando que ejecuta la etapa.
- **`deps`** — las entradas (datos y código) de las que depende.
- **`params`** — parámetros de configuración que, si cambian, invalidan la etapa.
- **`outs`** / **`metrics`** — las salidas que produce (artefactos y/o métricas).

A partir de las relaciones entre `deps` y `outs`, DVC construye un **grafo dirigido acíclico (DAG)**: la salida de una etapa es la entrada de la siguiente. Un pipeline típico encadena, por ejemplo, cinco etapas así:

```
ingestion → validation → preprocess → train → evaluation
```

donde `preprocess` depende tanto del `train.csv` de `ingestion` como del `status.txt` de `validation`, y `evaluation` consume el modelo de `train` más los datos de `preprocess`. Ese grafo puede visualizarse con:

```bash
dvc dag
```

La primera vez que se ejecuta el pipeline, DVC genera **`dvc.lock`**: un fichero que registra el *hash* exacto de cada dependencia, parámetro y salida. Es la "foto" del estado reproducible y **debe versionarse en Git** junto con `dvc.yaml`. Es también lo que permite a DVC detectar qué ha cambiado entre ejecuciones.

### Reproducir el pipeline: `dvc repro`

`dvc repro` recorre el DAG y **re-ejecuta únicamente las etapas cuyas dependencias, parámetros o comando han cambiado** respecto a `dvc.lock`. Las etapas cuyo estado no ha variado se saltan (su salida se reutiliza desde la *cache*). Esto es lo que hace el pipeline eficiente: no recalcula lo que no hace falta.

Reproducir el pipeline completo:

```bash
dvc repro
```

**Ejemplo.** Supón que ya has ejecutado el pipeline una vez y ahora modificas solo el código de entrenamiento, `src/mlops/components/train/model_trainer.py`. Al lanzar `dvc repro`:

- `ingestion`, `validation` y `preprocess` → **se saltan** (sus `deps` y `params` no han cambiado).
- `train` → **se re-ejecuta** (cambió una de sus `deps`).
- `evaluation` → **se re-ejecuta** (depende de la salida de `train`, que es nueva).

Ocurre lo mismo si cambias un parámetro: al editar el bloque `model_trainer` dentro de `config/config.yaml`, DVC lo detecta vía `params` y vuelve a correr `train` y `evaluation`, pero no las etapas anteriores.

Variantes útiles:

```bash
dvc repro <nombre_etapa>     # reproduce esa etapa y las de las que depende (aguas arriba)
dvc repro -s <nombre_etapa>  # ejecuta SOLO esa etapa (--single-item)
dvc repro -f                 # fuerza la re-ejecución de todo el pipeline (--force)
```

> **Nota:** tras un `dvc repro` que produzca cambios, `dvc.lock` se actualiza. Hay que confirmarlo en Git (`git add dvc.lock && git commit ...`) para dejar registrada la nueva versión reproducible del pipeline.

### Experimentos: `dvc exp run`

`dvc exp run` ejecuta el mismo pipeline que `dvc repro` (con idéntica lógica de DAG y detección de cambios), pero **captura el resultado como un experimento**: guarda parámetros, métricas y salidas de esa ejecución sin necesidad de crear ramas ni *commits* de Git manualmente. Es la herramienta idónea para **probar combinaciones de parámetros** y compararlas.

Ejecutar un experimento con los parámetros actuales:

```bash
dvc exp run
```

Mostrar los experimentos de la rama actual, con sus parámetros y métricas en una tabla comparativa:

```bash
dvc exp show
```

> **Nota:** como la etapa `evaluation` declara `metrics: artifacts/model_evaluation/metrics.json`, esos valores aparecen automáticamente como columnas en `dvc exp show`, lo que permite comparar experimentos de un vistazo.

Aplicar un experimento —volcar sus cambios (parámetros y resultados) al *workspace* para hacerlo efectivo y poder confirmarlo en Git—:

```bash
dvc exp apply <nombre_experimento>
```

Listar todos los experimentos:

```bash
dvc exp list --all
```

### Eliminar experimentos

Los experimentos se borran con `dvc exp remove`. El nombre a indicar es el que aparece en la primera columna de `dvc exp show` o en `dvc exp list --all`.

Borrar uno o varios experimentos por nombre:

```bash
dvc exp remove <nombre_experimento>
dvc exp remove <exp_1> <exp_2>   # varios a la vez, separados por espacios
```

Borrar **todos** los experimentos, o vaciar la cola de los pendientes de ejecutar (lanzados con `--queue`):

```bash
dvc exp remove -A        # todos los experimentos ejecutados (forma larga: --all)
dvc exp remove --queue   # solo los experimentos en cola
```

> **Cuidado con `-A`:** en DVC, el flag corto `-A` **no significa siempre lo mismo**. En `dvc exp remove` equivale a `--all`, pero en `dvc exp push`, `dvc exp pull` y `dvc exp list` equivale a `--all-commits`. Para evitar confusiones conviene usar la forma corta `-A`, que funciona en todos ellos.

> **Nota:** `dvc exp remove` elimina la *referencia* al experimento, pero no libera por sí solo el espacio que sus datos ocupan en la *cache*. Para recuperarlo se usa el recolector de basura, que borra de la cache todo lo que ya no esté referenciado:
>
> ```bash
> dvc gc --workspace   # conserva lo referenciado por el workspace actual
> ```
>
> `dvc gc` es una operación destructiva sobre la cache: conviene revisar bien los flags (`--workspace`, `--all-branches`, etc.) antes de ejecutarla.

> **Importante:** esto aplica a experimentos que **aún no se han aplicado ni convertido en *commits***. Si en su día se hizo `dvc exp apply` y luego se confirmó en Git, ese estado ya forma parte del historial normal: `dvc exp remove` no lo toca, y para deshacerlo hay que trabajar sobre los *commits* de Git (`revert`, `reset`, etc.), no sobre los experimentos.

### `dvc repro` frente a `dvc exp run`

| | `dvc repro` | `dvc exp run` |
|---|---|---|
| Ejecuta el pipeline (DAG + detección de cambios) | Sí | Sí |
| Registra el resultado como experimento | No | Sí |
| Pensado para | Reproducir/actualizar el pipeline "oficial" | Explorar y comparar variantes |

En la práctica: se usa `dvc exp run` para experimentar y comparar; cuando una variante convence, se aplica (`dvc exp apply`) y se confirma en Git, dejando el pipeline reproducible con `dvc repro`.

### Sincronización de experimentos con el remoto

Subir los *outputs* al repositorio remoto y los metadatos al repositorio Git:

```bash
dvc exp push origin -A     # -A equivale a --all-commits en este comando
```

Descargar experimentos del repositorio remoto:

```bash
dvc exp pull origin -A     # -A equivale a --all-commits en este comando
```

---

## 7. Eliminar experimentos remotos y desmantelar DVC

Borrar los experimentos publicados en el remoto Git, borrar también los locales y, finalmente, desvincular DVC del proyecto:

```bash
dvc exp remove --git-remote origin --all   # experimentos del remoto Git
dvc exp remove --all                       # experimentos locales
dvc destroy                                # elimina DVC del proyecto
```

> **Aviso:** `dvc destroy` es una operación **destructiva e irreversible**. Elimina el directorio `.dvc/`, todos los ficheros `.dvc`, `dvc.yaml`, `dvc.lock` y demás metadatos de DVC, dejando el repositorio como un proyecto Git normal. Los datos que solo estuvieran en la *cache* dejan de ser recuperables por DVC. Úsalo únicamente cuando quieras retirar DVC por completo.

---

## Apéndice: instalación de DVC en Windows

Seguir los pasos indicados en la [página web oficial](https://dvc.org/doc/install/windows).
