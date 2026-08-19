# Docker

**Docker** es una plataforma de código abierto que permite empaquetar aplicaciones y sus dependencias en contenedores, facilitando su despliegue y ejecución en cualquier entorno. Docker se apoya en dos componentes principales:

- **Imágenes:** plantilla construida por capas que contiene los archivos del sistema, el diseño y las configuraciones necesarias para crear instancias (contenedores).
- **Contenedores:** entorno aislado que incluye todo lo necesario para la ejecución de una aplicación. Se crean a partir de imágenes y pueden instanciarse en cualquier servidor.

## Contenedores frente a Máquinas Virtuales (MV)

Los **contenedores** equivalen a ejecutar varias aplicaciones independientes en la misma máquina, cada una con su propio entorno aislado. Las **máquinas virtuales**, en cambio, son como tener varias computadoras completas dentro de una sola.

| Criterio | Contenedores (Docker) | Máquinas Virtuales |
|---|---|---|
| **Nivel de virtualización** | A nivel de sistema operativo | A nivel de hardware |
| **Qué virtualiza** | Solo las aplicaciones y sus dependencias, compartiendo el *kernel* del SO anfitrión | Un sistema operativo completo (*kernel*, *drivers*, etc.) |
| **Arranque** | Muy rápido (segundos) | Más lento (minutos) |
| **Peso** | Ligero (comparten *kernel*, sin SO completo) | Pesado (cada MV requiere su propio SO) |
| **Uso típico** | Microservicios, despliegue rápido, CI/CD, empaquetado de aplicaciones | Aislamiento completo, ejecutar distintos SO (p. ej. Windows sobre Linux) |
| **Ventaja** | Mayor densidad y eficiencia de recursos | Aislamiento total del sistema (mayor seguridad o *kernels* distintos) |

---

## Comandos

### Contenedores e imágenes: listado

Listar contenedores en ejecución:

```bash
docker ps
```

Listar imágenes:

```bash
docker images
```

### Gestión de redes

```bash
docker network
```

Crear una red:

```bash
docker network create <nombre_red> --subnet <subnet> --ip-range <ip_range>
```

Listar redes:

```bash
docker network ls
```

Eliminar una red:

```bash
docker network rm <red>
```

Conectar un contenedor a una red:

```bash
docker network connect <nombre_red> <contenedor>
```

Desconectar un contenedor de una red:

```bash
docker network disconnect <nombre_red> <contenedor>
```

### Gestión de volúmenes

```bash
docker volume
```

Crear un volumen:

```bash
docker volume create <nombre_volumen>
```

Listar volúmenes:

```bash
docker volume ls
```

Eliminar un volumen:

```bash
docker volume rm <volumen>
```

### Gestión de contenedores

```bash
docker container
docker run
```

Crear un contenedor (sin lanzarlo):

```bash
docker container create --name <alias> --network <red> --volume <path_local:path_container:ro|rw> -p <puerto_local:puerto_container> <imagen>
```

Crear un contenedor y lanzarlo:

```bash
docker run <-itd> --name <alias> --network <red> --volume <path_local:path_container:ro|rw> -p <puerto_local:puerto_container> <imagen>
```

Argumentos más utilizados:

- `-i` (`--interactive`): mantiene la entrada estándar (*stdin*) abierta para poder interactuar con el contenedor.
- `-t` (`--tty`): asocia una terminal virtual (TTY) al contenedor, lo que permite que aplicaciones como `bash` o `vim` funcionen correctamente.
- `-d` (`--detach`): ejecuta el contenedor en segundo plano.
- `--name`: asigna un alias al contenedor.
- `--network`: conecta el contenedor a una red específica.
- `-p` (`--publish`): mapea un puerto del contenedor a un puerto de la máquina anfitriona.
- `-v` (`--volume`): mapea un directorio del anfitrión a un directorio del contenedor (volumen).
- `--volumes-from`: reutiliza los volúmenes de otro contenedor.

Ejemplo:

```bash
docker run -i -t -d --name prueba_ubuntu -v C:/Users/34660/projects/mlops/data:/projects/mlops/data/ -p 8080:8080 --network prueba_red ubuntu
```

### Gestión de imágenes

```bash
docker image
```

Eliminar una imagen:

```bash
docker image rm <imagen>
```

Crear una imagen a partir de un contenedor:

```bash
docker commit <nombre_container> <nombre_imagen:TAG>
```

No obstante, la forma recomendada de generar imágenes es mediante un **Dockerfile**.

---

## Dockerfile

Un **Dockerfile** es la opción recomendada para generar imágenes de forma reproducible. Para construir la imagen a partir de él se ejecuta:

```bash
docker <buildx> build --ssh default --secret id=<id_del_secret>,src=<file> -t <nombre_imagen:tag> -f <ubicacion>
```

- `--ssh`: permite utilizar las claves SSH del entorno local durante la construcción de la imagen. Para usarlo en PowerShell de Windows, el `ssh-agent` debe estar activo:

  ```powershell
  Start-Service ssh-agent
  ```

  Conviene comprobar que la clave está cargada; si no aparece, se añade con:

  ```powershell
  ssh-add ~/.ssh/<clave_privada>
  ```

- `--secret`: permite pasar secretos al proceso de construcción de forma segura, sin que queden expuestos en la imagen resultante. Los secretos pueden proporcionarse como archivos o como variables de entorno y estarán disponibles *durante* la construcción, pero no formarán parte de la imagen final.

### Directiva de sintaxis (*syntax directive*)

En la primera línea se puede indicar la versión de la sintaxis de construcción del Dockerfile, lo que habilita características avanzadas:

- `# syntax=docker/dockerfile:1` — sintaxis estándar con la funcionalidad general (valor por defecto si no se especifica).
- `# syntax=docker/dockerfile:1.2` — soporta `RUN --mount=type=cache`, entre otros.
- `# syntax=docker/dockerfile:1.3` — añade `--mount=type=secret` y *SSH forwarding*.
- `# syntax=docker/dockerfile:1.4` — soporte completo a `COPY --from`, *target*, *secrets*, *cache*, etc.
- `# syntax=docker/dockerfile:1.5` — versión más moderna, con mejoras en el manejo de características.
- `# syntax=docker/dockerfile:experimental` — alias de versiones avanzadas; su comportamiento puede variar con el tiempo.

### Principales instrucciones

- `FROM <imagen:tag>` — primera instrucción; indica la imagen base de la que se parte.
- `LABEL <clave>=<valor>` — añade metadatos a la imagen (p. ej. `maintainer`).
- `RUN <comando>` — ejecuta un comando durante la construcción de la imagen.
- `ENV <clave>=<valor>` — define variables de entorno.
- `WORKDIR <ruta>` — establece el directorio de trabajo.
- `ADD <origen> <destino>` — copia información del anfitrión al contenedor; además puede descomprimir archivos y soporta URLs.
- `COPY <origen> <destino>` — copia información del anfitrión al contenedor (sin descomprimir ni soportar URLs).
- `EXPOSE <puerto>` — documenta el puerto en el que el contenedor escuchará.
- `CMD [<ejecutable>, <arg_1>, ..., <arg_N>]` — se ejecuta al iniciar el contenedor. Si se pasan argumentos al crear el contenedor, se sobrescribe.
- `ENTRYPOINT [<ejecutable>, <arg_1>, ..., <arg_N>]` — se ejecuta al iniciar el contenedor y se aplica siempre, se pasen o no argumentos en su creación.

---

## Despliegue en Azure: del registro de contenedores a Azure Container Apps

Una vez construida la imagen, el siguiente paso para llevar la aplicación a producción consiste en **publicarla en un registro de contenedores remoto** y, desde ahí, **desplegarla en un servicio de ejecución**. En Azure este flujo se apoya en dos servicios:

- **Azure Container Registry (ACR):** registro privado y gestionado donde se almacenan las imágenes (el equivalente privado a Docker Hub). Es el "repositorio remoto" al que se sube la imagen.
- **Azure Container Apps (ACA):** plataforma *serverless* que ejecuta contenedores sin necesidad de gestionar la infraestructura subyacente (a diferencia de Kubernetes). Descarga la imagen desde el ACR, la ejecuta y, opcionalmente, la expone a Internet.

El flujo completo es: **construir la imagen → subirla al ACR → conceder permisos de lectura → desplegar en Container Apps**. Todos los **recursos** y **permisos** se crean desde el [portal de Azure](https://portal.azure.com); el único paso que requiere la línea de comandos es la **subida de la imagen**, ya que un *push* de Docker no puede realizarse desde la interfaz gráfica. Tanto la subida como la descarga se autentican mediante **identidades administradas** (*managed identities*), sin contraseñas.

### Requisitos previos

- Una cuenta de Azure con una **suscripción activa** y permisos para crear recursos y asignar roles (rol `Owner`, o la combinación `Contributor` + `User Access Administrator` sobre el grupo de recursos).
- Docker instalado en la máquina desde la que se sube la imagen. Para autenticarse con `az login --identity`, esa máquina debe ser un recurso de Azure con una **identidad administrada** asignada (p. ej. una VM de Azure) que tenga el rol `AcrPush` y `Reader` sobre el registro.

### Paso 1: crear el grupo de recursos (portal)

El **grupo de recursos** es el contenedor lógico que agrupa todos los recursos relacionados.

1. En el portal, busca **"Grupos de recursos"** en la barra superior y ábrelo.
2. Pulsa **Crear**.
3. Selecciona la **suscripción**, asigna un **nombre** al grupo (p. ej. `mi-grupo`) y elige la **región** (p. ej. *West Europe*).
4. Pulsa **Revisar y crear** → **Crear**.

### Paso 2: crear el Azure Container Registry (portal)

El **ACR** es el registro remoto donde se almacenarán las imágenes.

1. Busca **"Container Registries"** (Registros de contenedor) en la barra superior y pulsa **Crear**.
2. En la pestaña **Aspectos básicos**:
   - **Suscripción** y **grupo de recursos**: los creados en el paso anterior.
   - **Nombre del registro**: único a nivel global, solo minúsculas y números (p. ej. `miregistro`). Formará el servidor de acceso `miregistro.azurecr.io`.
   - **Ubicación**: la misma región del grupo de recursos.
   - **SKU**: `Basic` es suficiente para empezar (`Standard` y `Premium` añaden más capacidad y funciones como *geo-replicación* o *private endpoints*).
3. Pulsa **Revisar y crear** → **Crear**.

### Paso 3: subir la imagen al registro (línea de comandos con identidad administrada)

Este es el único paso que **no** puede hacerse desde el portal. En lugar de credenciales de usuario, la CLI de Azure se autentica con la **identidad administrada** de la máquina y obtiene un *token* temporal para Docker. La identidad usada debe tener el rol `AcrPush` sobre el registro (se concede desde **Control de acceso (IAM)** del ACR, igual que el `AcrPull` del Paso 5).

```bash
# 1. Autenticar la CLI con la identidad administrada del recurso (p. ej. la VM de Azure)
az login --identity
#    Para una identidad de usuario concreta: az login --identity --username <client_id>

# 2. Obtener credenciales temporales del registro para Docker
az acr login --name miregistro

# 3. Etiquetar la imagen local con la ruta del ACR
docker tag mi-app:v1 miregistro.azurecr.io/mi-app:v1

# 4. Subir la imagen
docker push miregistro.azurecr.io/mi-app:v1
```

`az acr login` configura el cliente de Docker con un *token* temporal derivado de la identidad; **no** almacena usuario ni contraseña. Para comprobar que la imagen quedó almacenada, en el portal abre el registro → **Servicios** → **Repositorios**; debería aparecer `mi-app` con su etiqueta `v1`.

#### Etiquetar la imagen con el commit de Git (primer *push* manual)

En lugar de una etiqueta fija como `v1`, conviene ligar cada imagen al **commit** que la generó, para saber con exactitud qué código corre en cada versión. El *hash* del commit se obtiene con `git rev-parse` y se reutiliza como etiqueta. Este es el **primer** *push*, que debe hacerse **antes** de crear la app (el asistente del Paso 5 seleccionará esta etiqueta):

```bash
# Etiqueta a partir del hash completo del commit (prefijo "gh-" para identificar el origen)
TAG=gh-$(git rev-parse HEAD)        # p. ej. gh-a1b2c3d4...  (40 caracteres)

# Autenticación (igual que arriba)
az login --identity
az acr login --name miregistro

# Construir, etiquetar y subir con la etiqueta del commit
docker build -t miregistro.azurecr.io/mi-app:$TAG .
docker push miregistro.azurecr.io/mi-app:$TAG

echo "Etiqueta subida: $TAG"        # anótala para seleccionarla al crear la app
```

Se usa el *hash* **completo** (`git rev-parse HEAD`, 40 caracteres) en lugar del corto (`--short`) para que coincida con el que produciría un *pipeline* de CI/CD basado en `github.sha`. Para listar las etiquetas presentes en el registro:

```bash
az acr repository show-tags --name miregistro --repository mi-app --output table
```

> El *hash* solo refleja lo que está **confirmado** en Git. Si construyes con cambios locales sin confirmar, la etiqueta no representará fielmente el código; confirma (*commit*) antes de construir.

### Paso 4: crear el entorno de Container Apps (portal)

El **entorno** de Container Apps es la frontera de red y de observabilidad que comparten las apps, y es quien aloja la **identidad de sistema** que se usará para descargar la imagen. Debe existir antes de crear la app para poder seleccionarlo:

1. Busca **"Container Apps Environments"** (Entornos de Container Apps) en el portal y pulsa **Crear**.
2. En **Aspectos básicos**: selecciona la **suscripción**, el **grupo de recursos**, asigna un **nombre** (p. ej. `mi-entorno`) y la **región**.
3. Pulsa **Revisar y crear** → **Crear**.

> No es necesario habilitar la identidad del entorno ni asignar el rol `AcrPull` a mano: el asistente de creación de la app lo hace **automáticamente** al elegir la identidad del entorno (ver Paso 5). Si se prefiere, puede habilitarse de antemano en **Entorno → Configuración → Identidad → Asignada por el sistema**.

### Paso 5: crear la Container App y configurar la autenticación del registro (portal)

1. Busca **"Container Apps"** en la barra superior y pulsa **Crear**.
2. En la pestaña **Aspectos básicos**:
   - **Suscripción** y **grupo de recursos**: los del proyecto.
   - **Nombre de la aplicación de contenedor** (p. ej. `mi-app`).
   - **Región**.
   - **Entorno de Container Apps**: selecciona el **entorno existente** `mi-entorno` (el creado en el Paso 4).
3. En la pestaña **Contenedor**:
   - **Desmarca** la casilla *Usar imagen de inicio rápido* (*Use quickstart image*).
   - **Origen de la imagen**: **Azure Container Registry**.
   - Selecciona el **registro** (`miregistro`), la **imagen** (`mi-app`) y la **etiqueta** (`v1`).
4. En el bloque **Autenticación del registro** (*Registry authentication*):
   - **Tipo de autenticación** (*Authentication type*): **Identidad administrada** (*Managed identity*). La otra opción, *Secrets* (usuario y contraseña), solo está disponible si el ACR tiene habilitado el usuario administrador, que aquí no usamos.
   - **Identidad administrada** (*Managed identity*): selecciona en el desplegable **`System assigned Identity (environment)`**, es decir, la identidad de sistema del entorno.
   - **Asignación de rol requerida** (*Required role assignment*): el portal muestra **`ACR pull`** con el ámbito del registro (`Scope: 'miregistro'`) e informa de que *"la nueva identidad administrada tendrá todas las asignaciones de rol necesarias"*. Es decir, el rol `AcrPull` se **crea automáticamente**; no hay que configurarlo a mano.
5. En la pestaña **Entrada** (*Ingress*):
   - Activa **Entrada habilitada**.
   - Tipo de tráfico: **Aceptar tráfico desde cualquier lugar** (equivale a *ingress* **externo**; elige la opción limitada al entorno si la app no debe ser pública).
   - **Puerto de destino**: el puerto en el que la aplicación escucha dentro del contenedor (el mismo que declara `EXPOSE` en el `Dockerfile`).
6. Pulsa **Revisar y crear** → **Crear** y espera unos minutos.
7. Al terminar, abre el recurso: en **Información general** aparece la **URL de la aplicación** (FQDN, p. ej. `https://mi-app.<sufijo>.westeurope.azurecontainerapps.io`), desde la que se accede a la app.

> **Sobre la asignación automática del rol:** para que el portal cree por ti la asignación `AcrPull` necesitas permisos de administración de RBAC (rol `Owner` o `User Access Administrator` sobre el registro o el grupo de recursos). Si no los tienes, o si el despliegue falla por permisos, asígnalo manualmente: **Container Registry → Control de acceso (IAM) → Agregar asignación de roles → `AcrPull` →** miembro de tipo **Entorno de Container Apps** (`mi-entorno`). La propagación puede tardar unos segundos.

> **Requisito del registro:** para autenticarse con identidad administrada, el ACR debe permitir *tokens* de audiencia ARM (comportamiento por defecto en registros actuales). No suele requerir ninguna acción.

> **Identidad de sistema del entorno frente a la de la app:** la identidad de sistema de una *app* no existe hasta que la app se crea, lo que obligaría a arrancar con una imagen pública y actualizar después. La identidad de sistema del **entorno** existe antes que la app y se autoriza en el propio asistente, evitando ese arranque en dos fases.

### Actualizar la aplicación (nueva versión de la imagen)

Cada cambio de código implica reconstruir la imagen, subirla con una **nueva etiqueta** (línea de comandos, mismo método del Paso 3) y, desde el portal, crear una nueva **revisión** que apunte a ella:

```bash
az login --identity
az acr login --name miregistro
docker build -t miregistro.azurecr.io/mi-app:v2 .
docker push miregistro.azurecr.io/mi-app:v2
```

1. En el portal, abre la **Container App** → **Administración de revisiones** → **Crear nueva revisión**.
2. Edita el contenedor y cambia la **etiqueta** de la imagen a `v2` (manteniendo la misma identidad de registro del entorno).
3. **Crea** la revisión; Container Apps desplegará la nueva versión.

> Es una buena práctica usar **etiquetas versionadas** (`v1`, `v2`, un *hash* de commit…) en lugar de `latest`, para que cada revisión sea trazable y reproducible.

### Resumen de servicios y conceptos de Azure

| Elemento | Servicio / recurso | Se crea o configura en | Función |
|---|---|---|---|
| **Grupo de recursos** | Resource Group | Portal | Agrupa lógicamente todos los recursos. |
| **Registro remoto** | Azure Container Registry (ACR) | Portal | Almacena de forma privada las imágenes Docker. |
| **Entorno** | Container Apps Environment | Portal | Frontera de red y *logs*; aloja su identidad de sistema. |
| **Aplicación** | Azure Container App | Portal | Ejecuta el contenedor de forma *serverless*. |
| **Identidad (descarga)** | Identidad de sistema del *entorno* | Portal (asistente de la app) | Autentica el *pull* del ACR sin contraseñas. |
| **Permiso de descarga** | Rol `AcrPull` (sobre la identidad del entorno) | Portal (automático en el asistente; o IAM del ACR) | Permite descargar la imagen del ACR. |
| **Subida de imagen** | `az login --identity` + `az acr login` + `docker push` | Línea de comandos | Publica la imagen local en el registro. |
| **Permiso de subida** | Rol `AcrPush` (sobre la identidad de la máquina) | Portal (IAM del ACR) | Permite hacer *push* de imágenes al ACR. |

> **Resumen de autenticación:** la **subida** se autentica con la identidad administrada de la máquina de compilación (`az login --identity` + `az acr login`, con rol `AcrPush`); la **descarga** en ejecución usa la **identidad de sistema del entorno** de Container Apps (con rol `AcrPull`). En ningún momento se almacenan usuarios ni contraseñas.

---

## Apéndice A: instalación de Docker

### En Windows

[Tutorial para instalar Docker en Windows](https://www.youtube.com/watch?v=ZyBBv1JmnWQ&ab_channel=CodeBear)

### En Linux (Ubuntu/Debian)

En Linux se instala **Docker Engine** desde el repositorio APT oficial de Docker, que proporciona siempre la última versión estable del *engine*, la CLI, *containerd* y los *plugins* de Compose y Buildx. Es el método recomendado frente al paquete `docker.io` de las distribuciones (suele estar desactualizado) y frente al *script* de conveniencia (recomendado solo para pruebas).

**1. Eliminar versiones antiguas o en conflicto:**

```bash
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt remove -y $pkg
done
```

**2. Añadir la clave GPG oficial de Docker:**

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

**3. Añadir el repositorio de Docker a las fuentes de APT:**

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
```

**4. Instalar Docker Engine y sus componentes:**

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

**5. Verificar la instalación:**

```bash
sudo docker run hello-world
```

> **Post-instalación (uso sin `sudo`):** por defecto Docker requiere privilegios de superusuario. Para ejecutar `docker` sin `sudo`, añade tu usuario al grupo `docker` y reinicia la sesión:
>
> ```bash
> sudo usermod -aG docker $USER
> newgrp docker
> ```
>
> El cambio surte efecto tras cerrar y volver a iniciar sesión. Ten en cuenta que pertenecer al grupo `docker` equivale a privilegios de *root*, por lo que debe concederse con criterio.

> Para otras distribuciones (Debian, Fedora, CentOS) o versiones concretas, consulta la [guía oficial de instalación](https://docs.docker.com/engine/install/).

---

## Apéndice B: redes en Docker

Docker gestiona la comunicación de los contenedores mediante **redes virtuales**. Entender los tipos de red (*drivers*) es clave para diseñar arquitecturas de microservicios, donde los servicios necesitan comunicarse entre sí de forma aislada y controlada.

### Tipos de red (*drivers*)

- **`bridge`** (por defecto) — red privada interna en el anfitrión. Los contenedores conectados a ella se comunican entre sí, y hacia el exterior salen a través de la IP del anfitrión. Es el *driver* más habitual para aplicaciones en una sola máquina.
- **`host`** — el contenedor comparte directamente la pila de red del anfitrión, sin aislamiento ni capa intermedia. Ofrece mayor rendimiento, pero el contenedor deja de tener su propia IP y los puertos se publican directamente en el anfitrión.
- **`none`** — el contenedor no tiene ninguna interfaz de red. Se usa cuando se requiere aislamiento total.
- **`overlay`** — conecta contenedores que se ejecutan en **anfitriones distintos**, formando una red distribuida. Es la base de las orquestaciones multi-nodo (Docker Swarm, Kubernetes).
- **`macvlan`** — asigna a cada contenedor una dirección MAC propia, de modo que aparezca en la red física como un dispositivo más. Útil para integrarse con redes ya existentes.

### Bridge por defecto frente a bridge definida por el usuario

Docker crea una red `bridge` por defecto, pero **se recomienda crear redes `bridge` propias** para las aplicaciones. La diferencia principal es la **resolución de nombres**:

- En la red `bridge` **por defecto**, los contenedores solo se localizan entre sí por dirección IP.
- En una red `bridge` **definida por el usuario**, Docker proporciona un **DNS interno** que permite a los contenedores comunicarse usando su **nombre** (o *alias*) en lugar de la IP.

Esto último es fundamental en microservicios: un servicio puede dirigirse a otro con `http://nombre_servicio:puerto` sin conocer ni fijar direcciones IP, que además son volátiles entre reinicios.

```bash
# Crear una red propia
docker network create --driver bridge mi_red

# Lanzar dos contenedores en ella
docker run -d --name api --network mi_red mi_imagen_api
docker run -d --name web --network mi_red mi_imagen_web

# Desde 'web', 'api' es alcanzable directamente por su nombre:
#   http://api:8000
```

### Direccionamiento: `--subnet` e `--ip-range`

Al crear una red propia se puede controlar el **rango de direcciones IP** que utilizará, mediante los argumentos `--subnet` e `--ip-range` que aparecen en el comando `docker network create`. Si no se especifican, Docker asigna un rango por defecto automáticamente.

Ambos se expresan en **notación CIDR** (`dirección/prefijo`). El prefijo indica cuántos bits iniciales identifican la red; los bits restantes quedan disponibles para las direcciones de los contenedores. Por ejemplo, `172.20.0.0/16` reserva los primeros 16 bits para la red, dejando los otros 16 para los *hosts* (unas 65 000 direcciones (2^(32 − prefijo)), desde `172.20.0.1` hasta `172.20.255.254`).

- **`--subnet`** define el **espacio de direcciones completo** de la red: el conjunto total de IPs que pertenecen a ella. Es el rango "grande".
- **`--ip-range`** define, **dentro de esa subred**, el subconjunto concreto de direcciones que Docker **asignará automáticamente** a los contenedores. Es un rango "más pequeño" contenido en el anterior.

¿Por qué separar ambos? Porque permite **reservar parte de la subred para asignación manual**. Docker solo reparte automáticamente IPs del `--ip-range`; las direcciones de la subred que quedan fuera de ese rango permanecen libres para asignarlas de forma fija (con `--ip` al lanzar un contenedor), sin riesgo de que Docker las ocupe por su cuenta.

```bash
docker network create mi_red \
  --subnet 172.20.0.0/16 \
  --ip-range 172.20.10.0/24
```

En este ejemplo:

- La red abarca todo `172.20.0.0/16` (de `172.20.0.1` a `172.20.255.254`).
- Docker asignará automáticamente a los contenedores solo direcciones del rango `172.20.10.0/24` (de `172.20.10.1` a `172.20.10.254`, unas 254 direcciones).
- El resto de la subred (p. ej. `172.20.50.x`) queda libre para asignación manual:

  ```bash
  docker run -d --name db --network mi_red --ip 172.20.50.5 postgres
  ```

Opcionalmente, `--gateway` fija la puerta de enlace de la red (si no se indica, Docker suele tomar la primera IP de la subred, p. ej. `172.20.0.1`).

> **Nota:** conviene usar rangos de **IP privadas** (`10.0.0.0/8`, `172.16.0.0/12` o `192.168.0.0/16`) y evitar solapamientos con otras redes de Docker o con la red física del anfitrión, ya que un solape provoca conflictos de enrutamiento.

### Inspeccionar una red

Para ver la configuración de una red y los contenedores conectados a ella:

```bash
docker network inspect <nombre_red>
```

### Publicación de puertos frente a comunicación interna

Conviene distinguir dos conceptos que suelen confundirse:

- **Comunicación interna** (contenedor ↔ contenedor): ocurre dentro de la red de Docker. No requiere publicar puertos; basta con que los contenedores compartan red.
- **Publicación de puertos** (`-p <host>:<container>`): expone un puerto del contenedor hacia el **exterior** (la máquina anfitriona). Solo es necesaria para los servicios que deben ser accesibles desde fuera de la red de Docker (p. ej. un API Gateway).

Como buena práctica, en una arquitectura de microservicios solo se publican al exterior los servicios que realmente lo necesitan; el resto se comunica de forma interna a través de una red propia.

---

## Apéndice C: volúmenes y persistencia de datos

Por defecto, el sistema de archivos de un contenedor es **efímero**: cuando el contenedor se elimina, todos los datos que contenía se pierden. Los **volúmenes** son el mecanismo de Docker para **persistir datos** más allá del ciclo de vida del contenedor y para **compartir información** entre el anfitrión y los contenedores, o entre varios contenedores.

### Tipos de almacenamiento

- **Volúmenes con nombre (*named volumes*)** — gestionados íntegramente por Docker y almacenados en un área propia del anfitrión (`/var/lib/docker/volumes/`). Son la opción **recomendada** para datos que deben persistir (bases de datos, ficheros generados por la aplicación), ya que Docker se encarga de su ciclo de vida y son portables entre entornos.
- **Montajes de enlace (*bind mounts*)** — mapean un directorio o fichero **concreto del anfitrión** a una ruta del contenedor. El contenido depende de la estructura de carpetas del anfitrión. Son ideales durante el **desarrollo**, para reflejar en el contenedor los cambios del código en tiempo real.
- **`tmpfs`** — almacenan datos únicamente en la **memoria RAM** del anfitrión, nunca en disco. Se usan para información temporal o sensible que no debe persistir (p. ej. secretos en tiempo de ejecución).

### Volumen con nombre frente a *bind mount*

| Criterio | Volumen con nombre | *Bind mount* |
|---|---|---|
| **Gestión** | La realiza Docker | La realiza el usuario (rutas del anfitrión) |
| **Ubicación** | Área interna de Docker | Ruta arbitraria del anfitrión |
| **Portabilidad** | Alta (independiente del anfitrión) | Baja (depende de la estructura de carpetas) |
| **Uso típico** | Persistencia en producción | Desarrollo, edición de código en vivo |

### Comandos básicos

```bash
# Crear un volumen con nombre
docker volume create <nombre_volumen>

# Listar volúmenes
docker volume ls

# Inspeccionar un volumen (ubicación, contenedores que lo usan, etc.)
docker volume inspect <nombre_volumen>

# Eliminar un volumen
docker volume rm <nombre_volumen>

# Eliminar todos los volúmenes no utilizados
docker volume prune
```

### Montar un volumen en un contenedor

Se emplea el argumento `-v` (o `--volume`) al crear o lanzar el contenedor, con la sintaxis `origen:destino[:modo]`:

```bash
# Volumen con nombre: 'datos' persiste aunque se elimine el contenedor
docker run -d --name db -v datos:/var/lib/postgresql/data postgres

# Bind mount: la carpeta local se refleja dentro del contenedor
docker run -d --name web -v /ruta/local/codigo:/app mi_imagen

# Modo de solo lectura (ro): el contenedor no puede modificar el contenido
docker run -d --name app -v config:/etc/app:ro mi_imagen
```

El **modo** final es opcional: `rw` (lectura y escritura, por defecto) o `ro` (solo lectura). Usar `ro` es una buena práctica de seguridad cuando el contenedor solo necesita **consumir** los datos, no modificarlos.

> **Nota:** al eliminar un contenedor con `docker rm`, sus volúmenes con nombre **no** se borran automáticamente; persisten hasta que se eliminan de forma explícita. Esto protege los datos frente a borrados accidentales del contenedor, pero conviene tenerlo presente para no acumular volúmenes huérfanos (de ahí la utilidad de `docker volume prune`).

---

## Apéndice D: instalación de la CLI de Azure (azure-cli) en la máquina virtual

El Paso 3 del despliegue (subir la imagen) se ejecuta desde una máquina que se autentica con `az login --identity`, lo que requiere tener instalada la **CLI de Azure**. El paquete se llama `azure-cli` y el comando que se usa después es `az`. Este apéndice cubre su instalación en una máquina virtual, con foco en Linux (el caso habitual de una VM de Azure).

### En Linux (Ubuntu/Debian) — método recomendado

Un único comando descarga y ejecuta el script oficial, que añade la clave de firma de Microsoft, configura el repositorio e instala el paquete:

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

Requiere `curl` y permisos de `sudo`. Está verificado para Ubuntu y Debian; en distribuciones derivadas puede ser necesario el método manual.

### En Linux (Ubuntu/Debian) — método manual por repositorio

Equivale al script anterior paso a paso; es preferible cuando se quiere control explícito o no ejecutar un script como superusuario. Mantiene las actualizaciones dentro de `apt` (`apt-get upgrade`):

```bash
# 1. Instalar dependencias
sudo apt-get update
sudo apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg

# 2. Importar la clave de firma de Microsoft
curl -sLS https://packages.microsoft.com/keys/microsoft.asc \
  | gpg --dearmor \
  | sudo tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null

# 3. Añadir el repositorio de azure-cli (según la versión de la distribución)
AZ_DIST=$(lsb_release -cs)
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $AZ_DIST main" \
  | sudo tee /etc/apt/sources.list.d/azure-cli.list

# 4. Instalar el paquete
sudo apt-get update
sudo apt-get install -y azure-cli
```

### En Linux (RHEL/CentOS/Fedora)

```bash
# Importar la clave y el repositorio de Microsoft (ajusta la versión de RHEL: 8, 9…)
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo dnf install -y https://packages.microsoft.com/config/rhel/9/packages-microsoft-prod.rpm

# Instalar
sudo dnf install -y azure-cli
```

### En Windows (opcional)

Si la VM es Windows, la vía más rápida es el gestor de paquetes:

```powershell
winget install -e --id Microsoft.AzureCLI
```

Alternativamente, se puede descargar e instalar el paquete **MSI** oficial. Tras instalar, conviene abrir una nueva terminal para que `az` quede en el `PATH`.

### Verificar la instalación

```bash
az version
```

Debe mostrar la versión de `azure-cli` y de sus componentes. Para actualizarla más adelante:

```bash
az upgrade
```

### Autenticación con la identidad de la máquina virtual

Una vez instalada la CLI, la VM se autentica con su **identidad administrada** (sin usuario ni contraseña), tal como se usa en el Paso 3. Para ello, la VM debe tener una identidad asignada **con el rol `AcrPush`** sobre el registro:

1. **Asignar la identidad a la VM (portal):** abre la máquina virtual → **Configuración → Identidad**. Activa la **Asignada por el sistema** (o añade una **Asignada por el usuario** en su pestaña) y guarda.
2. **Conceder `AcrPush` (portal):** en el **Container Registry → Control de acceso (IAM) → Agregar asignación de roles → `AcrPush` →** selecciona la identidad de la VM.
3. **Iniciar sesión y usar el registro (en la VM):**

```bash
az login --identity                 # usa la identidad de la VM
az acr login --name miregistro      # obtiene el token para Docker
```

> `az login --identity` funciona porque la VM expone su identidad a través del servicio de metadatos de la instancia (IMDS); no requiere navegador ni credenciales, por lo que es ideal en máquinas sin interfaz gráfica. A partir de aquí ya se pueden ejecutar `docker tag` y `docker push` del Paso 3.
