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

**GitHub Actions** permite automatizar tareas de **CI/CD** (integración y despliegue continuos) directamente en el repositorio: ejecutar pruebas, validar formato, entrenar o desplegar modelos, publicar *releases*, etc.

Los flujos se definen en ficheros `.yml` dentro de la carpeta `.github/workflows/`.

> [!NOTE]
> Sección en construcción. Aquí se documentarán los *workflows* del proyecto (disparadores, *jobs* y pasos).

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
