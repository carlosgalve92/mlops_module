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
