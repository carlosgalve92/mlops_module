# GitHub

> **Módulo 2 — Repositorios remotos**
> Colaboración y sincronización del código con la nube.

**GitHub** es una plataforma que permite almacenar, gestionar y compartir código fuente de manera eficiente, facilitando la colaboración en proyectos de software mediante repositorios remotos. Mientras que Git gestiona el versionado **local**, GitHub aporta la capa **remota** que permite trabajar en equipo.

---

## Tabla de contenidos

1. [Conectar con el repositorio remoto](#1-conectar-con-el-repositorio-remoto)
2. [Subir y eliminar ramas](#2-subir-y-eliminar-ramas)
3. [Descargar cambios: fetch, merge, rebase y pull](#3-descargar-cambios-fetch-merge-rebase-y-pull)
4. [Publicar tags en GitHub](#4-publicar-tags-en-github)
5. [Actions (workflows)](#5-actions-workflows)
6. [Apéndice: crear una cuenta en GitHub](#apéndice-crear-una-cuenta-en-github)

---

## 1. Conectar con el repositorio remoto

Para vincular tu repositorio local con uno remoto:

```bash
git remote add <nombre_remoto> <url_del_repositorio>
```

> [!NOTE]
> Por convención, al repositorio remoto principal se le llama **`origin`**.

### Subir cambios al remoto

La primera vez conviene usar `-u` (equivale a `--set-upstream`) para asociar la rama local con la remota:

```bash
git push -u origin main
```

En subidas posteriores basta con `git push`.

---

## 2. Subir y eliminar ramas

| Acción | Comando |
|---|---|
| Subir la rama actual (con seguimiento) | `git push -u origin <rama>` |
| Eliminar una rama en el remoto | `git push origin --delete <rama>` |

---

## 3. Descargar cambios: fetch, merge, rebase y pull

### 3.1 Verificar cambios antes de integrarlos (`fetch`)

`fetch` descarga las novedades del remoto **sin** modificar tu rama de trabajo, permitiéndote revisarlas primero:

```bash
git fetch origin
```

> [!NOTE]
> Esto genera en local **ramas de seguimiento** del remoto con el nombre `origin/<nombre de la rama>`.

### 3.2 Integrar los cambios descargados

Una vez revisados, puedes integrarlos con *merge* o con *rebase*:

```bash
# Merge
git merge origin/<rama>
```

```bash
# Rebase
git rebase origin/<rama>
```

### 3.3 Fetch + integración en un solo paso (`pull`)

`pull` combina la descarga y la integración:

```bash
# fetch + merge
git pull origin <rama>
```

```bash
# fetch + rebase
git pull --rebase origin <rama>
```

> [!TIP]
> `git pull --rebase` mantiene un historial **lineal y limpio**, evitando commits de merge innecesarios. Es la opción preferida en muchos equipos.

**Resumen:**

| Comando | Equivale a |
|---|---|
| `git pull origin <rama>` | `fetch` + `merge` |
| `git pull --rebase origin <rama>` | `fetch` + `rebase` |

---

## 4. Publicar tags en GitHub

Los *tags* creados en local **no se suben automáticamente**; hay que enviarlos de forma explícita.

| Acción | Comando |
|---|---|
| Subir un tag concreto | `git push origin <nombre del tag>` |
| Subir todos los tags | `git push <remoto> --tags` |
| Borrar un tag del remoto | `git push --delete <remoto> <nombre del tag>` |

---

## 5. Actions (workflows)

**GitHub Actions** es el sistema de automatización integrado en GitHub. Permite ejecutar tareas de **CI/CD** (Integración y Despliegue Continuos) —y cualquier otra automatización— en respuesta a eventos del repositorio: ejecutar pruebas, validar el formato del código, construir imágenes Docker, entrenar o desplegar modelos, publicar *releases*, etc.

Los flujos de trabajo se definen en ficheros **`.yml`** dentro de la carpeta **`.github/workflows/`**. Cada fichero es un *workflow* independiente.

### 5.1 Conceptos clave

| Concepto | Qué es |
|---|---|
| **Workflow** | Proceso automatizado completo, definido en un `.yml`. Un repo puede tener varios. |
| **Event / Trigger** (`on`) | Suceso que dispara el workflow (un `push`, un `pull_request`, una ejecución manual, un horario…). |
| **Job** | Conjunto de pasos que se ejecutan en la misma máquina (*runner*). Por defecto, los jobs corren en paralelo. |
| **Step** | Cada una de las tareas de un job. Puede ser un comando (`run`) o una acción reutilizable (`uses`). |
| **Action** | Componente reutilizable y empaquetado (p. ej. `actions/checkout`) que encapsula lógica común. |
| **Runner** | Máquina que ejecuta el job (`ubuntu-latest`, `windows-latest`… o *self-hosted*). |

> [!NOTE]
> Jerarquía: un **workflow** contiene uno o varios **jobs**, y cada **job** contiene una secuencia de **steps**.

### 5.2 Anatomía de un workflow

```yaml
name: Mi Workflow            # nombre visible en la pestaña Actions

on:                          # CUÁNDO se ejecuta
  push:
    branches: [ main ]

jobs:                        # QUÉ se ejecuta
  mi-job:
    runs-on: ubuntu-latest   # DÓNDE se ejecuta
    steps:
      - uses: actions/checkout@v4        # acción reutilizable
      - name: Saludar
        run: echo "Hola mundo"           # comando de shell
```

### 5.3 Disparadores (`on`)

| Disparador | Cuándo se ejecuta |
|---|---|
| `push` | Al subir commits (opcionalmente filtrando por `branches` o `paths`). |
| `pull_request` | Al abrir/actualizar una PR. Ideal para validar antes de fusionar. |
| `workflow_dispatch` | Ejecución **manual** desde la interfaz de GitHub (botón *Run workflow*). |
| `schedule` | En un horario definido con sintaxis *cron*. |

```yaml
on:
  push:
    branches: [ main ]
    paths: [ 'src/**' ]        # solo si cambian ficheros de src/
  workflow_dispatch:           # permite lanzarlo a mano
  schedule:
    - cron: '0 6 * * 1'        # lunes a las 06:00 UTC (min hora díaMes mes díaSemana)
```

> [!TIP]
> Combinar `push` con `workflow_dispatch` es muy habitual: automatizas en cada subida, pero también puedes relanzarlo manualmente sin hacer un commit.

### 5.4 Jobs: dependencias, condiciones y matrices

- **`needs`**: encadena jobs. Un job con `needs: build` no arranca hasta que `build` termina con éxito.
- **`if`**: ejecuta el job (o step) solo si se cumple una condición.
- **`strategy.matrix`**: repite el job con distintas combinaciones de variables (p. ej. varias versiones de Python).

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [ "3.10", "3.11", "3.12" ]
    steps:
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

  deploy:
    needs: test                              # espera a 'test'
    if: github.ref == 'refs/heads/main'      # solo en main
    runs-on: ubuntu-latest
    steps:
      - run: echo "Desplegando..."
```

### 5.5 Steps: `uses` vs `run`

- **`uses`** ejecuta una *action* ya empaquetada. Conviene **fijar la versión** (`@v4`) para builds reproducibles.
- **`run`** ejecuta comandos de shell. Con `|` puedes escribir varias líneas.

```yaml
steps:
  - uses: actions/checkout@v4        # acción oficial/de terceros
  - name: Instalar y probar
    run: |                           # varios comandos
      pip install .
      pytest
```

### 5.6 Secretos y variables

- **`secrets`**: valores sensibles (tokens, claves) guardados en *Settings → Secrets and variables → Actions*. Se leen con `${{ secrets.NOMBRE }}` y aparecen **enmascarados** en los logs.
- **`env`**: variables de entorno reutilizables. Pueden definirse a nivel de workflow, job o step.

```yaml
env:
  IMAGE_REPO: mi_imagen
steps:
  - run: echo "Repo=${{ env.IMAGE_REPO }} y token oculto=${{ secrets.MI_TOKEN }}"
```

> [!NOTE]
> Nunca escribas credenciales directamente en el `.yml`: usa siempre *secrets*.

### 5.7 Permisos y autenticación OIDC

`permissions` controla lo que puede hacer el `GITHUB_TOKEN` (principio de **mínimo privilegio**). Para autenticarte contra la nube (p. ej. Azure) sin guardar credenciales de larga duración, se usa **OIDC**: GitHub emite un token de identidad efímero que el proveedor valida contra una *credencial federada*.

```yaml
permissions:
  contents: read     # leer el repo
  id-token: write    # imprescindible para el login OIDC
```

### 5.8 Caché y artefactos

- **Caché** (`actions/cache` o la caché de Buildx): reutiliza dependencias/capas entre ejecuciones para acelerar los builds.
- **Artefactos** (`actions/upload-artifact` / `download-artifact`): guardan ficheros de una ejecución (informes, binarios) o los comparten **entre jobs** (los jobs no comparten disco por defecto).

### 5.9 Concurrencia

`concurrency` evita ejecuciones solapadas. Útil en despliegues: si llega un push nuevo mientras otro despliega, se cancela el anterior.

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
```

### 5.10 El workflow de este proyecto (`CD API`)

El fichero `deployment.yml` implementa el **despliegue continuo** de la API en Azure. Su estructura es:

1. **Disparadores**: `push` a `master` y ejecución manual (`workflow_dispatch`).
2. **Job `build-test`**: descarga el código, carga la clave SSH, instala dependencias, configura el remoto **DVC**, construye la imagen con **Buildx** (sin publicarla) y la valida con un *smoke test* contra `/api/health`.
3. **Job `release`** (tras `build-test` y solo en `master`): inicia sesión en **Azure vía OIDC**, publica la imagen en **Azure Container Registry (ACR)** etiquetada con el SHA del commit y despliega una nueva revisión en **Azure Container Apps (ACA)**.

> [!TIP]
> Separar *build-test* y *release* garantiza que solo se despliega código que ha pasado las pruebas. El uso de `needs` y `if` asegura ese orden y limita el despliegue a la rama principal.

---

## Apéndice 1: crear una cuenta en GitHub

📺 [Tutorial para crear una cuenta en GitHub](https://www.youtube.com/watch?v=h5cKAd94QNo&ab_channel=AISciences)

## Apéndice 2: configurar autenticacion a GitHub en mv azure por ssh

Se necesita una clave SSH cuya parte **pública** esté registrada en GitHub y cuya parte **privada** esté disponible en la VM para poder hacer `git push`/`git pull`. Para este proyecto se evita dejar la clave privada en el disco de la VM.

Para crear una clave ssh, ejecutar:

```
ssh-keygen -t ed25519 -C "carlosgalvemateo@micorreo.com"
```

#### Clave privada en Azure Key Vault + identidad administrada

La idea es guardar la clave privada como secreto en **Azure Key Vault** y cargarla en memoria (en el `ssh-agent`) solo cuando haga falta, usando la identidad administrada de la VM. Así la clave nunca se escribe en el disco de la VM.

Preparación (una sola vez):

- Crear un Key Vault y guardar en él la clave privada como secreto. Para evitar problemas de formato al reconstruir los saltos de línea, se recomienda guardarla **codificada en base64**:

    Linux
    ```
    base64 -w0 ~/.ssh/id_ed25519          # copia la salida y guárdala como secreto en Key Vault
    ```

    Windows
    ```
    [Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\.ssh\id_ed25519"))          # copia la salida y guárdala como secreto en Key Vault
    ```

- Registrar la clave **pública** correspondiente en GitHub: **Settings → SSH and GPG keys → New SSH key**.
- Dar permiso de lectura de secretos a la identidad administrada de la VM: rol **Key Vault Secrets User** (si el vault usa RBAC) o una directiva de acceso con permiso *Get* sobre secretos. (Es análogo al rol "Colaborador de datos de Storage Blob" que se asignó para el almacenamiento.)

    - Es necesario para poder crear el secret que tu usuario tenga permisos de **Key Vault Secrets Officer**

**A.1. Agente SSH persistente gestionado por systemd**

En lugar de que el script arranque su propio `ssh-agent` (lo que obliga a ejecutarlo con `source` y pierde el agente entre sesiones), se deja que **systemd** gestione el agente como servicio de usuario. Arranca solo, sobrevive entre sesiones y expone el socket en una ruta fija. Se configura una sola vez.

Crear el servicio de usuario:

```
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/ssh-agent.service
```

Con el siguiente contenido:

```ini
[Unit]
Description=SSH key agent

[Service]
Type=simple
Environment=SSH_AUTH_SOCK=%t/ssh-agent.socket
ExecStart=/usr/bin/ssh-agent -D -a $SSH_AUTH_SOCK

[Install]
WantedBy=default.target
```

Indicar a la shell que use ese socket, añadiendo al final de `~/.bashrc`:

```
export SSH_AUTH_SOCK="$XDG_RUNTIME_DIR/ssh-agent.socket"
```

Activar y arrancar el servicio:

```
systemctl --user daemon-reload
systemctl --user enable --now ssh-agent
```

(Opcional) Para que el agente siga vivo aunque no haya ninguna sesión abierta —útil si la VM ejecuta trabajos por su cuenta—:

```
loginctl enable-linger $USER
```

Recargar el entorno y comprobar:

```
source ~/.bashrc
echo $SSH_AUTH_SOCK                   # /run/user/<uid>/ssh-agent.socket
systemctl --user status ssh-agent     # active (running)
```

**A.2. Script de carga de la clave (`~/.local/bin/ssh_configuration.sh`)**

Como el agente ya lo gestiona systemd, el script se limita a traer la clave desde Key Vault y añadirla con `ssh-add`. Ya **no** arranca ningún agente y **no** hace falta ejecutarlo con `source`. Personaliza `KEY_VAULT_NAME` y `SECRET_NAME`:

```bash
#!/bin/bash
KEY_VAULT_NAME=""
SECRET_NAME=""

# Añade la huella de GitHub a known_hosts
mkdir -p ~/.ssh && chmod 700 ~/.ssh
if ! grep -q "github.com" ~/.ssh/known_hosts 2>/dev/null; then
    ssh-keyscan github.com >> ~/.ssh/known_hosts
fi

# Token de acceso a Key Vault vía identidad administrada de la VM
ACCESS_TOKEN=$(curl -s -H "Metadata:true" \
  "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net" \
  | jq -r .access_token)

# Descarga la clave (guardada en base64) y la carga en el agente que gestiona systemd
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
     "https://${KEY_VAULT_NAME}.vault.azure.net/secrets/${SECRET_NAME}?api-version=7.4" \
     | jq -r .value \
     | base64 -d \
     | ssh-add -
```

Añadir en `~/.bashrc`:

```
if ! ssh-add -l &>/dev/null; then
    ~/.local/bin/ssh_configuration.sh
fi
```

Y damos perimos de ejecución al script:

```
chmod +x ~/.local/bin/ssh_configuration.sh
```

Ejecutar y comprobar:

```
ssh-add -l                            # debe listar la clave cargada
ssh -T git@github.com                 # "Hi <usuario>! You've successfully authenticated..."
```

## Apéndice 3: configurar autenticación OIDC de GitHub Actions en Azure

El workflow de despliegue (`deployment.yml`) inicia sesión en Azure con **OIDC**, de modo que **no** hay que guardar credenciales de larga duración (contraseñas o *client secrets*) en GitHub. En su lugar, se crea una **credencial federada**: una relación de confianza por la que Azure acepta el token de identidad efímero que GitHub emite en cada ejecución.

**Cómo funciona (resumen):**

1. GitHub Actions genera un **token OIDC** efímero que describe *quién* pide acceso (organización, repositorio, rama…).
2. La acción `azure/login@v2` presenta ese token a Azure junto con `client-id`, `tenant-id` y `subscription-id`.
3. Azure valida el token contra la **credencial federada**: si el emisor (*issuer*) y el identificador (*subject*) coinciden con lo registrado, emite un token de acceso real.

> [!NOTE]
> El bloque `permissions: id-token: write` del workflow es lo que autoriza a GitHub a emitir ese token OIDC. Sin él, el login falla. Es el mismo principio que la **identidad administrada** del Apéndice 2: evitar credenciales de larga duración.

La identidad puede ser una **App Registration** (con su *service principal*) o una **user-assigned managed identity**. A continuación se detallan las dos vías: línea de comandos (reproducible) y portal.

### A.1. Vía CLI (`az`)

Define primero las variables:

```bash
APP_NAME="gh-actions-cd-api"
SUBSCRIPTION_ID="<tu-subscription-id>"
RESOURCE_GROUP="<tu-grupo-de-recursos>"
GH_ORG="<tu-org>"
GH_REPO="<tu-repo>"
ACR_NAME="<tu-acr>"
```

**1) Crear la App Registration y su service principal:**

```bash
az ad app create --display-name "$APP_NAME"
APP_ID=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv)
az ad sp create --id "$APP_ID"        # objeto sobre el que se asignan permisos
```

**2) Añadir la credencial federada** (el `subject` debe coincidir *exactamente* con el contexto que dispara el workflow; aquí, la rama `master`):

```bash
az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters '{
    "name": "github-master",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$GH_ORG"'/'"$GH_REPO"':ref:refs/heads/master",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

**3) Asignar permisos (RBAC):** desplegar en el grupo de recursos y publicar imágenes en el ACR:

```bash
# Desplegar en ACA
az role assignment create \
  --assignee "$APP_ID" \
  --role "Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP"

# Publicar imágenes en el ACR
ACR_ID=$(az acr show -n "$ACR_NAME" --query id -o tsv)
az role assignment create \
  --assignee "$APP_ID" \
  --role "AcrPush" \
  --scope "$ACR_ID"
```

**4) Recoger los identificadores** para los *secrets* de GitHub:

```bash
echo "$APP_ID"                            # -> AZURE_CLIENT_ID
az account show --query tenantId -o tsv    # -> AZURE_TENANT_ID
echo "$SUBSCRIPTION_ID"                    # -> AZURE_SUBSCRIPTION_ID
```

### A.2. Vía portal de Azure

| Paso | Dónde | Qué hacer |
|---|---|---|
| 1. Crear la App Registration | **Microsoft Entra ID → App registrations → New registration** | Nombre (p. ej. `gh-actions-cd-api`), tipo de cuenta por defecto, *Register*. Se crea también su *service principal*. |
| 2. Anotar los IDs | **App → Overview** | Copiar *Application (client) ID* (→ `AZURE_CLIENT_ID`) y *Directory (tenant) ID* (→ `AZURE_TENANT_ID`). El *subscription-id* está en **Subscriptions → tu suscripción**. |
| 3. Credencial federada | **App → Certificates & secrets → Federated credentials → Add credential** | Escenario: *GitHub Actions deploying Azure resources*. Rellenar *Organization* y *Repository*. *Entity type* = **Branch**, valor `master`. Poner un *Name* y *Add*. Los campos *Issuer/Audiences/Subject* se autorrellenan. |
| 4. Permisos en el grupo | **Resource group → Access control (IAM) → Add role assignment** | Rol **Contributor**, *Member* = la app creada. *Review + assign*. |
| 5. Permiso en el ACR | **ACR → Access control (IAM) → Add role assignment** | Rol **AcrPush**, *Member* = la app creada. |
| 6. Secrets en GitHub | **Repo → Settings → Secrets and variables → Actions** | Crear `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` y `AZURE_SUBSCRIPTION_ID`. |

> [!IMPORTANT]
> El **`subject`** debe coincidir *exactamente* con el contexto del workflow; **no** admite comodines para ramas ni tags. Como el `deployment.yml` corre en `master`, basta con `Branch = master`. Para cubrir además *pull requests* o un *environment*, hay que crear **una credencial federada por cada contexto** (misma app, distinto `subject` y `name`). Si el *on-push* se ejecutara contra muchas ramas o tags, la recomendación oficial es usar un **Environment** en lugar de una rama.

> [!TIP]
> Como alternativa a la App Registration, puedes usar una **user-assigned managed identity** y añadirle la credencial federada en la misma pestaña; en ese caso usarías su `clientId` como `AZURE_CLIENT_ID`.

Con esto, el paso `Azure login (OIDC)` del workflow autentica correctamente y ya no hay ningún secreto de credencial que rotar ni que pueda filtrarse.
